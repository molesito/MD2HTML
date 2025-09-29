def markdown_to_html(md_text: str) -> str:
    """
    Convierte Markdown a HTML completo con soporte de:
    - Tablas con bordes
    - Checklist como casillas reales
    - Bloques de código intactos
    - Ecuaciones LaTeX protegidas (MathJax)
    """
    # Normalizar saltos
    md_text = md_text.replace("\r\n", "\n").replace("\r", "\n").replace("\\n", "\n")

    # 1) Extraer bloques de código
    md_text, codeblocks = extract_codeblocks(md_text)

    # 2) Proteger fórmulas LaTeX
    md_text, formulas = protect_math(md_text)

    # 3) Procesar Markdown
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

    # 4) Restaurar fórmulas y bloques de código
    body_html = restore_math(body_html, formulas)
    body_html = restore_codeblocks(body_html, codeblocks)

    # 5) Envolver en HTML completo + CSS tablas + MathJax
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

    # 6) Compactar espacios, pero mantener saltos de línea
    # Sustituimos solo espacios múltiples, no los \n
    return re.sub(r"[ \t]+", " ", full_html)
