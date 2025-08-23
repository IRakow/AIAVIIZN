# Test route for calculation capture
from flask import Blueprint, render_template

calculation_test_bp = Blueprint('calculation_test', __name__)

@calculation_test_bp.route('/calculation-test')
def calculation_test():
    """Test page showing working AppFolio calculations"""
    return render_template('calculation_test.html')

# Add this to your main app.py:
"""
from calculation_test_route import calculation_test_bp
app.register_blueprint(calculation_test_bp)
"""
