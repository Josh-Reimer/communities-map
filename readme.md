# README.md
# Community Maps

A Flask application that displays community locations on an interactive map using Leaflet.js.

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Josh-Reimer/communities-map
   cd communities-map
   ```

2. **Run with Docker:**
   ```bash
   # Build the image
   docker build -t communities-map .

   # Run the container
   docker run -p 5000:5000 communities-map
   ```

3. **Access the application:**
   Open http://localhost:5000 in your browser

## Project Structure
```
communities-map/
├── Dockerfile
├── requirements.txt
├── app.py
├── .dockerignore
├── README.md
├── templates/
│   └── index.html
└── data/
    └── [community data files]
```

## Features

- **Interactive Map**: Leaflet.js-powered map with OpenStreetMap tiles
- **Color-coded Markers**: Different colors for different types of locations
- **Auto-discovery**: Automatically loads all response files from the responses directory
- **Production Ready**: Optimized for production deployment

## Environment Variables

- `FLASK_ENV`: Set to `production` for production deployment
- `FLASK_APP`: Set to `app.py` (configured in Dockerfile)
- `FLASK_RUN_HOST`: Host to bind to (default: 0.0.0.0)
- `FLASK_RUN_PORT`: Port to bind to (default: 5000)

## Development Setup

If you prefer to run the application without Docker:

1. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   flask run
   ```

## Stopping the Application

If running with Docker:
```bash
# Find the container ID
docker ps

# Stop the container
docker stop <container-id>
```
