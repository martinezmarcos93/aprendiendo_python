# Cada ejercicio enseña UNA cosa nueva o combina las anteriores (sin repetidos).
# La primera vez que aparece una palabra de TortuScript, la consigna muestra su "Forma".
# La evaluación compara lo que MUESTRA el programa con lo que muestra la solución,
# así que cualquier forma de llegar al mismo resultado es válida.
EJERCICIOS = [

# =========================
# NIVEL 1 - MOSTRAR
# =========================
{"nivel":1,"titulo":"1. Hola mundo",
 "descripcion":'Hacé que aparezca el texto Hola mundo.   Forma:  mostrar "tu texto"',
 "solucion":'mostrar "Hola mundo"'},
{"nivel":1,"titulo":"2. Texto o cuenta",
 "descripcion":"Utiliza mostrar 7+3 con comillas y luego en el renglon de abajo sin comillas, veras la diferencia",
 "solucion":'mostrar "7 + 3"\nmostrar 7 + 3'},
{"nivel":1,"titulo":"3. Dos líneas",
 "descripcion":"Mostrá Hola y, en la línea siguiente, Chau. Cada mostrar escribe una línea nueva.",
 "solucion":'mostrar "Hola"\nmostrar "Chau"'},

# =========================
# NIVEL 2 - VARIABLES
# =========================
{"nivel":2,"titulo":"4. Tu primera variable",
 "descripcion":"Guardá el número 12 en una variable llamada edad y mostrala.   Forma:  edad es 12. Llama a la variable edad sin comillas",
 "solucion":"edad es 12\nmostrar edad"},
{"nivel":2,"titulo":"5. Variable de texto",
 "descripcion":"Guardá el texto Juan en una variable llamada nombre y mostrala (el texto va con comillas).",
 "solucion":'nombre es "Juan"\nmostrar nombre'},
{"nivel":2,"titulo":"6. Dos variables",
 "descripcion":"Creá a con 5 y b con 10, y mostrá cada una en su línea.",
 "solucion":"a es 5\nb es 10\nmostrar a\nmostrar b"},

# =========================
# NIVEL 3 - PREGUNTAR
# =========================
{"nivel":3,"titulo":"7. Pedir el nombre",
 "descripcion":'Pedí el nombre y mostralo.   Forma:  nombre es preguntar("¿Cómo te llamás? ")',
 "solucion":'nombre es preguntar("¿Cómo te llamás? ")\nmostrar nombre'},
{"nivel":3,"titulo":"8. Saludo",
 "descripcion":"Pedí el nombre y mostrá Hola seguido del nombre (por ejemplo: Hola Juan). Los textos se pegan con +",
 "solucion":'nombre es preguntar("¿Cómo te llamás? ")\nmostrar "Hola " + nombre'},
{"nivel":3,"titulo":"9. Comida favorita",
 "descripcion":"Pedí la comida favorita y mostrá: Mi comida favorita es: (y la comida)",
 "solucion":'comida es preguntar("¿Cuál es tu comida favorita? ")\nmostrar "Mi comida favorita es: " + comida'},

# =========================
# NIVEL 4 - CUENTAS
# =========================
{"nivel":4,"titulo":"10. Suma",
 "descripcion":"Mostrá el resultado de 5 + 3 (sin comillas, así la cuenta la hace la compu).",
 "solucion":"mostrar 5 + 3"},
{"nivel":4,"titulo":"11. Resta y multiplicación",
 "descripcion":"Mostrá el resultado de 10 - 3 y, en la línea siguiente, el de 4 * 2 (el * es multiplicar).",
 "solucion":"mostrar 10 - 3\nmostrar 4 * 2"},
{"nivel":4,"titulo":"12. Sumar variables",
 "descripcion":"Guardá a con 5 y b con 7, y mostrá la suma de las dos variables.",
 "solucion":"a es 5\nb es 7\nmostrar a + b"},

# =========================
# NIVEL 5 - CONDICIONALES
# =========================
{"nivel":5,"titulo":"13. Si es grande",
 "descripcion":"Guardá n con 15. Si n es mayor que 10, mostrá Grande.   Forma:  si n > 10:   (y abajo, corrido 4 espacios, lo que pasa)",
 "solucion":"n es 15\nsi n > 10:\n    mostrar \"Grande\""},
{"nivel":5,"titulo":"14. Par",
 "descripcion":"Guardá n con 4. Si n es par, mostrá Par. Un número es par si  n % 2 == 0  (el resto de dividir por 2 es 0).",
 "solucion":"n es 4\nsi n % 2 == 0:\n    mostrar \"Par\""},
{"nivel":5,"titulo":"15. Par o impar",
 "descripcion":"Guardá n con 5 y mostrá Par o Impar según corresponda.   Forma:  sino:   (va a la misma altura que el si, y abajo lo que pasa si NO se cumple)",
 "solucion":"n es 5\nsi n % 2 == 0:\n    mostrar \"Par\"\nsino:\n    mostrar \"Impar\""},

# =========================
# NIVEL 6 - REPETIR
# =========================
{"nivel":6,"titulo":"16. Repetir",
 "descripcion":"Mostrá Hola 3 veces.   Forma:  repetir 3 veces:   (y abajo, corrido 4 espacios, lo que se repite)",
 "solucion":"repetir 3 veces:\n    mostrar \"Hola\""},
{"nivel":6,"titulo":"17. Contador",
 "descripcion":"Contá del 1 al 5, un número por línea, usando repetir y una variable a la que le sumás 1 cada vuelta.",
 "solucion":"contador es 1\nrepetir 5 veces:\n    mostrar contador\n    contador es contador + 1"},
{"nivel":6,"titulo":"18. Sumar en un bucle",
 "descripcion":"Sumá los números del 1 al 5 con un bucle y mostrá solo el total al final.",
 "solucion":"suma es 0\ncontador es 1\nrepetir 5 veces:\n    suma es suma + contador\n    contador es contador + 1\nmostrar suma"},

# =========================
# NIVEL 7 - FUNCIONES
# =========================
{"nivel":7,"titulo":"19. Tu primera función",
 "descripcion":'Creá la función saludar(nombre) que muestre Hola + nombre, y llamala con "Ana".   Forma:  funcion saludar(nombre):',
 "solucion":"funcion saludar(nombre):\n    mostrar \"Hola \" + nombre\n\nsaludar(\"Ana\")"},
{"nivel":7,"titulo":"20. Función con dos datos",
 "descripcion":"Creá la función sumar(a, b) que muestre la suma, y llamala con 3 y 4.",
 "solucion":"funcion sumar(a, b):\n    mostrar a + b\n\nsumar(3, 4)"},
{"nivel":7,"titulo":"21. Función que devuelve",
 "descripcion":"Creá la función doble(n) que DEVUELVA el doble, y mostrá doble(5).   Forma:  devolver n * 2",
 "solucion":"funcion doble(n):\n    devolver n * 2\n\nmostrar doble(5)"},

# =========================
# NIVEL 8 - DESAFÍOS (combinan lo anterior)
# =========================
{"nivel":8,"titulo":"22. Saludo repetido",
 "descripcion":"Guardá el nombre Ana y mostrá Hola Ana 3 veces (variable + repetir).",
 "solucion":"nombre es \"Ana\"\nrepetir 3 veces:\n    mostrar \"Hola \" + nombre"},
{"nivel":8,"titulo":"23. El mayor",
 "descripcion":"Guardá a con 5 y b con 8, y mostrá el mayor de los dos usando si y sino.",
 "solucion":"a es 5\nb es 8\nsi a > b:\n    mostrar a\nsino:\n    mostrar b"},
{"nivel":8,"titulo":"24. Tabla del 2",
 "descripcion":"Mostrá la tabla del 2 del 1 al 5: 2, 4, 6, 8 y 10, uno por línea (repetir + contador).",
 "solucion":"n es 2\ncontador es 1\nrepetir 5 veces:\n    mostrar n * contador\n    contador es contador + 1"},
{"nivel":8,"titulo":"25. Cuenta regresiva",
 "descripcion":"Mostrá 5, 4, 3, 2 y 1 (uno por línea) y al final Despegue (repetir + restar 1).",
 "solucion":"n es 5\nrepetir 5 veces:\n    mostrar n\n    n es n - 1\nmostrar \"Despegue\""},
{"nivel":8,"titulo":"26. Texto y números",
 "descripcion":"Guardá nombre con Ana y edad con 11, y mostrá: Ana tiene 11 años. Tip: mostrar puede recibir varias cosas separadas por comas.",
 "solucion":"nombre es \"Ana\"\nedad es 11\nmostrar nombre, \"tiene\", edad, \"años\""},
{"nivel":8,"titulo":"27. Solo los pares",
 "descripcion":"Del 1 al 10, mostrá solo los números pares, uno por línea (repetir + si).",
 "solucion":"n es 1\nrepetir 10 veces:\n    si n % 2 == 0:\n        mostrar n\n    n es n + 1"},
{"nivel":8,"titulo":"28. Contraseña",
 "descripcion":"Guardá clave con \"tortuga\". Si la clave es tortuga, mostrá Correcto; si no, mostrá Incorrecto.",
 "solucion":"clave es \"tortuga\"\nsi clave == \"tortuga\":\n    mostrar \"Correcto\"\nsino:\n    mostrar \"Incorrecto\""},
{"nivel":8,"titulo":"29. Mientras",
 "descripcion":"Mostrá los números del 1 al 3 usando mientras (repite MIENTRAS la condición se cumpla).   Forma:  mientras n <= 3:",
 "solucion":"n es 1\nmientras n <= 3:\n    mostrar n\n    n es n + 1"},
{"nivel":8,"titulo":"30. Desafío final",
 "descripcion":"Creá la función par_o_impar(n) que muestre Par o Impar, y llamala con 7 y después con 10.",
 "solucion":"funcion par_o_impar(n):\n    si n % 2 == 0:\n        mostrar \"Par\"\n    sino:\n        mostrar \"Impar\"\n\npar_o_impar(7)\npar_o_impar(10)"},

]
