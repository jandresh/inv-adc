import arxiv
from enum import (
    Enum,
)
from flask import (
    abort,
    Flask,
    request,
    Response,
)
from flask_cors import (
    CORS,
)
import json
import requests

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
    response = Response(response=json.dumps(object), mimetype="application/json")
    response.headers["Access-Control-Allow-Origin"] = "*"

    return response


#
# Este metodo retorna informacion de microservicios disponibles
#


@app.route("/")
def root():
    return "arxiv endpoints: /arxiv, /query"


#
# *****query_arxiv******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "query": "breast cancer" }' http://localhost:5005/arxiv | jq '.' | less
#


@app.route("/arxiv", methods=["POST"])
def query_arxiv():
    if not request.json:
        abort(400)
    big_slow_client = arxiv.Client(page_size=1000, delay_seconds=10, num_retries=5)
    query = request.json["query"]
    count = 0
    results = big_slow_client.results(arxiv.Search(query=query, max_results=200))
    titles = []
    for result in results:
        count = count + 1
        if count > 1000:
            break
        print(
            f"""Count={count}
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
            result.pdf_url: {result.pdf_url}""",
            flush=True,
        )
        print([author.name for author in result.authors], flush=True)
        titles.append(result.title)

    return object_to_response({"exit": 0, "titles": titles})


def search_equation(query: list[str]) -> str:
    pattern = "abs:"
    for i in range(len(query)):
        if i == len(query) - 1:
            pattern += "%s" % (query[i])
        else:
            pattern += "%s AND abs:" % (query[i])
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


#
# *****query_arxiv******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "query": "breast carcinoma", "patternid": 1, "maxdocs": 200, "organization": "test4", "project": "adc-cali" }' http://localhost:5005/query | jq '.' | less
#


@app.route("/query", methods=["POST"])
def query():
    if not request.json:
        abort(400)
    query: str = request.json["query"]
    database = request.json["organization"]
    project = request.json["project"]
    max_docs = request.json["maxdocs"]
    big_slow_client = arxiv.Client(page_size=500, delay_seconds=10, num_retries=5)
    patternid = request.json["patternid"]
    results = big_slow_client.results(
        arxiv.Search(query=search_equation(query.strip().split()), max_results=max_docs)
    )

    for result in results:
        try:
            abstract = result.summary
            title = result.title
            dbid = result.entry_id.replace("http://arxiv.org/abs/", "")
            doi = result.doi
            authors = [author.name for author in result.authors]
            url = result.pdf_url
            year = result.published.year
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
            keywords = [keyword[0] for keyword in keywords_with_score[:3]]
            organizations = list(
                {email.split("@")[1] for email in emails if "@" in email}
            )
            countries_with_score: list[list[str]] = sorted(
                post_json_request(
                    "http://preprocessing:5000/text2places",
                    {"text": full_text},
                ).get("places", []),
                key=lambda x: x[1],
                reverse=True,
            )
            countries = [country[0] for country in countries_with_score[:3]]
            language = (
                post_json_request(
                    "http://preprocessing:5000/text2lang",
                    {"text": full_text},
                ).get("lang", ""),
            )
            if title is not None:
                document = {
                    "pat_id": patternid,
                    "source": "arxiv",
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
                organizations_set = sorted(set(organizations), reverse=True)
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
                                "organizations": {"$each": organizations_set},
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
                                "organizations": {"$each": organizations_set},
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
                                "organizations": {"$each": organizations_set},
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
                                "organizations": {"$each": organizations_set},
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
                                "organizations": {"$each": organizations_set},
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
                                "organizations": {"$each": organizations_set},
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
                                "organizations": {"$each": organizations_set},
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
                                "organizations": {"$each": organizations_set},
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
                                "organizations": {"$each": organizations_set},
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
                                "organizations": {"$each": organizations_set},
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
                                "organizations": {"$each": organizations_set},
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
                                "organizations": {"$each": organizations_set},
                                "year": year,
                            },
                            "add_to_set": True,
                        },
                    )
        except requests.exceptions.JSONDecodeError as error:
            print(error, flush=True)

    return object_to_response({"exit": 0})
