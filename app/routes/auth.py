from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login')
def login():
    return render_template('auth/login.html')

@bp.route('/register')
def register():
    return render_template('auth/register.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))