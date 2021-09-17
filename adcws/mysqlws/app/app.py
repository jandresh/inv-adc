from flask import Flask, jsonify, request
import mysql.connector
import requests
import time

app = Flask(__name__)

config = {
        'user': 'adccali',
        'password': 'adccali',
        'host': 'db',
        'port': '3306',
        'database': 'adccali'
    }

#Initial database creation
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
    return requests.post(url, json = obj).json()

def execute_mysql_query(query, connection):
    # connection = mysql.connector.connect(**config)
    # connection.set_charset_collation('utf8')
    cursor = connection.cursor()
    cursor.execute(query)
    try:
        columns = cursor.description 
        results = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
    except:
        results = None
    #results=cursor.fetchall()
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
        results = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
        #results=cursor.fetchall()
        cursor.close()
        # connection.close()
    except:
        results = None
    return results
   
@app.route('/init',methods=['GET'])
def init():
    connection = mysql.connector.connect(**config)
    # Init tables
    # database_init()
    try:
        execute_mysql_query2(
                """CREATE TABLE patterns (
                    id INT(10) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                    pattern TEXT NOT NULL,
                    description TEXT NOT NULL
                )""", connection)
        execute_mysql_query2(
                """CREATE TABLE searches (
                    id_pattern INT(10) NOT NULL,
                    pmid INT(10) NOT NULL,
                    title TEXT NOT NULL,
                    abstract TEXT NOT NULL,
                    PRIMARY KEY (id_pattern,pmid)
                )""", connection)
        execute_mysql_query2(
            """INSERT INTO 
                    patterns (pattern, description)
                VALUES 
                    ('Cancer de mama','Principales'),
                    ('Breast cancer','Main'),
                    ('Cancer de cervix','Principales'),
                    ('Cervical Cancer','Main'),
                    ('Cancer de prostata','Principales'),
                    ('Prostate cancer','Main'),
                    ('Cancer de pulmon','Principales'),
                    ('Lung cancer','Main');
            """, connection)
    except:
        print('Error on tables creation')
    results=execute_mysql_query('SELECT * FROM patterns', connection)
    connection.close()
    return jsonify(results)

@app.route('/patterns',methods=['GET'])
def patterns():
    connection = mysql.connector.connect(**config)
    results=execute_mysql_query('SELECT * FROM patterns', connection)
    connection.close()
    return jsonify(results)
    
@app.route('/searches',methods=['GET'])
def searches():
    connection = mysql.connector.connect(**config)
    results=execute_mysql_query('SELECT * FROM searches', connection)
    connection.close()
    return jsonify(results)
    
@app.route('/execute',methods=['GET'])
def execute():
    connection = mysql.connector.connect(**config)
    # Para cada patron sacar 1000 pmid
    # para cada pmid recuperar metadatos
    # llenar la base de datos
    results=execute_mysql_query('SELECT * FROM patterns', connection)
    for pattern in results:
        # {'id': 1, 'pattern': 'Cancer de mama', 'description': 'Principales'}
        try:
            pmids_json=post_json_request('http://metapubws:5000/pmids',{"query": pattern['pattern']})
        except:#Pendiente manejo excepciones
            pmids_json=None
        pmids=pmids_json['pmids']
        for pmid in pmids:
            print(pattern['id'])
            print(pattern['pattern'])
            print(pmid)
            if pmid is not None:
                try:
                    metadata_json=post_json_request('http://metapubws:5000/metadata',{"id": pmid})
                except:#Pendiente manejo excepciones
                    metadata_json=None
                #print(metadata_json['title'])
                #print(metadata_json['abstract'])
                # time.sleep(0.3)
                #query='INSERT INTO searches (id_pattern, pmid, title, abstract) VALUES (%s,%s,"%s","%s") ON DUPLICATE KEY UPDATE title="%s", abstract="%s";'%(pattern['id'],pmid,metadata_json['title'],metadata_json['abstract'],metadata_json['title'],metadata_json['abstract'])
                try:
                    query='INSERT INTO searches (id_pattern, pmid, title, abstract) VALUES (%s,%s,"%s","%s") ON DUPLICATE KEY UPDATE title="%s", abstract="%s";'%(pattern['id'],pmid,metadata_json['title'].replace('"',''),metadata_json['abstract'].replace('"',''),metadata_json['title'].replace('"',''),metadata_json['abstract'].replace('"',''))
                    results=execute_mysql_query2(query, connection)
                except:#Pendiente manejo excepciones
                    query="Mysql not executed"                
    results=execute_mysql_query('SELECT id_pattern, title, abstract FROM searches',connection)
    connection.close()
    return jsonify(results)
    
