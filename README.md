Guia

1.- En la lista de archivos buscamos uno con el nombre "Downloads_Data". dentro de el se econtrararn los link
de descarga de archivos (Daymet, Chiprs, Livneh y era5 land).
NOTA: en caso de era5 land ahi que descargar un dia antes del periodo que trabajremos ejemplo 31 de mayo de x año ya que nosotros trabajaremos en junio y de igual manera al finalizar si terminamos el 31 de agosto de x año agarramos extra el 1 de septirmbre. asi en cada periodo de tiempo que trabajemos.

2.- Crear una carpeta llamada "new" donde se tenga todos los archivos descargados.

3.- Iniciamos con Chirps nos dirijimos al script con ese nombre.
NOTA: si trabaja con un diferente intervalo de tiempo se puede modificar al igual si quiere cambiarle 
la estructura del nombre.
una vez dentro si es neceario se puede cambiar la fecha del "for" dejando la misam estrucura solo cambiar la fecha y mes.

3. Continuamos con Daymet nos dirijimos al script, en este caso es igual que el paso anterior si es necasario
   cambiamos año y meses,la diferencia en este es que tenemos divididos las temperaturas maximas, minimas y precipitacion.

4.- El siguiente es Livneh en este si no es neceario modificar nada solo es copiarlo y pegarlo el mismo trabajra todo.

5.- por ultimo Era5 land al entrar al Script apreciaremos que mencioan seaparacion de variables.
una vez terminado con la separcacion de variables. trabajaremos con la variable de precipitacion ya que esta en era5 tiene una estructura diferente py ahi qeu ordenar los datos para eso copiamos todo el codigo de abajo y modificamos lo necesario de pendiendo al periodo que estemos trabajando.


6.-Una vez finalizado todo trabajaremos el archivo de "getVar.gs" en el solo se ocupa modificar el [dom, date1, date2], se guardan cambios y se ejecuta... y asi susesivamente a los periodos.

7.- Finalizado el procesamiento abrimos el archivo "Script_wrf_out_vars_merge" modificamos [les, sal] si es necesario ya que son las fechas y la ruta de salida se puede modificar, en caso no de reuqerir esa ruta elimine lo siguiente (../../wrf_out_vars_merge).

