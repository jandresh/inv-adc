# Análisis de Literatura Científica en el Dominio del Cáncer Usando Técnicas de Redes Complejas

## Descripción
Este proyecto desarrolla un sistema especializado en cáncer de mama que accede automáticamente a la literatura científica y extrae información relevante a partir de reportes médicos de la ciudad de Cali, Colombia. El sistema procesará y pondrá a disposición del personal de salud la información necesaria para apoyar la toma de decisiones médicas. Identificará redes de investigación, autores y entidades clave, proporcionando acceso inmediato a los textos completos y otros datos relevantes.

## Características
- **Acceso Automático a Literatura Científica**: Conexión a bases de datos científicas mediante APIs para recuperar artículos sobre cáncer de mama.
- **Extracción de Información**: Obtención de datos clave como autores, instituciones, países, palabras clave, correos electrónicos e idiomas.
- **Análisis de Redes**: Identificación de redes de investigación, autores relevantes, universidades y entidades.
- **Procesamiento de Información**: Selección y procesamiento de la información recuperada para su uso en la toma de decisiones médicas.
- **Interfaz de Usuario**: Aplicación web para configurar proyectos y visualizar análisis y resultados.

## Tecnologías Utilizadas
- **Servicios Web e Integración Continua**: Tecnologías para despliegue en entornos locales y en la nube.
- **Bases de Datos**: Sistemas de gestión de bases de datos para almacenar y manejar los datos descargados.
- **Análisis de Redes Complejas**: Librerías especializadas para el análisis y visualización de redes.
- **Microservicios**: Arquitectura basada en microservicios para el desarrollo del aplicativo web.

## Instalación
1. Clonar el repositorio:
    ```bash
    git clone https://github.com/jandresh/inv-adc.git
    ```

2. Navegar al directorio del proyecto:
    ```bash
    cd inv-adc
    ```

3. Instalar dependencias:
    ```bash
    npm install
    ```

## Inicio Local
1. Ingresar a cada uno de los siguientes directorios y ejecutar `docker compose up`:
    - `metapub`
    - `core`
    - `arxiv`
    - `preprocessing`
    - `db`
    - `orchestrator`

2. Ingresar al directorio `gui` y ejecutar:
    ```bash
    docker compose up
    ```

    o para desarrollar en tiempo real:
    ```bash
    npm start
    ```


## Uso
1. Acceder a la aplicación web en tu navegador:
    ```plaintext
    http://localhost:3000
    ```


## Contribución
1. Hacer un fork del repositorio.
2. Crear una rama nueva:
    ```bash
    git checkout -b feature-nueva
    ```

3. Realizar los cambios y commit:
    ```bash
    git commit -m "Añadir nueva funcionalidad"
    ```

4. Subir los cambios al repositorio:
    ```bash
    git push origin feature-nueva
    ```

5. Crear un Pull Request.

## Licencia
Este proyecto está licenciado bajo los términos de la [Licencia MIT](LICENSE).

## Autor y Agradecimientos
Este trabajo está siendo desarrollado por [Jaime Andrés Hurtado](mailto:jaime.hurtado@correounivalle.edu.co) como tesis de maestría en Ingeniería con énfasis en Ingeniería de Sistemas de la [Escuela de Ingeniería de Sistemas y Computación](https://eisc.univalle.edu.co/) de la [Universidad del Valle](https://univalle.edu.co/) en Cali, Colombia, y pertenece al [grupo de investigación GUIA](https://eisc.univalle.edu.co/index.php/grupos-investigacion/guia). Los directores de la investigación son los profesores [Oswaldo Solarte Pabón](mailto:oswaldo.solarte@correounivalle.edu.co) y [Víctor Andrés Bucheli Guerrero](mailto:victor.bucheli@correounivalle.edu.co).