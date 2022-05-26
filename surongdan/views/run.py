import datetime
import pickle
from flask import current_app
from flask import request, jsonify, Blueprint, session
from sqlalchemy import and_

from surongdan.models import project_table, layer_table
from surongdan.precode import *
from surongdan.gencode import *


run_bp = Blueprint('run', __name__)

@run_bp.route('/test_gen_code', methods={'GET'})
def test_gen_code():
    if gen_code(3):
        return jsonify({'msg':'ok'}), 201
    else:
        return jsonify({'fault':'false'}), 500
