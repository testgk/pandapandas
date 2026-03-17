/**
 * GeoChallenge - Main Game Logic
 * Uses Globe.GL for 3D globe rendering and backend API for game logic.
 */

// Game state
const gameState = {
    globe: null,
    currentChallenge: null,
    guessSubmitted: false,
    score: 0,
    streak: 0,
    challengeNumber: 0,
    completedChallengeIds: [],
    hintIndex: 0,
    stats: {
        totalGames: 0,
        totalScore: 0,
        bestScore: 0,
        totalAccuracy: 0,
        guessCount: 0,
        bestStreak: 0
    }
};

// Initialize the game
document.addEventListener('DOMContentLoaded', async () => {
    initGlobe();
    loadStats();
    setupEventListeners();
});

/**
 * Initialize the Globe.GL globe
 */
function initGlobe() {
    const container = document.getElementById('globe-container');
    
    gameState.globe = Globe()
        .globeImageUrl('//unpkg.com/three-globe/example/img/earth-blue-marble.jpg')
        .bumpImageUrl('//unpkg.com/three-globe/example/img/earth-topology.png')
        .backgroundImageUrl('//unpkg.com/three-globe/example/img/night-sky.png')
        .width(container.clientWidth)
        .height(container.clientHeight)
        .pointOfView({ lat: 30, lng: 0, altitude: 2.5 })
        .onGlobeClick(handleGlobeClick)
        // Configure polygon layer for country borders
        .polygonsData([])
        .polygonCapColor(() => 'rgba(255, 255, 100, 0.15)')
        .polygonSideColor(() => 'rgba(255, 255, 100, 0.1)')
        .polygonStrokeColor(() => '#ffff00')
        .polygonAltitude(0.01)
        (container);
    
    // Handle window resize
    window.addEventListener('resize', () => {
        gameState.globe
            .width(container.clientWidth)
            .height(container.clientHeight);
    });
}

/**
 * Set up event listeners for UI elements
 */
function setupEventListeners() {
    document.getElementById('start-btn').addEventListener('click', startGame);
    document.getElementById('next-btn-result').addEventListener('click', nextChallenge);
    document.getElementById('hint-btn').addEventListener('click', showHint);
    document.querySelector('.close-btn').addEventListener('click', hideStatsModal);
    
    // Close modal when clicking outside
    document.getElementById('stats-modal').addEventListener('click', (e) => {
        if (e.target.id === 'stats-modal') hideStatsModal();
    });
}

/**
 * Start a new game
 */
async function startGame() {
    gameState.score = 0;
    gameState.streak = 0;
    gameState.challengeNumber = 0;
    gameState.completedChallengeIds = [];
    
    updateScoreDisplay();
    
    document.getElementById('start-btn').classList.add('hidden');
    
    await nextChallenge();
}

/**
 * Load the next challenge
 */
async function nextChallenge() {
    try {
        const difficulty = document.getElementById('difficulty-select').value;
        
        // Fetch random challenge from API
        gameState.currentChallenge = await getRandomChallenge(
            difficulty,
            gameState.completedChallengeIds
        );
        
        if (!gameState.currentChallenge) {
            showMessage('No more challenges available!', 'Congratulations!');
            endGame();
            return;
        }
        
        gameState.challengeNumber++;
        gameState.hintIndex = 0;
        gameState.guessSubmitted = false; // Allow new guess
        
        // Update UI
        document.getElementById('challenge-number').textContent = `Challenge ${gameState.challengeNumber}`;
        document.getElementById('difficulty-badge').textContent = gameState.currentChallenge.difficulty;
        document.getElementById('difficulty-badge').className = `badge ${gameState.currentChallenge.difficulty.toLowerCase()}`;
        document.getElementById('challenge-title').textContent = `Find: ${gameState.currentChallenge.location_name}`;
        document.getElementById('challenge-description').textContent = 
            `Country: ${gameState.currentChallenge.country} | Continent: ${gameState.currentChallenge.continent}`;
        
        // Show first hint
        updateHints();
        
        // Hide result area, show hint button
        document.getElementById('result-area').classList.add('hidden');
        document.getElementById('hint-btn').classList.remove('hidden');
        document.getElementById('challenge-location').classList.add('hidden');
        
        // Show challenge description (hidden when result was shown)
        document.getElementById('challenge-description').classList.remove('hidden');
        
        // Clear markers and paths
        gameState.globe
            .pointsData([])
            .pathsData([])
            .arcsData([])
            .polygonsData([]);
        
        // Focus camera on continent
        focusOnContinent(gameState.currentChallenge.continent);
        
    } catch (error) {
        console.error('Error loading challenge:', error);
        showMessage('Error loading challenge. Please try again.', 'Error');
    }
}

/**
 * Handle click on the globe
 */
async function handleGlobeClick({ lat, lng }) {
    if (!gameState.currentChallenge) return;
    if (gameState.guessSubmitted) return; // Prevent multiple submissions
    
    gameState.guessSubmitted = true;
    
    try {
        // Submit guess to API
        const result = await submitGuess(
            gameState.currentChallenge.id,
            lat,
            lng
        );
        
        // Add to completed challenges
        gameState.completedChallengeIds.push(gameState.currentChallenge.id);
        
        // Update score (stored, but not displayed yet)
        gameState.score += result.score;
        
        if (result.is_correct) {
            gameState.streak++;
        } else {
            gameState.streak = 0;
        }
        
        // Show markers
        showResultMarkers(lat, lng, result.actual_lat, result.actual_lng);
        
        // Check if guess was inside the country
        const isInsideCountry = result.scoring_zone !== 'outside';
        
        // Show country border with appropriate style (await to finish before showing result)
        await displayCountryBorder(
            gameState.currentChallenge.country,
            result.is_correct,  // green if correct
            isInsideCountry     // glow only if inside
        );
        
        // Only draw scoring zone circles if guess was inside the country
        if (isInsideCountry) {
            drawScoringZones(gameState.currentChallenge.id, result.actual_lat, result.actual_lng);
        }
        
        // Now update the score display (after map is updated)
        updateScoreDisplay();
        
        // Show result panel (after map is updated)
        showResult(result);
        
        // Update stats
        updateStats(result);
        
    } catch (error) {
        console.error('Error submitting guess:', error);
    }
}

/**
 * Show result markers on the globe
 */
function showResultMarkers(guessLat, guessLng, actualLat, actualLng) {
    const points = [
        {
            lat: guessLat,
            lng: guessLng,
            color: '#ff6b6b',
            label: 'Your Guess',
            size: 0.5
        },
        {
            lat: actualLat,
            lng: actualLng,
            color: '#4ecdc4',
            label: 'Actual',
            size: 0.7
        }
    ];
    
    gameState.globe
        .pointsData(points)
        .pointAltitude(0.01)
        .pointColor('color')
        .pointRadius('size')
        .pointLabel('label');
    
    // Draw line between points
    gameState.globe
        .arcsData([{
            startLat: guessLat,
            startLng: guessLng,
            endLat: actualLat,
            endLng: actualLng,
            color: '#ffd93d'
        }])
        .arcColor('color')
        .arcDashLength(0.5)
        .arcDashGap(0.1)
        .arcDashAnimateTime(2000);
}

/**
 * Fetch and display country border on the globe
 * @param {string} countryName - Name of the country
 * @param {boolean} isCorrect - Whether the guess was correct (for color)
 * @param {boolean} isInsideCountry - Whether click was inside the country
 */
async function displayCountryBorder(countryName, isCorrect = false, isInsideCountry = true) {
    try {
        const boundary = await getCountryBoundary(countryName);
        if (!boundary || !boundary.geometry) {
            console.warn('No boundary data for:', countryName);
            return;
        }
        
        // Configure border colors based on result
        let strokeColor, capColor, sideColor;
        
        if (isCorrect) {
            // Green glowing border for correct answer
            strokeColor = '#00ff00';
            capColor = 'rgba(0, 255, 0, 0.15)';
            sideColor = 'rgba(0, 255, 0, 0.2)';
        } else if (!isInsideCountry) {
            // Red border for outside country
            strokeColor = '#ff4444';
            capColor = 'rgba(255, 68, 68, 0.1)';
            sideColor = 'rgba(255, 68, 68, 0.15)';
        } else {
            // Orange/yellow border for inside but not correct
            strokeColor = '#ffaa00';
            capColor = 'rgba(255, 170, 0, 0.12)';
            sideColor = 'rgba(255, 170, 0, 0.15)';
        }
        
        // Configure polygon layer with appropriate colors
        gameState.globe
            .polygonCapColor(() => capColor)
            .polygonSideColor(() => sideColor)
            .polygonStrokeColor(() => strokeColor)
            .polygonAltitude(isCorrect ? 0.02 : 0.01)  // Raise for glow effect
            .polygonsData([boundary]);
        
    } catch (error) {
        console.warn('Error displaying country border:', error);
    }
}

/**
 * Generate circle coordinates around a center point
 */
function generateCircleCoords(centerLat, centerLng, radiusKm, segments = 64) {
    const coords = [];
    const earthRadiusKm = 6371;
    
    for (let i = 0; i <= segments; i++) {
        const angle = (i / segments) * 2 * Math.PI;
        
        // Calculate point at distance radiusKm from center
        const latRad = centerLat * Math.PI / 180;
        const lngRad = centerLng * Math.PI / 180;
        const angularDist = radiusKm / earthRadiusKm;
        
        const newLatRad = Math.asin(
            Math.sin(latRad) * Math.cos(angularDist) +
            Math.cos(latRad) * Math.sin(angularDist) * Math.cos(angle)
        );
        const newLngRad = lngRad + Math.atan2(
            Math.sin(angle) * Math.sin(angularDist) * Math.cos(latRad),
            Math.cos(angularDist) - Math.sin(latRad) * Math.sin(newLatRad)
        );
        
        coords.push([newLngRad * 180 / Math.PI, newLatRad * 180 / Math.PI]);
    }
    
    return coords;
}

/**
 * Draw scoring zone circles around the target
 */
async function drawScoringZones(challengeId, centerLat, centerLng) {
    try {
        const zonesData = await getScoringZones(challengeId);
        const paths = [];
        
        // Zone colors matching desktop app
        const zoneColors = {
            'green': 'rgba(25, 217, 38, 0.9)',
            'yellow': 'rgba(255, 230, 0, 0.85)',
            'orange': 'rgba(255, 140, 0, 0.8)',
            'red': 'rgba(255, 38, 0, 0.75)'
        };
        
        for (const zone of zonesData.zones) {
            // Draw outer boundary circle for each zone
            const radiusKm = zone.outer_km;
            const coords = generateCircleCoords(centerLat, centerLng, radiusKm);
            
            paths.push({
                coords: coords,
                color: zoneColors[zone.color] || 'white'
            });
        }
        
        gameState.globe
            .pathsData(paths)
            .pathPoints('coords')
            .pathPointLat(p => p[1])
            .pathPointLng(p => p[0])
            .pathColor('color')
            .pathStroke(2.5)
            .pathDashLength(1)
            .pathDashGap(0)
            .pathDashAnimateTime(0)
            .pathPointAlt(0.03);  // Render above country polygon
            
    } catch (error) {
        console.error('Error drawing scoring zones:', error);
    }
}

/**
 * Show the result panel
 */
function showResult(result) {
    const resultArea = document.getElementById('result-area');
    const icon = document.getElementById('result-icon');
    const title = document.getElementById('result-title');
    
    // Determine message based on score ranges
    if (result.scoring_zone === 'outside') {
        icon.textContent = '✗';
        icon.style.color = '#ff4444';
        title.textContent = 'Outside!';
    } else if (result.score >= 100) {
        icon.textContent = '🎯';
        icon.style.color = '#00ff00';
        title.textContent = 'Perfect!';
    } else if (result.score >= 80) {
        icon.textContent = '✓';
        icon.style.color = '#4ecdc4';
        title.textContent = 'Excellent!';
    } else if (result.score >= 50) {
        icon.textContent = '✓';
        icon.style.color = '#4ecdc4';
        title.textContent = 'Good!';
    } else if (result.score >= 20) {
        icon.textContent = '~';
        icon.style.color = '#ffaa00';
        title.textContent = 'Not bad!';
    } else {
        icon.textContent = '✗';
        icon.style.color = '#ff6b6b';
        title.textContent = 'Try again!';
    }
    
    document.getElementById('result-distance').textContent = `${result.distance_km.toLocaleString()}km`;
    document.getElementById('result-points').textContent = `+${result.score}`;
    
    // Show location info inline under title
    const challenge = gameState.currentChallenge;
    const locationEl = document.getElementById('challenge-location');
    locationEl.textContent = `${challenge.city}, ${challenge.country}, ${challenge.continent}`;
    locationEl.classList.remove('hidden');
    
    // Hide hints and description to make room
    document.getElementById('hints-container').classList.add('hidden');
    document.getElementById('challenge-description').classList.add('hidden');
    
    resultArea.classList.remove('hidden');
    document.getElementById('hint-btn').classList.add('hidden');
}

/**
 * Show additional hints and zoom near the target location
 */
function showHint() {
    if (!gameState.currentChallenge) return;
    
    gameState.hintIndex++;
    updateHints();
    
    // Zoom near the target location with random offset (like Panda3D)
    zoomToHint();
}

/**
 * Zoom camera near the challenge target with a random offset (doesn't reveal exact location)
 */
function zoomToHint() {
    if (!gameState.currentChallenge) return;
    
    // Challenge uses latitude/longitude directly
    const actualLat = gameState.currentChallenge.latitude;
    const actualLng = gameState.currentChallenge.longitude;
    
    // Random offset: 15-25 degrees in a random direction (same as Panda3D)
    const offsetDist = 15 + Math.random() * 10; // 15-25 degrees
    const offsetAngle = Math.random() * 360;
    
    let hintLat = actualLat + offsetDist * Math.cos(offsetAngle * Math.PI / 180);
    let hintLng = actualLng + offsetDist * Math.sin(offsetAngle * Math.PI / 180);
    
    // Clamp latitude to valid range
    hintLat = Math.max(-85, Math.min(85, hintLat));
    
    console.log(`Hint zoom: actual (${actualLat}, ${actualLng}) -> hint (${hintLat.toFixed(2)}, ${hintLng.toFixed(2)})`);
    
    // Animate camera to the hint location (zoomed in)
    gameState.globe.pointOfView({ lat: hintLat, lng: hintLng, altitude: 0.8 }, 1000);
}

/**
 * Update hints display
 */
function updateHints() {
    const hints = gameState.currentChallenge.hints;
    const container = document.getElementById('hints-container');
    const list = document.getElementById('hints-list');
    
    if (!hints || hints.length === 0) {
        container.classList.add('hidden');
        return;
    }
    
    list.innerHTML = '';
    const visibleHints = hints.slice(0, gameState.hintIndex + 1);
    
    visibleHints.forEach(hint => {
        const li = document.createElement('li');
        li.textContent = hint;
        list.appendChild(li);
    });
    
    container.classList.remove('hidden');
    
    // Hide hint button if all hints shown
    if (gameState.hintIndex >= hints.length - 1) {
        document.getElementById('hint-btn').classList.add('hidden');
    }
}

/**
 * Focus camera on a continent
 */
function focusOnContinent(continent) {
    const centers = {
        'Europe': { lat: 54, lng: 15, altitude: 2 },
        'Asia': { lat: 35, lng: 100, altitude: 2.5 },
        'Africa': { lat: 0, lng: 20, altitude: 2 },
        'North America': { lat: 40, lng: -100, altitude: 2 },
        'South America': { lat: -15, lng: -60, altitude: 2 },
        'Oceania': { lat: -25, lng: 140, altitude: 2 },
        'Antarctica': { lat: -85, lng: 0, altitude: 2 }
    };
    
    const target = centers[continent] || { lat: 20, lng: 0, altitude: 2.5 };
    gameState.globe.pointOfView(target, 1000);
}

/**
 * Update score display
 */
function updateScoreDisplay() {
    document.getElementById('current-score').textContent = `Score: ${gameState.score}`;
    document.getElementById('streak').textContent = `Streak: ${gameState.streak}`;
}

/**
 * Show a message in the challenge panel
 */
function showMessage(description, title) {
    document.getElementById('challenge-title').textContent = title;
    document.getElementById('challenge-description').textContent = description;
}

/**
 * End the game
 */
function endGame() {
    gameState.stats.totalGames++;
    gameState.stats.totalScore += gameState.score;
    if (gameState.score > gameState.stats.bestScore) {
        gameState.stats.bestScore = gameState.score;
    }
    
    saveStats();
    
    document.getElementById('start-btn').classList.remove('hidden');
    document.getElementById('start-btn').textContent = 'Play Again';
    document.getElementById('hint-btn').classList.add('hidden');
}

/**
 * Update statistics
 */
function updateStats(result) {
    gameState.stats.totalAccuracy += result.score;
    gameState.stats.guessCount++;
    if (gameState.streak > gameState.stats.bestStreak) {
        gameState.stats.bestStreak = gameState.streak;
    }
    saveStats();
}

/**
 * Load stats from localStorage
 */
function loadStats() {
    const saved = localStorage.getItem('geochallenge_stats');
    if (saved) {
        gameState.stats = JSON.parse(saved);
    }
}

/**
 * Save stats to localStorage
 */
function saveStats() {
    localStorage.setItem('geochallenge_stats', JSON.stringify(gameState.stats));
}

/**
 * Show stats modal
 */
function showStatsModal() {
    const avgAccuracy = gameState.stats.guessCount > 0 
        ? (gameState.stats.totalAccuracy / gameState.stats.guessCount).toFixed(1)
        : 0;
    
    document.getElementById('stat-total-games').textContent = gameState.stats.totalGames;
    document.getElementById('stat-total-score').textContent = gameState.stats.totalScore;
    document.getElementById('stat-avg-accuracy').textContent = `${avgAccuracy}%`;
    document.getElementById('stat-best-score').textContent = gameState.stats.bestScore;
    document.getElementById('stat-streak').textContent = gameState.streak;
    document.getElementById('stat-best-streak').textContent = gameState.stats.bestStreak;
    
    document.getElementById('stats-modal').classList.remove('hidden');
}

/**
 * Hide stats modal
 */
function hideStatsModal() {
    document.getElementById('stats-modal').classList.add('hidden');
}
