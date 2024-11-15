# Metapub as a microservice in a Docker container

A basic Docker setup to run services and query PubMed.

## Prerequisites

- Install [Docker](https://www.docker.com/).

## Quick Start

1. **Build the image**:

   Run the following command in the project root directory (where the `Dockerfile` is located):

   ```bash
   docker build -t metapubws .
   ```

2. **Run the container**:

   Start the Flask app by exposing port 5000:

   ```
   docker run -p 5000:5000 metapubws
   ```

3. **Access the endpoints*:

   ```
   # Get title from the pubmedid
   curl -X POST -H "Content-type: application/json" -d '{ "id": "39302353" }' http://localhost:5000/title

   # Get abstrac from the pubmedid
   curl -X POST -H "Content-type: application/json" -d '{ "id": "39302353" }' http://localhost:5000/abstract

   # Get pubmed ids from a text
   curl -X POST -H "Content-type: application/json" -d '{ "query": "breast cancer" }' http://localhost:5000/pmids

   # Get metadata from a pubmed id
   curl -X POST -H "Content-type: application/json" -d '{ "id": "39302353" }' http://localhost:5000/metadata

   # Get a pdf url link from the pubmedid
   curl -X POST -H "Content-type: application/json" -d '{ "id": "39302353" }' http://localhost:5000/metadata
   ```
