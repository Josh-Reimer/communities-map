from flask import Flask, render_template, jsonify
import json
import os
import glob

app = Flask(__name__)

def load_all_json_files(directory_path='./responses'):
    """Load all JSON files from the specified directory"""
    all_features = []
    congregations = []
    
    # Find all JSON files in the directory
    json_files = glob.glob(os.path.join(directory_path, '*.json'))
    
    for file_path in json_files:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            # Extract features from the geojson
            if 'data' in data and 'geojson' in data['data']:
                features = data['data']['geojson']['features']
                all_features.extend(features)
                
            # Extract congregation info if available
            if 'data' in data and 'cong' in data['data']:
                cong_data = data['data']['cong']
                cong_data['source_file'] = os.path.basename(file_path)
                congregations.append(cong_data)
                
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    return all_features, congregations

@app.route('/')
def index():
    return render_template('map.html')

@app.route('/api/data')
def get_map_data():
    """API endpoint to get all map data"""
    features, congregations = load_all_json_files()
    
    # Calculate bounds for all features
    if features:
        lats = [f['geometry']['coordinates'][1] for f in features if f['geometry']['type'] == 'Point']
        lngs = [f['geometry']['coordinates'][0] for f in features if f['geometry']['type'] == 'Point']
        
        if congregations:
            cong_lats = [c['geometry']['coordinates'][1] for c in congregations if c['geometry']['type'] == 'Point']
            cong_lngs = [c['geometry']['coordinates'][0] for c in congregations if c['geometry']['type'] == 'Point']
            lats.extend(cong_lats)
            lngs.extend(cong_lngs)
        
        bounds = {
            'north': max(lats),
            'south': min(lats),
            'east': max(lngs),
            'west': min(lngs)
        }
    else:
        bounds = None
    
    return jsonify({
        'features': features,
        'congregations': congregations,
        'bounds': bounds,
        'total_features': len(features),
        'total_congregations': len(congregations)
    })

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Create the HTML template
    html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Community Map</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
        }
        #map {
            height: 100vh;
            width: 100%;
        }
        .info-panel {
            position: absolute;
            top: 10px;
            right: 10px;
            background: white;
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            z-index: 1000;
            max-width: 250px;
        }
        .info-panel h3 {
            margin-top: 0;
            color: #333;
        }
        .legend {
            margin-top: 10px;
        }
        .legend-item {
            display: flex;
            align-items: center;
            margin: 5px 0;
        }
        .legend-color {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .person { background-color: #3388ff; }
        .church { background-color: #ff4444; }
        .school { background-color: #44ff44; }
        .building { background-color: #ffaa00; }
        .congregation { background-color: #8844ff; }
    </style>
</head>
<body>
    <div id="map"></div>
    <div class="info-panel">
        <h3>Community Map</h3>
        <div id="stats">Loading...</div>
        <div class="legend">
            <h4>Legend</h4>
            <div class="legend-item">
                <div class="legend-color person"></div>
                <span>People</span>
            </div>
            <div class="legend-item">
                <div class="legend-color church"></div>
                <span>Churches</span>
            </div>
            <div class="legend-item">
                <div class="legend-color school"></div>
                <span>Schools</span>
            </div>
            <div class="legend-item">
                <div class="legend-color building"></div>
                <span>Buildings</span>
            </div>
            <div class="legend-item">
                <div class="legend-color congregation"></div>
                <span>Congregations</span>
            </div>
        </div>
    </div>

    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        // Initialize map
        const map = L.map('map').setView([46.9, -116.8], 10);

        // Add tile layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);

        // Function to get marker color based on type
        function getMarkerColor(tp) {
            switch(tp) {
                case '0': return '#3388ff'; // People - blue
                case '6': return '#ff4444'; // Church - red
                case '5': return '#44ff44'; // School - green
                case '4': return '#ffaa00'; // Building - orange
                default: return '#888888'; // Default - gray
            }
        }

        // Function to get type name
        function getTypeName(tp) {
            switch(tp) {
                case '0': return 'Person';
                case '6': return 'Church';
                case '5': return 'School';
                case '4': return 'Building';
                default: return 'Unknown';
            }
        }

        // Load and display data
        fetch('/api/data')
            .then(response => response.json())
            .then(data => {
                console.log('Loaded data:', data);
                
                // Update stats
                document.getElementById('stats').innerHTML = `
                    <strong>Total Locations:</strong> ${data.total_features}<br>
                    <strong>Congregations:</strong> ${data.total_congregations}
                `;

                // Add regular features
                data.features.forEach(feature => {
                    if (feature.geometry && feature.geometry.type === 'Point') {
                        const [lng, lat] = feature.geometry.coordinates;
                        const props = feature.properties;
                        
                        const marker = L.circleMarker([lat, lng], {
                            radius: 6,
                            fillColor: getMarkerColor(props.tp),
                            color: '#000',
                            weight: 1,
                            opacity: 1,
                            fillOpacity: 0.8
                        });

                        // Create popup content
                        let popupContent = '<div>';
                        if (props.f || props.l) {
                            popupContent += `<strong>${props.f || ''} ${props.l || ''}</strong><br>`;
                        }
                        popupContent += `<em>Type:</em> ${getTypeName(props.tp)}<br>`;
                        if (props.id) {
                            popupContent += `<em>ID:</em> ${props.id}<br>`;
                        }
                        popupContent += `<em>Coordinates:</em> ${lat.toFixed(5)}, ${lng.toFixed(5)}`;
                        popupContent += '</div>';

                        marker.bindPopup(popupContent);
                        marker.addTo(map);
                    }
                });

                // Add congregations with different styling
                data.congregations.forEach(cong => {
                    if (cong.geometry && cong.geometry.type === 'Point') {
                        const [lng, lat] = cong.geometry.coordinates;
                        const props = cong.properties;
                        
                        const marker = L.circleMarker([lat, lng], {
                            radius: 10,
                            fillColor: '#8844ff',
                            color: '#000',
                            weight: 2,
                            opacity: 1,
                            fillOpacity: 0.8
                        });

                        let popupContent = '<div>';
                        popupContent += '<strong style="color: #8844ff;">CONGREGATION</strong><br>';
                        if (props.f || props.l) {
                            popupContent += `<strong>${props.f || ''} ${props.l || ''}</strong><br>`;
                        }
                        if (cong.source_file) {
                            popupContent += `<em>Source:</em> ${cong.source_file}<br>`;
                        }
                        popupContent += `<em>Coordinates:</em> ${lat.toFixed(5)}, ${lng.toFixed(5)}`;
                        popupContent += '</div>';

                        marker.bindPopup(popupContent);
                        marker.addTo(map);
                    }
                });

                // Fit map to bounds if we have data
                if (data.bounds) {
                    const bounds = L.latLngBounds(
                        [data.bounds.south, data.bounds.west],
                        [data.bounds.north, data.bounds.east]
                    );
                    map.fitBounds(bounds, { padding: [20, 20] });
                }
            })
            .catch(error => {
                console.error('Error loading data:', error);
                document.getElementById('stats').innerHTML = '<span style="color: red;">Error loading data</span>';
            });
    </script>
</body>
</html>'''
    
    # Write the HTML template to file
    with open('templates/map.html', 'w') as f:
        f.write(html_template)
    
    print("Flask app starting...")
    print("Place your JSON files in the same directory as this script")
    print("Open http://127.0.0.1:5000 in your browser to view the map")
    
    app.run(debug=True)