# calendar_api.py - Calendar API endpoints for AIVIIZN
# This file contains all the API endpoints needed for calendar functionality

from flask import Blueprint, request, jsonify, session
from datetime import datetime, timedelta
from supabase import create_client, Client
import os
from functools import wraps

# Create a blueprint for calendar APIs
calendar_api = Blueprint('calendar_api', __name__)

# Supabase Configuration
SUPABASE_URL = os.environ.get('SUPABASE_URL', "https://sejebqdhcilwcpjpznep.supabase.co")
SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY', "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNlamVicWRoY2lsd2NwanB6bmVwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTg5NjQsImV4cCI6MjA3MDAzNDk2NH0.vFM0Gr3QZF4MN3vtDGghjyCpnIkyC_mmUOOkVO3ahPQ")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Get all calendar events
@calendar_api.route('/api/calendar/events', methods=['GET'])
@login_required
def get_events():
    """Get calendar events within a date range"""
    try:
        start = request.args.get('start')
        end = request.args.get('end')
        event_type = request.args.get('type', 'all')
        
        # For now, return mock data
        # In production, query from Supabase
        events = get_mock_events(start, end, event_type)
        
        return jsonify(events), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Create a new calendar event
@calendar_api.route('/api/calendar/events', methods=['POST'])
@login_required
def create_event():
    """Create a new calendar event"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['title', 'start_datetime', 'end_datetime', 'event_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Add company ID from session
        data['company_id'] = session.get('company', 'demo-company')
        data['created_by'] = session.get('user_id')
        data['created_at'] = datetime.now().isoformat()
        
        # In production, insert into Supabase
        # response = supabase.table('calendar_events').insert(data).execute()
        
        # Mock response for now
        event = {
            'id': 'event-' + datetime.now().strftime('%Y%m%d%H%M%S'),
            **data
        }
        
        return jsonify(event), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Update an existing calendar event
@calendar_api.route('/api/calendar/events/<event_id>', methods=['PUT'])
@login_required
def update_event(event_id):
    """Update an existing calendar event"""
    try:
        data = request.json
        
        # Add updated metadata
        data['updated_by'] = session.get('user_id')
        data['updated_at'] = datetime.now().isoformat()
        
        # In production, update in Supabase
        # response = supabase.table('calendar_events').update(data).eq('id', event_id).execute()
        
        # Mock response
        event = {
            'id': event_id,
            **data
        }
        
        return jsonify(event), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Delete a calendar event
@calendar_api.route('/api/calendar/events/<event_id>', methods=['DELETE'])
@login_required
def delete_event(event_id):
    """Delete a calendar event"""
    try:
        # In production, delete from Supabase
        # response = supabase.table('calendar_events').delete().eq('id', event_id).execute()
        
        return jsonify({'message': 'Event deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Check for scheduling conflicts
@calendar_api.route('/api/calendar/conflicts', methods=['POST'])
@login_required
def check_conflicts():
    """Check for scheduling conflicts"""
    try:
        data = request.json
        start = data.get('start_datetime')
        end = data.get('end_datetime')
        unit_id = data.get('unit_id')
        exclude_event_id = data.get('exclude_event_id')
        
        # In production, query Supabase for conflicts
        # For now, return no conflicts
        conflicts = []
        
        return jsonify({
            'has_conflicts': len(conflicts) > 0,
            'conflicts': conflicts
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get event statistics
@calendar_api.route('/api/calendar/stats', methods=['GET'])
@login_required
def get_event_stats():
    """Get calendar event statistics"""
    try:
        # Calculate stats for the current month
        today = datetime.now()
        start_of_month = datetime(today.year, today.month, 1)
        end_of_month = start_of_month + timedelta(days=32)
        end_of_month = datetime(end_of_month.year, end_of_month.month, 1) - timedelta(days=1)
        
        stats = {
            'total_events': 156,
            'move_ins': 12,
            'move_outs': 8,
            'showings': 45,
            'maintenance': 38,
            'inspections': 25,
            'appointments': 28,
            'upcoming_today': 7,
            'upcoming_week': 42
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get recurring event templates
@calendar_api.route('/api/calendar/recurring-templates', methods=['GET'])
@login_required
def get_recurring_templates():
    """Get recurring event templates"""
    try:
        templates = [
            {
                'id': 'template-1',
                'title': 'Monthly Inspection',
                'event_type': 'inspection',
                'recurrence_pattern': 'monthly',
                'description': 'Monthly property inspection'
            },
            {
                'id': 'template-2',
                'title': 'Weekly Maintenance',
                'event_type': 'maintenance',
                'recurrence_pattern': 'weekly',
                'description': 'Weekly maintenance check'
            },
            {
                'id': 'template-3',
                'title': 'Quarterly Review',
                'event_type': 'appointment',
                'recurrence_pattern': 'quarterly',
                'description': 'Quarterly property review with owner'
            }
        ]
        
        return jsonify(templates), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Export calendar events
@calendar_api.route('/api/calendar/export', methods=['GET'])
@login_required
def export_events():
    """Export calendar events in iCal format"""
    try:
        start = request.args.get('start')
        end = request.args.get('end')
        format_type = request.args.get('format', 'ical')
        
        # In production, generate actual iCal file
        # For now, return a simple response
        
        if format_type == 'ical':
            ical_content = generate_ical_content(start, end)
            return ical_content, 200, {
                'Content-Type': 'text/calendar',
                'Content-Disposition': 'attachment; filename="calendar_events.ics"'
            }
        else:
            return jsonify({'error': 'Unsupported format'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Helper functions

def get_mock_events(start, end, event_type):
    """Generate mock calendar events"""
    events = []
    
    # Sample event data based on your screenshots
    base_events = [
        {
            'title': 'Move In: Unit 3745',
            'event_type': 'move_in',
            'property_name': 'Rock Ridge Ranch',
            'unit_number': '3745',
            'tenant_name': 'John Smith',
            'time': '11:00'
        },
        {
            'title': 'Showing: Unit 4407',
            'event_type': 'showing',
            'property_name': 'Sunset Apartments',
            'unit_number': '4407',
            'tenant_name': 'Jane Doe',
            'time': '12:30'
        },
        {
            'title': 'Showing: Unit 10549',
            'event_type': 'showing',
            'property_name': 'Downtown Properties',
            'unit_number': '10549',
            'tenant_name': 'Mike Johnson',
            'time': '13:00'
        },
        {
            'title': 'Showing: Unit 3934',
            'event_type': 'showing',
            'property_name': 'Riverside Complex',
            'unit_number': '3934',
            'tenant_name': 'Sarah Williams',
            'time': '15:00'
        },
        {
            'title': 'Showing: Unit 3043',
            'event_type': 'showing',
            'property_name': 'Park View Apartments',
            'unit_number': '3043',
            'tenant_name': 'Robert Brown',
            'time': '16:15'
        },
        {
            'title': 'Showing: Unit 4853',
            'event_type': 'showing',
            'property_name': 'Garden Heights',
            'unit_number': '4853',
            'tenant_name': 'Emily Davis',
            'time': '16:45'
        },
        {
            'title': 'Showing: Unit 3902',
            'event_type': 'showing',
            'property_name': 'Lakeview Estates',
            'unit_number': '3902',
            'tenant_name': 'Chris Wilson',
            'time': '16:45'
        },
        {
            'title': 'Move In: Valentine Ap...',
            'event_type': 'move_in',
            'property_name': 'Valentine Apartments',
            'unit_number': '201',
            'tenant_name': 'Alex Martinez',
            'time': '08:00'
        },
        {
            'title': 'Move In: Homestead V...',
            'event_type': 'move_in',
            'property_name': 'Homestead Villas',
            'unit_number': '105',
            'tenant_name': 'Lisa Anderson',
            'time': '08:00'
        },
        {
            'title': 'Collect Applic...',
            'event_type': 'appointment',
            'property_name': 'Various',
            'unit_number': '',
            'tenant_name': '',
            'time': '09:00'
        },
        {
            'title': 'Double check...',
            'event_type': 'maintenance',
            'property_name': 'Building B',
            'unit_number': '',
            'tenant_name': '',
            'time': '10:00'
        }
    ]
    
    # Generate events for the requested date range
    current_date = datetime.fromisoformat(start) if start else datetime.now()
    end_date = datetime.fromisoformat(end) if end else current_date + timedelta(days=7)
    
    event_id = 1
    while current_date <= end_date:
        for base_event in base_events:
            if event_type == 'all' or base_event['event_type'] == event_type:
                # Parse time
                hour, minute = map(int, base_event['time'].split(':'))
                event_datetime = current_date.replace(hour=hour, minute=minute)
                
                event = {
                    'id': f'event-{event_id}',
                    'title': base_event['title'],
                    'start': event_datetime.isoformat(),
                    'end': (event_datetime + timedelta(hours=1)).isoformat(),
                    'extendedProps': {
                        'event_type': base_event['event_type'],
                        'property_name': base_event['property_name'],
                        'unit_number': base_event['unit_number'],
                        'tenant_name': base_event['tenant_name'],
                        'status': 'scheduled'
                    }
                }
                events.append(event)
                event_id += 1
        
        current_date += timedelta(days=1)
    
    return events

def generate_ical_content(start, end):
    """Generate iCal format content"""
    ical = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//AIVIIZN//Property Management System//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
X-WR-CALNAME:AIVIIZN Calendar
X-WR-TIMEZONE:America/Chicago
"""
    
    events = get_mock_events(start, end, 'all')
    
    for event in events:
        start_dt = datetime.fromisoformat(event['start'])
        end_dt = datetime.fromisoformat(event['end'])
        
        ical += f"""
BEGIN:VEVENT
UID:{event['id']}@aiviizn.com
DTSTART:{start_dt.strftime('%Y%m%dT%H%M%S')}
DTEND:{end_dt.strftime('%Y%m%dT%H%M%S')}
SUMMARY:{event['title']}
DESCRIPTION:Property: {event['extendedProps']['property_name']}\\nUnit: {event['extendedProps']['unit_number']}\\nTenant: {event['extendedProps']['tenant_name']}
STATUS:CONFIRMED
END:VEVENT"""
    
    ical += "\nEND:VCALENDAR"
    
    return ical
