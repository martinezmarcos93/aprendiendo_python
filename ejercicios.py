EJERCICIOS = [

# =========================
# NIVEL 1 - MOSTRAR
# =========================
{"nivel":1,"titulo":"1. Hola mundo","descripcion":"Mostrá: Hola mundo","solucion":'mostrar "Hola mundo"'},
{"nivel":1,"titulo":"2. Mensaje","descripcion":"Mostrá: Aprender es divertido","solucion":'mostrar "Aprender es divertido"'},
{"nivel":1,"titulo":"3. Dos mensajes","descripcion":"Mostrá dos mensajes distintos","solucion":'mostrar "Hola"\nmostrar "Chau"'},

# =========================
# NIVEL 2 - VARIABLES
# =========================
{"nivel":2,"titulo":"4. Variable simple","descripcion":"Creá una variable edad=12 y mostrála","solucion":"edad es 12\nmostrar edad"},
{"nivel":2,"titulo":"5. Nombre","descripcion":"Guardá tu nombre y mostralo","solucion":'nombre es "Juan"\nmostrar nombre'},
{"nivel":2,"titulo":"6. Dos variables","descripcion":"Creá a=5 y b=10 y mostralas","solucion":"a es 5\nb es 10\nmostrar a\nmostrar b"},

# =========================
# NIVEL 3 - INPUT
# =========================
{"nivel":3,"titulo":"7. Pedir nombre","descripcion":"Pedí el nombre y mostralo","solucion":'nombre es preguntar("Nombre: ")\nmostrar nombre'},
{"nivel":3,"titulo":"8. Saludo","descripcion":"Saludar con el nombre","solucion":'nombre es preguntar("Nombre: ")\nmostrar "Hola " + nombre'},
{"nivel":3,"titulo":"9. Edad","descripcion":"Pedí edad y mostrála","solucion":'edad es preguntar("Edad: ")\nmostrar edad'},

# =========================
# NIVEL 4 - OPERACIONES
# =========================
{"nivel":4,"titulo":"10. Suma","descripcion":"Mostrar 5+3","solucion":"mostrar 5 + 3"},
{"nivel":4,"titulo":"11. Multiplicar","descripcion":"Mostrar 4*2","solucion":"mostrar 4 * 2"},
{"nivel":4,"titulo":"12. Variables suma","descripcion":"Sumar variables","solucion":"a es 5\nb es 7\nmostrar a + b"},

# =========================
# NIVEL 5 - CONDICIONALES
# =========================
{"nivel":5,"titulo":"13. Mayor a 10","descripcion":"Si n>10 mostrar 'Grande'","solucion":"n es 15\nsi n > 10:\n    mostrar \"Grande\""},
{"nivel":5,"titulo":"14. Par","descripcion":"Detectar par","solucion":"n es 4\nsi n % 2 == 0:\n    mostrar \"Par\""},
{"nivel":5,"titulo":"15. Par o impar","descripcion":"Par o impar","solucion":"n es 5\nsi n % 2 == 0:\n    mostrar \"Par\"\nsino:\n    mostrar \"Impar\""},

# =========================
# NIVEL 6 - BUCLES
# =========================
{"nivel":6,"titulo":"16. Repetir","descripcion":"Mostrar Hola 3 veces","solucion":"repetir 3 veces:\n    mostrar \"Hola\""},
{"nivel":6,"titulo":"17. Contador","descripcion":"Contar 1 a 5","solucion":"contador es 1\nrepetir 5 veces:\n    mostrar contador\n    contador es contador + 1"},
{"nivel":6,"titulo":"18. Sumar en loop","descripcion":"Sumar números","solucion":"suma es 0\ncontador es 1\nrepetir 5 veces:\n    suma es suma + contador\n    contador es contador + 1\nmostrar suma"},

# =========================
# NIVEL 7 - FUNCIONES
# =========================
{"nivel":7,"titulo":"19. Saludar","descripcion":"Función saludar","solucion":"funcion saludar(nombre):\n    mostrar \"Hola \" + nombre\n\nsaludar(\"Ana\")"},
{"nivel":7,"titulo":"20. Sumar función","descripcion":"Función sumar","solucion":"funcion sumar(a,b):\n    mostrar a + b\n\nsumar(3,4)"},
{"nivel":7,"titulo":"21. Doble","descripcion":"Mostrar doble","solucion":"funcion doble(n):\n    mostrar n * 2\n\ndoble(5)"},

# =========================
# NIVEL 8 - DESAFÍOS
# =========================
{"nivel":8,"titulo":"22. Saludo repetido","descripcion":"Saludar 3 veces","solucion":"nombre es \"Ana\"\nrepetir 3 veces:\n    mostrar \"Hola \" + nombre"},
{"nivel":8,"titulo":"23. Mayor","descripcion":"Comparar dos números","solucion":"a es 5\nb es 8\nsi a > b:\n    mostrar a\nsino:\n    mostrar b"},
{"nivel":8,"titulo":"24. Tabla","descripcion":"Tabla del 2","solucion":"n es 2\ncontador es 1\nrepetir 5 veces:\n    mostrar n * contador\n    contador es contador + 1"},

# =========================
# EXTRA (más práctica)
# =========================
{"nivel":8,"titulo":"25. Triple","descripcion":"Mostrar triple","solucion":"n es 3\nmostrar n * 3"},
{"nivel":8,"titulo":"26. Nombre largo","descripcion":"Mostrar nombre dos veces","solucion":"nombre es \"Ana\"\nmostrar nombre + nombre"},
{"nivel":8,"titulo":"27. Loop saludo","descripcion":"Saludar varias veces","solucion":"repetir 4 veces:\n    mostrar \"Hola\""},
{"nivel":8,"titulo":"28. Condición texto","descripcion":"Comparar texto","solucion":"nombre es \"Ana\"\nsi nombre == \"Ana\":\n    mostrar \"Correcto\""},
{"nivel":8,"titulo":"29. Número fijo","descripcion":"Mostrar número","solucion":"mostrar 100"},
{"nivel":8,"titulo":"30. Suma simple","descripcion":"Sumar 1+2","solucion":"mostrar 1 + 2"},

]