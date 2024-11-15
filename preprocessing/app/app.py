from flask import (
    abort,
    Flask,
    jsonify,
    request,
)
from flask_cors import (
    CORS,
)
import geograpy
import io
import nltk
from nltk import (
    ne_chunk,
    pos_tag,
    Tree,
    word_tokenize,
)
import pdftotext
import re
from urllib.request import (
    Request,
    urlopen,
)

nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")
nltk.download("maxent_ne_chunker")
nltk.download("words")
nltk.download("punkt_tab")
nltk.download("averaged_perceptron_tagger_eng")
nltk.download("maxent_ne_chunker_tab")

from gensim.summarization import (
    keywords,
)
from langdetect import (
    detect,
)
import warnings

warnings.filterwarnings("ignore")

app = Flask(__name__)
CORS(app)


def get_continuous_chunks(text, label):
    chunked = ne_chunk(pos_tag(word_tokenize(text)))
    continuous_chunk = []
    current_chunk = []

    for subtree in chunked:
        if type(subtree) == Tree and subtree.label() == label:
            current_chunk.append(
                " ".join([token for token, pos in subtree.leaves()])
            )
        if current_chunk:
            named_entity = " ".join(current_chunk)
            if named_entity not in continuous_chunk:
                continuous_chunk.append(named_entity)
                current_chunk = []
        else:
            continue

    return continuous_chunk


def get_pdf_text_by_page(url):
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    pdf_pages = pdftotext.PDF(io.BytesIO(urlopen(req).read()))
    return pdf_pages


@app.route("/")
def helloworld():
    return "preprocesing endpoints: /\n/url2text\n/url2htext\n/text2locations\n/text2places\n/text2ner\n/text2emails"


# *****text_from_pdf_url()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "url": "http://europepmc.org/backend/ptpmcrender.fcgi?accid=PMC7350007&blobtype=pdf"}' http://localhost:5002/url2text


@app.route("/url2text", methods=["POST"])
def text_from_pdf_url():
    if not request.json:
        abort(400)
    url = request.json["url"]
    return jsonify(url2text="\n\n".join(get_pdf_text_by_page(url)))


# *****htext_from_url()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "url": "http://europepmc.org/backend/ptpmcrender.fcgi?accid=PMC7350007&blobtype=pdf"}' http://localhost:5002/url2htext


@app.route("/url2htext", methods=["POST"])
def htext_from_url():
    if not request.json:
        abort(400)
    url = request.json["url"]
    full_text = get_pdf_text_by_page(url)
    return jsonify(htext=full_text[0] if full_text else "")


# *****locations_from_text()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "text": ""}' http://localhost:5002/text2locations


@app.route("/text2locations", methods=["POST"])
def locations_from_text():
    if not request.json:
        abort(400)
    text = request.json["text"]
    return jsonify(locations=get_continuous_chunks(text, "GPE"))


# *****places_from_text()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "text": ""}' http://localhost:5002/text2places


@app.route("/text2places", methods=["POST"])
def places_from_text():
    if not request.json:
        abort(400)
    text = request.json["text"]
    return jsonify(
        places=geograpy.get_place_context(text=text).country_mentions
    )


# *****ner_from_text()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "text": ""}' http://localhost:5002/text2ner


@app.route("/text2ner", methods=["POST"])
def ner_from_text():
    if not request.json:
        abort(400)
    text = request.json["text"]
    tokens = nltk.word_tokenize(text)
    tagged = nltk.pos_tag(tokens)
    nltk.chunk.ne_chunk(tagged)
    return jsonify(entities=nltk.chunk.ne_chunk(tagged))


# *****emails_from_text()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "text": ""}' http://localhost:5002/text2emails


@app.route("/text2emails", methods=["POST"])
def emails_from_text():
    if not request.json:
        abort(400)
    text = request.json["text"]
    return jsonify(
        emails=re.findall(
            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            text,
        )
    )


# *****language_from_text()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "text": ""}' http://localhost:5002/text2lang


@app.route("/text2lang", methods=["POST"])
def language_from_text():
    if not request.json:
        abort(400)
    try:
        lang = detect(request.json["text"].lower())
    except:
        lang = ""

    return jsonify(lang=lang)


# *****keywords_from_text()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "text": ""}' http://localhost:5002/text2keywords


@app.route("/text2keywords", methods=["POST"])
def keywords_from_text():
    if not request.json:
        abort(400)
    try:
        output = keywords(text=request.json["text"], split="\n", scores=True)
    except ValueError as ex:
        print(f"Exception in fetch keywords: {ex}", flush=True)
        output = []

    return jsonify(keywords=output)
