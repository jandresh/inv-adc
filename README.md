# inv-adc
Investigación Analitica de datos de Cancer en Cali

# Implementación de una maquina virtual para pruebas de software del proyecto

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

# Instalación de app django-pwa

Se utilizó el repositorio de [django-pwa](https://gitlab.com/Jenselme/django-pwa) para empezar la implementación de una interfaz de usuario de prueba. En el proceso de implementación se requiere la instalación de pipenv y se sigue el procedimeinto de las [notas de instalación](https://gist.github.com/planetceres/8adb62494717c71e93c96d8adad26f5c) utilizando Python3.

Adicional instalar python3.7 con el siguiente comando:

```
sudo apt install python3.7
```

A continuación ejecutar los siguientes comandos para iniciar un entorno virtual con pipenv:

```
pipenv install
pipenv shell
```
Correr las migraciones por defecto, esto creara la base de datos SQlite con el comando:
```
python manage.py migrate
```
Iniciar el servidor con el comando:
```
python manage.py runserver
```
De esta manera se ha creado un servidor web en la maquina virtual direción 127.0.0.1/8000

# Instalación de Ngrok

Ngrock permite facilmente publicar temporalmente en la web. Siga el tutorial [NGROK](https://ngrok.com/download) para ver su sitio en la web.
