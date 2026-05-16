import re
import tkinter as tk

class TortuHighlighter:
    PALABRAS_CLAVE = [
        "mostrar", "preguntar", "funcion", "devolver",
        "repetir", "veces", "mientras", "si", "sino",
        "Verdadero", "Falso", "es", "clase", "hereda", "de",
        "y", "o", "no",
        "avanzar", "girar_der", "girar_izq", "color", "bajar_lapiz", "subir_lapiz"
    ]
    
    PALABRAS_PYTHON = [
        "print", "input", "def", "return", "for", "in", "range",
        "while", "if", "else", "elif", "True", "False", "class",
        "and", "or", "not"
    ]

    def __init__(self, text_widget, es_python=False):
        self.text = text_widget
        self.es_python = es_python
        self.text.bind("<KeyRelease>", self.resaltar)
        
        # Colores (Tema oscuro tipo One Dark / VSCode)
        self.text.tag_config("keyword", foreground="#c678dd") # morado/rosa
        self.text.tag_config("string", foreground="#98c379")  # verde
        self.text.tag_config("number", foreground="#d19a66")  # naranja
        self.text.tag_config("comment", foreground="#5c6370") # gris
        self.text.tag_config("operator", foreground="#56b6c2") # cian

        self.resaltar() # Aplicar al inicio

    def resaltar(self, event=None):
        for tag in ["keyword", "string", "number", "comment", "operator"]:
            self.text.tag_remove(tag, "1.0", tk.END)

        contenido = self.text.get("1.0", "end-1c")
        if not contenido:
            return

        palabras = self.PALABRAS_PYTHON if self.es_python else self.PALABRAS_CLAVE

        # Operators
        for match in re.finditer(r'[\+\-\*/%=><!]', contenido):
            self._aplicar_tag("operator", match.start(), match.end())

        # Keywords
        patron_kw = r'\b(?:' + '|'.join(palabras) + r')\b'
        for match in re.finditer(patron_kw, contenido):
            self._aplicar_tag("keyword", match.start(), match.end())

        # Numbers
        for match in re.finditer(r'\b\d+\b', contenido):
            self._aplicar_tag("number", match.start(), match.end())
            
        # Strings
        for match in re.finditer(r'\"[^\"]*\"|\'[^\']*\'', contenido):
            self._aplicar_tag("string", match.start(), match.end())
            
        # Comments
        for match in re.finditer(r'#.*', contenido):
            self._aplicar_tag("comment", match.start(), match.end())

    def _aplicar_tag(self, tag, start, end):
        inicio_idx = f"1.0 + {start} chars"
        fin_idx = f"1.0 + {end} chars"
        self.text.tag_add(tag, inicio_idx, fin_idx)
