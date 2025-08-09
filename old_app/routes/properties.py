from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint('properties', __name__, url_prefix='/properties')

@bp.route('/')
@login_required
def list():
    return render_template('properties/list.html')

@bp.route('/<int:id>')
@login_required
def detail(id):
    return render_template('properties/detail.html', property_id=id)