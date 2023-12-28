# -*- coding: utf-8 -*-
"""
Created on Thu Dec 14 13:14:24 2023

@author: Diego
"""


from pulp import *
import pandas as pd
import random
from math import radians, sin, cos, sqrt, atan2
import time

comienzo = time.time()

LpSolverDefault.msg=0

def encontrar_ciclos(ciudades, x):
    for i in ciudades:
        cuenta = 0
        for k in ciudades:
            if k != i:
                if x[(i, k)].value() == 1:
                    cuenta += 1
        if i not in visitados:
            for w in range(cuenta):
                ciclo = []
                nodo = i
                while True:
                    ciclo.append(nodo)
                    visitados.add(nodo)
                    for j in ciudades:
                        if j != nodo:
                            if x[(nodo, j)].value() == 1 and j not in ciclo and j not in visitados:
                                nodo = j
                                break
                    else:
                        break
                if ciclo:
                    conjunto.append(ciclo)

datos = pd.read_excel('Windfarms_ReAcciona.xlsx', sheet_name='Windfarms')

ciudades = list(datos['Name'])
latitud = list(datos['Latitude'])
longitud = list(datos['Longitude'])

def distancia_entre_puntos(lat1, lon1, lat2, lon2):
    # Convertir grados a radianes
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Diferencia de latitud y longitud
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Fórmula de Haversine
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    radio_tierra = 6371  # Radio medio de la Tierra en kilómetros

    # Distancia en kilómetros
    distancia = radio_tierra * c
    return distancia

distanciass = [0 for i in range(len(ciudades)) for j in range(len(ciudades))if i != j]

contador = 0
for i in range(len(ciudades)):
    for j in range(len(ciudades)):
        if i != j:
            distanciass[contador] = distancia_entre_puntos(latitud[i], longitud[i],latitud[j], longitud[j])
            contador += 1
    
combinaciones = {(i,j):0 for i in ciudades for j in ciudades if i != j}

distancias = dict(zip(combinaciones,distanciass))

for m in range(1,len(ciudades)):
    
    tiempo_inicio = time.time()
    
    print("----------X----------")
    print("\n")
    print("SOLUCION PARA M=",m)
    
    # Definición del problema primal
    model = LpProblem("Minimizar costes de transporte", LpMinimize)
    
    #Variables del problema primal
    keyX = [(i,j) for i in ciudades for j in ciudades if i != j]
    keyU = [i for i in ciudades]
    x = LpVariable.dicts("Arco",keyX,0,cat=LpBinary)
    u = LpVariable.dicts("Posicion",keyU,lowBound=1,cat=LpContinuous)
    
    # Función objetivo
    model += lpSum(distancias[(i,j)] * x[(i,j)] for i in ciudades for j in ciudades if i != j)
    
    # #Restricciones del problema primal
    
    model += lpSum(x['Breña',j] for j in ciudades if j != 'Breña') == m
    
    model += lpSum(x[i,'Breña'] for i in ciudades if i != 'Breña') == m
    
    for i in ciudades:
        if i!= 'Breña':
            model += lpSum(x[(i,j)] for j in ciudades if j != i) == 1
        else:
            model += lpSum(x[(i,j)] for j in ciudades if j != i) == m
    
    for j in ciudades:
        if j!= 'Breña':
            model += lpSum(x[(i,j)] for i in ciudades if i != j) == 1
        else:
            model += lpSum(x[(i,j)] for i in ciudades if i != j) == m
  
    for i in ciudades:
        for j in ciudades:
            if i != j and i != 'Breña' and j != 'Breña':
                model += u[i] - u[j] + (len(ciudades)-m) * x[(i,j)] <= len(ciudades) - m -1
    
    # Solución del problema primal
    
    model.solve()
    
    print("\n")
    
    conjunto = []
    visitados = set()
    
    encontrar_ciclos(ciudades, x)
    
    subciclos = []
    for ciclo in conjunto:
        ciclo.sort()
        if ciclo not in subciclos:
            subciclos.append(ciclo)
    
    variable = []
    for v in model.variables():
        if v.varValue!=0:
            variable.append(v.name)
            print(v.name, " = ", v.varValue)
    
    variable = []
    for v in model.variables():
        variable.append("valor {}: {}".format(v.name,v.varValue))
    
    print("Estado:", LpStatus[model.status])
    print("\n")
    print("Los ciclos finales son {}:".format(m))
    print("\n")
    for i,j in enumerate(conjunto):
        print("Ciclo {}:\n{}".format(i+1,j))
        print("\n")   
    print("Distancia total recorrida con {} drones: {} km".format(m,round(value(model.objective),2)))
    print("Tiempo total con {} drones: {} horas".format(m,round(value(model.objective)/(140*m),2)))
    
    tiempo_fin = time.time()
    tiempo_ejecucion = tiempo_fin - tiempo_inicio

    print("Tiempo de cálculo de ordenador para {} drones: {} segundos".format(m,round(tiempo_ejecucion,3)))

    
print("\n")

final = time.time()
tiempo_total = final - comienzo

print("Tiempo de cálculo de ordenador total: {} segundos".format(round(tiempo_total,3)))
print("\n")

