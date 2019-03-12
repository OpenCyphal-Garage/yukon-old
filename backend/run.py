from flask import Flask, render_template, jsonify
from random import *
import requests

app = Flask(__name__,
            static_folder = "../frontend/dist/static",
            template_folder = "../frontend/dist")

@app.route('/api/v1/nodes')
def random_number():
    response = {
        'nodes': ['node0', 'node1', 'node2']
    }
    return jsonify(response)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if app.debug:
        return requests.get('http://localhost:8080/{}'.format(path)).text
    return render_template("index.html")