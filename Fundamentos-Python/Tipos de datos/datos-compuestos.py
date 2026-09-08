#son datos compuestos porque los podemos agrupar
#una matriz es un conjunto de datos

#encontramos 2 tipos de datos compuestos / lista y tupla

# creando una lista (se puede modificar los datos)
lista = ["Soy Duver","contreras",True,1.79,"contreras"]
print(lista[2])

# este es valido (se esta modificando un dato)
lista[3] = "maquinola"

# creando una tupla (no se puede modificar los datos), con tupla  podemos tener un conjunto de datos que nunca se van a modificar, siempre van a estar los que nosotros pongamos
tupla = ("Soy Duver","contreras",True,1.79,"contreras")

# este no es valido, genera error
#tupla[3] = "maquinola"

print(lista[3])

#creando un conjunto (set), no tienen un orden fijo (el conjunto como tal) y pueden intercambiarse de lugar los conjuntos, pero no pueden cambiarse los elementos dentro del conjunto
#no se puede imprimir por indice, se imprime por conjunto
#en un conjunto no puede haber datos duplicados, en lista, duplas, diccionaio si
#para acceder a los datos(elementos) del conjunto, debemos utilizar un bucle (ver mas adelante del video)

conjunto = {"Soy Duver","contreras",True,1.79}
print(conjunto)

#creando un diccionario (dict) (es similar a la lista)
#La estructura es key : value y separamos con comas menos la ultima o la primera si solamente hay un valor
#se imprime por diccionario y se muestra por nombre asociado 'altura' etc..

diccionario = {
    'nombre' : 'duver contreras',
    'canal' : 'soy dalto',
    'esta_emocionado' : True,
    'altura' : 1.79,
    'dato_repetido' :'soy dalto'   
}

print(diccionario['altura'])