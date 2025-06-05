#!/usr/bin/env python
#
# Author: Jaime Hurtado - jaime.hurtado@correounivalle.edu.co
# Fecha: 2024-03-19
#
from enum import Enum
from flask import abort, Flask, jsonify, request, Response
from flask_cors import CORS
import json
import requests
import time
from typing import List, Dict, Any

app = Flask(__name__)
CORS(app)

# Configuración de la API de Elsevier
ELSEVIER_API_KEY = "YOUR_API_KEY"  # Reemplazar con tu API key
ELSEVIER_BASE_URL = "https://api.elsevier.com/content/embase"

class GraphType(str, Enum):
    AUTHORS = "authors"
    COUNTRIES = "countries"
    KEYWORDS = "keywords"
    ORGANIZATIONS = "organizations"

def post_json_request(url: str, obj: Dict[str, Any]) -> Dict[str, Any]:
    """Realiza una petición POST y retorna la respuesta como JSON"""
    return requests.post(url, json=obj).json()

def object_to_response(obj: Dict[str, Any]) -> Response:
    """Convierte un objeto a una respuesta HTTP con CORS"""
    response = Response(response=json.dumps(obj), mimetype="application/json")
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

@app.route("/")
def root():
    """Endpoint raíz que muestra los endpoints disponibles"""
    return "elsevier endpoints: /title, /abstract, /emids, /metadata, /emid2pdf, /query"

@app.route("/title", methods=["POST"])
def title_from_emid():
    """Obtiene el título de un artículo usando su Embase ID"""
    if not request.json:
        abort(400)
    emid = request.json["id"]
    
    headers = {
        "X-ELS-APIKey": ELSEVIER_API_KEY,
        "Accept": "application/json"
    }
    
    url = f"{ELSEVIER_BASE_URL}/article/{emid}"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return jsonify(error="Article not found"), 404
        
    data = response.json()
    return jsonify(title=data.get("title", ""))

@app.route("/abstract", methods=["POST"])
def abstract_from_emid():
    """Obtiene el resumen de un artículo usando su Embase ID"""
    if not request.json:
        abort(400)
    emid = request.json["id"]
    
    headers = {
        "X-ELS-APIKey": ELSEVIER_API_KEY,
        "Accept": "application/json"
    }
    
    url = f"{ELSEVIER_BASE_URL}/article/{emid}"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return jsonify(error="Article not found"), 404
        
    data = response.json()
    return jsonify(abstract=data.get("abstract", ""))

@app.route("/emids", methods=["POST"])
def emid_from_query():
    """Busca Embase IDs basados en una consulta de texto"""
    if not request.json:
        abort(400)
    query = request.json["query"]
    
    headers = {
        "X-ELS-APIKey": ELSEVIER_API_KEY,
        "Accept": "application/json"
    }
    
    url = f"{ELSEVIER_BASE_URL}/search"
    params = {
        "query": query,
        "count": 100
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        return jsonify(error="Search failed"), 500
        
    data = response.json()
    emids = [entry.get("id") for entry in data.get("entries", [])]
    return jsonify(emids=emids)

@app.route("/metadata", methods=["POST"])
def metadata_from_emid():
    """Obtiene metadatos completos de un artículo usando su Embase ID"""
    if not request.json:
        abort(400)
    emid = request.json["id"]
    
    headers = {
        "X-ELS-APIKey": ELSEVIER_API_KEY,
        "Accept": "application/json"
    }
    
    url = f"{ELSEVIER_BASE_URL}/article/{emid}"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return jsonify(error="Article not found"), 404
        
    data = response.json()
    return jsonify(
        emid=data.get("id"),
        title=data.get("title"),
        abstract=data.get("abstract"),
        authors=data.get("authors", []),
        doi=data.get("doi"),
        year=data.get("publicationDate", "")[:4],
        journal=data.get("journal", {}).get("title"),
        keywords=data.get("keywords", []),
        organizations=[org.get("name") for org in data.get("affiliations", [])]
    )

@app.route("/emid2pdf", methods=["POST"])
def pdf_from_emid():
    """Obtiene la URL del PDF de un artículo usando su Embase ID"""
    if not request.json:
        abort(400)
    emid = request.json["id"]
    
    headers = {
        "X-ELS-APIKey": ELSEVIER_API_KEY,
        "Accept": "application/json"
    }
    
    url = f"{ELSEVIER_BASE_URL}/article/{emid}"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return jsonify(error="Article not found"), 404
        
    data = response.json()
    pdf_url = data.get("pdfUrl", "")
    return jsonify(pdf_url=pdf_url)

def search_equation(query: List[str]) -> str:
    """Convierte una lista de términos de búsqueda en una ecuación de búsqueda"""
    pattern = " AND ".join([f'"{term}"' for term in query])
    print(f"search_equation={pattern}", flush=True)
    return pattern

def fill_graph(
    graph_type: GraphType,
    items: List[str],
    organization: str,
    project: str,
    pattern_id: str,
) -> None:
    """Llena un grafo con las relaciones entre items"""
    if len(items) < 2:
        return None

    singular = graph_type.value[:-1] if graph_type.value != "countries" else "country"
    item = items.pop()
    document = {"related": {"$each": sorted(items)}}
    
    post_json_request(
        "http://db:5000/mongo-doc-update",
        {
            "db_name": organization,
            "coll_name": f"{graph_type.value}#{project}#global",
            "filter": {singular: item},
            "document": document,
            "add_to_set": True,
        },
    )
    
    post_json_request(
        "http://db:5000/mongo-doc-update",
        {
            "db_name": organization,
            "coll_name": f"{graph_type.value}#{project}#{pattern_id}",
            "filter": {singular: item},
            "document": document,
            "add_to_set": True,
        },
    )
    
    fill_graph(graph_type, items, organization, project, pattern_id)

@app.route("/query", methods=["POST"])
def query():
    """Endpoint principal para búsqueda y procesamiento de artículos"""
    if not request.json:
        abort(400)
        
    query = request.json["query"]
    patternid = request.json["patternid"]
    database = request.json["organization"]
    project = request.json["project"]
    maxdocs = request.json["maxdocs"]
    
    headers = {
        "X-ELS-APIKey": ELSEVIER_API_KEY,
        "Accept": "application/json"
    }
    
    # Realizar búsqueda
    search_url = f"{ELSEVIER_BASE_URL}/search"
    search_params = {
        "query": search_equation(query.strip().split()),
        "count": maxdocs * 10
    }
    
    response = requests.get(search_url, headers=headers, params=search_params)
    if response.status_code != 200:
        return jsonify(error="Search failed"), 500
        
    data = response.json()
    articles = data.get("entries", [])
    
    count = 0
    for article in articles:
        if count >= maxdocs:
            break
            
        emid = article.get("id")
        if not emid:
            continue
            
        # Obtener detalles del artículo
        article_url = f"{ELSEVIER_BASE_URL}/article/{emid}"
        article_response = requests.get(article_url, headers=headers)
        
        if article_response.status_code != 200:
            continue
            
        article_data = article_response.json()
        
        # Procesar datos del artículo
        title = article_data.get("title", "")
        abstract = article_data.get("abstract", "")
        authors = [author.get("name") for author in article_data.get("authors", [])]
        doi = article_data.get("doi", "")
        year = article_data.get("publicationDate", "")[:4]
        keywords = article_data.get("keywords", [])
        organizations = [org.get("name") for org in article_data.get("affiliations", [])]
        pdf_url = article_data.get("pdfUrl", "")
        
        if not pdf_url:
            continue
            
        # Obtener texto completo
        full_text = post_json_request(
            "http://preprocessing:5000/url2text",
            {"url": pdf_url}
        ).get("url2text")
        
        if not full_text:
            continue
            
        # Procesar texto completo
        emails = list(set(
            post_json_request(
                "http://preprocessing:5000/text2emails",
                {"text": full_text}
            ).get("emails", [])
        ))
        
        keywords_with_score = sorted(
            post_json_request(
                "http://preprocessing:5000/text2keywords",
                {"text": full_text}
            ).get("keywords", []),
            key=lambda x: x[1],
            reverse=True
        )
        
        keywords = [keyword[0] for keyword in keywords_with_score[:3]]
        organizations = list({email.split("@")[1] for email in emails if "@" in email})
        
        countries_with_score = sorted(
            post_json_request(
                "http://preprocessing:5000/text2places",
                {"text": full_text}
            ).get("places", []),
            key=lambda x: x[1],
            reverse=True
        )
        
        countries = [country[0] for country in countries_with_score[:3]]
        language = post_json_request(
            "http://preprocessing:5000/text2lang",
            {"text": full_text}
        ).get("lang", "")
        
        # Crear documento principal
        document = {
            "pat_id": patternid,
            "source": "embase",
            "dbid": emid,
            "doi": doi,
            "title": title,
            "abstract": abstract,
            "authors": authors,
            "emails": emails,
            "keywords": keywords,
            "organizations": organizations,
            "countries": countries,
            "url": pdf_url,
            "year": year,
            "language": language,
        }
        
        # Almacenar en MongoDB
        post_json_request(
            "http://db:5000/mongo-doc-update",
            {
                "db_name": database,
                "coll_name": f"metadata#{project}#{patternid}",
                "filter": {"title": title},
                "document": document,
            }
        )
        
        # Crear grafos
        authors_set = sorted(set(emails), reverse=True)
        fill_graph(GraphType.AUTHORS, authors_set.copy(), database, project, patternid)
        
        keywords_set = sorted(set(keywords), reverse=True)
        fill_graph(GraphType.KEYWORDS, keywords_set.copy(), database, project, patternid)
        
        organizations_set = sorted(set(organizations), reverse=True)
        fill_graph(GraphType.ORGANIZATIONS, organizations_set.copy(), database, project, patternid)
        
        countries_set = sorted(set(countries), reverse=True)
        fill_graph(GraphType.COUNTRIES, countries_set.copy(), database, project, patternid)
        
        # Almacenar información global
        post_json_request(
            "http://db:5000/mongo-doc-update",
            {
                "db_name": database,
                "coll_name": f"metadata#{project}#global",
                "filter": {"title": title},
                "document": document,
            }
        )
        
        count += 1
    
    return object_to_response({"exit": 0})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000) 