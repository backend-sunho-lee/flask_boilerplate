from flask import Blueprint
import app.module01.controllers as ctrl

module01 = Blueprint('module01', __name__)
module01.add_url_rule('/', view_func=ctrl.index, methods=['GET'])
