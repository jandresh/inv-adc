# Cancer Literature Analysis Using Complex Network Techniques

## Description
This project develops a system specialized in breast cancer that automatically accesses scientific literature and extracts relevant information from medical reports in Cali, Colombia. The system will process and provide necessary information to healthcare personnel to support medical decision-making. It will identify research networks, key authors, and entities, providing immediate access to full texts and other relevant data.

## Features
- **Automatic Access to Scientific Literature**: Connect to scientific databases via APIs to retrieve articles on breast cancer.
- **Information Extraction**: Obtain key data such as authors, institutions, countries, keywords, emails, and languages.
- **Network Analysis**: Identify research networks, relevant authors, universities, and entities.
- **Information Processing**: Select and process the retrieved information for medical decision support.
- **User Interface**: Web application for project configuration and visualization of analysis and results.

## Technologies Used
- **Web Services and Continuous Integration**: Technologies for deployment in local and cloud environments.
- **Databases**: Database management systems to store and handle downloaded data.
- **Complex Network Analysis**: Specialized libraries for network analysis and visualization.
- **Microservices**: Microservices architecture for the development of the web application.

## Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/jandresh/inv-adc.git
    ```

2. Navigate to the project directory:
    ```bash
    cd inv-adc
    ```

3. Install required software:
    - Docker
    - Docker-compose
    - npm

## Local Startup
1. Navigate to each of the following directories and run `docker compose up`:
    - `metapub`
    - `core`
    - `arxiv`
    - `preprocessing`
    - `db`
    - `orchestrator`

2. Navigate to the `gui` directory and run:
    ```bash
    docker compose up
    ```

    or for real-time development:
    ```bash
    npm start
    ```


## Usage
1. Access the web application in your browser:
    ```plaintext
    http://localhost:3000
    ```


## Contribution
1. Fork the repository.

2. Create a new branch:
    ```bash
    git checkout -b new-feature
    ```

3. Make your changes and commit them:
    ```bash
    git commit -m "Add new feature"
    ```

4. Push your changes to the repository:
    ```bash
    git push origin new-feature
    ```

5. Create a Pull Request.

## License
This project is licensed under the terms of the [MIT License](LICENSE).

## Author and Acknowledgments
This work is being developed by [Jaime Andrés Hurtado](mailto:jaime.hurtado@correounivalle.edu.co) as a Master's thesis in Engineering with an emphasis on Systems Engineering at the [School of Systems and Computing Engineering](https://eisc.univalle.edu.co/) of the [Universidad del Valle](https://univalle.edu.co/) in Cali, Colombia, and belongs to the [GUIA research group](https://eisc.univalle.edu.co/index.php/grupos-investigacion/guia). The research directors are Professors [Oswaldo Solarte Pabón](mailto:oswaldo.solarte@correounivalle.edu.co) and [Víctor Andrés Bucheli Guerrero](mailto:victor.bucheli@correounivalle.edu.co).