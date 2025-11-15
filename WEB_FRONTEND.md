# Aid Dispatch System - Web Frontend

A modern, user-friendly web interface for the Aid Dispatch System that replaces the CLI with an interactive dashboard.

## Features

### For Non-Government Users (Regular Requesters)
- **📋 File Disaster Reports** - Report disasters with type, details, and optional location
- **📦 Request Aid** - Browse available supplies and request what you need
- **🏢 View Help Stations** - See registered aid centres in your area
- **💚 Mental Health Support** - Access AI-powered emotional support with OpenAI integration

### For Government Users (Admin)
- **📦 Inventory Management** - Add and track supply inventory
- **📋 Manage Reports** - View and delete disaster reports from requesters
- **🏢 Aid Centre Management** - Add, list, and delete aid centres

## Getting Started

### Prerequisites
- Python 3.7+
- Flask (included in requirements)
- All dependencies from `requirements.txt`

### Installation

1. Install dependencies:
```bash
python -m pip install -r requirements.txt
```

2. Run the Flask app:
```bash
python app.py
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

## Login

### Regular User
- Leave the password field blank
- Enter your name
- Click "Login"

### Government User
- Enter password: `gov`
- Enter your name
- Click "Login"

## Usage

### For Requesters
1. **File a Report**: Click "File Report" tab, select disaster type, provide details and optional location
2. **Request Aid**: Click "Request Aid", select supply type and quantity, click "Request"
3. **View Stations**: Click "Help Stations" to see registered aid centres
4. **Mental Health**: Click "Mental Health Support" and configure with your OpenAI API key

### For Government
1. **Add Supplies**: Enter supply type and quantity, click "Add Supply"
2. **View Inventory**: All supplies are displayed with quantities
3. **Manage Reports**: View all filed reports and delete as needed
4. **Manage Centres**: Add new aid centres and delete existing ones

## Mental Health Support

To use the mental health AI feature:

1. Click the "Mental Health Support" tab
2. Enter your **OpenAI API key** (get one from https://platform.openai.com/)
3. The app will:
   - Attempt to initialize the AI with your key
   - Auto-install the `openai` package if needed
   - Persist the key for the current session only (not saved to disk)

4. Start chatting! The AI provides emotional support based on your input

**Note:** API keys are temporary for the session and are NOT saved to files after the program closes.

## Project Structure

```
exampler/
├── app.py                    # Flask backend (main app)
├── requirements.txt          # Python dependencies
├── src/                      # Core modules
│   ├── storage.py
│   ├── trucks.py
│   ├── help_stations.py
│   ├── report_utils.py
│   └── ...
├── templates/                # HTML templates
│   ├── index.html           # Login page
│   ├── nongov_dashboard.html # Requester dashboard
│   ├── gov_dashboard.html    # Government dashboard
│   ├── 404.html
│   └── 500.html
├── static/                   # CSS & JavaScript
│   ├── styles.css           # Main styles
│   ├── nongov.js            # Requester frontend
│   └── gov.js               # Government frontend
├── data/                     # JSON data files
│   ├── storage.json
│   ├── stations.json
│   └── ...
└── mental_health_ai.py      # AI companion (optional)
```

## Running in Production

For production deployment, use a proper WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Technology Stack

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Database**: JSON files (data/*)
- **AI**: OpenAI GPT-4o-mini (optional)
- **Testing**: pytest

## Troubleshooting

### App won't start
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check if port 5000 is already in use

### Mental Health AI not working
- Verify `openai` package is installed: `pip install openai`
- Check that your API key is valid
- Ensure network access to OpenAI API

### Can't login
- Clear browser cookies or use incognito mode
- Check browser console (F12) for errors

## Contributing

To add features or fix bugs:

1. Make changes to `app.py` (backend) or `static/` and `templates/` (frontend)
2. Run tests: `python -m pytest`
3. Test locally: `python app.py`
4. Submit your changes

## License

This project is part of the Aid Dispatch System. See main README for details.
