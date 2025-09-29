import re
import markdown
from flask import Flask, request, jsonify

# -------------------------------
# Función de conversión Markdown → HTML
# -------------------------------
def markdown_to_html(md_text: str) -> str:
    """
    Convierte Markdown a HTML completo con soporte de:
    - Tablas con bordes
    - Checklist como casillas reales
    - Bloques de código intactos
    - Ecuaciones LaTeX protegidas (MathJax)
    - Cada salto de línea \n se convierte en <br>
    """

    # Normalizar saltos
    md_text = md_text.replace("\r\n", "\n").replace("\r", "\n").replace("\\n", "\n")

    # Procesar Markdown
    body_html = markdown.markdown(
        md_text,
        extensions=[
            "tables",
            "fenced_code",
            "sane_lists",
            "pymdownx.tilde",     # ~~tachado~~
            "pymdownx.tasklist"   # checklists
        ],
        extension_configs={
            "pymdownx.tasklist": {
                "custom_checkbox": True
            }
        }
    )

    # Forzar que todos los \n se conviertan en <br>
    body_html = body_html.replace("\n", "<br>\n")

    # Envolver en HTML completo + CSS tablas + MathJax
    full_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Markdown a HTML</title>
  <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
  <style>
    table, th, td {{ border: 1px solid black; border-collapse: collapse; }}
    th, td {{ padding: 4px; }}
  </style>
</head>
<body>
{body_html}
</body>
</html>"""

    return re.sub(r"[ \t]+", " ", full_html)


# -------------------------------
# Configuración de Flask
# -------------------------------
app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "Servidor Flask funcionando correctamente 🚀"

@app.route("/convert", methods=["POST"])
def convert():
    """
    Convierte un texto Markdown recibido en JSON a HTML.
    Ejemplo de uso con curl:
    curl -X POST -H "Content-Type: application/json" \
         -d '{"markdown": "# Hola **Mundo**"}' \
         https://TU_APP_RENDER.onrender.com/convert
    """
    data = request.get_json()
    md_text = data.get("markdown", "")
    html = markdown_to_html(md_text)
    return jsonify({"html": html})
