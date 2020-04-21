from flask import Flask, request, make_response, jsonify
from pathlib import Path
from cap.store.textobjectfiles import TextObjectFile, TextObjectFileGroup
from cap.store.textobjects import TextObject, RegexTextObject, Line
from cap.lists.lists import main_list_set as lists
from cap import plugins
from functools import wraps

app = Flask(__name__)
BAD_REQUEST = 400

def tryexceptbadrequest(operation):
    @wraps(operation)
    def trying(*args, **kwargs):
        try:
            return operation(*args, **kwargs)
        except Exception as exception:
                return(str(exception.args), BAD_REQUEST)
    return trying

@app.route('/create/<textobjtype>/<list_name>', methods=['POST'])
@tryexceptbadrequest
def create(textobjtype, list_name):
    lists.add(list_name, textobjtype)
    return f'added list {list_name} of type {textobjtype}'

@app.route('/delete/<list_name>', methods=['POST'])
@tryexceptbadrequest
def delete(list_name):
    del lists[list_name]
    return f"{list_name} was deleted"

@app.route('/add/<list_name>', methods = ['POST'])
@tryexceptbadrequest
def addto(list_name):
    items = request.get_json()['items']
    lists[list_name].add(*items)
    return f"{items} were added to {list_name}"

@app.route('/remove/<list_name>', methods=['POST'])
@tryexceptbadrequest
def removefrom(list_name):
    items = request.get_json()['items']
    lists[list_name].remove(*items)
    return f"{items} were removed from {list_name}"

@app.route('/replace/<list_name>', methods=['POST'])
@tryexceptbadrequest
def replace_in(list_name):
    items = request.get_json()
    for item, repl in items.items():
        lists[list_name].replace(item, repl)

def start():
    app.run()

