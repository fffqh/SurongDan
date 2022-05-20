import datetime
import pickle
from flask import current_app
from flask import request, jsonify, Blueprint, session
from sqlalchemy import and_

from surongdan.models import project_table, layer_table
from surongdan.precode import *

run_bp = Blueprint('run', __name__)

import_package = "import time \
import numpy as np \
from torchvision import transforms \
from torchvision.datasets import mnist \
from torch.utils.data import DataLoader \
import matplotlib.pyplot as plt \
import torch.nn as nn"




