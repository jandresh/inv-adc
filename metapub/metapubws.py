#!/usr/bin/env python
#
# Author: Jaime Hurtado - jaime.hurtado@correounivalle.edu.co
# Fecha: 2022-03-02
#
from flask import Flask, jsonify, request, Response
import json
from metapub import PubMedFetcher
from metapub import FindIt
import requests
import time
import sys

app = Flask(__name__)


def post_json_request(url, obj):
    return requests.post(url, json=obj).json()


def object_to_response(object):
    response = Response(
        response=json.dumps(object), mimetype="application/json"
    )
    response.headers["Access-Control-Allow-Origin"] = "*"

    return response


#
# Este metodo retorna informacion de microservicios disponibles
#


@app.route("/")
def root():
    return "metapub endpoints: /title, /abstract, /pmids, /metadata, /pmid2pdf, /query"


#
# *****title_from_pmid()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "id": "2020202" }' http://localhost:5000/title
#


@app.route("/title", methods=["POST"])
def title_from_pmid():
    fetch = PubMedFetcher()
    if not request.json:
        abort(400)
    pmid = request.json["id"]
    unsuccess = True
    while unsuccess:
        try:
            article = fetch.article_by_pmid(pmid)
            unsuccess = False
        except:
            time.sleep(1)
            unsuccess = True
    return jsonify(title=article.title)


#
# *****abstract_from_pmid()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "id": "2020202" }' http://localhost:5000/abstract
#


@app.route("/abstract", methods=["POST"])
def abstract_from_pmid():
    fetch = PubMedFetcher()
    if not request.json:
        abort(400)
    pmid = request.json["id"]
    unsuccess = True
    while unsuccess:
        try:
            article = fetch.article_by_pmid(pmid)
            unsuccess = False
        except:
            time.sleep(1)
            unsuccess = True
    return jsonify(abstract=article.abstract)


#
# *****pmid_from_query()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "query": "breast neoplasm" }' http://localhost:5000/pmids
#


@app.route("/pmids", methods=["POST"])
def pmid_from_query():
    fetch = PubMedFetcher()
    if not request.json:
        abort(400)
    query = request.json["query"]
    unsuccess = True
    while unsuccess:
        try:
            pmids = fetch.pmids_for_query(query, retmax=100)
            unsuccess = False
        except:
            time.sleep(1)
            unsuccess = True
    return jsonify(pmids=pmids)


#
# *****metadata_from_pmid()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "id": "2020202" }' http://localhost:5000/metadata
#


@app.route("/metadata", methods=["POST"])
def metadata_from_pmid():
    fetch = PubMedFetcher()
    if not request.json:
        abort(400)
    pmid = request.json["id"]
    unsuccess = True
    while unsuccess:
        try:
            article = fetch.article_by_pmid(pmid)
            unsuccess = False
        except:
            time.sleep(1)
            unsuccess = True
    return jsonify(
        pmid=article.pmid,
        title=article.title,
        abstract=article.abstract,
        citation=article.citation,
        pubmed_type=article.pubmed_type,
        url=article.url,
        authors=article.authors,
        # author_list=article.author_list, #Puede no funionar porque devuelve una lista
        # authors_str=article.authors_str,
        # author1_last_fm=article.author1_last_fm,
        # author1_lastfm=article.author1_lastfm,
        # pages=article.pages,
        # first_page=article.first_page,
        # last_page=article.last_page,
        # volume=article.volume,
        # issue=article.issue,
        # volume_issue=article.volume_issue,
        doi=article.doi,
        # pii=article.pii,
        # pmc=article.pmc,
        # issn=article.issn,
        # mesh=article.mesh,
        # chemicals=article.chemicals,
        # grants=article.grants,
        # publication_types=article.publication_types,
        # book_accession_id=article.book_accession_id,
        # book_title=article.book_title,
        # book_publisher=article.book_publisher,
        # book_language=article.book_language,
        # book_editors=article.book_editors,
        # book_abstracts=article.book_abstracts,
        # book_sections =article.book_sections,
        # book_copyright=article.book_copyright,
        # book_medium=article.book_medium,
        # book_synonyms=article.book_synonyms,
        # book_publication_status=article.book_publication_status,
        # book_history =article.book_history ,
        # book_contribution_date=article.book_contribution_date,
        # book_date_revised=article.book_date_revised,
        # journal=article.journal,
        year=article.year
        # history=article.history,
    )


#
# *****pdf_from_pmid()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "id": "32599772"}' http://localhost:5000/pmid2pdf


@app.route("/pmid2pdf", methods=["POST"])
def pdf_from_pmid():
    fetch = PubMedFetcher()
    if not request.json:
        abort(400)
    pmid = request.json["id"]
    try:
        src = FindIt(pmid)
    except:
        return jsonify(pdf_url="")
    return jsonify(pdf_url=src.url)


#
# *****query******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "query": "terms: AND abstract=BREAST; AND abstract=CANCER", "patternid": 1, "maxdocs": 2000 }' http://localhost:5000/query | jq '.' | less
#


@app.route("/query", methods=["POST"])
def query():
    fetch = PubMedFetcher()
    if not request.json:
        abort(400)
    query = request.json["query"]
    patternid = request.json["patternid"]
    maxdocs = request.json["maxdocs"]
    count = 0
    success = False
    attempts = 0
    pmids = []
    while not success:
        attempts += 1
        try:
            pmids = fetch.pmids_for_query(query, retmax=maxdocs)
            success = True
        except:
            time.sleep(5)
            success = False if attempts > 2 else True
    if success:
        for pmid in pmids:
            count = count + 1
            if count > maxdocs:
                break
            success = False
            attempts = 0
            article = {}
            while not success:
                attempts += 1
                try:
                    article = fetch.article_by_pmid(pmid)
                    success = True
                except:
                    time.sleep(5)
                    success = False if attempts > 2 else True
            if success:
                abstract = article.abstract
                title = article.title
                dbid = article.pmid
                doi = article.doi
                authors = article.authors
                url = ""
                try:
                    url = FindIt(pmid).url
                except:
                    url = ""
                year = article.year
                try:
                    if abstract is not None:
                        text = abstract
                    elif title is not None:
                        text = title
                    else:
                        text = ""
                    lang_json = post_json_request(
                        "http://preprocessing:5000/text2lang", {"text": text}
                    )
                except:
                    lang_json["lang"] = ""
                if pmid is not None:
                    document = {
                        "pat_id": patternid if patternid is not None else "",
                        "dbid": dbid if dbid is not None else "",
                        "doi": doi if doi is not None else "",
                        "title": title if title is not None else "",
                        "abstract": abstract if abstract is not None else "",
                        "authors": authors if authors is not None else "",
                        "org": "",
                        "url": url if url is not None else "",
                        "year": year if year is not None else "",
                        "lang": lang_json["lang"]
                        if lang_json["lang"] is not None
                        else "",
                    }
                    try:
                        post_json_request(
                            "http://db:5000/mongo-doc-insert",
                            {
                                "db_name": "metadata",
                                "coll_name": f"metadata_{patternid}",
                                "document": document,
                            },
                        )
                    except:
                        print(f"Exception on can't insert document for {dbid}")
                    try:
                        post_json_request(
                            "http://db:5000/mongo-doc-insert",
                            {
                                "db_name": "metadata",
                                "coll_name": f"metadata_global",
                                "document": document,
                            },
                        )
                    except:
                        print(
                            f"Exception on can't insert global document for {dbid}"
                        )
                    for author in authors:
                        try:
                            post_json_request(
                                "http://db:5000/mongo-doc-insert",
                                {
                                    "db_name": "authors",
                                    "coll_name": f"author_vs_doc_id_{patternid}",
                                    "document": {
                                        "author": author,
                                        "doc_id": dbid
                                        if dbid is not None
                                        else "",
                                        "doi": doi if doi is not None else "",
                                    },
                                },
                            )
                        except:
                            print(
                                f"Exception on can't insert document for author {author}"
                            )
                        try:
                            post_json_request(
                                "http://db:5000/mongo-doc-insert",
                                {
                                    "db_name": "authors",
                                    "coll_name": f"author_vs_doc_id_global",
                                    "document": {
                                        "author": author,
                                        "doc_id": dbid
                                        if dbid is not None
                                        else "",
                                        "doi": doi if doi is not None else "",
                                    },
                                },
                            )
                        except:
                            print(
                                f"Exception on can't insert document for author {author}"
                            )
                    sys.stdout.flush()
    return object_to_response({"exit": 0})
