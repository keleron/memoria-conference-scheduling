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

# Formato de las salidas

Las salidas van al archivo `logs/[instancia].sol`, las primeras infinitas lineas son las que entrega gurobi con el valor que le asigno a cada variable. Y al final final hay unos datos que asemejan ser un `.csv`; asi que basta con copiar eso.

- excel > texto en columnas > separar por `;` > reemplazar # por saltos de linea.

## Version Normal.

WIP

## Version extended.

Para la primera tabla son tuplas (articulo, autor) mientras que para la segunda son (chair, organizador), el valor de la función objetivo está en la letra `z`, asi que `ctrl+f` sobre la solución y ya!.
