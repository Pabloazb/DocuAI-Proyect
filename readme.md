DOCUAI es una aplicación web desarrollada con Django que clasifica imágenes de documentos usando un modelo de inteligencia artificial basado en ONNX. La idea principal es permitir a los usuarios registrar, iniciar sesión, subir imágenes y ver los resultados de la clasificación. Todo esto se almacena en una base de datos.

El sistema utiliza un modelo entrenado con ResNet-18 para reconocer 16 tipos diferentes de documentos: carta, formulario, correo electrónico, manuscrito, publicidad, informe científico, publicación científica, especificación, carpeta de archivos, artículo de noticias, presupuesto, factura, presentación, cuestionario, currículum y memorándum.

La aplicación está hecha con Python y Django, y usa el ORM para gestionar los datos. Se conecta a una base de datos SQLite localmente, pero en producción funciona con PostgreSQL mediante Neon. El modelo de IA se ejecuta con ONNX Runtime, y se procesan las imágenes con Pillow. También se usan NumPy, HTML, CSS y JavaScript para mejorar la interfaz.

Entre las funciones principales están el registro de usuarios, autenticación, subida de imágenes con validación, clasificación automática, cálculo del porcentaje de confianza del resultado, almacenamiento de datos y un panel de administración. Las imágenes admitidas son JPG, JPEG, PNG y TIFF. Los archivos se verifican antes de ser enviados al modelo.

La estructura del proyecto incluye carpetas como `config/`, `core/` (donde están los modelos, vistas, formularios), `modelo/` (archivos del modelo ONNX), `static/` (estilos y scripts), y `core/templates/` (plantillas HTML).

Para ejecutarlo localmente, hay que clonar el repositorio, crear un entorno virtual, instalar las dependencias desde `requirements.txt`, aplicar las migraciones con `python manage.py migrate` y crear un usuario administrador si se quiere acceder al panel de gestión. Luego se inicia el servidor con `runserver`.

La base de datos se maneja con Django ORM. Hay tres modelos principales: TipoDocumento, Documento y Clasificacion. Cada uno se relaciona con los demás para mantener los datos correctamente.

Antes de clasificar, la imagen se valida: se comprueba la extensión, el tamaño y si realmente es una imagen válida. Si hay problemas, se lanza la excepción personalizada `DocumentoInvalidoError`. Esto ayuda a distinguir errores de validación de fallos técnicos.

Se registra todo lo que pasa en el sistema gracias al módulo `logging`. Los mensajes van tanto a la consola como a un archivo llamado `docuai.log`. Así se puede revisar lo que ocurrió durante el proceso, especialmente cuando hay fallas.

En producción, la app se despliega en Vercel, y usa PostgreSQL por Neon. Las variables de entorno deben configurarse bien, y los archivos del modelo deben estar en su lugar correcto. Pero para probarlo localmente, no hace falta tener esa base de datos, ya que se usa SQLite por defecto.

El control de versiones se hace con Git y GitHub. Es importante hacer commits claros que expliquen qué cambios se hicieron.

No se deben subir al repositorio contraseñas, credenciales de servicios, archivos de entorno con secretos ni otros datos sensibles.

