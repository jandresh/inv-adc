#!/usr/bin/env python
#
# Este scriptmuestra como consumir un *endpoint*  que 
# accede a un web service que consulta por artículos de 
# la base de datos pubmed.
#
# Para ejecutar este script debe ejecutar los siguientes pasos:
#  virtualenv venv
#  . venv/bin/activate
#  sudo apt-get install libxml2-dev libxslt-dev python-dev
#  pip3 install Flask metapub
#  export FLASK_APP=metapubws.py
#  export NCBI_API_KEY=”CLAVE_PUBMED”
#  flask run --host=0.0.0.0
#
# Author: Jaime Hurtado - jaime.hurtado@correounivalle.edu.co
# Fecha: 2021-03-02
#
from flask import Flask, jsonify, request
from metapub import PubMedFetcher

app = Flask(__name__)

#
# Este metodo retorna informacion de microservicios disponibles
#
@app.route('/')
def helloworld():
    return 'metapubws endpoints: /title, /abstract, /pmids'

#
# *****title_from_pmid()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "id": "2020202" }' http://localhost:5000/title
#
@app.route("/title",methods=['POST'])
def title_from_pmid():
  fetch = PubMedFetcher()
  if not request.json:
    abort(400)
  pmid = request.json['id']
  article = fetch.article_by_pmid(pmid)
  return jsonify(title=article.title)
#
# *****abstract_from_pmid()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "id": "2020202" }' http://localhost:5000/abstract
#
@app.route("/abstract",methods=['POST'])
def abstract_from_pmid():
  fetch = PubMedFetcher()
  if not request.json:
    abort(400)
  pmid = request.json['id']
  article = fetch.article_by_pmid(pmid)
  return jsonify(abstract=article.abstract)
#
# *****pmid_from_query()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "query": "breast neoplasm" }' http://localhost:5000/pmids
#
@app.route("/pmids",methods=['POST'])
def pmid_from_query():
  fetch = PubMedFetcher()
  if not request.json:
    abort(400)
  query = request.json['query']
  pmids = fetch.pmids_for_query(query, retmax=1000)
  return jsonify(pmids=pmids)