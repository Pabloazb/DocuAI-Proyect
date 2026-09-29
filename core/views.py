from django.contrib.auth.decorators import login_required
from pathlib import Path
import torch
from torchvision.models import resnet18
from torchvision import transforms
from PIL import Image
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth import login
from django.shortcuts import redirect
from .forms import RegistroForm

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "modelo" / "modelo_rvlcdip_resnet18.pth"


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


DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


print("Cargando modelo ResNet18...")
print("Modelo:", MODEL_PATH)
print("Dispositivo:", DEVICE)


model = resnet18(weights=None)

model.fc = torch.nn.Linear(
    model.fc.in_features,
    16
)


model.load_state_dict(
    torch.load(
        MODEL_PATH,
        map_location=DEVICE
    )
)


model = model.to(DEVICE)
model.eval()


print("Modelo cargado correctamente.")


transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


def explicacion(request):
    return render(request, "clasificador/explicacion.html")

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

            image_tensor = transform(image)

            image_tensor = image_tensor.unsqueeze(0)

            image_tensor = image_tensor.to(DEVICE)

            with torch.no_grad():

                outputs = model(image_tensor)

                probabilities = torch.softmax(
                    outputs,
                    dim=1
                )

                confidence, predicted = torch.max(
                    probabilities,
                    dim=1
                )

            predicted_class = predicted.item()

            confidence_value = (
                confidence.item() * 100
            )

            category = CLASS_NAMES[predicted_class]

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
    return render(request, "clasificador/index.html")

def registro(request):
    if request.user.is_authenticated:
        return redirect("inicio")

    if request.method == "POST":
        form = RegistroForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("inicio")
    else:
        form = RegistroForm()

    return render(
        request,
        "clasificador/registro.html",
        {"form": form}
    )