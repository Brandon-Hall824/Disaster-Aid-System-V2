"""
Flask web application for the Aid Dispatch System.
Provides a user-friendly web interface for disaster reporting, aid requests,
and mental health support.
"""

import os
import sys
import json
import subprocess
import importlib
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime, timedelta

sys.path.append('src')
from storage import Storage
from trucks import Truck
from help_stations import HelpStation
from report_utils import geocode

# Import mental health AI
try:
    import mental_health_ai
except Exception:
    mental_health_ai = None

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'aid-dispatch-secret-key-2025'

# Initialize persistent storage
storage = Storage('data/storage.json')
trucks = Truck()
help_stations = HelpStation()

# Seed trucks if needed
if not trucks.trucks:
    for i in range(1, 6):
        trucks.add_truck(f"Truck {i}")

# Configuration for supply categories
SUPPLY_CATEGORIES = {
    'food': 'lbs',
    'medical': None,
    'blankets': 'quantity',
    'water': 'lbs'
}

# ============ AUTHENTICATION ROUTES ============

@app.route('/')
def index():
    """Home page with login options."""
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    """Authenticate user as government or non-government."""
    data = request.json
    password = data.get('password', '').strip()
    user_type = 'gov' if password == 'gov' else 'non-gov'
    
    session['user_type'] = user_type
    session['user_name'] = data.get('name', 'User').strip() if user_type == 'non-gov' else 'Government'
    
    return jsonify({'success': True, 'user_type': user_type})

@app.route('/logout')
def logout():
    """Log out the user."""
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """Main dashboard based on user type."""
    if 'user_type' not in session:
        return redirect(url_for('index'))
    
    user_type = session.get('user_type')
    if user_type == 'gov':
        return render_template('gov_dashboard.html', user_name=session.get('user_name'))
    else:
        return render_template('nongov_dashboard.html', user_name=session.get('user_name'))

# ============ NON-GOVERNMENT USER ROUTES ============

@app.route('/api/file-report', methods=['POST'])
def file_report():
    """File a disaster report."""
    data = request.json
    user_name = session.get('user_name', 'User')
    
    disaster_type = data.get('disaster_type', 'Unknown')
    details = data.get('details', '')
    address = data.get('address', '')
    city = data.get('city', '')
    country = data.get('country', '')
    
    # Attempt geocoding
    coords = geocode(None, address, city, country)
    
    if coords:
        lat, lon, display = coords
        details_with_location = f"{details} | location_resolved: {display} | lat:{lat} lon:{lon}"
    else:
        details_with_location = details
    
    storage.add_report(user_name, disaster_type, details_with_location)
    
    return jsonify({'success': True, 'message': 'Report filed successfully.'})

@app.route('/api/request-aid', methods=['POST'])
def request_aid():
    """Request aid supplies."""
    data = request.json
    user_name = session.get('user_name', 'User')
    supply = data.get('supply', '').lower()
    quantity = int(data.get('quantity', 1))
    
    # Check inventory
    available = storage.check_inventory(supply)
    if quantity > available:
        return jsonify({'success': False, 'message': f'Only {available} available.'}), 400
    
    # Find available truck
    available_truck = None
    for name, avail in trucks.trucks.items():
        if avail:
            available_truck = name
            break
    
    if not available_truck:
        return jsonify({'success': False, 'message': 'No trucks available.'}), 400
    
    # Dispatch truck and remove supplies
    trucks.dispatch_truck(available_truck)
    storage.remove_supplies(supply, quantity)
    
    unit = SUPPLY_CATEGORIES.get(supply, '')
    message = f"{available_truck} dispatched with {quantity} {unit} of {supply}."
    
    return jsonify({'success': True, 'message': message})

@app.route('/api/available-supplies', methods=['GET'])
def available_supplies():
    """Get list of available supplies."""
    supplies = storage.get_supplies()
    result = []
    
    for supply, quantity in supplies.items():
        supply_lower = supply.lower()
        if quantity > 0:
            unit = SUPPLY_CATEGORIES.get(supply_lower, '')
            result.append({
                'name': supply_lower,
                'quantity': quantity,
                'unit': unit
            })
    
    return jsonify(result)

@app.route('/api/list-stations', methods=['GET'])
def list_stations():
    """Get list of help stations."""
    stations = help_stations.list_stations()
    return jsonify(stations)

# ============ GOVERNMENT USER ROUTES ============

@app.route('/api/add-supplies', methods=['POST'])
def add_supplies():
    """Add supplies to inventory."""
    data = request.json
    supply = data.get('supply', '').lower()
    quantity = int(data.get('quantity', 0))
    
    if quantity <= 0:
        return jsonify({'success': False, 'message': 'Quantity must be positive.'}), 400
    
    storage.add_supplies(supply, quantity)
    return jsonify({'success': True, 'message': f'Added {quantity} of {supply}.'})

@app.route('/api/inventory', methods=['GET'])
def inventory():
    """Get current inventory."""
    supplies = storage.get_supplies()
    result = []
    
    for supply, quantity in supplies.items():
        unit = SUPPLY_CATEGORIES.get(supply.lower(), '')
        result.append({
            'name': supply,
            'quantity': quantity,
            'unit': unit
        })
    
    return jsonify(result)

@app.route('/api/reports', methods=['GET'])
def get_reports():
    """Get all disaster reports."""
    reports = storage.get_reports()
    return jsonify(reports)

@app.route('/api/delete-report/<int:report_id>', methods=['POST'])
def delete_report(report_id):
    """Delete a report."""
    if storage.delete_report(report_id):
        return jsonify({'success': True})
    return jsonify({'success': False}), 404

@app.route('/api/add-station', methods=['POST'])
def add_station():
    """Add a help station."""
    data = request.json
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({'success': False, 'message': 'Station name required.'}), 400
    
    if help_stations.add_station(name):
        return jsonify({'success': True, 'message': f'Added station: {name}'})
    return jsonify({'success': False, 'message': 'Station already exists.'}), 400

@app.route('/api/delete-station/<name>', methods=['POST'])
def delete_station(name):
    """Delete a help station."""
    if help_stations.delete_station(name):
        return jsonify({'success': True})
    return jsonify({'success': False}), 404

@app.route('/api/stations', methods=['GET'])
def get_stations():
    """Get all help stations."""
    stations = help_stations.list_stations()
    return jsonify(stations)

# ============ MENTAL HEALTH SUPPORT ROUTES ============

@app.route('/api/mental-health/check', methods=['GET'])
def check_mental_health():
    """Check if mental health AI is configured."""
    if mental_health_ai is None:
        return jsonify({'configured': False, 'available': False})
    
    configured = mental_health_ai.is_configured()
    return jsonify({'configured': configured, 'available': True})

@app.route('/api/mental-health/configure', methods=['POST'])
def configure_mental_health():
    """Configure mental health AI with API key."""
    if mental_health_ai is None:
        return jsonify({'success': False, 'message': 'Mental health module not available.'}), 400
    
    data = request.json
    api_key = data.get('api_key', '').strip()
    
    if not api_key:
        return jsonify({'success': False, 'message': 'API key required.'}), 400
    
    try:
        # Try to initialize with the provided key
        ok = mental_health_ai.set_api_key(api_key, persist_env=True, write_dotenv=False)
        
        if ok:
            return jsonify({'success': True, 'message': 'Mental health AI configured.'})
        
        # If failed due to missing SDK, try to install
        openai_present = getattr(mental_health_ai, 'OpenAI', None) is not None
        if not openai_present:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "openai", "-q"])
                importlib.reload(mental_health_ai)
                ok2 = mental_health_ai.set_api_key(api_key, persist_env=True, write_dotenv=False)
                if ok2:
                    return jsonify({'success': True, 'message': 'Installed OpenAI and configured AI.'})
            except Exception as ie:
                return jsonify({'success': False, 'message': f'Installation failed: {str(ie)}'}), 400
        
        return jsonify({'success': False, 'message': 'Failed to initialize AI client.'}), 400
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 400

@app.route('/api/mental-health/message', methods=['POST'])
def mental_health_message():
    """Send a message to the mental health AI."""
    if mental_health_ai is None or not mental_health_ai.is_configured():
        return jsonify({'success': False, 'message': 'AI not configured.'}), 400
    
    data = request.json
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'success': False, 'message': 'Message required.'}), 400
    
    try:
        reply = mental_health_ai.update_memory_with_gpt(user_message)
        user_name = session.get('user_name', 'User')
        storage.add_report(user_name, 'mental_support', f"user: {user_message} | response: {reply}")
        return jsonify({'success': True, 'message': reply})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 400

# ============ ERROR HANDLERS ============

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    return render_template('500.html'), 500

# ============ MAIN ENTRY POINT ============

if __name__ == '__main__':
    print("🚀 Aid Dispatch System - Web Frontend")
    print("Starting Flask server on http://localhost:5000")
    print("Press Ctrl+C to stop.")
    app.run(debug=True, host='0.0.0.0', port=5000)
