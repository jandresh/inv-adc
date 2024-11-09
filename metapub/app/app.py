#!/usr/bin/env python
#
# Author: Jaime Hurtado - jaime.hurtado@correounivalle.edu.co
# Fecha: 2022-03-02
#
from enum import (
    Enum,
)
from flask import (
    abort,
    Flask,
    jsonify,
    request,
    Response,
)
from flask_cors import (
    CORS,
)
import json
from metapub import (
    FindIt,
    PubMedFetcher,
)
import requests
import sys
import time

app = Flask(__name__)
CORS(app)


class GraphType(str, Enum):
    AUTHORS = "authors"
    COUNTRIES = "countries"
    KEYWORDS = "keywords"
    ORGANIZATIONS = "organizations"


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
# curl -X POST -H "Content-type: application/json" -d '{ "query": "breast cancer" }' http://localhost:5000/pmids
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


def search_equation(query: list[str]) -> str:
    pattern = ""
    for i in range(len(query)):
        if i == len(query) - 1:
            pattern += "%s[Title/Abstract]" % (query[i])
        else:
            pattern += "%s[Title/Abstract] AND " % (query[i])
    print(f"search_equation={pattern}", flush=True)
    return pattern


def fill_graph(
    graph_type: GraphType,
    items: list[str],
    organization: str,
    project: str,
    pattern_id: str,
) -> None:
    if len(items) < 2:
        return None

    singular = (
        graph_type.value[:-1] if graph_type.value != "countries" else "country"
    )
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


#
# *****query******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "query": "breast carcinoma", "patternid": 1, "maxdocs": 200, "organization": "test4", "project": "adc-cali" }' http://localhost:5000/query
#


@app.route("/query", methods=["POST"])
def query():
    fetch = PubMedFetcher()
    if not request.json:
        abort(400)
    query = request.json["query"]
    patternid = request.json["patternid"]
    database = request.json["organization"]
    project = request.json["project"]
    maxdocs = request.json["maxdocs"]
    count = 0
    success = False
    attempts = 0
    pmids = []
    while not success:
        attempts += 1
        try:
            pmids = fetch.pmids_for_query(
                search_equation(query.strip().split()), retmax=maxdocs
            )
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
                    article = (fetch.article_by_pmid(pmid)).__dict__
                    success = True
                except:
                    time.sleep(5)
                    success = False if attempts > 2 else True
            if success:
                try:
                    abstract = article.get("abstract", "")
                    title = article.get("title", "")
                    dbid = article.get("pmid", "")
                    doi = article.get("doi", "")
                    authors = article.get("authors", "")
                    url = ""
                    try:
                        url = FindIt(pmid).url
                    except:
                        url = ""
                    year = article.get("year", "")
                    if not url:
                        continue
                    full_text = post_json_request(
                        "http://preprocessing:5000/url2text", {"url": url}
                    ).get("url2text")
                    if not full_text:
                        continue
                    emails: list[str] = list(
                        set(
                            post_json_request(
                                "http://preprocessing:5000/text2emails",
                                {"text": full_text},
                            ).get("emails", [])
                        )
                    )
                    keywords_with_score: list[list[str]] = sorted(
                        post_json_request(
                            "http://preprocessing:5000/text2keywords",
                            {"text": full_text},
                        ).get("keywords", []),
                        key=lambda x: x[1],
                        reverse=True,
                    )
                    keywords = [
                        keyword[0] for keyword in keywords_with_score[:3]
                    ]
                    organizations = list(
                        {
                            email.split("@")[1]
                            for email in emails
                            if "@" in email
                        }
                    )
                    countries_with_score: list[list[str]] = sorted(
                        post_json_request(
                            "http://preprocessing:5000/text2places",
                            {"text": full_text},
                        ).get("places", []),
                        key=lambda x: x[1],
                        reverse=True,
                    )
                    countries = [
                        country[0] for country in countries_with_score[:3]
                    ]
                    language = (
                        post_json_request(
                            "http://preprocessing:5000/text2lang",
                            {"text": full_text},
                        ).get("lang", ""),
                    )
                    if title is not None:
                        document = {
                            "pat_id": patternid,
                            "source": "pubmed",
                            "dbid": dbid,
                            "doi": doi,
                            "title": title,
                            "abstract": abstract,
                            "authors": authors,
                            "emails": emails,
                            "keywords": keywords,
                            "organizations": organizations,
                            "countries": countries,
                            "url": url,
                            "year": year,
                            "language": language,
                        }
                        post_json_request(
                            "http://db:5000/mongo-doc-update",
                            {
                                "db_name": database,
                                "coll_name": f"metadata#{project}#{patternid}",
                                "filter": {"title": title},
                                "document": document,
                            },
                        )
                        authors_set = sorted(set(emails), reverse=True)
                        fill_graph(
                            GraphType.AUTHORS,
                            authors_set.copy(),
                            database,
                            project,
                            patternid,
                        )
                        keywords_set = sorted(set(keywords), reverse=True)
                        fill_graph(
                            GraphType.KEYWORDS,
                            keywords_set.copy(),
                            database,
                            project,
                            patternid,
                        )
                        organizations_set = sorted(
                            set(organizations), reverse=True
                        )
                        fill_graph(
                            GraphType.ORGANIZATIONS,
                            organizations_set.copy(),
                            database,
                            project,
                            patternid,
                        )
                        countries_set = sorted(set(countries), reverse=True)
                        fill_graph(
                            GraphType.COUNTRIES,
                            countries_set.copy(),
                            database,
                            project,
                            patternid,
                        )
                        post_json_request(
                            "http://db:5000/mongo-doc-update",
                            {
                                "db_name": database,
                                "coll_name": f"metadata#{project}#global",
                                "filter": {"title": title},
                                "document": document,
                            },
                        )
                        if language:
                            post_json_request(
                                "http://db:5000/mongo-doc-update",
                                {
                                    "db_name": database,
                                    "coll_name": f"language_info#{project}#{patternid}",
                                    "filter": {"language": language},
                                    "document": {
                                        "authors": {"$each": authors_set},
                                        "countries": {"$each": countries_set},
                                        "doc_id": dbid,
                                        "doi": doi,
                                        "keywords": {"$each": keywords_set},
                                        "organizations": {
                                            "$each": organizations_set
                                        },
                                        "year": year,
                                    },
                                    "add_to_set": True,
                                },
                            )
                            post_json_request(
                                "http://db:5000/mongo-doc-update",
                                {
                                    "db_name": database,
                                    "coll_name": f"language_info#{project}#global",
                                    "filter": {"language": language},
                                    "document": {
                                        "authors": {"$each": authors_set},
                                        "countries": {"$each": countries_set},
                                        "doc_id": dbid,
                                        "doi": doi,
                                        "keywords": {"$each": keywords_set},
                                        "organizations": {
                                            "$each": organizations_set
                                        },
                                        "year": year,
                                    },
                                    "add_to_set": True,
                                },
                            )
                        if year:
                            post_json_request(
                                "http://db:5000/mongo-doc-update",
                                {
                                    "db_name": database,
                                    "coll_name": f"year_info#{project}#{patternid}",
                                    "filter": {"year": str(year)},
                                    "document": {
                                        "authors": {"$each": authors_set},
                                        "countries": {"$each": countries_set},
                                        "doc_id": dbid,
                                        "doi": doi,
                                        "keywords": {"$each": keywords_set},
                                        "organizations": {
                                            "$each": organizations_set
                                        },
                                    },
                                    "add_to_set": True,
                                },
                            )
                            post_json_request(
                                "http://db:5000/mongo-doc-update",
                                {
                                    "db_name": database,
                                    "coll_name": f"year_info#{project}#global",
                                    "filter": {"year": str(year)},
                                    "document": {
                                        "authors": {"$each": authors_set},
                                        "countries": {"$each": countries_set},
                                        "doc_id": dbid,
                                        "doi": doi,
                                        "keywords": {"$each": keywords_set},
                                        "organizations": {
                                            "$each": organizations_set
                                        },
                                    },
                                    "add_to_set": True,
                                },
                            )
                        for email in emails:
                            post_json_request(
                                "http://db:5000/mongo-doc-update",
                                {
                                    "db_name": database,
                                    "coll_name": f"author_info#{project}#{patternid}",
                                    "filter": {"author": email},
                                    "document": {
                                        "authors": {"$each": authors_set},
                                        "countries": {"$each": countries_set},
                                        "doc_id": dbid,
                                        "doi": doi,
                                        "keywords": {"$each": keywords_set},
                                        "language": language,
                                        "organizations": {
                                            "$each": organizations_set
                                        },
                                        "year": year,
                                    },
                                    "add_to_set": True,
                                },
                            )
                            post_json_request(
                                "http://db:5000/mongo-doc-update",
                                {
                                    "db_name": database,
                                    "coll_name": f"author_info#{project}#global",
                                    "filter": {"author": email},
                                    "document": {
                                        "authors": {"$each": authors_set},
                                        "countries": {"$each": countries_set},
                                        "doc_id": dbid,
                                        "doi": doi,
                                        "keywords": {"$each": keywords_set},
                                        "language": language,
                                        "organizations": {
                                            "$each": organizations_set
                                        },
                                        "year": year,
                                    },
                                    "add_to_set": True,
                                },
                            )
                        for keyword in keywords:
                            post_json_request(
                                "http://db:5000/mongo-doc-insert",
                                {
                                    "db_name": database,
                                    "coll_name": f"wordcloud#{project}#{patternid}",
                                    "document": {
                                        "keyword": keyword,
                                    },
                                },
                            )
                            post_json_request(
                                "http://db:5000/mongo-doc-insert",
                                {
                                    "db_name": database,
                                    "coll_name": f"wordcloud#{project}#global",
                                    "document": {
                                        "keyword": keyword,
                                    },
                                },
                            )
                            post_json_request(
                                "http://db:5000/mongo-doc-update",
                                {
                                    "db_name": database,
                                    "coll_name": f"keyword_info#{project}#{patternid}",
                                    "filter": {"keyword": keyword},
                                    "document": {
                                        "authors": {"$each": authors_set},
                                        "countries": {"$each": countries_set},
                                        "doc_id": dbid,
                                        "doi": doi,
                                        "keywords": {"$each": keywords_set},
                                        "language": language,
                                        "organizations": {
                                            "$each": organizations_set
                                        },
                                        "year": year,
                                    },
                                    "add_to_set": True,
                                },
                            )
                            post_json_request(
                                "http://db:5000/mongo-doc-update",
                                {
                                    "db_name": database,
                                    "coll_name": f"keyword_info#{project}#global",
                                    "filter": {"keyword": keyword},
                                    "document": {
                                        "authors": {"$each": authors_set},
                                        "countries": {"$each": countries_set},
                                        "doc_id": dbid,
                                        "doi": doi,
                                        "keywords": {"$each": keywords_set},
                                        "language": language,
                                        "organizations": {
                                            "$each": organizations_set
                                        },
                                        "year": year,
                                    },
                                    "add_to_set": True,
                                },
                            )
                        for organization in organizations:
                            post_json_request(
                                "http://db:5000/mongo-doc-update",
                                {
                                    "db_name": database,
                                    "coll_name": f"organization_info#{project}#{patternid}",
                                    "filter": {"organization": organization},
                                    "document": {
                                        "authors": {"$each": authors_set},
                                        "countries": {"$each": countries_set},
                                        "doc_id": dbid,
                                        "doi": doi,
                                        "keywords": {"$each": keywords_set},
                                        "language": language,
                                        "organizations": {
                                            "$each": organizations_set
                                        },
                                        "year": year,
                                    },
                                    "add_to_set": True,
                                },
                            )
                            post_json_request(
                                "http://db:5000/mongo-doc-update",
                                {
                                    "db_name": database,
                                    "coll_name": f"organization_info#{project}#global",
                                    "filter": {"organization": organization},
                                    "document": {
                                        "authors": {"$each": authors_set},
                                        "countries": {"$each": countries_set},
                                        "doc_id": dbid,
                                        "doi": doi,
                                        "keywords": {"$each": keywords_set},
                                        "language": language,
                                        "organizations": {
                                            "$each": organizations_set
                                        },
                                        "year": year,
                                    },
                                    "add_to_set": True,
                                },
                            )
                        for country in countries:
                            post_json_request(
                                "http://db:5000/mongo-doc-update",
                                {
                                    "db_name": database,
                                    "coll_name": f"country_info#{project}#{patternid}",
                                    "filter": {"country": country},
                                    "document": {
                                        "authors": {"$each": authors_set},
                                        "countries": {"$each": countries_set},
                                        "doc_id": dbid,
                                        "doi": doi,
                                        "keywords": {"$each": keywords_set},
                                        "language": language,
                                        "organizations": {
                                            "$each": organizations_set
                                        },
                                        "year": year,
                                    },
                                    "add_to_set": True,
                                },
                            )
                            post_json_request(
                                "http://db:5000/mongo-doc-update",
                                {
                                    "db_name": database,
                                    "coll_name": f"country_info#{project}#global",
                                    "filter": {"country": country},
                                    "document": {
                                        "authors": {"$each": authors_set},
                                        "countries": {"$each": countries_set},
                                        "doc_id": dbid,
                                        "doi": doi,
                                        "keywords": {"$each": keywords_set},
                                        "language": language,
                                        "organizations": {
                                            "$each": organizations_set
                                        },
                                        "year": year,
                                    },
                                    "add_to_set": True,
                                },
                            )
                except requests.exceptions.JSONDecodeError as error:
                    print(error, flush=True)

    return object_to_response([{"exit": 0}])
