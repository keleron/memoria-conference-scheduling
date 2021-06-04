import sys
from gurobipy import *
import numpy as np

if len(sys.argv) < 2:
    print('Uso:$ python3 csTrackSolverv1.py nombre_instancia')
    exit(1)

file_temp = 'temp.txt'
file = open(file_temp, 'w')
with open(sys.argv[1]) as f:
    for line in f:
        # create a temp file without coments and blank lines
        if line.startswith('#') or line.startswith('\n'):
            continue
        else:
            file.write(line)
file.close()

m = Model('CSSolver')

with open(file_temp) as f:
    nCTP = 0
    nA, nP, nS, nH, nT, nAS, nSD = [
        int(x) for x in f.readline().split()]  # read first line

    print("nArticulos:" + str(nA) + ", nParticipantes:" + str(nP) + ", nSesiones \"totales en todos los días en todas las salas\":" + str(nS) +
          ", nHabitaciones:" + str(nH) + ", nTracks: " + str(nT) + ", nArticulos por Sesión:" + str(nAS) + ", nSesiones por Dia: " + str(nSD))

    nB = int(nS/nH)  # NBloques de sesiones (no considera la cantidad de salas)

    # 1 si el artículo a pertenece al track t
    pertenece = np.zeros((int(nA), int(nT)))
    # 1 si el participante p presenta el articulo a
    presenta = np.zeros((int(nP), int(nA)))
    # 1 si el articulo a esta nominado a Best Paper o no
    nominadoBP = np.zeros(int(nA))
    for a in range(nA):
        # cada linea contiene el track y un boleano indicando si está nominado a best paper o no.
        values = f.readline().strip().split(' ')
        #print (values)
        pertenece[a][int(values[0])-1] = 1
        presenta[int(values[1])-1][a] = 1
        nominadoBP[a] = int(values[2])
    print("Pertenece:")
    print(pertenece)
    print("nominadoBP:")
    print(nominadoBP)
    print("Presenta:")
    print(presenta)

    nST = []
    nS = int(0)  # computa el numero de Sesiones

    # Calculo de sesiones por track
    cont = 0
    for t in range(nT):
        totalArticulos = 0
        for a in range(nA):
            if pertenece[a][t] == 1:
                print("El articulo: " + str(a+1) +
                      " pertenece al track: " + str(t+1))
                totalArticulos = totalArticulos + 1

        print("El track " + str(t+1) + " tiene: " + str(totalArticulos) +
              " artículos que se dividen en " + str(totalArticulos/nAS) + " sesiones. ")
        nST.append(totalArticulos/nAS)
        cont = cont + 1
        nS = nS + int(totalArticulos/nAS)

    print("En total se tiene: " + str(nS) + " sesiones. ")

    # 1 si la sesión s corresponde al track t
    corresponde = np.zeros((int(nS), int(nT)))
    cont = 0
    for t in range(nT):
        totalArticulos = 0
        for a in range(nA):
            if pertenece[a][t]:
                totalArticulos = totalArticulos + 1
        for i in range(int(totalArticulos/nAS)):
            corresponde[int(cont+i)][t] = int(1)

        cont = cont + int(totalArticulos/nAS)

    print("Corresponde: ")
    for s in range(nS):
        for t in range(nT):
            if corresponde[s][t]:
                print("La sesión: " + str(s+1) +
                      " corresponde al track: " + str(t+1))

    estaDisponible = [[0 for s in range(nS)] for p in range(nP)]
    for p in range(nP):
        for s in range(nS):
            estaDisponible[p][s] = 1

    for p in range(nP):
        # cada linea contiene el track y un boleano indicando si está nominado a best paper o no.
        values = f.readline().strip().split(' ')
        for v in values:
            if int(v) > 0:
                estaDisponible[p][int(v)-1] = 0

    print("EstaDisponible:")
    print(estaDisponible)

    # Leer capacidad requerida por track
    # Entero: indica la cantidad de personas que atiende una sesion del track t
    capacidadRequerida = []
    for t in range(nT):
        capacidad = int(f.readline().strip())
        capacidadRequerida.append(capacidad)

    # Leer capacidad disponible en salas
    capacidadDisponible = []  # Entero: indica la capacidad disponible de cada sala
    for h in range(nH):
        capacidad = int(f.readline().strip())
        capacidadDisponible.append(capacidad)

    # Leer chairs disponibles para cada track
    chairs = []  # lista de participantes que pueden actuar como chairs de las sesiones del track t
    for t in range(nT):
        chairs.append([int(x)-1 for x in f.readline().strip().split(' ')])

    print("Chairs: ")
    print(chairs)

    # Leer organizadores disponibles para cada sesion
    # lista de participantes que pueden actuar como organizadores de las sesiones del track t
    organizadores = []
    for t in range(nT):
        organizadores.append(
            [int(x)-1 for x in f.readline().strip().split(' ')])

    print("Organizadores:")
    print(organizadores)

    # Variables
    # 1 si el articulo a está asignado al bloque ab de la sesion s
    x = m.addVars(nA, nAS, nS, vtype=GRB.BINARY, name='x')
    # 1 si la sesion s está asignada al bloque b en la sala h
    y = m.addVars(nS, nB, nH, vtype=GRB.BINARY, name='y')
    z = m.addVar(vtype=GRB.INTEGER, name='z')
    # 1 si el participante p dirige la sesion s # para chairs
    Dy = m.addVars(nP, nS, vtype=GRB.BINARY, name='Dy')
    # 1 si el participante p organiza la sesion s # para organizadores
    Oy = m.addVars(nP, nS, vtype=GRB.BINARY, name='Oy')
    # si la sesion s posee al menos un artículo nominado a Best Paper
    xBP = m.addVars(nS, vtype=GRB.BINARY, name='xBP')
    # si la sesion s del bloque b posee al menos un artículo nominado a Best Paper
    yBP = m.addVars(nS, nB, vtype=GRB.BINARY, name='yBP')

    # Cada sesión debe programarse en un bloque en una sala
    for s in range(nS):
        m.addConstr(
            sum(
                sum(y[s, b, h] for b in range(nB)) for h in range(nH)
            ) == 1
        )

    # En cada sala, en cada bloque solo se puede programar una sesión
    for h in range(nH):
        for b in range(nB):
            m.addConstr(sum(y[s, b, h] for s in range(nS)) <= 1)

    # Cada sesión debe programarse en una sala que cumpla las restricciones de capacidad
    for s in range(nS):
        for b in range(nB):
            for h in range(nH):
                for t in range(nT):
                    if corresponde[s, t]:
                        m.addConstr(y[s, b, h]*capacidadRequerida[t]
                                    <= capacidadDisponible[h])

    # Cada artículo debe programarse en un bloque de una sesión
    for a in range(nA):
        m.addConstr(sum(sum(x[a, ab, s] for ab in range(nAS))
                        for s in range(nS)) == 1)

    # Cada artículo debe programarse en una sesión del track correspondiente
    for a in range(nA):
        for t in range(nT):
            if pertenece[a][t]:
                for s in range(nS):
                    m.addConstr(sum(x[a, ab, s]*pertenece[a][t]
                                    for ab in range(nAS)) <= corresponde[s, t])

    # En cada sesión, en cada bloque solo se puede programar un artículo
    for s in range(nS):
        for ab in range(nAS):
            m.addConstr(sum(x[a, ab, s] for a in range(nA)) <= 1)

    # Las sesiones del mismo track deben asignarse en diferentes bloques
    for t in range(nT):
        for b in range(nB):
            m.addConstr(sum(sum(y[s, b, h] * corresponde[s, t]
                                for s in range(nS)) for h in range(nH)) <= 1)

    # Forzar valor de xBestPaper de acuerdo a los articulos asignados en el bloque.
    for s in range(nS):
        m.addConstr(sum(sum(x[a, ab, s]*nominadoBP[a]
                            for a in range(nA)) for ab in range(nAS)) <= nAS*xBP[s])

    # Las sesiones que tienen articulos nominados a Best Paper deben asignarse a diferentes bloques
    for s1 in range(nS):
        for s2 in range(s1, nS):
            if s1 != s2:
                for b in range(nB):
                    # Ambas sesiones pueden estar agendadas en el mismo bloque, pero no pueden tener ambas un BP.
                    m.addConstr(sum(y[s1, b, h] for h in range(
                        nH)) + xBP[s1] + sum(y[s2, b, h] for h in range(nH)) + xBP[s2] <= 3)

    # Cada sesion necesita un chair de los que aparecen en su lista
    for s in range(nS):
        for t in range(nT):
            if corresponde[s, t]:
                m.addConstr(sum(Dy[p, s] for p in chairs[t]) >= 1)

    # Cada chair debe ser asignado a lo más a una sesión de cada track
    for t in range(nT):
        for p in chairs[t]:
            m.addConstr(sum(Dy[p, s]*corresponde[s, t]
                            for s in range(nS)) <= 1)

    # Una persona no puede dirigir más de una sesión en un mismo instante de tiempo
    for p in range(nP):
        for s1 in range(nS):
            for s2 in range(s1, nS):
                if s1 != s2:
                    for b in range(nB):
                        # Ambas sesiones pueden estar agendadas en el mismo bloque, pero no pueden ser ambas dirigidas por la misma persona.
                        m.addConstr(sum(y[s1, b, h] for h in range(
                            nH)) + Dy[p, s1] + sum(y[s2, b, h] for h in range(nH)) + Dy[p, s2] <= 3)

    # Cada sesion necesita un organizador de los que aparecen en su lista
    for s in range(nS):
        for t in range(nT):
            if corresponde[s, t]:
                m.addConstr(sum(Oy[p, s] for p in organizadores[t]) >= 1)

    # Cada chair debe ser asignado a lo más a una sesión de cada track
    for t in range(nT):
        for p in organizadores[t]:
            m.addConstr(sum(Oy[p, s]*corresponde[s, t]
                            for s in range(nS)) <= 1)

    # Una persona no puede dirigir más de una sesión en un mismo instante de tiempo
    for p in range(nP):
        for s1 in range(nS):
            for s2 in range(s1, nS):
                if s1 != s2:
                    for b in range(nB):
                        # Ambas sesiones pueden estar agendadas en el mismo bloque, pero no puede estar el mismo organizador en ambas sesiones.
                        m.addConstr(sum(y[s1, b, h] for h in range(
                            nH)) + Oy[p, s1] + sum(y[s2, b, h] for h in range(nH)) + Oy[p, s2] <= 3)

    # Una persona no puede presentar artículos en el mismo bloque de tiempo en dos salas
    for p in range(nP):
        for s1 in range(nS):
            for s2 in range(s1, nS):
                if s1 != s2:
                    for b in range(nB):
                        for ab in range(nAS):
                            m.addConstr(sum(x[a, ab, s1]*presenta[p][a] for a in range(nA)) + sum(x[a, ab, s2]*presenta[p][a] for a in range(
                                nA)) + sum(y[s1, b, h] for h in range(nH)) + sum(y[s2, b, h] for h in range(nH)) <= 3, name="presenta")

    # Si una persona no puede atender una sesión en un horario dado, entonces las sesiones en que participa no pueden estar agendadas en dichos horarios.
    for p in range(nP):
        for b in range(nB):
            if estaDisponible[p][b] == 0:
                print("El participante: " + str(p+1) +
                      " no está disponible en el bloque: " + str(b+1))
                for s in range(nS):
                    for ab in range(nAS):
                        m.addConstr(sum(x[a, ab, s]*presenta[p][a]
                                        for a in range(nA)) + sum(y[s, b, h] for h in range(nH)) <= 1)

    for p in range(nP):
        for b in range(nB):
            if estaDisponible[p][b] == 0:
                for s in range(nS):
                    m.addConstr(Dy[p, s] + sum(y[s, b, h]
                                               for h in range(nH)) <= 1)

    for p in range(nP):
        for b in range(nB):
            if estaDisponible[p][b] == 0:
                for s in range(nS):
                    m.addConstr(Oy[p, s] + sum(y[s, b, h]
                                               for h in range(nH)) <= 1)

    m.setObjective(z, GRB.MINIMIZE)
    m.optimize()
    m.write('csTrackSolver.lp')
    m.write('csTrackSolver.sol')

    print("\t \t \t ")
    for h in range(nH):
        print("    H" + str(h+1) + " \t|", end='')
    print('')
    for b in range(nB):
        print(str(b+1), end='')
        for h in range(nH):
            for s in range(nS):
                if y[s, b, h].X == 1:
                    #print ("La sesión: " + str(s+1) + " se asigno a la habitación: " + str(h+1) + " el bloque: " + str(b+1))
                    print("|", end='')
                    for ab in range(nAS):
                        for a in range(nA):
                            if x[a, ab, s].X == 1:
                                print(str(a+1) + " ", end='')
        print('')
    print('')

    print("Articulos asignados: ")

    for a in range(nA):
        for ab in range(nAS):
            for s in range(nS):
                if x[a, ab, s].X == 1:
                    print(" Artículo: " + str(a+1) + " asignado al bloque: " +
                          str(ab+1) + " de la sesión: " + str(s+1))

    print("Sesiones asignadas: ")
    for b in range(nB):
        for h in range(nH):
            for s in range(nS):
                if y[s, b, h].X == 1:
                    print(" Sesión: " + str(s+1) + " asignada al bloque: " +
                          str(b+1) + " en la habitación: " + str(h+1))

    print("Sesiones con best papers: ")
    for s in range(nS):
        if xBP[s].X == 1:
            print(" Sesión: " + str(s+1) + " tiene un Best Paper")

    #print ("Sesiones con best papers: " )
    # for b in range (nB):
        # for s in range (nS):
            # if yBP[s,b].X == 1:
            #print (" Sesión: " + str(s+1) + " asignada al bloque: " + str(b+1) + " tiene un Best Paper")
            # for a in range (nA):
            # for ab in range (nAS):
            # for s1 in range (nS):
            # if s1 == s:
            #print (" Artículo: " + str(a+1) + " asignado al bloque: " + str(ab+1) + " de la sesión: " + str(s+1) )

    print("Directores (chairs) de sesiones: ")
    for t in range(nT):
        for s in range(nS):
            if corresponde[s, t]:
                for p in chairs[t]:
                    if Dy[p, s].X == 1:
                        print(" Sesión: " + str(s+1) +
                              " es dirigida por el participante :" + str(p+1))

    print("Organizadores de sesiones: ")
    for t in range(nT):
        for s in range(nS):
            if corresponde[s, t]:
                for p in organizadores[t]:
                    if Oy[p, s].X == 1:
                        print(" Sesión: " + str(s+1) +
                              " es organizada por el participante :" + str(p+1))

    print("z: " + str(z.X))
