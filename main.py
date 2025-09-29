import re
import markdown
from flask import Flask, request, jsonify, Response

app = Flask(__name__)

# Regex para bloques de código ```...```
CODEBLOCK_RE = re.compile(r'```.*?```', re.S)


def extract_codeblocks(md_text: str):
    """
    Extrae bloques de código (```...```) y los reemplaza por marcadores
    para que no se rompan en el procesamiento de Markdown.
    """
    codeblocks = {}
    counter = 0

    def repl(m):
        nonlocal counter
        key = f"§§CODE{counter}§§"
        codeblocks[key] = m.group(0)  # guardamos el bloque completo
        counter += 1
        return key

    md_text = CODEBLOCK_RE.sub(repl, md_text)
    return md_text, codeblocks


def restore_codeblocks(html: str, codeblocks: dict):
    """Restaura los bloques de código en el HTML final."""
    for key, block in codeblocks.items():
        block_html = markdown.markdown(block, extensions=["fenced_code"])
        html = html.replace(key, block_html)
    return html


def markdown_to_html(md_text: str) -> str:
    """
    Convierte Markdown a HTML completo con soporte de:
    - Tablas con bordes
    - Checklist como casillas reales
    - Bloques de código intactos
    """
    # Normalizar saltos
    md_text = md_text.replace("\r\n", "\n").replace("\r", "\n").replace("\\n", "\n")

    # 1) Extraer bloques de código
    md_text, codeblocks = extract_codeblocks(md_text)

    # 2) Procesar Markdown
    body_html = markdown.markdown(
        md_text,
        extensions=[
            "tables",
            "fenced_code",
            "sane_lists",
            "nl2br",
            "pymdownx.tilde",     # ~~tachado~~
            "pymdownx.tasklist"   # checklists
        ],
        extension_configs={
            "pymdownx.tasklist": {
                "custom_checkbox": True
            }
        }
    )

    # 3) Restaurar bloques de código
    body_html = restore_codeblocks(body_html, codeblocks)

    # 4) Envolver en HTML completo + CSS tablas
    full_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Markdown a HTML</title>
  <style>
    table, th, td {{ border: 1px solid black; border-collapse: collapse; }}
    th, td {{ padding: 4px; }}
  </style>
</head>
<body>
{body_html}
</body>
</html>"""

    return full_html


@app.post("/html")
def make_html():
    data = request.get_json(silent=True)
    if not data or "markdown" not in data:
        return jsonify({"error": "Bad request: falta 'markdown'"}), 400

    md_text = data["markdown"]
    html = markdown_to_html(md_text)

    return Response(html, mimetype="text/html")


# Render lo lanza con:
# gunicorn -w 4 -b 0.0.0.0:$PORT main:app
