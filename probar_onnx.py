from pathlib import Path

import numpy as np
import onnxruntime as ort


BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = (
    BASE_DIR
    / "modelo"
    / "modelo_rvlcdip_resnet18.onnx"
)


print("Cargando modelo ONNX...")

session = ort.InferenceSession(
    str(MODEL_PATH),
    providers=["CPUExecutionProvider"]
)

print("Modelo ONNX cargado correctamente.")

input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name

print("Entrada:", input_name)
print("Salida:", output_name)


dummy_input = np.random.randn(
    1,
    3,
    224,
    224
).astype(np.float32)


outputs = session.run(
    [output_name],
    {
        input_name: dummy_input
    }
)


print("Inferencia realizada correctamente.")
print("Forma de salida:", outputs[0].shape)