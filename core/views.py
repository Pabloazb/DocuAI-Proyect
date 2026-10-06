from pathlib import Path
import numpy as np
import onnxruntime as ort
from PIL import Image
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from .forms import RegistroForm

BASE_DIR = Path(__file__).resolve().parent.parent
#Buscamos el modelo en la carpeta 
MODEL_PATH = (BASE_DIR/ "modelo"/ "modelo_rvlcdip_resnet18.onnx")

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

# =========================================================
# CARGA DEL MODELO ONNX
# =========================================================

print("Cargando modelo ONNX...")
print("Modelo:", MODEL_PATH)

try:
    #Se carga el modelo
    session = ort.InferenceSession(
        str(MODEL_PATH),
        providers=["CPUExecutionProvider"]
    )

    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name
    print("ONNX: modelo cargado correctamente")
    print("Input:", input_name)
    print("Output:", output_name)

except Exception as e:
    print("ONNX ERROR:", repr(e))
    session = None
    input_name = None
    output_name = None

#Aqui estoy preprocesando la imagen para el modelo
def preparar_imagen(image):
    #Redimensionando la imagen para que se pueda pasar cualquier imagen
    image = image.resize((224, 224))
    #Aqui lo convierto a numeros 
    image = np.array(image).astype(np.float32) / 255.0
    #Normalizacion
    mean = np.array([0.485, 0.456, 0.406],dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    image = (image - mean) / std
    #Aqui cambio el orden de las dimensiones de la imagen
    image = np.transpose(image,  (2, 0, 1))
    #Aqui lo que hago es dimensionar la imgaen
    image = np.expand_dims( image, axis=0)
    return image.astype(np.float32)


def explicacion(request):
    return render(
        request,
        "clasificador/explicacion.html"
    )

#Forzamos que inicien sesion para usar lo que sea
@login_required(login_url="/login/")
def inicio(request):
    #Comprobando si se ha enviado una imagen
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
            if session is None:
                return JsonResponse(
                    {
                        "error": (
                            "El modelo ONNX no pudo "
                            "cargarse en producción."
                        )
                    },
                    status=500
                )

            # Abrir imagen
            image = Image.open(
                uploaded_file
            ).convert("RGB")

            # Preparar imagen
            image_tensor = preparar_imagen(
                image
            )

            outputs = session.run(
                [output_name],{input_name: image_tensor}
            )
            outputs = outputs[0]

            # Esto convierte los resultados del modelo en nu mumeros para dar una resapuesta
            exp_outputs = np.exp(outputs- np.max(outputs,axis=1,keepdims=True))

            probabilities = (exp_outputs/ exp_outputs.sum(axis=1,keepdims=True))

            # Esto nos permite dedcuir la clase
            predicted_class = int(np.argmax(probabilities,axis=1)[0])

            #Esto es para el valor de confianza
            confidence_value = (
                float(probabilities[0,predicted_class])* 100
            )

            category = CLASS_NAMES[
                predicted_class
            ]
            #Creacion del JSON
            resultado = {
                "document": uploaded_file.name,
                "category": category,
                "confidence": round(confidence_value,2),
            }

            request.session["resultado_json"] = resultado
            return JsonResponse(resultado)

        except Exception as e:
            print("ERROR CLASIFICANDO:", repr(e))
            return JsonResponse({"error": str(e)},
                status=500
            )

    return render(
        request,
        "clasificador/index.html"
    )

def registro(request):
    #Forzamos la autenticación
    if request.user.is_authenticated:
        return redirect("inicio")
    #Comprobamos que los datos son correctos y guardamos el formulario
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect("inicio")
    else:
        form = RegistroForm()

    return render(request,"clasificador/registro.html",{"form": form})

def resultado_json(request):
    resultado = request.session.get("resultado_json")
    if not resultado:
        return redirect("inicio")
    return render(request,"clasificador/resultado.html",
        {
            "resultado": resultado
        }
    )