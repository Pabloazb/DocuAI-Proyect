const fileInput = document.getElementById("fileInput");
const uploadBox = document.getElementById("uploadBox");
const uploadButton = document.getElementById("uploadButton");
const fileName = document.getElementById("fileName");
const analyzeButton = document.getElementById("analyzeButton");

const resultCategory = document.getElementById("resultCategory");
const resultConfidence = document.getElementById("resultConfidence");
const resultMessage = document.getElementById("resultMessage");

let selectedFile = null;


uploadButton.addEventListener("click", function () {

    fileInput.click();

});


fileInput.addEventListener("change", function () {

    const file = this.files[0];

    if (file) {

        showFile(file);

    }

});

function showFile(file) {

    selectedFile = file;

    fileName.textContent = file.name;

    analyzeButton.disabled = false;

    resultCategory.textContent = "—";

    resultConfidence.textContent = "—";

    resultMessage.textContent =
        "Documento preparado para analizar.";

}

uploadBox.addEventListener("dragover", function (event) {

    event.preventDefault();

    uploadBox.style.borderColor = "#4f46e5";

});


uploadBox.addEventListener("dragleave", function () {

    uploadBox.style.borderColor = "#cfd5e2";

});


uploadBox.addEventListener("drop", function (event) {

    event.preventDefault();

    uploadBox.style.borderColor = "#cfd5e2";

    const file = event.dataTransfer.files[0];

    if (file) {

        showFile(file);

    }

});


analyzeButton.addEventListener("click", function () {

    if (!selectedFile) {

        return;

    }

    analyzeButton.disabled = true;

    resultMessage.textContent =
        "Analizando documento...";

    resultCategory.textContent =
        "Analizando...";

    resultConfidence.textContent =
        "—";

    setTimeout(function () {

        const categories = [
            "invoice",
            "letter",
            "form",
            "resume",
            "email"
        ];

        const randomCategory =
            categories[
                Math.floor(
                    Math.random() * categories.length
                )
            ];

        const confidence =
            (90 + Math.random() * 9).toFixed(2);


        resultCategory.textContent =
            randomCategory;

        resultConfidence.textContent =
            confidence + "%";


        resultMessage.textContent =
            "Documento clasificado correctamente.";


        analyzeButton.disabled = false;

    }, 1500);

});