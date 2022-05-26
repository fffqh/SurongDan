from flask import request, jsonify, session, make_response, Blueprint
from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound


vue_bp = Blueprint('vue', 'vue',  template_folder='templates')

@vue_bp.route('/')
def get_vue():
    print('test')
    return render_template('index.html')
    