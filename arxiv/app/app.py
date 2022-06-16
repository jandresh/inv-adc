import json
from unittest import skip
from flask import Flask, request, Response
import arxiv
import requests
import sys

app = Flask(__name__)

def post_json_request(url, obj):
    return requests.post(url, json=obj).json()

def object_to_response(object):
    response = Response(
        response=json.dumps(object),
        mimetype="application/json"
    )
    response.headers['Access-Control-Allow-Origin'] = '*'

    return response

#
# Este metodo retorna informacion de microservicios disponibles
#

@app.route('/')
def root():
    return 'arxiv endpoints: /arxiv, /query'

#
# *****query_arxiv******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "query": "terms: AND abstract=BREAST; AND abstract=CANCER" }' http://localhost:5005/arxiv | jq '.' | less
#

@app.route("/arxiv", methods=['POST'])
def query_arxiv():
    if not request.json:
        abort(400)
    big_slow_client = arxiv.Client(
        page_size = 1000,
        delay_seconds = 10,
        num_retries = 5
    )
    query = request.json['query']
    count = 0
    results = big_slow_client.results(arxiv.Search(query=query))
    for result in results:
        count = count + 1
        if count > 1000 :
            break
        print(
            f'''Count={count}
            result.entry_id: {result.entry_id}
            result.updated: {result.updated}
            result.published: {result.published}
            result.title: {result.title}
            result.authors: {result.authors}
            result.summary: {result.summary}
            result.comment: {result.comment}
            result.journal_ref: {result.journal_ref}
            result.doi: {result.doi}
            result.primary_category: {result.primary_category}
            result.categories: {result.categories}
            result.links: {result.links}
            result.pdf_url: {result.pdf_url}'''
        )
        authors=list(map(lambda author: author.name))
        print(authors)
        sys.stdout.flush()

    return object_to_response({"exit": 0})

#
# *****query_arxiv******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "query": "terms: AND abstract=BREAST; AND abstract=CANCER", "patternid": 1, "maxdocs": 2000 }' http://localhost:5005/query | jq '.' | less
#

@app.route("/query", methods=['POST'])
def query():
    if not request.json:
        abort(400)
    big_slow_client = arxiv.Client(
        page_size = 500,
        delay_seconds = 10,
        num_retries = 5
    )
    query = request.json['query']
    patternid = request.json['patternid']
    maxdocs = request.json['maxdocs']
    count = 0
    results = big_slow_client.results(arxiv.Search(query=query))
    for result in results:
        count = count + 1
        if count > maxdocs :
            break
        abstract = result.summary
        title = result.title
        dbid = result.entry_id.replace('http://arxiv.org/abs/','')
        doi = result.doi
        authors = list(map(lambda author: author.name, result.authors))
        url = result.pdf_url
        year = result.published.isoformat()
        try:
            if abstract is not None:
                text = abstract
            elif title is not None:
                text = title
            else:
                text = ""
            lang_json = post_json_request(
                'http://preprocessing:5000/text2lang', {"text": text})
        except:
            lang_json['lang'] = ""
        if result is not None:
            document = {
                "pat_id": patternid if patternid is not None else "",
                "dbid" : dbid if dbid is not None else "",
                "doi" : doi if doi is not None else "",
                "title" : title if title is not None else "",
                "abstract" : abstract if abstract is not None else "",
                "authors" : authors if authors is not None else "",
                "org" : "",
                "url" : url if url is not None else "",
                "year" : year if year is not None else "",
                "lang" : lang_json['lang'] if lang_json['lang'] is not None else ""
            }
            try:
                post_json_request(
                    'http://db:5000/mongo-doc-insert',
                    {
                        "db_name" : "metadata",
                        "coll_name" : f"metadata_{patternid}",
                        "document" : document
                    }
                )
            except:
                print(f"Exception on can't insert document for {dbid}")
            try:
                post_json_request(
                    'http://db:5000/mongo-doc-insert',
                    {
                        "db_name" : "metadata",
                        "coll_name" : f"metadata_global",
                        "document" : document
                    }
                )
            except:
                print(f"Exception on can't insert document for {dbid}")
            for author in authors:
                try:
                    post_json_request(
                        'http://db:5000/mongo-doc-insert',
                        {
                            "db_name" : "authors",
                            "coll_name" : f"author_vs_doc_id_{patternid}",
                            "document" : {
                                "author" : author,
                                "doc_id" : dbid if dbid is not None else "",
                                "doi" : doi if doi is not None else "",
                            }
                        }
                    )
                except:
                    print(f"Exception on can't insert document for author {author}")
                try:
                    post_json_request(
                        'http://db:5000/mongo-doc-insert',
                        {
                            "db_name" : "authors",
                            "coll_name" : f"author_vs_doc_id_global",
                            "document" : {
                                "author" : author,
                                "doc_id" : dbid if dbid is not None else "",
                                "doi" : doi if doi is not None else "",
                            }
                        }
                    )
                except:
                    print(f"Exception on can't insert document for author {author}")
            sys.stdout.flush()
    return object_to_response({"exit": 0})
