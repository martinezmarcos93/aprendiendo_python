EJERCICIOS = [

# =========================
# NIVEL 1 - MOSTRAR
# =========================
{"nivel":1,"titulo":"1. Hola mundo","descripcion":"Mostrá: Hola mundo","solucion":'mostrar "Hola mundo"'},
{"nivel":1,"titulo":"2. Mensaje","descripcion":"Mostrá: Aprender es divertido","solucion":'mostrar "Aprender es divertido"'},
{"nivel":1,"titulo":"3. Dos mensajes","descripcion":"Mostrá Hola y, en la línea siguiente, Chau","solucion":'mostrar "Hola"\nmostrar "Chau"'},

# =========================
# NIVEL 2 - VARIABLES
# =========================
{"nivel":2,"titulo":"4. Variable simple","descripcion":"Creá la variable edad con el valor 12 y mostrala","solucion":"edad es 12\nmostrar edad"},
{"nivel":2,"titulo":"5. Nombre","descripcion":"Guardá el nombre Juan en una variable y mostralo","solucion":'nombre es "Juan"\nmostrar nombre'},
{"nivel":2,"titulo":"6. Dos variables","descripcion":"Creá a con 5 y b con 10, y mostrá cada una en su línea","solucion":"a es 5\nb es 10\nmostrar a\nmostrar b"},

# =========================
# NIVEL 3 - INPUT
# =========================
{"nivel":3,"titulo":"7. Pedir nombre","descripcion":"Pedí el nombre con preguntar y mostralo","solucion":'nombre es preguntar("Nombre: ")\nmostrar nombre'},
{"nivel":3,"titulo":"8. Saludo","descripcion":"Pedí el nombre con preguntar y mostrá: Hola + el nombre","solucion":'nombre es preguntar("Nombre: ")\nmostrar "Hola " + nombre'},
{"nivel":3,"titulo":"9. Edad","descripcion":"Pedí la edad con preguntar y mostrala","solucion":'edad es preguntar("Edad: ")\nmostrar edad'},

# =========================
# NIVEL 4 - OPERACIONES
# =========================
{"nivel":4,"titulo":"10. Suma","descripcion":"Mostrá el resultado de 5 + 3","solucion":"mostrar 5 + 3"},
{"nivel":4,"titulo":"11. Multiplicar","descripcion":"Mostrá el resultado de 4 * 2","solucion":"mostrar 4 * 2"},
{"nivel":4,"titulo":"12. Variables suma","descripcion":"Guardá a con 5 y b con 7, y mostrá la suma","solucion":"a es 5\nb es 7\nmostrar a + b"},

# =========================
# NIVEL 5 - CONDICIONALES
# =========================
{"nivel":5,"titulo":"13. Mayor a 10","descripcion":"Guardá n con 15. Si n es mayor que 10, mostrá Grande","solucion":"n es 15\nsi n > 10:\n    mostrar \"Grande\""},
{"nivel":5,"titulo":"14. Par","descripcion":"Guardá n con 4. Si n es par, mostrá Par","solucion":"n es 4\nsi n % 2 == 0:\n    mostrar \"Par\""},
{"nivel":5,"titulo":"15. Par o impar","descripcion":"Guardá n con 5 y mostrá Par o Impar según corresponda","solucion":"n es 5\nsi n % 2 == 0:\n    mostrar \"Par\"\nsino:\n    mostrar \"Impar\""},

# =========================
# NIVEL 6 - BUCLES
# =========================
{"nivel":6,"titulo":"16. Repetir","descripcion":"Mostrá Hola 3 veces usando repetir","solucion":"repetir 3 veces:\n    mostrar \"Hola\""},
{"nivel":6,"titulo":"17. Contador","descripcion":"Contá del 1 al 5 (un número por línea)","solucion":"contador es 1\nrepetir 5 veces:\n    mostrar contador\n    contador es contador + 1"},
{"nivel":6,"titulo":"18. Sumar en loop","descripcion":"Sumá los números del 1 al 5 con un bucle y mostrá solo el total","solucion":"suma es 0\ncontador es 1\nrepetir 5 veces:\n    suma es suma + contador\n    contador es contador + 1\nmostrar suma"},

# =========================
# NIVEL 7 - FUNCIONES
# =========================
{"nivel":7,"titulo":"19. Saludar","descripcion":"Creá la función saludar(nombre) que muestre Hola + nombre y llamala con \"Ana\"","solucion":"funcion saludar(nombre):\n    mostrar \"Hola \" + nombre\n\nsaludar(\"Ana\")"},
{"nivel":7,"titulo":"20. Sumar función","descripcion":"Creá la función sumar(a, b) que muestre la suma y llamala con 3 y 4","solucion":"funcion sumar(a,b):\n    mostrar a + b\n\nsumar(3,4)"},
{"nivel":7,"titulo":"21. Doble","descripcion":"Creá la función doble(n) que muestre el doble y llamala con 5","solucion":"funcion doble(n):\n    mostrar n * 2\n\ndoble(5)"},

# =========================
# NIVEL 8 - DESAFÍOS
# =========================
{"nivel":8,"titulo":"22. Saludo repetido","descripcion":"Guardá el nombre Ana y mostrá Hola Ana 3 veces","solucion":"nombre es \"Ana\"\nrepetir 3 veces:\n    mostrar \"Hola \" + nombre"},
{"nivel":8,"titulo":"23. Mayor","descripcion":"Guardá a con 5 y b con 8, y mostrá el mayor","solucion":"a es 5\nb es 8\nsi a > b:\n    mostrar a\nsino:\n    mostrar b"},
{"nivel":8,"titulo":"24. Tabla","descripcion":"Mostrá la tabla del 2 del 1 al 5 (2, 4, 6, 8, 10; uno por línea)","solucion":"n es 2\ncontador es 1\nrepetir 5 veces:\n    mostrar n * contador\n    contador es contador + 1"},

# =========================
# EXTRA (más práctica)
# =========================
{"nivel":8,"titulo":"25. Triple","descripcion":"Guardá n con 3 y mostrá su triple","solucion":"n es 3\nmostrar n * 3"},
{"nivel":8,"titulo":"26. Nombre largo","descripcion":"Guardá el nombre Ana y mostralo dos veces pegado: AnaAna","solucion":"nombre es \"Ana\"\nmostrar nombre + nombre"},
{"nivel":8,"titulo":"27. Loop saludo","descripcion":"Mostrá Hola 4 veces usando repetir","solucion":"repetir 4 veces:\n    mostrar \"Hola\""},
{"nivel":8,"titulo":"28. Condición texto","descripcion":"Guardá el nombre Ana. Si el nombre es Ana, mostrá Correcto","solucion":"nombre es \"Ana\"\nsi nombre == \"Ana\":\n    mostrar \"Correcto\""},
{"nivel":8,"titulo":"29. Número fijo","descripcion":"Mostrá el número 100","solucion":"mostrar 100"},
{"nivel":8,"titulo":"30. Suma simple","descripcion":"Mostrá el resultado de 1 + 2","solucion":"mostrar 1 + 2"},

]