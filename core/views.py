from pathlib import Path
import logging
import numpy as np
import onnxruntime as ort
from PIL import Image
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from .forms import RegistroForm
from .models import Documento, Clasificacion, TipoDocumento
from .validadores import validar_imagen

logger = logging.getLogger(__name__)

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

logger.info("Cargando modelo ONNX")

logger.info(
    "Modelo: %s",
    MODEL_PATH
)

try:
    #Se carga el modelo
    session = ort.InferenceSession(
        str(MODEL_PATH),
        providers=["CPUExecutionProvider"]
    )

    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name

    logger.info("ONNX: modelo cargado correctamente")
    logger.info("Input: %s", input_name)
    logger.info("Output: %s", output_name)

except Exception:
    logger.exception("ONNX ERROR")
    session = None
    input_name = None
    output_name = None

#Aqui estoy preprocesando la imagen para el modelo
def preparar_imagen(image):
    """
    Prepara una imagen para ser procesada por el modelo ONNX.
    """
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
    """
    Muestra la página de explicación del funcionamiento de DOCUAI.
    """
    return render(
        request,
        "clasificador/explicacion.html"
    )

#Forzamos que inicien sesion para usar lo que sea
@login_required(login_url="/login/")
def inicio(request):
    """
    Gestiona la página principal y la clasificación de documentos.
    """
    #Comprobando si se ha enviado una imagen
    if request.method == "POST":
        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            logger.warning("No se ha recibido ningún archivo.")
            return JsonResponse(
                {
                    "error": "No se ha recibido ningún archivo."
                },
                status=400
            )
        try:
            validar_imagen(
                uploaded_file
            )
            if session is None:
                logger.error(
                    "El modelo ONNX no está disponible."
                )
                return JsonResponse(
                    {
                        "error": (
                            "El modelo ONNX no pudo "
                            "cargarse en producción."
                        )
                    },
                    status=500
                )

            logger.info(
                "Documento recibido: %s",
                uploaded_file.name
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

            #Buscamos o creamos el tipo de documento
            tipo_documento, creado = (
                TipoDocumento.objects.get_or_create(
                    nombre=category
                )
            )

            #Creamos el documento en la base de datos
            documento = Documento.objects.create(
                usuario=request.user,
                formato_documento=uploaded_file.content_type,
                nombre_documento=uploaded_file.name
            )

            #Guardamos la clasificacion
            Clasificacion.objects.create(
                documento=documento,
                tipo_documento=tipo_documento,
                confianza=confidence_value
            )

            #Creacion del JSON
            resultado = {
                "document": uploaded_file.name,
                "category": category,
                "confidence": round(confidence_value,2),
            }

            logger.info(
                "Documento clasificado: %s | Categoría: %s | Confianza: %.2f%%",
                uploaded_file.name,
                category,
                confidence_value
            )

            request.session["resultado_json"] = resultado
            return JsonResponse(resultado)

        except Exception as e:
            logger.exception(
                "ERROR CLASIFICANDO: %s",
                uploaded_file.name
            )
            return JsonResponse({"error": str(e)},
                status=500
            )

    return render(
        request,
        "clasificador/index.html"
    )

def registro(request):
    """
    Gestiona el registro de nuevos usuarios.
    """
    #Forzamos la autenticación
    if request.user.is_authenticated:
        return redirect("inicio")
    #Comprobamos que los datos son correctos y guardamos el formulario
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            logger.info(
                "Usuario registrado: %s",
                user.username
            )
            return redirect("inicio")
    else:
        form = RegistroForm()

    return render(request,"clasificador/registro.html",{"form": form})

def resultado_json(request):
    """
    Muestra el resultado de la última clasificación realizada.
    """
    resultado = request.session.get("resultado_json")
    if not resultado:
        return redirect("inicio")
    return render(request,"clasificador/resultado.html",
        {
            "resultado": resultado
        }
    )
