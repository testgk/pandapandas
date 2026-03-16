/**
 * GeoChallenge - Main Game Logic
 * Uses Globe.GL for 3D globe rendering and backend API for game logic.
 */

// Game state
const gameState = {
    globe: null,
    currentChallenge: null,
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
    document.getElementById('next-btn').addEventListener('click', nextChallenge);
    document.getElementById('hint-btn').addEventListener('click', showHint);
    document.getElementById('stats-btn').addEventListener('click', showStatsModal);
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
        
        // Update UI
        document.getElementById('challenge-number').textContent = `Challenge ${gameState.challengeNumber}`;
        document.getElementById('difficulty-badge').textContent = gameState.currentChallenge.difficulty;
        document.getElementById('difficulty-badge').className = `badge ${gameState.currentChallenge.difficulty.toLowerCase()}`;
        document.getElementById('challenge-title').textContent = `Find: ${gameState.currentChallenge.location_name}`;
        document.getElementById('challenge-description').textContent = 
            `Country: ${gameState.currentChallenge.country} | Continent: ${gameState.currentChallenge.continent}`;
        
        // Show first hint
        updateHints();
        
        // Hide result panel, show hint button
        document.getElementById('result-panel').classList.add('hidden');
        document.getElementById('next-btn').classList.add('hidden');
        document.getElementById('hint-btn').classList.remove('hidden');
        document.getElementById('challenge-info').classList.add('hidden');
        
        // Clear markers
        gameState.globe.pointsData([]);
        
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
    
    try {
        // Submit guess to API
        const result = await submitGuess(
            gameState.currentChallenge.id,
            lat,
            lng
        );
        
        // Add to completed challenges
        gameState.completedChallengeIds.push(gameState.currentChallenge.id);
        
        // Update score
        gameState.score += result.points_earned;
        
        if (result.is_correct) {
            gameState.streak++;
        } else {
            gameState.streak = 0;
        }
        
        updateScoreDisplay();
        
        // Show markers
        showResultMarkers(lat, lng, result.actual_lat, result.actual_lng);
        
        // Show result panel
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
 * Show the result panel
 */
function showResult(result) {
    const panel = document.getElementById('result-panel');
    const icon = document.getElementById('result-icon');
    const title = document.getElementById('result-title');
    
    if (result.is_correct) {
        icon.textContent = '✓';
        icon.style.color = '#4ecdc4';
        title.textContent = result.accuracy_percent > 80 ? 'Excellent!' : 'Good job!';
    } else {
        icon.textContent = '✗';
        icon.style.color = '#ff6b6b';
        title.textContent = 'Keep practicing!';
    }
    
    document.getElementById('result-distance').textContent = result.distance_km.toLocaleString();
    document.getElementById('result-accuracy').textContent = result.accuracy_percent.toFixed(1);
    document.getElementById('result-points').textContent = `+${result.points_earned}`;
    
    // Show challenge info
    document.getElementById('info-country').textContent = gameState.currentChallenge.country;
    document.getElementById('info-continent').textContent = gameState.currentChallenge.continent;
    document.getElementById('challenge-info').classList.remove('hidden');
    
    panel.classList.remove('hidden');
    document.getElementById('hint-btn').classList.add('hidden');
    document.getElementById('next-btn').classList.remove('hidden');
}

/**
 * Show additional hints
 */
function showHint() {
    if (!gameState.currentChallenge) return;
    
    gameState.hintIndex++;
    updateHints();
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
    document.getElementById('next-btn').classList.add('hidden');
    document.getElementById('hint-btn').classList.add('hidden');
}

/**
 * Update statistics
 */
function updateStats(result) {
    gameState.stats.totalAccuracy += result.accuracy_percent;
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
