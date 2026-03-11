#!/usr/bin/env python3
"""
Web-based Interactive GeoChallenge Game
Click on the map in your web browser to make your guess!
"""
import sys
import os
from pathlib import Path
import webbrowser
import time
import json
import http.server
import socketserver
import threading
from urllib.parse import urlparse, parse_qs

# Add p3d directory to path so we can import the game modules
sys.path.append(str(Path(__file__).parent / "p3d"))

try:
    import pandas as pd
    import numpy as np
    import folium
    from shapely.geometry import Point
    print("✅ Successfully imported core dependencies")
except ImportError as e:
    print(f"❌ Missing required dependency: {e}")
    print("Please install required packages with: pip install pandas numpy shapely folium")
    sys.exit(1)

class WebGeoChallenge:
    def __init__(self):
        # Import the game class
        from geo_challenge_game import GeoChallengeGame, DifficultyLevel
        
        # Simple WorldDataManager mock
        class SimpleWorldDataManager:
            def __init__(self):
                pass
        
        # Initialize game
        world_manager = SimpleWorldDataManager()
        self.game = GeoChallengeGame(world_manager)
        self.DifficultyLevel = DifficultyLevel
        
        # Game state
        self.current_challenge = None
        self.game_count = 0
        self.max_games = 5
        self.extra_hints_used = 0
        self.game_active = False
        self.results = []
        
        # Web server state
        self.server = None
        self.server_thread = None
        self.port = 8888
    
    def start_new_round(self):
        """Start a new round"""
        if self.game_count >= self.max_games:
            return False
        
        self.game_count += 1
        self.extra_hints_used = 0
        
        # Get new challenge
        difficulty = self.DifficultyLevel.EASY if self.game_count <= 2 else self.DifficultyLevel.MEDIUM
        self.current_challenge = self.game.get_challenge_by_difficulty(difficulty)
        self.game_active = True
        
        return True
    
    def get_extra_hint(self):
        """Get an extra hint"""
        self.extra_hints_used += 1
        
        if self.extra_hints_used == 1:
            return f"This location is in {self.current_challenge.continent}"
        elif self.extra_hints_used == 2:
            actual_lat, actual_lon = self.current_challenge.actual_coordinates
            hemisphere = "Northern" if actual_lat > 0 else "Southern"
            return f"This location is in the {hemisphere} Hemisphere"
        elif self.extra_hints_used == 3:
            actual_lat, actual_lon = self.current_challenge.actual_coordinates
            hemisphere = "Eastern" if actual_lon > 0 else "Western"
            return f"This location is in the {hemisphere} Hemisphere"
        else:
            return "No more hints available!"
    
    def submit_guess(self, lat, lon):
        """Submit a guess and return results"""
        if not self.game_active or not self.current_challenge:
            return {"error": "No active game"}
        
        # Score the attempt
        attempt = self.game.score_attempt((lat, lon))
        actual_lat, actual_lon = self.current_challenge.actual_coordinates
        
        # Calculate final score with hint penalty
        penalty = min(100, self.extra_hints_used * 25) if self.extra_hints_used > 0 else 0
        final_score = max(0, attempt.accuracy_score - penalty)
        
        # Performance feedback
        if final_score >= 800:
            feedback = "🎉 Excellent! You're very close!"
        elif final_score >= 600:
            feedback = "👍 Good guess! Getting warmer!"
        elif final_score >= 400:
            feedback = "🤔 Not bad, but you can do better!"
        else:
            feedback = "📚 Keep practicing! Geography takes time to master!"
        
        result = {
            "guess_lat": lat,
            "guess_lon": lon,
            "actual_lat": actual_lat,
            "actual_lon": actual_lon,
            "distance_km": attempt.distance_km,
            "base_score": attempt.accuracy_score,
            "penalty": penalty,
            "final_score": final_score,
            "feedback": feedback,
            "location_name": self.current_challenge.location_name,
            "round": self.game_count
        }
        
        self.results.append(result)
        self.game_active = False
        
        return result
    
    def get_game_state(self):
        """Get current game state for the web interface"""
        if not self.current_challenge:
            return {"error": "No active challenge"}
        
        # Get base hints
        hints = list(self.current_challenge.hints)
        
        # Add geographic hint
        additional_hint = self.game.get_hint(len(self.current_challenge.hints))
        hints.append(additional_hint)
        
        return {
            "round": self.game_count,
            "max_rounds": self.max_games,
            "location_name": self.current_challenge.location_name,
            "difficulty": self.current_challenge.difficulty.value,
            "country": self.current_challenge.country,
            "continent": self.current_challenge.continent,
            "hints": hints,
            "extra_hints_used": self.extra_hints_used,
            "game_active": self.game_active
        }
    
    def get_final_stats(self):
        """Get final game statistics"""
        analytics = self.game.get_performance_analytics()
        
        if "message" not in analytics:
            overview = analytics["overview"]
            distance = analytics["distance_analysis"]
            
            return {
                "total_games": overview['total_games'],
                "average_score": overview['average_score'],
                "best_score": overview['best_score'],
                "average_distance": distance['average_distance_km'],
                "best_distance": distance['best_distance_km']
            }
        else:
            return {"message": analytics["message"]}
    
    def create_map_html(self):
        """Create the interactive HTML map"""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>🌍 GeoChallenge - Interactive Web Map</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f0f8ff;
        }
        
        .header {
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        
        .game-container {
            display: flex;
            gap: 20px;
        }
        
        .sidebar {
            width: 300px;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            height: fit-content;
        }
        
        .map-container {
            flex: 1;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        #map {
            height: 600px;
            width: 100%;
        }
        
        .challenge-info {
            background: #e8f4fd;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        
        .hints-section {
            background: #fff3cd;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        
        .hint-item {
            margin: 5px 0;
            padding: 5px;
            background: white;
            border-radius: 4px;
        }
        
        .button {
            width: 100%;
            padding: 12px;
            margin: 5px 0;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        
        .btn-primary {
            background-color: #007bff;
            color: white;
        }
        
        .btn-primary:hover {
            background-color: #0056b3;
        }
        
        .btn-success {
            background-color: #28a745;
            color: white;
        }
        
        .btn-success:hover {
            background-color: #1e7e34;
        }
        
        .btn-warning {
            background-color: #ffc107;
            color: #212529;
        }
        
        .btn-warning:hover {
            background-color: #e0a800;
        }
        
        .coordinates {
            background: #d4edda;
            padding: 10px;
            border-radius: 6px;
            text-align: center;
            font-weight: bold;
        }
        
        .results {
            background: #f8d7da;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
        }
        
        .hidden {
            display: none;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🌍 GeoChallenge Game</h1>
        <p>Click anywhere on the map to make your guess!</p>
    </div>

    <div class="game-container">
        <div class="sidebar">
            <div id="challenge-info" class="challenge-info">
                <div class="loading">Loading challenge...</div>
            </div>
            
            <div id="hints-section" class="hints-section hidden">
                <h3>💡 Hints</h3>
                <div id="hints-list"></div>
                <button id="extra-hint-btn" class="button btn-warning" onclick="getExtraHint()">
                    Get Extra Hint
                </button>
            </div>
            
            <div id="coordinates" class="coordinates">
                Click on the map to make your guess!
            </div>
            
            <button id="submit-btn" class="button btn-success hidden" onclick="submitGuess()">
                Submit Guess
            </button>
            
            <button id="next-btn" class="button btn-primary hidden" onclick="nextRound()">
                Next Round
            </button>
            
            <div id="results" class="results hidden">
            </div>
        </div>
        
        <div class="map-container">
            <div id="map"></div>
        </div>
    </div>

    <script>
        let map;
        let currentGuess = null;
        let guessMarker = null;
        let actualMarker = null;
        let gameState = null;
        
        // Initialize the map
        function initMap() {
            map = L.map('map').setView([20, 0], 2);
            
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(map);
            
            // Add click handler
            map.on('click', function(e) {
                if (gameState && gameState.game_active) {
                    makeGuess(e.latlng.lat, e.latlng.lng);
                }
            });
            
            loadGameState();
        }
        
        function makeGuess(lat, lng) {
            // Remove previous guess marker
            if (guessMarker) {
                map.removeLayer(guessMarker);
            }
            
            // Add new guess marker
            guessMarker = L.marker([lat, lng], {
                icon: L.icon({
                    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
                    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                    iconSize: [25, 41],
                    iconAnchor: [12, 41],
                    popupAnchor: [1, -34]
                })
            }).addTo(map);
            
            guessMarker.bindPopup("Your Guess").openPopup();
            
            currentGuess = {lat: lat, lng: lng};
            
            document.getElementById('coordinates').innerHTML = 
                `🎯 Your Guess: (${lat.toFixed(2)}°, ${lng.toFixed(2)}°)`;
            
            document.getElementById('submit-btn').classList.remove('hidden');
        }
        
        async function submitGuess() {
            if (!currentGuess) return;
            
            try {
                const response = await fetch('/submit', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(currentGuess)
                });
                
                const result = await response.json();
                
                if (result.error) {
                    alert(result.error);
                    return;
                }
                
                showResults(result);
                
            } catch (error) {
                console.error('Error submitting guess:', error);
                alert('Error submitting guess. Please try again.');
            }
        }
        
        function showResults(result) {
            // Add actual location marker
            if (actualMarker) {
                map.removeLayer(actualMarker);
            }
            
            actualMarker = L.marker([result.actual_lat, result.actual_lon], {
                icon: L.icon({
                    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png',
                    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                    iconSize: [25, 41],
                    iconAnchor: [12, 41],
                    popupAnchor: [1, -34]
                })
            }).addTo(map);
            
            actualMarker.bindPopup(`${result.location_name}<br>Actual Location`).openPopup();
            
            // Draw line between guess and actual
            const polyline = L.polyline([
                [result.guess_lat, result.guess_lon],
                [result.actual_lat, result.actual_lon]
            ], {color: 'red', weight: 3, dashArray: '5, 5'}).addTo(map);
            
            // Show results
            let resultsHtml = `
                <h3>📊 Round ${result.round} Results</h3>
                <p><strong>🎯 Location:</strong> ${result.location_name}</p>
                <p><strong>📏 Distance:</strong> ${result.distance_km.toFixed(1)} km</p>
                <p><strong>⭐ Base Score:</strong> ${result.base_score}/1000</p>
            `;
            
            if (result.penalty > 0) {
                resultsHtml += `<p><strong>🔻 Hint Penalty:</strong> -${result.penalty}</p>`;
                resultsHtml += `<p><strong>📊 Final Score:</strong> ${result.final_score}/1000</p>`;
            }
            
            resultsHtml += `<p><strong>💬</strong> ${result.feedback}</p>`;
            
            document.getElementById('results').innerHTML = resultsHtml;
            document.getElementById('results').classList.remove('hidden');
            
            document.getElementById('submit-btn').classList.add('hidden');
            
            if (result.round < 5) {
                document.getElementById('next-btn').classList.remove('hidden');
            } else {
                document.getElementById('next-btn').innerHTML = 'View Final Results';
                document.getElementById('next-btn').classList.remove('hidden');
            }
        }
        
        async function loadGameState() {
            try {
                const response = await fetch('/game-state');
                gameState = await response.json();
                
                if (gameState.error) {
                    document.getElementById('challenge-info').innerHTML = 
                        '<div class="loading">Starting new game...</div>';
                    nextRound();
                    return;
                }
                
                updateUI();
                
            } catch (error) {
                console.error('Error loading game state:', error);
            }
        }
        
        function updateUI() {
            if (!gameState) return;
            
            // Update challenge info
            const challengeHtml = `
                <h3>🎯 Round ${gameState.round}/${gameState.max_rounds}</h3>
                <p><strong>📍 Location:</strong> ${gameState.location_name}</p>
                <p><strong>🎚️ Difficulty:</strong> ${gameState.difficulty}</p>
                <p><strong>🏛️ Country:</strong> ${gameState.country}</p>
                <p><strong>🌎 Continent:</strong> ${gameState.continent}</p>
            `;
            
            document.getElementById('challenge-info').innerHTML = challengeHtml;
            
            // Update hints
            let hintsHtml = '';
            gameState.hints.forEach((hint, index) => {
                hintsHtml += `<div class="hint-item">${index + 1}. ${hint}</div>`;
            });
            
            document.getElementById('hints-list').innerHTML = hintsHtml;
            document.getElementById('hints-section').classList.remove('hidden');
            
            // Update extra hint button
            if (gameState.extra_hints_used >= 3) {
                document.getElementById('extra-hint-btn').disabled = true;
                document.getElementById('extra-hint-btn').innerHTML = 'No more hints';
            }
        }
        
        async function getExtraHint() {
            try {
                const response = await fetch('/extra-hint');
                const data = await response.json();
                
                if (data.hint) {
                    const hintsDiv = document.getElementById('hints-list');
                    hintsDiv.innerHTML += `<div class="hint-item">💡 Extra: ${data.hint}</div>`;
                    
                    if (data.no_more_hints) {
                        document.getElementById('extra-hint-btn').disabled = true;
                        document.getElementById('extra-hint-btn').innerHTML = 'No more hints';
                    }
                }
                
            } catch (error) {
                console.error('Error getting hint:', error);
            }
        }
        
        async function nextRound() {
            try {
                // Clear map
                if (guessMarker) {
                    map.removeLayer(guessMarker);
                    guessMarker = null;
                }
                if (actualMarker) {
                    map.removeLayer(actualMarker);
                    actualMarker = null;
                }
                
                // Clear polylines
                map.eachLayer(function (layer) {
                    if (layer instanceof L.Polyline) {
                        map.removeLayer(layer);
                    }
                });
                
                const response = await fetch('/next-round');
                const data = await response.json();
                
                if (data.game_complete) {
                    showFinalResults(data.stats);
                } else {
                    gameState = data;
                    updateUI();
                    
                    // Reset UI
                    document.getElementById('results').classList.add('hidden');
                    document.getElementById('submit-btn').classList.add('hidden');
                    document.getElementById('next-btn').classList.add('hidden');
                    document.getElementById('coordinates').innerHTML = 'Click on the map to make your guess!';
                    document.getElementById('extra-hint-btn').disabled = false;
                    document.getElementById('extra-hint-btn').innerHTML = 'Get Extra Hint';
                    
                    currentGuess = null;
                }
                
            } catch (error) {
                console.error('Error starting next round:', error);
            }
        }
        
        function showFinalResults(stats) {
            const resultsHtml = `
                <div class="header">
                    <h2>🎮 Game Complete!</h2>
                </div>
                <div class="challenge-info">
                    <h3>📈 Final Statistics</h3>
                    <p><strong>🎮 Games played:</strong> ${stats.total_games}</p>
                    <p><strong>⭐ Average score:</strong> ${stats.average_score.toFixed(1)}/1000</p>
                    <p><strong>🏆 Best score:</strong> ${stats.best_score}/1000</p>
                    <p><strong>📏 Average distance:</strong> ${stats.average_distance.toFixed(1)} km</p>
                    <p><strong>🎯 Best guess:</strong> ${stats.best_distance.toFixed(1)} km away</p>
                </div>
                <button class="button btn-primary" onclick="location.reload()">Play Again</button>
            `;
            
            document.querySelector('.sidebar').innerHTML = resultsHtml;
        }
        
        // Initialize the game when page loads
        window.onload = function() {
            initMap();
        };
    </script>
</body>
</html>
        """
    
    def start_web_server(self):
        """Start the web server for the game"""
        
        class GameHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, game_instance=None, **kwargs):
                self.game_instance = game_instance
                super().__init__(*args, **kwargs)
            
            def do_GET(self):
                parsed_path = urlparse(self.path)
                
                if parsed_path.path == '/' or parsed_path.path == '/index.html':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(self.game_instance.create_map_html().encode())
                
                elif parsed_path.path == '/game-state':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    state = self.game_instance.get_game_state()
                    self.wfile.write(json.dumps(state).encode())
                
                elif parsed_path.path == '/extra-hint':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    hint = self.game_instance.get_extra_hint()
                    response = {
                        "hint": hint,
                        "no_more_hints": self.game_instance.extra_hints_used >= 3
                    }
                    self.wfile.write(json.dumps(response).encode())
                
                elif parsed_path.path == '/next-round':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    
                    if self.game_instance.start_new_round():
                        state = self.game_instance.get_game_state()
                        self.wfile.write(json.dumps(state).encode())
                    else:
                        # Game complete
                        stats = self.game_instance.get_final_stats()
                        response = {"game_complete": True, "stats": stats}
                        self.wfile.write(json.dumps(response).encode())
                
                else:
                    self.send_error(404)
            
            def do_POST(self):
                if self.path == '/submit':
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length)
                    
                    try:
                        data = json.loads(post_data.decode('utf-8'))
                        lat = float(data['lat'])
                        lng = float(data['lng'])
                        
                        result = self.game_instance.submit_guess(lat, lng)
                        
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps(result).encode())
                        
                    except Exception as e:
                        self.send_response(400)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        error_response = {"error": str(e)}
                        self.wfile.write(json.dumps(error_response).encode())
                
                else:
                    self.send_error(404)
            
            def log_message(self, format, *args):
                pass  # Suppress log messages
        
        def handler(*args, **kwargs):
            return GameHandler(*args, game_instance=self, **kwargs)
        
        # Start the server
        with socketserver.TCPServer(("", self.port), handler) as httpd:
            self.server = httpd
            print(f"🌐 GeoChallenge web server starting on http://localhost:{self.port}")
            print("🎮 Your browser should open automatically...")
            
            # Open browser
            threading.Timer(1.0, lambda: webbrowser.open(f'http://localhost:{self.port}')).start()
            
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n👋 Thanks for playing! Game server stopped.")
    
    def run(self):
        """Run the web-based game"""
        print("🌍 Starting Web-based GeoChallenge Game...")
        print("🗺️  This will open an interactive map in your web browser!")
        
        # Start first round
        self.start_new_round()
        
        # Start web server (this will block)
        self.start_web_server()

def main():
    """Main function to run the web-based game"""
    try:
        game = WebGeoChallenge()
        game.run()
        
    except Exception as e:
        print(f"❌ Error starting web game: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
