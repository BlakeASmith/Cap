from flask import Flask, request
import plugins
from builtin import *
import hooks

app = Flask(__name__)


plugs = {t.__name__:t() for t in plugins.Plugin.__subclasses__()}

text_object_types = {p.TextObjectType.__name__:p.TextObjectType
        for p in plugs.values()}

print(text_object_types)

@app.route('/add/<list_name>/<obj_type>', methods=['POST'])
def add(list_name, obj_type):
    try:
        assert(task_type in text_object_types)

        task = text_object_types[task_type](**request.get_json())
        return task.__dict__
    except Exception:
        return "Invalid Task Type"



