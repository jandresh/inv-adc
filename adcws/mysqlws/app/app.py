from flask import Flask, jsonify, request
import mysql.connector
import requests
import time
import re

app = Flask(__name__)

config = {
    'user': 'adccali',
    'password': 'adccali',
    'host': 'db',
    'port': '3306',
    'database': 'adccali'
}

# Initial database creation
# def database_init():
#     try:
#         connection = mysql.connector.connect(
#             host='db',
#             user='root',
#             password='root',
#             port='3306'
#         )
#         cursor = connection.cursor()
#         cursor.execute('create database adccali CHARACTER SET utf8 COLLATE utf8_general_ci')
#         connection.commit()
#         cursor.close()
#         connection.close()
#         print('adc database created')
#         return True
#     except:
#         print('adc database exist')
#         return False


def post_json_request(url, obj):
    return requests.post(url, json=obj).json()


def execute_mysql_query(query, connection):
    # connection = mysql.connector.connect(**config)
    # connection.set_charset_collation('utf8')
    cursor = connection.cursor()
    cursor.execute(query)
    try:
        columns = cursor.description
        results = [{columns[index][0]:column for index,
                    column in enumerate(value)} for value in cursor.fetchall()]
    except:
        results = None
    # results=cursor.fetchall()
    cursor.close()
    # connection.close()
    return results


def execute_mysql_query2(query, connection):
    try:
        # connection = mysql.connector.connect(**config)
        # connection.set_charset_collation('utf8')
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        columns = cursor.description
        results = [{columns[index][0]:column for index,
                    column in enumerate(value)} for value in cursor.fetchall()]
        # results=cursor.fetchall()
        cursor.close()
        # connection.close()
    except:
        results = None
    return results


def txt2text(path):
    with open(path, mode="r", encoding="utf-8") as f:
        text_str = f.read()
        f.close()
    return text_str


def str2eq(pattern, sentences_str):
    pattern = re.compile(pattern)
    match = ''
    sentences = []
    while match != None:
        match = pattern.search(sentences_str)
        if(match != None):
            sentences.append(sentences_str[:match.start()].split())
            # print(string[:match.start()])
            sentences_str = sentences_str[match.end():]
    return sentences


@app.route('/init', methods=['GET'])
def init():
    connection = mysql.connector.connect(**config)
    # Init tables
    # database_init()
    try:
        execute_mysql_query2(
            """CREATE TABLE patterns (
                    id INT(10) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                    pattern TEXT NOT NULL,
                    db TEXT NOT NULL,
                    description TEXT
                )""", connection)
        execute_mysql_query2(
                """CREATE TABLE searches (
                    patid INT(10) NOT NULL,
                    docid INT(10) NOT NULL,
                    title TEXT,
                    abs TEXT,
                    ftext TEXT,
                    PRIMARY KEY (patid,docid)
                )""", connection)
        # execute_mysql_query2(
        #     """CREATE TABLE searches (
        #             patternid INT(10) NOT NULL,
        #             docid INT(10) NOT NULL,
        #             title TEXT,
        #             abstract TEXT
        #             PRIMARY KEY (patternid, docid)
        #         )""", connection)
        # execute_mysql_query2(
        #     """INSERT INTO
        #             patterns (pattern, db, description)
        #         VALUES
        #             ('Carcinoma[Title/Abstract] AND lobulillar[Title/Abstract] AND mama[Title/Abstract]',
        #              'PUBMED','Principales'),
        #             ('abstract:((carcinoma AND lobulillar AND mama))',
        #              'CORE','Principales'),
        #             ('Carcinoma[Title/Abstract] AND escamoso[Title/Abstract] AND pulmón[Title/Abstract]',
        #              'PUBMED','Principales'),
        #             ('abstract:((Carcinoma AND escamoso AND pulmón))',
        #              'CORE','Principales'),
        #             ('Carcinoma[Title/Abstract] AND ductal[Title/Abstract] AND infiltrante[Title/Abstract] AND mama[Title/Abstract]','PUBMED','Principales'),
        #             ('abstract:((Carcinoma AND ductal AND infiltrante AND mama))',
        #              'CORE','Principales'),
        #             ('Mastectomía[Title/Abstract] AND radical[Title/Abstract] AND modificada[Title/Abstract]',
        #              'PUBMED','Principales'),
        #             ('abstract:((Mastectomía AND radical AND modificada))',
        #              'CORE','Principales'),
        #             ('Cáncer[Title/Abstract] AND pulmón[Title/Abstract] AND carboplatino[Title/Abstract]',
        #              'PUBMED','Principales'),
        #             ('abstract:((Cáncer AND pulmón AND carboplatino))',
        #              'CORE','Principales'),
        #             ('Carcinoma[Title/Abstract] AND pulmón[Title/Abstract] AND quimioterapia[Title/Abstract]',
        #              'PUBMED','Principales'),
        #             ('abstract:((Carcinoma AND pulmón AND quimioterapia))',
        #              'CORE','Principales');
        #     """, connection)
    except:
        print('Error on tables creation')
    results = execute_mysql_query('SELECT * FROM patterns', connection)
    connection.close()
    return jsonify(results)

# *****patten_insert()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "pattern": "Cancer de piel", "db": "PUBMED", "description": "Cancer muy comun"}' http://localhost:5001/pattern2mysql


@app.route("/pattern2mysql", methods=['POST'])
def pattern_insert():
    if not request.json:
        abort(400)
    connection = mysql.connector.connect(**config)
    pattern = request.json['pattern']
    db = request.json['db']
    description = request.json['description']
    try:
        query = 'INSERT INTO patterns (pattern, db, description) VALUES ("%s", "%s", "%s");' % (
            pattern, db, description)
        execute_mysql_query2(query, connection)
        result = execute_mysql_query('SELECT * FROM patterns', connection)
    except:
        result = "Pattern can't be inserted"
    connection.close()
    return jsonify(result=result)

# *****search_insert()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "patternid": "1", "docid": "CORE", "title": "Test title", "abstract": "Abstract: This is a test", "fulltext": "Tele, abstract, body"}' http://localhost:5001/search2mysql


@app.route("/search2mysql", methods=['POST'])
def search_insert():
    if not request.json:
        abort(400)
    connection = mysql.connector.connect(**config)
    # id_pattern INT(10) NOT NULL,
    #                 id INT(10) NOT NULL,
    #                 title TEXT,
    #                 abstract TEXT,
    #                 fulltext TEXT,
    patternid = request.json['patternid']
    docid = request.json['docid']
    title = request.json['title']
    abstract = request.json['abstract']
    fulltext = request.json['fulltext']
    try:
        query = '''INSERT INTO searches (
            patid,
            docid,
            title,
            abs, 
            ftext
            ) 
            VALUES ("%s", "%s", "%s", "%s", "%s") 
            ON DUPLICATE KEY UPDATE 
            title="%s", 
            abs="%s", 
            ftext="%s"
            ;'''%(
            patternid,
            docid, 
            title.replace('"', '').replace('\n', ''), 
            abstract.replace('"', '').replace('\n', ''), 
            fulltext.replace('"', '').replace('\n', ''),
            title.replace('"', '').replace('\n', ''), 
            abstract.replace('"', '').replace('\n', ''), 
            fulltext.replace('"', '').replace('\n', ''))
        execute_mysql_query2(query, connection)
        result = 0
    except:
        result = 1
    connection.close()
    return jsonify(result=result)

@app.route("/txt2insert", methods=['GET'])
def txt_insert():
    connection = mysql.connector.connect(**config)
    patterns_text = txt2text('patterns.txt')
    search_queries = str2eq(r'\n', patterns_text)
    error_count = 0
    for query_words in search_queries:
        pattern = 'abstract:('
        for i in range(len(query_words)):
            if(i == len(query_words)-1):
                pattern += '%s)' % (query_words[i])
            else:
                pattern += '%s AND ' % (query_words[i])
        try:
            query = 'INSERT INTO patterns (pattern, db, description) VALUES ("%s", "%s", "%s");' % (
                pattern, 'CORE', 'Corpus 1')
            execute_mysql_query2(query, connection)
        except:
            error_count += 1
    if(i == 0):
        result = execute_mysql_query('SELECT * FROM patterns', connection)
    else:
        result = "%i Patterns can't be inserted" % (error_count)
    connection.close()
    return jsonify(result=result)


@app.route('/patterns', methods=['GET'])
def patterns():
    connection = mysql.connector.connect(**config)
    results = execute_mysql_query('SELECT * FROM patterns', connection)
    connection.close()
    return jsonify(results)


@app.route('/searches', methods=['GET'])
def searches():
    connection = mysql.connector.connect(**config)
    results = execute_mysql_query('SELECT * FROM searches', connection)
    connection.close()
    return jsonify(results)


@app.route('/pipeline1', methods=['GET'])
def pipeline1():
    connection = mysql.connector.connect(**config)
    # Para cada patron sacar 1000 pmid o coreid
    # para cada pmid o coreid recuperar metadatos
    # llenar la base de datos
    results = execute_mysql_query('SELECT * FROM patterns', connection)
    for pattern in results:
        get_metadata = True
        if (pattern['db'] == 'PUBMED'):
            try:
                pmids_json = post_json_request(
                    'http://metapubws:5000/pmids', {"query": pattern['pattern']})
            except:
                get_metadata = False
            if get_metadata:
                pmids = pmids_json['pmids']
                doc_id_counter = 0
                insert_counter = 0
                for doc_id in pmids:
                    print("id_pattern:%s" % pattern['id'])
                    print("pattern:%s" % pattern['pattern'])
                    print("doc_id:%s" % doc_id)
                    doc_id_counter += 1
                    print("doc_id_counter:%s" % doc_id_counter)
                    success = 0
                    if doc_id is not None:
                        insert_mysql = True
                        try:
                            metadata_json = post_json_request(
                                'http://metapubws:5000/metadata', {"id": doc_id})
                        except:
                            insert_mysql = False
                        print("title:%s" % metadata_json['title'])
                        print("abstract:%s" % metadata_json['abstract'])
                        # time.sleep(0.3)
                        if(metadata_json['abstract'] == None):
                            insert_abstract = ""
                        else:
                            insert_abstract = metadata_json['abstract']
                        if(metadata_json['title'] == None):
                            insert_title = ""
                        else:
                            insert_title = metadata_json['title']
                        if insert_mysql:
                            try:
                                query = 'INSERT INTO searches (patid, docid, title, abs, ftext) VALUES (%s,%s,"%s","%s","%s") ON DUPLICATE KEY UPDATE title="%s", abs="%s", ftext="%s";' % (pattern['id'], doc_id, insert_title.replace(
                                    '"', '').replace('\n', ''), insert_abstract.replace('"', '').replace('\n', ''), '', insert_title.replace('"', '').replace('\n', ''), insert_abstract.replace('"', '').replace('\n', ''), '')
                                results = execute_mysql_query2(
                                    query, connection)
                                success = 1
                            except:
                                query = "Mysql not executed"
                                success = 0
                    insert_counter += success
                    print("insert_counter:%s" % insert_counter)
        elif (pattern['db'] == 'CORE'):
            try:
                search_json = post_json_request(
                    'http://corews:5000/core', {"query": pattern['pattern']})
            except:
                get_metadata = False
                print('Not Success')
            if get_metadata and metadata_json != None :
                insert_counter = 0
                for metadata_json in search_json:
                    print('title : ', metadata_json['title'])
                    print('Abstract :', metadata_json['abstract'])
                    # time.sleep(0.3)
                    doc_id = metadata_json['id']
                    if(metadata_json['abstract'] == None):
                        insert_abstract = ""
                    else:
                        insert_abstract = metadata_json['abstract']
                    if(metadata_json['title'] == None):
                        insert_title = ""
                    else:
                        insert_title = metadata_json['title']
                    if(metadata_json['fullText'] == None):
                        insert_fulltext = ""
                    else:
                        insert_fulltext = metadata_json['fullText']
                    try:
                        query = 'INSERT INTO searches (patid, docid, title, abs, ftext) VALUES (%s,%s,"%s","%s","%s") ON DUPLICATE KEY UPDATE title="%s", abs="%s", ftext="%s";' % (pattern['id'], doc_id, insert_title.replace(
                            '"', '').replace('\n', ''), insert_abstract.replace('"', '').replace('\n', ''), insert_fulltext.replace('"', '').replace('\n', ''), insert_title.replace('"', '').replace('\n', ''), insert_abstract.replace('"', '').replace('\n', ''), insert_fulltext.replace('"', '').replace('\n', ''))
                        results = execute_mysql_query2(query, connection)
                        success = 1
                    except:
                        query = "Mysql not executed"
                        success = 0
                    insert_counter += success
                print("insert_counter:%s" % insert_counter)

    results = execute_mysql_query(
        'SELECT id_pattern, id, title, abstract FROM searches', connection)
    connection.close()
    return jsonify(results)


@app.route('/pipeline2', methods=['GET'])
def pipeline2():
    connection = mysql.connector.connect(**config)
    # Para cada patron sacar 1000 pmid o coreid
    # para cada pmid o coreid recuperar metadatos
    # llenar la base de datos
    results = execute_mysql_query('SELECT * FROM patterns', connection)
    for pattern in results:
        get_metadata = True
        if (pattern['db'] == 'PUBMED'):
            try:
                pmids_json = post_json_request(
                    'http://metapubws:5000/pmids', {"query": pattern['pattern']})
            except:
                get_metadata = False
            if get_metadata:
                pmids = pmids_json['pmids']
                doc_id_counter = 0
                insert_counter = 0
                for doc_id in pmids:
                    print("id_pattern:%s" % pattern['id'])
                    print("pattern:%s" % pattern['pattern'])
                    print("doc_id:%s" % doc_id)
                    doc_id_counter += 1
                    print("doc_id_counter:%s" % doc_id_counter)
                    success = 0
                    if doc_id is not None:
                        insert_mysql = True
                        try:
                            metadata_json = post_json_request(
                                'http://metapubws:5000/metadata', {"id": doc_id})
                        except:
                            insert_mysql = False
                        print("title:%s" % metadata_json['title'])
                        print("abstract:%s" % metadata_json['abstract'])
                        # time.sleep(0.3)
                        if(metadata_json['abstract'] == None):
                            insert_abstract = ""
                        else:
                            insert_abstract = metadata_json['abstract']
                        if(metadata_json['title'] == None):
                            insert_title = ""
                        else:
                            insert_title = metadata_json['title']
                        if insert_mysql:
                            try:
                                query = 'INSERT INTO searches (patid, docid, title, abs, ftext) VALUES (%s,%s,"%s","%s","%s") ON DUPLICATE KEY UPDATE title="%s", abs="%s", ftext="%s";' % (pattern['id'], doc_id, insert_title.replace(
                                    '"', '').replace('\n', ''), insert_abstract.replace('"', '').replace('\n', ''), '', insert_title.replace('"', '').replace('\n', ''), insert_abstract.replace('"', '').replace('\n', ''), '')
                                results = execute_mysql_query2(
                                    query, connection)
                                success = 1
                            except:
                                query = "Mysql not executed"
                                success = 0
                    insert_counter += success
                    print("insert_counter:%s" % insert_counter)
        elif (pattern['db'] == 'CORE'):
            try:
                search_json = post_json_request(
                    'http://corews:5000/core2', {"query": pattern['pattern'], "idpattern": pattern['id']})
            except:
                get_metadata = False
                print('Not Success')
            if get_metadata:
                print("CORE insert success:%s" % pattern['pattern'])
                print('Spanish results: ', search_json['result'])
            else:
                print("CORE insert not success:%s" % pattern['pattern'])

    results = execute_mysql_query(
        'SELECT patid, docid, title FROM searches order by patid desc', connection)
    connection.close()
    return jsonify(results)
# Eliminar volumenes en docker
# sudo docker volume rm mysqlws_my-db
# sudo docker volume ls
