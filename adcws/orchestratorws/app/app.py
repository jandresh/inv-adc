from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

def post_json_request(url, obj):
    return requests.post(url, json=obj).json()

#
# Este metodo retorna informacion de microservicios disponibles
#

@app.route('/')
def root():
    return 'orchestratorws endpoints: /'

@app.route('/pipeline3', methods=['GET'])
def pipeline3():
    # Query patterns
    try:
        patterns_list = post_json_request(
            'http://dbws:5000/mysql-query',
            {"query" : "select * from patterns"}
        )
    except:
        patterns_list = None
    # For every pattern get metadata
    for pattern in patterns_list:
        print (str(pattern))
        if (pattern['db'] == 'PUBMED'):
            try:
                pmids = post_json_request(
                    'http://metapubws:5000/pmids', {"query": pattern['pattern']})
            except:
                pmids = None
            if pmids is not None:
                print (str(pmids_json))
                for pmid in pmids:

    return jsonify(patterns_list)


# @app.route('/pipeline2', methods=['GET'])
# def pipeline2():
#     connection = mysql.connector.connect(**config)
#     # Para cada patron sacar 1000 pmid o coreid
#     # para cada pmid o coreid recuperar metadatos
#     # llenar la base de datos
#     results = execute_mysql_query('SELECT * FROM patterns', connection)
#     for pattern in results:
#         get_metadata = True
#         if (pattern['db'] == 'PUBMED'):
#             try:
#                 pmids_json = post_json_request(
#                     'http://metapubws:5000/pmids', {"query": pattern['pattern']})
#             except:
#                 get_metadata = False
#             if get_metadata:
#                 pmids = pmids_json['pmids']
#                 doc_id_counter = 0
#                 insert_counter = 0
#                 for doc_id in pmids:
#                     print("id_pattern:%s" % pattern['id'])
#                     print("pattern:%s" % pattern['pattern'])
#                     print("doc_id:%s" % doc_id)
#                     doc_id_counter += 1
#                     print("doc_id_counter:%s" % doc_id_counter)
#                     success = 0
#                     if doc_id is not None:
#                         insert_mysql = True
#                         try:
#                             metadata_json = post_json_request(
#                                 'http://metapubws:5000/metadata', {"id": doc_id})
#                         except:
#                             insert_mysql = False
#                         print("title:%s" % metadata_json['title'])
#                         print("abstract:%s" % metadata_json['abstract'])
#                         # time.sleep(0.3)
#                         if(metadata_json['abstract'] == None):
#                             insert_abstract = ""
#                         else:
#                             insert_abstract = metadata_json['abstract']
#                         if(metadata_json['title'] == None):
#                             insert_title = ""
#                         else:
#                             insert_title = metadata_json['title']
#                         if insert_mysql:
#                             try:
#                                 query = 'INSERT INTO searches (patid, docid, title, abs, ftext) VALUES (%s,%s,"%s","%s","%s") ON DUPLICATE KEY UPDATE title="%s", abs="%s", ftext="%s";' % (pattern['id'], doc_id, insert_title.replace(
#                                     '"', '').replace('\n', ''), insert_abstract.replace('"', '').replace('\n', ''), '', insert_title.replace('"', '').replace('\n', ''), insert_abstract.replace('"', '').replace('\n', ''), '')
#                                 results = execute_mysql_query2(
#                                     query, connection)
#                                 success = 1
#                             except:
#                                 query = "Mysql not executed"
#                                 success = 0
#                     insert_counter += success
#                     print("insert_counter:%s" % insert_counter)
#         elif (pattern['db'] == 'CORE'):
#             try:
#                 search_json = post_json_request(
#                     'http://corews:5000/core2', {"query": pattern['pattern'], "idpattern": pattern['id']})
#             except:
#                 get_metadata = False
#                 print('Not Success')
#             if get_metadata:
#                 print("CORE insert success:%s" % pattern['pattern'])
#                 print('Spanish results: ', search_json['result'])
#             else:
#                 print("CORE insert not success:%s" % pattern['pattern'])

#     results = execute_mysql_query(
#         'SELECT patid, docid, title FROM searches order by patid desc', connection)
#     connection.close()
#     return jsonify(results)


# METAPUB OUT:

# {
#   "abstract": "This article proposes and evaluates two models for integrating self-reported health status measures for the elderly with dominant conceptualizations of physical health. Each model includes three dimensions of physical health: chronic illness, functional limitation, and self-rated health. In Model 1, the dimensions are linked in a causal framework, whereas in Model 2, a second-order factor, labeled physical health status, is hypothesized to account for the relationships among the three dimensions. Each model was tested with data gathered in Cleveland (N = 1,834) and Virginia (N = 2,146) using the Older Americans Resources and Services Multidimensional Functional Assessment Questionnaire (OARS MFAQ). Analyses were further replicated by randomly dividing each sample. Both models fit the data well; their utilities will depend on the way in which physical health is conceptualized and on the nature of the research question at hand.",
#   "authors": [
#     "Whitelaw NA",
#     "Liang J"
#   ],
#   "authors_str": "Whitelaw NA; Liang J",
#   "citation": "Whitelaw NA and Liang J. The structure of the OARS physical health measures. The structure of the OARS physical health measures. 1991; 29:332-47. doi: 10.1097/00005650-199104000-00003",
#   "doi": "10.1097/00005650-199104000-00003",
#   "history": {
#     "entrez": "Mon, 01 Apr 1991 00:00:00 GMT",
#     "medline": "Mon, 01 Apr 1991 00:00:00 GMT",
#     "pubmed": "Mon, 01 Apr 1991 00:00:00 GMT"
#   },
#   "pmid": "2020202",
#   "title": "The structure of the OARS physical health measures.",
#   "url": "https://ncbi.nlm.nih.gov/pubmed/2020202",
#   "year": "1991"
# }
