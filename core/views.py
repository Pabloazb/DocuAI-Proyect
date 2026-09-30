from django.contrib.auth.decorators import login_required
from pathlib import Path

import numpy as np
import onnxruntime as ort
from PIL import Image

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login

from .forms import RegistroForm


BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    BASE_DIR
    / "modelo"
    / "modelo_rvlcdip_resnet18.onnx"
)


CLASS_NAMES = {
    0: "letter",
    1: "form",
    2: "email",
    3: "handwritten",
    4: "advertisement",
    5: "scientific_report",
    6: "scientific_publication",
    7: "specification",
    8: "file_folder",
    9: "news_article",
    10: "budget",
    11: "invoice",
    12: "presentation",
    13: "questionnaire",
    14: "resume",
    15: "memo",
}


print("Cargando modelo ONNX...")
print("Modelo:", MODEL_PATH)


session = ort.InferenceSession(
    str(MODEL_PATH),
    providers=["CPUExecutionProvider"]
)


input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name


print("Modelo ONNX cargado correctamente.")


def preparar_imagen(image):
    image = image.resize((224, 224))

    image = np.array(image).astype(np.float32) / 255.0

    mean = np.array(
        [0.485, 0.456, 0.406],
        dtype=np.float32
    )

    std = np.array(
        [0.229, 0.224, 0.225],
        dtype=np.float32
    )

    image = (image - mean) / std

    image = np.transpose(
        image,
        (2, 0, 1)
    )

    image = np.expand_dims(
        image,
        axis=0
    )

    return image.astype(np.float32)


def explicacion(request):
    return render(
        request,
        "clasificador/explicacion.html"
    )


@login_required(login_url="/login/")
def inicio(request):

    if request.method == "POST":

        uploaded_file = request.FILES.get("file")

        if not uploaded_file:
            return JsonResponse(
                {
                    "error": "No se ha recibido ningún archivo."
                },
                status=400
            )

        try:

            image = Image.open(
                uploaded_file
            ).convert("RGB")

            image_tensor = preparar_imagen(image)

            outputs = session.run(
                [output_name],
                {
                    input_name: image_tensor
                }
            )

            outputs = outputs[0]

            exp_outputs = np.exp(
                outputs - np.max(
                    outputs,
                    axis=1,
                    keepdims=True
                )
            )

            probabilities = (
                exp_outputs
                / exp_outputs.sum(
                    axis=1,
                    keepdims=True
                )
            )

            predicted_class = int(
                np.argmax(
                    probabilities,
                    axis=1
                )[0]
            )

            confidence_value = (
                float(
                    probabilities[
                        0,
                        predicted_class
                    ]
                )
                * 100
            )

            category = CLASS_NAMES[
                predicted_class
            ]

            return JsonResponse(
                {
                    "category": category,
                    "confidence": round(
                        confidence_value,
                        2
                    ),
                    "message": (
                        "Documento clasificado correctamente."
                    )
                }
            )

        except Exception as e:

            print("ERROR:", e)

            return JsonResponse(
                {
                    "error": str(e)
                },
                status=500
            )

    return render(
        request,
        "clasificador/index.html"
    )


def registro(request):

    if request.user.is_authenticated:
        return redirect("inicio")

    if request.method == "POST":

        form = RegistroForm(request.POST)

        if form.is_valid():

            user = form.save()

            login(
                request,
                user
            )

            return redirect("inicio")

    else:

        form = RegistroForm()

    return render(
        request,
        "clasificador/registro.html",
        {
            "form": form
        }
    )