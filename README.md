# inv-adc
Investigación Analitica de datos de Cancer en Cali

#Implementación de una maquina virtual para pruebas de software del proyecto

Se usa tecnología de vagrant con virtualBox para la creación de una maquina virtual usando como host cualquier sistema operativo que permita la instalación de vagrant o vitualBox. Revisar [tutorial vagrant](https://learn.hashicorp.com/vagrant)

Abra terminal o linea de comandos en equipo Host e ingrese a carpeta vagrant descargada o clonada de este repositorio ejecute el comando:

```
vagrant up
```
De esta manera se provisiona una maquina virtual con un box de vagrant que corre el sistema operativo ubuntu 18.04.3 LTS (Bionic Beaver) y que carga configurada con servidor web apache2 en el puerto local 2222 y con X11 server para ejecutar desde consola aplicaciones con interfaz gráfica.

Para iniciar comunicación con la maquina vitual ejecute el comando:

```
vagrant ssh
```

Desde alli se ingresa a la maquina virtual, salga de la maquina virtual con el comando exit que lo retornará a la linea de comandos del equipo host.

Apague la maquna virtual con el comando:

```
vagrant halt
```
Dentro de la maquina virtual en el directorio raiz esta la capeta ```/vagrant``` que corresponde a una carpeta compartida cuyo equivalente en el equipo host es el directorio vagrant desde el cual se arrancó la maquina virtual. Acceda a esa como su carpeta de trabajo desde la maquina virtual con el comando:
```
cd /vagrant
```



