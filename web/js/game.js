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
    hintPenalty: 0.0,  // Accumulated penalty (0.0 to 1.0)
    usedShowCountry: false,
    usedZoomHint: false,
    stats: {
        totalGames: 0,
        totalScore: 0,
        bestScore: 0,
        totalAccuracy: 0,
        guessCount: 0,
        bestStreak: 0
    },
    justEnded: false,
    // Timer state
    timer: {
        duration: 15,           // Default time limit in seconds
        elapsedTime: 0,         // Elapsed time in seconds
        intervalId: null,       // Timer interval ID
        isRunning: false,       // Timer status
        startTime: null         // Timestamp when timer started
    },
    // Time trial mode
    isTimeTrial: false          // Whether time trial mode is enabled
};

// Loading overlay helpers
function showLoading(text = 'Loading data...') {
    document.getElementById('loading-text').textContent = text;
    document.getElementById('loading-overlay').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading-overlay').classList.add('hidden');
}

// Initialize the game
document.addEventListener('DOMContentLoaded', async () => {
    initGlobe();
    loadStats();
    setupEventListeners();
    updateCenterButtons();  // Set initial button state
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
    document.getElementById('next-btn-result').addEventListener('click', nextChallenge);
    document.getElementById('hint-btn').addEventListener('click', showHint);
    document.getElementById('country-btn').addEventListener('click', showCountry);
    document.getElementById('zoom-btn').addEventListener('click', zoomHint);
    document.querySelector('.close-btn').addEventListener('click', hideStatsModal);
    
    // Header buttons
    document.getElementById('help-btn').addEventListener('click', showHelpModal);
    document.getElementById('menu-btn').addEventListener('click', toggleMenu);
    
    // Menu items
    document.getElementById('menu-signin-btn').addEventListener('click', showSignInModal);
    document.getElementById('menu-signup-btn').addEventListener('click', showSignUpModal);
    document.getElementById('menu-signout-btn').addEventListener('click', signOut);
    document.getElementById('menu-stats-btn').addEventListener('click', () => { hideMenu(); showStatsModal(); });
    document.getElementById('menu-leaderboard-btn').addEventListener('click', showLeaderboard);
    document.getElementById('menu-about-btn').addEventListener('click', showAboutModal);
    
    // Start panel events
    document.getElementById('time-trial-checkbox').addEventListener('change', toggleTimeTrial);
    document.getElementById('start-game-btn').addEventListener('click', startGameFromPanel);

    // Time preset buttons - only provide visual selection, don't update custom input
    document.querySelectorAll('.time-preset-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            // Remove active from all buttons
            document.querySelectorAll('.time-preset-btn').forEach(b => b.classList.remove('active'));
            // Add active to clicked button
            e.target.classList.add('active');
            // Update the current time display
            const timeValue = e.target.getAttribute('data-time');
            document.getElementById('current-time-display').textContent = timeValue;
            // Do NOT update custom input - user must manually type if they want custom value
        });
    });

    // Custom time input - remove button active state when user focuses on input
    document.getElementById('time-custom-input').addEventListener('focus', (e) => {
        // Remove active state from all preset buttons when user focuses on custom input
        document.querySelectorAll('.time-preset-btn').forEach(b => b.classList.remove('active'));
        // Add focus indicator to custom input
        e.target.classList.add('has-value');
    });

    // Custom time input - validate and keep deselected if custom value entered
    document.getElementById('time-custom-input').addEventListener('change', (e) => {
        const customTime = parseInt(e.target.value);
        if (customTime >= 1 && customTime <= 300) {
            // Keep buttons deselected since user entered custom value
            document.querySelectorAll('.time-preset-btn').forEach(b => b.classList.remove('active'));
            // Add has-value indicator
            e.target.classList.add('has-value');
            // Update the current time display
            document.getElementById('current-time-display').textContent = customTime;
        } else {
            // Invalid value, reset to 15
            e.target.value = '15';
            document.getElementById('current-time-display').textContent = '15';
            e.target.classList.remove('has-value');
        }
    });

    // Also track input event to show has-value while typing
    document.getElementById('time-custom-input').addEventListener('input', (e) => {
        const customTime = parseInt(e.target.value);
        if (e.target.value && customTime >= 1 && customTime <= 300) {
            e.target.classList.add('has-value');
            // Update the current time display in real-time while typing
            document.getElementById('current-time-display').textContent = customTime;
        } else if (!e.target.value || customTime < 1 || customTime > 300) {
            e.target.classList.remove('has-value');
        }
    });

    // Center action buttons
    document.getElementById('center-start-btn').addEventListener('click', startGameFromCenter);
    document.getElementById('center-return-btn').addEventListener('click', returnToGame);
    document.getElementById('center-end-btn').addEventListener('click', endGameFromCenter);
    document.getElementById('center-submit-btn').addEventListener('click', submitScoreFromCenter);
    document.getElementById('center-no-thanks-btn').addEventListener('click', () => {
        gameState.justEnded = false;
        updateCenterButtons();
    });
    
    // Panel close button
    document.getElementById('panel-close-btn').addEventListener('click', hidePanel);
    
    // Modal close buttons
    document.getElementById('help-close-btn').addEventListener('click', hideHelpModal);
    document.getElementById('about-close-btn').addEventListener('click', hideAboutModal);
    document.getElementById('leaderboard-close-btn').addEventListener('click', hideLeaderboard);
    document.getElementById('signin-close-btn').addEventListener('click', hideSignInModal);
    document.getElementById('signup-close-btn').addEventListener('click', hideSignUpModal);
    
    // Auth form links
    document.getElementById('goto-signup').addEventListener('click', (e) => { e.preventDefault(); hideSignInModal(); showSignUpModal(); });
    document.getElementById('goto-signin').addEventListener('click', (e) => { e.preventDefault(); hideSignUpModal(); showSignInModal(); });
    
    // Auth forms
    document.getElementById('signin-form').addEventListener('submit', handleSignIn);
    document.getElementById('signup-form').addEventListener('submit', handleSignUp);
    
    // Sync difficulty selects
    document.getElementById('difficulty-select-start').addEventListener('change', (e) => {
        document.getElementById('difficulty-select').value = e.target.value;
    });
    document.getElementById('difficulty-select').addEventListener('change', (e) => {
        document.getElementById('difficulty-select-start').value = e.target.value;
    });
    
    // Close modals when clicking outside
    document.getElementById('stats-modal').addEventListener('click', (e) => {
        if (e.target.id === 'stats-modal') hideStatsModal();
    });
    document.getElementById('help-modal').addEventListener('click', (e) => {
        if (e.target.id === 'help-modal') hideHelpModal();
    });
    document.getElementById('signin-modal').addEventListener('click', (e) => {
        if (e.target.id === 'signin-modal') hideSignInModal();
    });
    document.getElementById('signup-modal').addEventListener('click', (e) => {
        if (e.target.id === 'signup-modal') hideSignUpModal();
    });
    
    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
        const menu = document.getElementById('menu-dropdown');
        const menuBtn = document.getElementById('menu-btn');
        if (!menu.classList.contains('hidden') && !menu.contains(e.target) && e.target !== menuBtn) {
            hideMenu();
        }
    });
    
    // Update auth UI on load
    updateAuthUI();
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
    // Show sign-in message during loading if not signed in
    if (!authState.isSignedIn) {
        showLoading('Sign in to submit scores!');
        setTimeout(() => {
            showLoading('Loading challenge...');
            nextChallenge();
        }, 2000);
    } else {
        showLoading('Loading challenge...');
        await nextChallenge();
    }
}

/**
 * Load the next challenge
 */
async function nextChallenge() {
    showLoading('Loading challenge...');
    try {
        const difficulty = document.getElementById('difficulty-select').value;
        
        // Fetch random challenge from API
        gameState.currentChallenge = await getRandomChallenge(
            difficulty,
            gameState.completedChallengeIds
        );
        
        if (!gameState.currentChallenge) {
            hideLoading();
            showMessage('No more challenges available!', 'Congratulations!');
            endGame();
            return;
        }
        
        gameState.challengeNumber++;
        gameState.hintIndex = 0;
        gameState.hintPenalty = 0.0;  // Reset penalties
        gameState.usedShowCountry = false;
        gameState.usedZoomHint = false;
        gameState.guessSubmitted = false; // Allow new guess
        
        // Update UI
        document.getElementById('challenge-number').textContent = `Challenge ${gameState.challengeNumber}`;
        document.getElementById('difficulty-badge').textContent = gameState.currentChallenge.difficulty;
        document.getElementById('difficulty-badge').className = `badge ${gameState.currentChallenge.difficulty.toLowerCase()}`;
        document.getElementById('challenge-title').textContent = `Find: ${gameState.currentChallenge.location_name}`;
        document.getElementById('challenge-description').textContent = 
            `Continent: ${gameState.currentChallenge.continent}`;
        
        // Update hints display (without auto-showing first hint)
        updateHintsArea();
        
        // Hide result area, show hints area (with hint buttons)
        document.getElementById('result-area').classList.add('hidden');
        document.getElementById('hints-area').classList.remove('hidden');
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
        
        // Hide center buttons since game is active
        updateCenterButtons();
        
        // Start the timer for the challenge
        startTimer();

        hideLoading();
    } catch (error) {
        hideLoading();
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
    stopTimer();  // Stop the timer when guess is submitted
    showLoading('Checking your guess...');
    
    try {
        // Submit guess to API
        const result = await submitGuess(
            gameState.currentChallenge.id,
            lat,
            lng
        );
        
        // Add to completed challenges
        gameState.completedChallengeIds.push(gameState.currentChallenge.id);
        
        // Calculate score with outside country rules
        const isOutsideCountry = result.scoring_zone === 'outside';
        const isWithinScoringMargin = result.distance_km <= 500;  // Scoring margin = 500km (red zone max)
        
        // If outside country, API returns 0 - we need to calculate what score would have been
        // based on distance to apply the 50% penalty properly
        let baseScore = result.score;
        let calculatedBaseScore = result.score;  // Track the pre-penalty score for display
        if (isOutsideCountry && isWithinScoringMargin) {
            // Calculate score based on distance (same formula as API uses for scoring zones)
            // max 500km for red zone, score decreases linearly
            calculatedBaseScore = Math.max(0, Math.floor(100 * (1 - result.distance_km / 500)));
            baseScore = calculatedBaseScore;
        }
        
        // Apply outside country penalty:
        // - Outside country AND outside margin (>500km) = 0 points
        // - Outside country BUT within margin (≤500km) = 50% reduction
        let outsideCountryPenalty = 0;
        if (isOutsideCountry) {
            if (!isWithinScoringMargin) {
                // Outside margin = 0 points
                outsideCountryPenalty = baseScore;
                baseScore = 0;
            } else {
                // Within margin but outside country = 50% reduction
                outsideCountryPenalty = Math.floor(baseScore * 0.5);
                baseScore = baseScore - outsideCountryPenalty;
            }
        }
        
        // Apply hint penalties to remaining score
        const hintPenaltyAmount = Math.floor(baseScore * gameState.hintPenalty);
        const finalScore = Math.max(0, baseScore - hintPenaltyAmount);
        
        result.baseScore = calculatedBaseScore;  // Score before penalties (may be recalculated for outside country)
        result.outsideCountryPenalty = outsideCountryPenalty;
        result.hintPenaltyAmount = hintPenaltyAmount;
        result.penaltyAmount = outsideCountryPenalty + hintPenaltyAmount;  // Total penalty
        result.finalScore = finalScore;
        result.isWithinScoringMargin = isWithinScoringMargin;
        
        // Update score with penalty applied
        gameState.score += finalScore;
        
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
        
        hideLoading();
    } catch (error) {
        hideLoading();
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
    
    const finalScore = result.finalScore;
    
    // Determine message based on score ranges
    if (result.scoring_zone === 'outside') {
        icon.textContent = '✗';
        icon.style.color = '#ff4444';
        if (!result.isWithinScoringMargin) {
            title.textContent = 'Outside Country! (0 pts)';
        } else {
            title.textContent = 'Outside Country! (-50%)';
        }
    } else if (finalScore >= 100) {
        icon.textContent = '🎯';
        icon.style.color = '#00ff00';
        title.textContent = 'Perfect!';
    } else if (finalScore >= 80) {
        icon.textContent = '✓';
        icon.style.color = '#4ecdc4';
        title.textContent = 'Excellent!';
    } else if (finalScore >= 50) {
        icon.textContent = '✓';
        icon.style.color = '#4ecdc4';
        title.textContent = 'Good!';
    } else if (finalScore >= 20) {
        icon.textContent = '~';
        icon.style.color = '#ffaa00';
        title.textContent = 'Not bad!';
    } else {
        icon.textContent = '✗';
        icon.style.color = '#ff6b6b';
        title.textContent = 'Try again!';
    }
    
    document.getElementById('result-distance').textContent = `${result.distance_km.toLocaleString()}km`;
    
    // Show score with penalty info if applicable
    if (result.penaltyAmount > 0) {
        let penaltyDetails = [];
        if (result.outsideCountryPenalty > 0) {
            penaltyDetails.push(`outside: -${result.outsideCountryPenalty}`);
        }
        if (result.hintPenaltyAmount > 0) {
            penaltyDetails.push(`hints: -${result.hintPenaltyAmount}`);
        }
        document.getElementById('result-points').innerHTML = 
            `+${result.finalScore} <small style="color:#ff6b6b">(base: ${result.baseScore}, ${penaltyDetails.join(', ')})</small>`;
    } else {
        document.getElementById('result-points').textContent = `+${result.finalScore}`;
    }
    
    // Show location info inline under title
    const challenge = gameState.currentChallenge;
    const locationEl = document.getElementById('challenge-location');
    locationEl.textContent = `${challenge.city}, ${challenge.country}, ${challenge.continent}`;
    locationEl.classList.remove('hidden');
    
    // Hide hints area and description to make room
    document.getElementById('hints-area').classList.add('hidden');
    document.getElementById('challenge-description').classList.add('hidden');
    
    resultArea.classList.remove('hidden');
}

/**
 * Show country (-20% penalty)
 */
function showCountry() {
    if (!gameState.currentChallenge) return;
    if (gameState.usedShowCountry) return; // Already used
    
    gameState.usedShowCountry = true;
    gameState.hintPenalty = Math.min(1.0, gameState.hintPenalty + 0.20);
    
    // Show country in the hints area
    const hintsContainer = document.getElementById('hints-container');
    const countryHint = document.createElement('li');
    countryHint.innerHTML = `<strong>Country: ${gameState.currentChallenge.country}</strong> <span style="color:#ff6b6b">(-20%)</span>`;
    countryHint.style.color = '#4ecdc4';
    document.getElementById('hints-list').insertBefore(countryHint, document.getElementById('hints-list').firstChild);
    hintsContainer.classList.remove('hidden');
    
    // Disable button
    document.getElementById('country-btn').disabled = true;
    document.getElementById('country-btn').style.opacity = '0.5';
}

/**
 * Show additional text hints (-10% per hint)
 */
function showHint() {
    if (!gameState.currentChallenge) return;
    
    const hints = gameState.currentChallenge.hints;
    if (!hints || gameState.hintIndex >= hints.length) return;
    
    // Add 10% penalty per hint
    gameState.hintPenalty = Math.min(1.0, gameState.hintPenalty + 0.10);
    
    const hint = hints[gameState.hintIndex];
    gameState.hintIndex++;
    
    // Show hint in the list
    const list = document.getElementById('hints-list');
    const li = document.createElement('li');
    li.innerHTML = `${hint} <span style="color:#ff6b6b">(-10%)</span>`;
    list.appendChild(li);
    document.getElementById('hints-container').classList.remove('hidden');
    
    // Hide hint button if all hints shown
    if (gameState.hintIndex >= hints.length) {
        document.getElementById('hint-btn').disabled = true;
        document.getElementById('hint-btn').style.opacity = '0.5';
    }
}

/**
 * Zoom near target location (-50% penalty)
 */
function zoomHint() {
    if (!gameState.currentChallenge) return;
    if (gameState.usedZoomHint) return; // Already used
    
    gameState.usedZoomHint = true;
    gameState.hintPenalty = Math.min(1.0, gameState.hintPenalty + 0.50);
    
    // Show zoom message
    const list = document.getElementById('hints-list');
    const li = document.createElement('li');
    li.innerHTML = `<strong>Zooming near location...</strong> <span style="color:#ff6b6b">(-50%)</span>`;
    li.style.color = '#ffd93d';
    list.appendChild(li);
    document.getElementById('hints-container').classList.remove('hidden');
    
    // Disable button
    document.getElementById('zoom-btn').disabled = true;
    document.getElementById('zoom-btn').style.opacity = '0.5';
    
    // Zoom to hint location
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
 * Initialize hints area for a new challenge (clears previous hints, enables buttons)
 */
function updateHintsArea() {
    const container = document.getElementById('hints-container');
    const list = document.getElementById('hints-list');
    
    // Clear previous hints
    list.innerHTML = '';
    container.classList.add('hidden');
    
    // Reset buttons
    const countryBtn = document.getElementById('country-btn');
    const hintBtn = document.getElementById('hint-btn');
    const zoomBtn = document.getElementById('zoom-btn');
    
    countryBtn.disabled = false;
    countryBtn.style.opacity = '1';
    hintBtn.disabled = false;
    hintBtn.style.opacity = '1';
    zoomBtn.disabled = false;
    zoomBtn.style.opacity = '1';
    
    // Show hint button only if hints exist
    const hints = gameState.currentChallenge?.hints;
    if (!hints || hints.length === 0) {
        hintBtn.classList.add('hidden');
    } else {
        hintBtn.classList.remove('hidden');
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
 * Start the challenge timer
 */
function startTimer() {
    stopTimer();  // Clear any existing timer

    gameState.timer.isRunning = true;
    gameState.timer.elapsedTime = 0;
    gameState.timer.startTime = Date.now();

    updateTimerDisplay();

    // Update timer every 100ms for smooth display
    gameState.timer.intervalId = setInterval(() => {
        const elapsed = (Date.now() - gameState.timer.startTime) / 1000;
        gameState.timer.elapsedTime = Math.min(elapsed, gameState.timer.duration);

        updateTimerDisplay();

        // If time expired, auto-submit guess as timeout
        if (gameState.timer.elapsedTime >= gameState.timer.duration) {
            stopTimer();
            handleTimeExpired();
        }
    }, 100);
}

/**
 * Stop the challenge timer
 */
function stopTimer() {
    if (gameState.timer.intervalId) {
        clearInterval(gameState.timer.intervalId);
        gameState.timer.intervalId = null;
    }
    gameState.timer.isRunning = false;
}

/**
 * Update the timer display
 */
function updateTimerDisplay() {
    const timerText = document.getElementById('timer-text');
    const remaining = Math.max(0, gameState.timer.duration - gameState.timer.elapsedTime);
    const seconds = Math.ceil(remaining);

    // Update text
    timerText.textContent = `Time: ${seconds}s`;

    // Update color based on remaining time
    timerText.classList.remove('timer-warning', 'timer-critical');
    if (remaining <= 3) {
        timerText.classList.add('timer-critical');
    } else if (remaining <= 7) {
        timerText.classList.add('timer-warning');
    }
}

/**
 * Handle when time expires
 */
function handleTimeExpired() {
    if (!gameState.currentChallenge || gameState.guessSubmitted) {
        return;  // Already submitted or no active challenge
    }

    gameState.guessSubmitted = true;
    stopTimer();

    // Show zero points result without submission
    const timeoutResult = {
        challenge_id: gameState.currentChallenge.id,
        is_correct: false,
        distance_km: 0,
        actual_lat: gameState.currentChallenge.latitude,
        actual_lng: gameState.currentChallenge.longitude,
        scoring_zone: 'timeout',
        score: 0,
        baseScore: 0,
        outsideCountryPenalty: 0,
        hintPenaltyAmount: 0,
        penaltyAmount: 0,
        finalScore: 0,
        isWithinScoringMargin: false
    };

    // Hide hints and show result
    document.getElementById('hints-area').classList.add('hidden');
    document.getElementById('challenge-description').classList.add('hidden');

    // Show timeout result
    const resultArea = document.getElementById('result-area');
    const icon = document.getElementById('result-icon');
    const title = document.getElementById('result-title');

    icon.textContent = '⏱';
    icon.style.color = '#ef4444';
    title.textContent = 'Time\'s Up!';
    document.getElementById('result-distance').textContent = 'No guess submitted';
    document.getElementById('result-points').textContent = '0 points';

    // Show country border in red
    displayCountryBorder(gameState.currentChallenge.country, false, true).catch(() => {});

    resultArea.classList.remove('hidden');
    hideLoading();
}

/**
 * Get elapsed time for current guess
 */
function getElapsedTime() {
    return Math.round(gameState.timer.elapsedTime * 10) / 10;  // Round to 1 decimal place
}

/**
 * Toggle time trial mode
 */
function toggleTimeTrial() {
    const checkbox = document.getElementById('time-trial-checkbox');
    const pickerSection = document.getElementById('time-picker-section');

    gameState.isTimeTrial = checkbox.checked;

    if (gameState.isTimeTrial) {
        pickerSection.style.display = 'flex';
    } else {
        pickerSection.style.display = 'none';
    }
}

/**
 * Start game from start panel with time trial settings
 */
function startGameFromPanel() {
    gameState.justEnded = false;

    // Get difficulty selection
    const difficulty = document.getElementById('difficulty-select-start').value;
    document.getElementById('difficulty-select').value = difficulty;

    // Get time trial settings
    if (gameState.isTimeTrial) {
        // Check if a preset button is selected
        const activeButton = document.querySelector('.time-preset-btn.active');
        if (activeButton) {
            // Use the selected preset button's time
            gameState.timer.duration = parseInt(activeButton.getAttribute('data-time'));
        } else {
            // No preset selected, use custom input value
            const customTime = parseInt(document.getElementById('time-custom-input').value);
            gameState.timer.duration = Math.max(1, Math.min(customTime, 300)); // Clamp 1-300
        }
    } else {
        gameState.timer.duration = 15; // Default
    }

    // Hide start panel and show challenge panel
    document.getElementById('start-panel').classList.add('hidden');
    document.getElementById('challenge-panel').classList.remove('hidden');

    startGame();
}

/**
 * Show start panel
 */
function showStartPanel() {
    document.getElementById('start-panel').classList.remove('hidden');
    document.getElementById('challenge-panel').classList.add('hidden');
    document.getElementById('center-action').classList.add('hidden');
}

/**
 * Hide start panel
 */
function hideStartPanel() {
    document.getElementById('start-panel').classList.add('hidden');
    updateCenterButtons();
}

/**
 * End the game
 */
function endGame() {
    stopTimer();  // Stop timer when game ends
    gameState.stats.totalGames++;
    gameState.stats.totalScore += gameState.score;
    if (gameState.score > gameState.stats.bestScore) {
        gameState.stats.bestScore = gameState.score;
    }
    
    saveStats();
    
    // Hide panel and show center buttons
    document.getElementById('challenge-panel').classList.add('hidden');
    document.getElementById('hints-area').classList.add('hidden');
    updateCenterButtons();
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
        const loadedStats = JSON.parse(saved);
        // Merge with defaults to ensure all fields exist
        gameState.stats = {
            totalGames: loadedStats.totalGames || 0,
            totalScore: loadedStats.totalScore || 0,
            bestScore: loadedStats.bestScore || 0,
            totalAccuracy: loadedStats.totalAccuracy || 0,
            guessCount: loadedStats.guessCount || 0,
            bestStreak: loadedStats.bestStreak || 0
        };
    }
}

/**
 * Save stats to localStorage
 */
function saveStats() {
    localStorage.setItem('geochallenge_stats', JSON.stringify(gameState.stats));
    console.log('Stats saved:', gameState.stats);
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
    
    // Display submitted scores
    const scores = getSubmittedScores();
    const scoresList = document.getElementById('submitted-scores-list');
    
    if (scores.length === 0) {
        scoresList.innerHTML = '<p class="no-scores">No scores submitted yet</p>';
    } else {
        // Show last 5 scores, most recent first
        const recent = [...scores].reverse().slice(0, 5);
        scoresList.innerHTML = recent.map(entry => {
            const date = new Date(entry.date).toLocaleDateString();
            return `<div class="score-entry">
                <span class="score-value">${entry.score} pts</span>
                <span class="score-info">${entry.challenges} challenges • ${date}</span>
            </div>`;
        }).join('');
    }
    
    document.getElementById('stats-modal').classList.remove('hidden');
    document.getElementById('center-action').classList.add('hidden');
}

/**
 * Hide stats modal
 */
function hideStatsModal() {
    document.getElementById('stats-modal').classList.add('hidden');
    updateCenterButtons();
}

// ============================================
// Menu Functions
// ============================================

/**
 * Toggle menu dropdown visibility
 */
function toggleMenu() {
    const menu = document.getElementById('menu-dropdown');
    menu.classList.toggle('hidden');
}

/**
 * Hide menu dropdown
 */
function hideMenu() {
    document.getElementById('menu-dropdown').classList.add('hidden');
}

/**
 * Update center action buttons based on game state
 */
function updateCenterButtons() {
    const startBtn = document.getElementById('center-start-btn');
    const returnBtn = document.getElementById('center-return-btn');
    const endBtn = document.getElementById('center-end-btn');
    const submitBtn = document.getElementById('center-submit-btn');
    const noThanksBtn = document.getElementById('center-no-thanks-btn');
    const centerAction = document.getElementById('center-action');
    const panel = document.getElementById('challenge-panel');
    const gameActive = gameState.currentChallenge !== null;
    const hasScore = gameState.score > 0;
    const panelHidden = panel.classList.contains('hidden');
    // Hide all by default
    startBtn.classList.add('hidden');
    returnBtn.classList.add('hidden');
    endBtn.classList.add('hidden');
    submitBtn.classList.add('hidden');
    noThanksBtn.classList.add('hidden');
    if (!gameActive && gameState.justEnded && authState.isSignedIn) {
        // Game just ended for signed-in user - offer to submit score
        submitBtn.classList.remove('hidden');
        noThanksBtn.classList.remove('hidden');
        centerAction.classList.remove('hidden');
    } else if (!gameActive) {
        // No active game (initial state, guest after game end, or after dismissing submit)
        startBtn.classList.remove('hidden');
        centerAction.classList.remove('hidden');
    } else if (panelHidden) {
        // Game active but panel hidden - show Return and End only
        returnBtn.classList.remove('hidden');
        endBtn.classList.remove('hidden');
        centerAction.classList.remove('hidden');
    } else {
        // Game active and panel visible - hide all center buttons
        centerAction.classList.add('hidden');
    }
}

/**
 * Hide the challenge panel (minimize)
 */
function hidePanel() {
    document.getElementById('challenge-panel').classList.add('hidden');
    updateCenterButtons();
}

/**
 * Show the challenge panel
 */
function showPanel() {
    document.getElementById('challenge-panel').classList.remove('hidden');
    updateCenterButtons();
}

/**
 * Start game from center button
 */
function startGameFromCenter() {
    gameState.justEnded = false;
    showStartPanel();  // Show start panel instead of directly starting game
}

/**
 * End game from center button
 */
function endGameFromCenter() {
    hideMenu();
    // End the current game
    gameState.currentChallenge = null;
    document.getElementById('challenge-panel').classList.add('hidden');
    gameState.justEnded = true;
    if (!authState.isSignedIn) {
        showLoading('Sign in to submit scores!');
        setTimeout(hideLoading, 2000);
    }
    updateCenterButtons();
}

/**
 * Submit score from center button
 */
function submitScoreFromCenter() {
    // Hide submit and no-thanks buttons
    document.getElementById('center-submit-btn').classList.add('hidden');
    document.getElementById('center-no-thanks-btn').classList.add('hidden');
    // Submit score and open leaderboard
    submitScore(true);
}

/**
 * Return to active game (show panel and hide menu)
 */
function returnToGame() {
    hideMenu();
    showPanel();
}

// ============================================
// Help Modal Functions
// ============================================

/**
 * Show help/rules modal
 */
function showHelpModal() {
    document.getElementById('help-modal').classList.remove('hidden');
    document.getElementById('center-action').classList.add('hidden');
}

/**
 * Hide help modal
 */
function hideHelpModal() {
    document.getElementById('help-modal').classList.add('hidden');
    updateCenterButtons();
}

/**
 * Show about modal
 */
function showAboutModal() {
    hideMenu();
    document.getElementById('about-modal').classList.remove('hidden');
    document.getElementById('center-action').classList.add('hidden');
}

/**
 * Hide about modal
 */
function hideAboutModal() {
    document.getElementById('about-modal').classList.add('hidden');
    updateCenterButtons();
}

// ============================================
// Auth Functions
// ============================================

// Auth state
const authState = {
    isSignedIn: false,
    user: null
};

/**
 * Update UI based on auth state
 */
function updateAuthUI() {
    const saved = localStorage.getItem('geochallenge_user');
    if (saved) {
        authState.user = JSON.parse(saved);
        authState.isSignedIn = true;
    }
    
    const signinBtn = document.getElementById('menu-signin-btn');
    const signupBtn = document.getElementById('menu-signup-btn');
    const signoutBtn = document.getElementById('menu-signout-btn');
    
    if (authState.isSignedIn) {
        signinBtn.classList.add('hidden');
        signupBtn.classList.add('hidden');
        signoutBtn.classList.remove('hidden');
        signoutBtn.textContent = `Sign Out (${authState.user.username})`;
    } else {
        signinBtn.classList.remove('hidden');
        signupBtn.classList.remove('hidden');
        signoutBtn.classList.add('hidden');
    }
}

/**
 * Cookie helper functions
 */
function setCookie(name, value, days) {
    const expires = new Date();
    expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);
    document.cookie = `${name}=${encodeURIComponent(value)};expires=${expires.toUTCString()};path=/;SameSite=Strict`;
}

function getCookie(name) {
    const nameEQ = name + '=';
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.indexOf(nameEQ) === 0) {
            return decodeURIComponent(cookie.substring(nameEQ.length));
        }
    }
    return null;
}

function deleteCookie(name) {
    document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;`;
}

/**
 * Show sign in modal
 */
function showSignInModal() {
    hideMenu();
    
    // Hide center buttons to avoid z-index conflicts
    document.getElementById('center-action').classList.add('hidden');
    
    // Pre-fill form if Remember me was checked
    const savedEmail = getCookie('geochallenge_email');
    const savedPassword = getCookie('geochallenge_password');
    const rememberMe = getCookie('geochallenge_remember') === 'true';
    
    if (rememberMe && savedEmail && savedPassword) {
        document.getElementById('signin-email').value = savedEmail;
        document.getElementById('signin-password').value = savedPassword;
        document.getElementById('remember-me').checked = true;
    }
    
    document.getElementById('signin-modal').classList.remove('hidden');
}

/**
 * Hide sign in modal
 */
function hideSignInModal() {
    document.getElementById('signin-modal').classList.add('hidden');
    document.getElementById('signin-form').reset();
    updateCenterButtons();  // Restore center buttons
}

/**
 * Show sign up modal
 */
function showSignUpModal() {
    hideMenu();
    // Hide center buttons to avoid z-index conflicts
    document.getElementById('center-action').classList.add('hidden');
    document.getElementById('signup-modal').classList.remove('hidden');
}

/**
 * Hide sign up modal
 */
function hideSignUpModal() {
    document.getElementById('signup-modal').classList.add('hidden');
    document.getElementById('signup-form').reset();
    updateCenterButtons();  // Restore center buttons
}

/**
 * Handle sign in form submission
 */
async function handleSignIn(e) {
    e.preventDefault();
    
    const email = document.getElementById('signin-email').value;
    const password = document.getElementById('signin-password').value;
    const rememberMe = document.getElementById('remember-me').checked;
    
    // TODO: Replace with actual API call
    // For now, simulate sign in
    try {
        // Simulated auth - in production, call your auth API
        authState.user = {
            username: email.split('@')[0],
            email: email
        };
        authState.isSignedIn = true;
        localStorage.setItem('geochallenge_user', JSON.stringify(authState.user));
        
        // Save credentials to cookies if Remember me is checked
        if (rememberMe) {
            setCookie('geochallenge_email', email, 30);
            setCookie('geochallenge_password', password, 30);
            setCookie('geochallenge_remember', 'true', 30);
        } else {
            deleteCookie('geochallenge_email');
            deleteCookie('geochallenge_password');
            deleteCookie('geochallenge_remember');
        }
        
        hideSignInModal();
        updateAuthUI();
        alert('Signed in successfully!');
    } catch (error) {
        alert('Sign in failed. Please try again.');
    }
}

/**
 * Handle sign up form submission
 */
async function handleSignUp(e) {
    e.preventDefault();
    
    const username = document.getElementById('signup-username').value;
    const email = document.getElementById('signup-email').value;
    const password = document.getElementById('signup-password').value;
    
    // TODO: Replace with actual API call
    // For now, simulate sign up
    try {
        // Simulated auth - in production, call your auth API
        authState.user = {
            username: username,
            email: email
        };
        authState.isSignedIn = true;
        localStorage.setItem('geochallenge_user', JSON.stringify(authState.user));
        
        hideSignUpModal();
        updateAuthUI();
        alert('Account created successfully!');
    } catch (error) {
        alert('Sign up failed. Please try again.');
    }
}

/**
 * Sign out
 */
function signOut() {
    authState.user = null;
    authState.isSignedIn = false;
    localStorage.removeItem('geochallenge_user');
    hideMenu();
    updateAuthUI();
    alert('Signed out successfully!');
}

// ============================================
// Score Submission
// ============================================

// Submitted scores storage
function getSubmittedScores() {
    const saved = localStorage.getItem('geochallenge_submitted_scores');
    return saved ? JSON.parse(saved) : [];
}

function saveSubmittedScore(scoreEntry) {
    const scores = getSubmittedScores();
    scores.push(scoreEntry);
    // Keep only last 50 scores
    if (scores.length > 50) scores.shift();
    localStorage.setItem('geochallenge_submitted_scores', JSON.stringify(scores));
}

/**
 * Submit current score to database
 */
async function submitScore(openLeaderboard = false) {
    if (gameState.score === 0) {
        alert('Play some challenges first to build up your score!');
        return;
    }
    
    const scoreEntry = {
        username: authState.isSignedIn ? (authState.user.username || authState.user.email) : 'Guest',
        score: gameState.score,
        challenges: gameState.challengeNumber,
        date: new Date().toISOString(),
        isGuest: !authState.isSignedIn
    };
    
    // Save locally
    saveSubmittedScore(scoreEntry);
    
    // Update stats
    gameState.stats.totalScore += gameState.score;
    if (gameState.score > gameState.stats.bestScore) {
        gameState.stats.bestScore = gameState.score;
    }
    gameState.stats.totalGames++;
    saveStats();
    
    // Reset current game score after submission
    gameState.score = 0;
    gameState.challengeNumber = 0;
    gameState.currentChallenge = null;
    gameState.completedChallengeIds = [];
    gameState.justEnded = false;
    updateScoreDisplay();

    // Open leaderboard if requested
    if (openLeaderboard) {
        showLeaderboard();
    } else {
        alert(`Score submitted: ${gameState.score} points!\n(${gameState.challengeNumber} challenges completed)\n\nCheck 'My Stats' or 'Leaderboard' to see your scores.`);
    }

    updateCenterButtons();  // Show Start Game button again
}

/**
 * Show leaderboard modal
 */
async function showLeaderboard() {
    hideMenu();
    const scores = getSubmittedScores();
    const tbody = document.getElementById('leaderboard-body');
    if (scores.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="no-scores">No scores submitted yet. Play a game and submit your score!</td></tr>';
    } else {
        // Sort by score descending
        const sorted = [...scores].sort((a, b) => b.score - a.score);
        tbody.innerHTML = sorted.slice(0, 20).map((entry, idx) => {
            const date = new Date(entry.date).toLocaleDateString();
            const rankEmoji = idx === 0 ? '🥇' : idx === 1 ? '🥈' : idx === 2 ? '🥉' : `${idx + 1}`;
            // Use username if present, otherwise email prefix
            let playerName = entry.username || (entry.email ? entry.email.split('@')[0] : 'Player');
            return `<tr>
                <td>${rankEmoji}</td>
                <td>${playerName}${entry.isGuest ? ' (Guest)' : ''}</td>
                <td>${entry.score}</td>
                <td>${entry.challenges}</td>
                <td>${date}</td>
            </tr>`;
        }).join('');
    }
    document.getElementById('leaderboard-modal').classList.remove('hidden');
    document.getElementById('center-action').classList.add('hidden');
}

/**
 * Hide leaderboard modal
 */
function hideLeaderboard() {
    document.getElementById('leaderboard-modal').classList.add('hidden');
    updateCenterButtons();
}
