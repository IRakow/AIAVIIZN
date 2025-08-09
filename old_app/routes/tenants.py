from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint('tenants', __name__, url_prefix='/tenants')

@bp.route('/')
@login_required
def list():
    return render_template('tenants/list.html')

@bp.route('/<int:id>')
@login_required
def detail(id):
    return render_template('tenants/detail.html', tenant_id=id)