from datetime import (
    datetime,
)
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
import requests
import time

app = Flask(__name__)
CORS(app)


class GraphType(str, Enum):
    AUTHORS = "authors"
    COUNTRIES = "countries"
    KEYWORDS = "keywords"
    ORGANIZATIONS = "organizations"


apikey = "JAnjvcE7LDiB0aHeh8ruR3gUGFVW6qSI"


def post_json_request(url, obj):
    try:
        response = requests.post(url, json=obj).json()
    except:
        print(f"Error: Can't process the request to {url}\n {obj}", flush=True)
        response = {}

    return response


def object_to_response(object):
    response = Response(response=json.dumps(object), mimetype="application/json")
    response.headers["Access-Control-Allow-Origin"] = "*"

    return response


def query_api(search_url, query, scroll_id=None):
    result_flag = 0
    while result_flag < 5:
        try:
            headers = {"Authorization": "Bearer " + apikey}
            if not scroll_id:
                response = requests.get(
                    f"{search_url}?q={query}&limit=100&scroll=true",
                    headers=headers,
                )
            else:
                response = requests.get(
                    f"{search_url}?q={query}&limit=100&scroll_id={scroll_id}",
                    headers=headers,
                )
        except:
            time.sleep(3)
            response = None
        if response is not None:
            success = False
            if str(response) == "<Response [200]>":
                success = True
                try:
                    result = response.json()
                    elapsed = response.elapsed.total_seconds()
                except:
                    success = False
            elif str(response) == "<Response [429]>":
                time.sleep(300)
            if success:
                return result, elapsed
        result_flag += 1
    return None, None


def scroll(search_url, query, extract_info_callback=None):
    allresults = []
    count = 0
    scroll_id = None
    while True:
        result, elapsed = query_api(search_url, query, scroll_id)
        if result is None:
            break
        scroll_id = result.get("scroll_id")
        totalhits = result.get("totalHits")
        result_size = len(result.get("results", 0))
        if result_size == 0:
            break
        for hit in result["results"]:
            if extract_info_callback:
                allresults.append(extract_info_callback(hit))
            else:
                allresults.append(hit)
        count += result_size
        print(f"{count}/{totalhits} {elapsed}s", flush=True)
        if scroll_id is None:
            break
    return allresults


def format_pubmed_author(author: str):
    formatted_author = author.split(",")
    if len(formatted_author) > 2:
        authors = []
        for nested_author in formatted_author:
            author_name = nested_author.split(" ")
            if len(author_name) > 1:
                authors.append(
                    author_name[-1]
                    + f"""{''.join(list(map(
                        lambda name: name[0] if len(name) > 0 else '',
                        author_name[0:-2])))}"""
                )
        return authors
    if len(formatted_author) == 2:
        return (
            f"{formatted_author[0]} "
            + f"""{''.join(list(map(
                lambda name: name[0] if len(name) > 0 else '',
                formatted_author[1].split(' '))))}"""
        )
    if len(formatted_author) == 1:
        spaced_author = list(
            filter(lambda item: len(item) > 0, formatted_author[0].split(" "))
        )
        if len(spaced_author) > 1:
            return (
                spaced_author[-1]
                + f""" {''.join(list(map(
                lambda name: name[0] if len(name) > 0 else '',
                spaced_author[0:-2])))}"""
            )

    return ""


def standardize_authors(authors):
    standardized_authors = list(
        filter(
            lambda item: item != "",
            map(
                lambda author: format_pubmed_author(author.get("name", "")),
                authors,
            ),
        )
    )
    if len(standardized_authors) == 1 and type(standardized_authors[0]) == "list":
        return list(
            filter(
                lambda item: item != "",
                map(
                    lambda author: format_pubmed_author(author.get("name", "")),
                    standardized_authors[0],
                ),
            )
        )

    return standardized_authors


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


def iterator(search_url, query, patternid, database, project, maxdocs):
    count = 0
    spanish_count = 0
    scroll_id = None
    while True:
        try:
            results, elapsed = query_api(search_url, query, scroll_id)
            time.sleep(2)
            print(f'scroll_id : {result["scroll_id"]}', flush=True)
            if results is None:
                break
        except:
            result = None
        if results is not None:
            scroll_id = results.get("scrollId")
            totalhits = results["totalHits"]
            result_size = len(results["results"])
            if result_size == 0:
                break
            for result in results["results"]:
                try:
                    abstract = result.get("abstract", "")
                    title = result.get("title", "")
                    dbid = result.get("id", "")
                    doi = result.get("doi", "")
                    authors = standardize_authors(result.get("authors", ""))
                    url = result.get("downloadUrl", "")
                    year = result.get("publishedDate", "")
                    year = datetime.fromisoformat(year).year if year else None
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
                            "source": "core",
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

                    count += 1
                except requests.exceptions.JSONDecodeError as error:
                    print(error, flush=True)

                if count > maxdocs:
                    break
            print(f"{count}/{totalhits} {elapsed}s", flush=True)
            if count > maxdocs or count == totalhits:
                break
        else:
            break
    return spanish_count


#
# Este metodo retorna informacion de microservicios disponibles
#


@app.route("/")
def root():
    return "core endpoints: /core, /core2, /query"


#
# *****query_core******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "query": "carcinoma lobulillar de mama" }' http://localhost:5003/core | jq '.' | less
#


@app.route("/core", methods=["POST"])
def query_core():
    if not request.json:
        abort(400)
    result = None
    query = request.json["query"]
    search, _seconds = query_api("https://api.core.ac.uk/v3/search/works", query)
    for key, value in search.items():
        if key == "results":
            result = value

    return jsonify(result)


#
# *****query_core******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "query": "carcinoma lobulillar de mama" }' http://localhost:5003/core2 | jq '.' | less
#


@app.route("/core2", methods=["POST"])
def query_core_scroll():
    if not request.json:
        abort(400)
    result = None
    query = request.json["query"]
    result = scroll("https://api.core.ac.uk/v3/search/works", query)
    return jsonify(result=result)


def search_equation(query: list[str]) -> str:
    pattern = "abstract:("
    for i in range(len(query)):
        if i == len(query) - 1:
            pattern += "%s)" % (query[i])
        else:
            pattern += "%s AND " % (query[i])
    print(f"search_equation={pattern}", flush=True)
    return pattern


#
# *****query******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "query": "breast carcinoma", "patternid": 1, "maxdocs": 200, "organization": "test4", "project": "adc-cali" }' http://localhost:5003/query
#


@app.route("/query", methods=["POST"])
def query():
    if not request.json:
        abort(400)
    query: str = request.json["query"]
    ptid = request.json["patternid"]
    organization = request.json["organization"]
    project = request.json["project"]
    max_docs = request.json["maxdocs"]
    iterator(
        "https://api.core.ac.uk/v3/search/works",
        search_equation(query.strip().split()),
        ptid,
        organization,
        project,
        max_docs,
    )
    return object_to_response({"exit": 0})
