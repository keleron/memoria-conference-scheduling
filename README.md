# Buenas!

- `csTrackSolver.py` Este es el solver de usted

- `main.py` & `main-extended.py` son los mios

# Formato de las instancias

```
# ARTICULOS	HUMANOS TOTAL	BLOQUES	SALONES	TRACKS	ARTICULOS POR SESION	SESIONES POR DIA
#articulos #personas #salones #tracks #slots #unused
# ARTICULO	TRACK	PRESENTADOR	BEST PAPER
id track autor bestpaper?
id track autor bestpaper?
id track autor bestpaper?
...
#PERSONA CONFLICTO (CON TIEMPO)
id [bloques conflictivos]
id [bloques conflictivos]
id [bloques conflictivos]
...
#TRACK	ASISTENTES HISTORICOS
#id #asistentes
#id #asistentes
#id #asistentes
...
#SALON	CAPACIDAD
#id #capacidad
#id #capacidad
#id #capacidad
...
#TRACK	CHAIRS
#id [listado de chairs]
#id [listado de chairs]
#id [listado de chairs]
...
#TRACK	ORGANIZADORES
#id [listado de organizadores]
#id [listado de organizadores]
#id [listado de organizadores]
...

```
