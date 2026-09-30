from pathlib import Path

import torch
from torchvision.models import resnet18


BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "modelo" / "modelo_rvlcdip_resnet18.pth"
ONNX_PATH = BASE_DIR / "modelo" / "modelo_rvlcdip_resnet18.onnx"


print("Cargando modelo PyTorch...")

model = resnet18(weights=None)

model.fc = torch.nn.Linear(
    model.fc.in_features,
    16
)

model.load_state_dict(
    torch.load(
        MODEL_PATH,
        map_location="cpu"
    )
)

model.eval()

print("Modelo cargado correctamente.")
print("Convirtiendo a ONNX...")


dummy_input = torch.randn(
    1,
    3,
    224,
    224
)


torch.onnx.export(
    model,
    dummy_input,
    ONNX_PATH,
    input_names=["input"],
    output_names=["output"],
    dynamic_axes={
        "input": {0: "batch"},
        "output": {0: "batch"},
    },
    opset_version=18,
)


print("Conversión terminada.")
print("Archivo:", ONNX_PATH)