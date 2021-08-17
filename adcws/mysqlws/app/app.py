from typing import List, Dict
from flask import Flask
import mysql.connector
import json

app = Flask(__name__)


def patterns() -> List[Dict]:
    config = {
        'user': 'root',
        'password': 'root',
        'host': 'db',
        'port': '3306',
        'database': 'test'
    }
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute('SELECT pattern, description FROM pattern')
    results = [{pattern: description} for (pattern, description) in cursor]
    cursor.close()
    connection.close()

    return results


@app.route('/')
def index() -> str:
    return json.dumps({'patterns': patterns()})


if __name__ == '__main__':
    app.run(host='0.0.0.0')
