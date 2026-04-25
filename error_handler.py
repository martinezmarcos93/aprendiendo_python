def explicar_error(error_msg):
    error_msg = error_msg.lower()

    # -------------------------
    # SYNTAX ERROR
    # -------------------------
    if "syntaxerror" in error_msg:
        return (
            "❌ Error de sintaxis\n\n"
            "Python no entendió cómo escribiste una línea.\n\n"
            "💡 Posibles causas:\n"
            "- Te faltó un : (dos puntos)\n"
            "- Te faltó un paréntesis\n"
            "- Escribiste algo en un orden incorrecto\n\n"
            "👉 Revisá bien esa línea."
        )

    # -------------------------
    # VARIABLE NO DEFINIDA
    # -------------------------
    elif "nameerror" in error_msg:
        return (
            "❌ Variable no definida\n\n"
            "Estás usando un nombre que no existe.\n\n"
            "💡 Ejemplo:\n"
            "mostrar edad  ← pero nunca creaste 'edad'\n\n"
            "👉 Primero tenés que crear la variable con 'es'."
        )

    # -------------------------
    # TIPO DE DATO
    # -------------------------
    elif "typeerror" in error_msg:
        return (
            "❌ Error de tipo\n\n"
            "Estás mezclando cosas que no van juntas.\n\n"
            "💡 Ejemplo:\n"
            "\"hola\" + 5  ❌\n\n"
            "👉 Convertí los datos o usá el mismo tipo."
        )

    # -------------------------
    # INDENTACIÓN
    # -------------------------
    elif "indentationerror" in error_msg:
        return (
            "❌ Error de indentación\n\n"
            "Python necesita espacios correctos para entender bloques.\n\n"
            "💡 Ejemplo:\n"
            "si algo:\n"
            "mostrar 'hola'  ❌ (falta espacio)\n\n"
            "👉 Asegurate de usar espacios debajo del bloque."
        )

    # -------------------------
    # DIVISIÓN POR CERO
    # -------------------------
    elif "zerodivisionerror" in error_msg:
        return (
            "❌ División por cero\n\n"
            "No se puede dividir por 0.\n\n"
            "👉 Cambiá el número por otro distinto de cero."
        )

    # -------------------------
    # VALOR INCORRECTO
    # -------------------------
    elif "valueerror" in error_msg:
        return (
            "❌ Valor incorrecto\n\n"
            "Ingresaste un valor que no es válido.\n\n"
            "💡 Ejemplo:\n"
            "int('hola')  ❌\n\n"
            "👉 Asegurate de ingresar el tipo correcto."
        )

    # -------------------------
    # ERROR GENÉRICO
    # -------------------------
    else:
        return (
            "❌ Ocurrió un error\n\n"
            "Algo salió mal, pero no es un error común.\n\n"
            "📄 Detalle técnico:\n"
            f"{error_msg}\n\n"
            "👉 Revisá tu código paso a paso."
        )