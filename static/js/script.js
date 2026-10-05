const fileInput =
    document.getElementById("fileInput");

const uploadBox =
    document.getElementById("uploadBox");

const uploadButton =
    document.getElementById("uploadButton");

const fileName =
    document.getElementById("fileName");

const analyzeButton =
    document.getElementById("analyzeButton");

const resultCategory =
    document.getElementById("resultCategory");

const resultConfidence =
    document.getElementById("resultConfidence");

const resultMessage =
    document.getElementById("resultMessage");


let selectedFile = null;


// =========================================================
// SELECCIONAR ARCHIVO
// =========================================================

uploadButton.addEventListener(
    "click",
    function () {

        fileInput.click();

    }
);


fileInput.addEventListener(
    "change",
    function () {

        const file =
            this.files[0];

        if (file) {

            showFile(file);

        }

    }
);


// =========================================================
// MOSTRAR ARCHIVO SELECCIONADO
// =========================================================

function showFile(file) {

    selectedFile =
        file;

    fileName.textContent =
        file.name;

    analyzeButton.disabled =
        false;

    resultCategory.textContent =
        "—";

    resultConfidence.textContent =
        "—";

    resultMessage.textContent =
        "Documento preparado para analizar.";

}


// =========================================================
// ARRASTRAR ARCHIVO
// =========================================================

uploadBox.addEventListener(
    "dragover",
    function (event) {

        event.preventDefault();

        uploadBox.style.borderColor =
            "#4f46e5";

    }
);


uploadBox.addEventListener(
    "dragleave",
    function () {

        uploadBox.style.borderColor =
            "#cfd5e2";

    }
);


uploadBox.addEventListener(
    "drop",
    function (event) {

        event.preventDefault();

        uploadBox.style.borderColor =
            "#cfd5e2";

        const file =
            event.dataTransfer.files[0];

        if (file) {

            showFile(file);

        }

    }
);

analyzeButton.addEventListener(
    "click",
    async function () {

        if (!selectedFile) {
            return;
        }

        analyzeButton.disabled =
            true;
        resultMessage.textContent =
            "Analizando documento...";
        resultCategory.textContent =
            "Analizando...";
        resultConfidence.textContent =
            "—";

        const formData =
            new FormData();

        formData.append(
            "file",
            selectedFile
        );


        try {
            const response =
                await fetch(
                    window.location.href,
                    {
                        method: "POST",
                        body: formData,
                        headers: {
                            "X-CSRFToken":
                                getCookie(
                                    "csrftoken"
                                )
                        }
                    }
                );

            const data =
                await response.json();

            if (!response.ok) {

                throw new Error(
                    data.error ||
                    "Error al analizar el documento."
                );

            }

            resultCategory.textContent =
                data.category;

            resultConfidence.textContent =
                data.confidence + "%";

            resultMessage.textContent =
                data.message;

            console.log(
                "Resultado del modelo:",
                data
            );

            window.location.href =
                "/resultado/";

        } catch (error) {

            console.error(
                "Error:",
                error
            );

            resultCategory.textContent =
                "Error";
            resultConfidence.textContent =
                "—";
            resultMessage.textContent =
                error.message;

        } finally {
            analyzeButton.disabled =
                false;
        }
    }
);


// =========================================================
// OBTENER COOKIE CSRF
// =========================================================

function getCookie(name) {

    let cookieValue =
        null;


    if (
        document.cookie &&
        document.cookie !== ""
    ) {

        const cookies =
            document.cookie.split(";");

        for (
            let cookie of cookies
        ) {

            cookie =
                cookie.trim();


            if (
                cookie.substring(
                    0,
                    name.length + 1
                ) ===
                (name + "=")
            ) {

                cookieValue =
                    decodeURIComponent(
                        cookie.substring(
                            name.length + 1
                        )
                    );

                break;
            }
        }
    }
    return cookieValue;
}