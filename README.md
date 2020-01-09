# Project-Lidar_Mine_Jtk1

El repositorio cuenta con cinco subcarpetas descritas a continuación:

## Executable

Esta carpeta contiene archivos necesarios para crear el programa o ícono que ejecuta todos los comandos necesarios para que funcione el sistema.

* **Images**: Imagen utilizada en el ícono del programa, actualmente fue bajado de internet pero se puede poner un propio diseño.

* **Indicaciones ubuntu**: Indicaciones y archivo de configuración del ejecutable para ubuntu.

* **bin**: Archivo que contiene los comandos a ejecutar, se utiliza xterm para lanzar cada comando en un terminal propio.

## Arduino scripts

Esta carpeta contiene los archivos desarrollados para arduino

* **Codigo de servo**: Es el código para el movimiento del servo, actualmente esta seleccionado para enviar cada 5 grados el valor al procesador central, pero el movimiento es suave haciendo que el servo se mueda cada grado.

* **Primer codigo encoder**: Código de prueba del módulo del encoder.

## quanergy_client

Esta carpeta contiene el sdk del sensor LiDAR Quanergy M8.

## Scripts

Esta carpeta contiene los scripts desarrollados durante el proyecto, el script final a utilizar es **main_volume_calc.py** si se tiene una generación de nube de puntos en formato .pcd.

## carkin_ws

Espacio de trabajo de nuestro programa en ROS.

### quanergy_client_ros

* **cfg**: Contiene el archivo de configuración para la interfaz **Dinamic reconfigure**, aquí se configura la resolución.

* **config**: Parametros de sistema mecatrónico (robot), no utilizado.

* **launch**: Archivos launch del programa.
  - main_m8.launch: Archivo launch principal del programa.
  - pointcloud_assembler: Archivo launch encargado del stack. 
  
    ***Nota:** Aqui se configura la cantidad de nube de puntos a ensamblar, este parámetro va de acuerdo a la cantidad de valores que recibe del arduino, cuando es cada 5 grados son un total de 37 nube de puntos, sin embargo, debido al buffer del servicio assembler se debe considerar más para obtener todos los puntos cerrados. De 180° a 0° el valor puesto se de **42***.
  - filter_cloud.launch: Archivo launch encargado de ejecutar el filtro estadístico. Sus parámetros se pueden variar en la interfaz rqt dinamic_reconfigure.

* **rviz**: Configuración del rviz.

* **scripts**: Aqui se encuentran los codigos utilizados en el programa.
  - cloud_assembler_jtk1.py: Nodo encargado de realizar el stack - Servicio assembler ros.
  - cloud_save_jtk1.py: Nodo encargado de crear la carpeta de data y guardar la data cada vez que se genera un stack completo.
  - module_m8_serial.py: Nodo que lee la información del arduino y publica el estado en JointState para realizar la transformada de la nube de puntos capturado por el sensor según su posición real.
  - pointcloud_optimization_interfaz.py: Filtro de la nube de puntos mediante un muestreo de puntos, considerand el parámetro de resolución de la interfaz rqt dinamic reconfigure.
  - server.py: Archivo de ejemplo de la configuración del rqt dinamic reconfigure.
  . scripts pasados: Carpeta que contiene los archivos desarrollados previamente a las modificaciones últimas desarrolladas.
 
* **urdf**: Se encuentra el archivo urdf de la descripción del sistema mecatrónico (robot), las dimensiones son de acuerdo al diseño mecánico, este archivo debe modificarse si el mecanismo se cambia.

