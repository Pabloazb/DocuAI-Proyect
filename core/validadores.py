from pathlib import Path

from PIL import Image, UnidentifiedImageError


EXTENSIONES_PERMITIDAS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".tiff",
}


def validar_imagen(uploaded_file):
    extension = Path(
        uploaded_file.name
    ).suffix.lower()

    if extension not in EXTENSIONES_PERMITIDAS:
        raise ValueError(
            "El formato del archivo no esta permitido. "
        )

    if uploaded_file.size == 0:
        raise ValueError(
            "El archivo esta vacio."
        )

    try:
        image = Image.open(uploaded_file)
        image.verify()

    except (UnidentifiedImageError,OSError) as e:
        raise ValueError(
            "El archivo no contiene una imagen valida."
        ) from e

    uploaded_file.seek(0)

    return True