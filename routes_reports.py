# AIVIIZN Reports Routes
# Quick build version - basic Flask routes

from flask import Blueprint, render_template, request, jsonify, flash
from datetime import datetime
import json

# Create reports blueprint
reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

# Sample data (in production, this would come from Supabase)
SAMPLE_REPORTS = [
    {
        "id": 1,
        "name": "Monthly Rent Roll",
        "type": "financial",
        "created_at": "2025-08-20",
        "status": "active"
    },
    {
        "id": 2,
        "name": "Vacancy Report",
        "type": "occupancy", 
        "created_at": "2025-08-20",
        "status": "active"
    },
    {
        "id": 3,
        "name": "Delinquency Report",
        "type": "financial",
        "created_at": "2025-08-19",
        "status": "active"
    }
]

@reports_bp.route('/')
def reports_dashboard():
    """Main reports dashboard"""
    return render_template('reports/reports.html', 
                         reports=SAMPLE_REPORTS,
                         page_title="Reports Dashboard")

@reports_bp.route('/rent-roll')
def rent_roll():
    """Rent roll report"""
    return render_template('reports/rent_roll.html',
                         page_title="Rent Roll Report")

@reports_bp.route('/vacancy')
def vacancy():
    """Vacancy report"""
    return render_template('vacancies/vacancies.html',
                         page_title="Vacancy Report")

@reports_bp.route('/delinquency')
def delinquency():
    """Delinquency report"""
    return render_template('reports/delinquency_report.html',
                         page_title="Delinquency Report")

@reports_bp.route('/financial')
def financial():
    """Financial reports"""
    return render_template('reports/income_statement.html',
                         page_title="Financial Reports")

@reports_bp.route('/generate', methods=['POST'])
def generate_report():
    """Generate a report"""
    report_type = request.json.get('type', 'unknown')
    
    # Simulate report generation
    result = {
        "success": True,
        "message": f"AIVIIZN {report_type} report generated successfully",
        "report_id": len(SAMPLE_REPORTS) + 1,
        "generated_at": datetime.now().isoformat()
    }
    
    return jsonify(result)

@reports_bp.route('/api/reports')
def api_reports():
    """API endpoint for reports data"""
    return jsonify({
        "reports": SAMPLE_REPORTS,
        "total": len(SAMPLE_REPORTS),
        "generated_at": datetime.now().isoformat()
    })

# To integrate with main Flask app, add this to your main app.py:
# from routes_reports import reports_bp
# app.register_blueprint(reports_bp)
