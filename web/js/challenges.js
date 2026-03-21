/**
 * GeoChallenge - API Client
 * All game logic is handled by the backend API.
 */

const API_BASE = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? 'http://localhost:8000/api'
    : 'https://geochallenge-api.onrender.com/api';

/**
 * Fetch challenges from the backend API.
 */
async function fetchChallenges(difficulty = null) {
    const url = difficulty && difficulty !== 'random' 
        ? `${API_BASE}/challenges/?difficulty=${difficulty.toLowerCase()}`
        : `${API_BASE}/challenges/`;
    
    const response = await fetch(url);
    if (!response.ok) throw new Error('Failed to fetch challenges');
    
    const data = await response.json();
    return data.challenges;
}

/**
 * Get a random challenge from the backend API.
 */
async function getRandomChallenge(difficulty = null, excludeIds = []) {
    let url = `${API_BASE}/challenges/random`;
    const params = new URLSearchParams();
    
    if (difficulty && difficulty.toLowerCase() !== 'random') {
        params.append('difficulty', difficulty.toLowerCase());
    }
    if (excludeIds.length > 0) {
        params.append('exclude', excludeIds.join(','));
    }
    
    if (params.toString()) {
        url += '?' + params.toString();
    }
    
    const response = await fetch(url);
    if (!response.ok) throw new Error('Failed to get random challenge');
    
    return await response.json();
}

/**
 * Submit a guess to the backend API and get the result.
 */
async function submitGuess(challengeId, guessedLat, guessedLng) {
    const response = await fetch(`${API_BASE}/challenges/guess`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            challenge_id: challengeId,
            guessed_lat: guessedLat,
            guessed_lng: guessedLng
        })
    });
    
    if (!response.ok) throw new Error('Failed to submit guess');
    
    return await response.json();
}

/**
 * Fetch scoring zones for a challenge (for drawing rings).
 */
async function getScoringZones(challengeId) {
    const response = await fetch(`${API_BASE}/challenges/${challengeId}/scoring-zones`);
    if (!response.ok) throw new Error('Failed to get scoring zones');
    return await response.json();
}

/**
 * Fetch global scoring zone boundaries (single source of truth).
 * Zone fractions are the same for all challenges.
 */
async function getGlobalScoringZones() {
    const response = await fetch(`${API_BASE}/scoring/zones`);
    if (!response.ok) throw new Error('Failed to get scoring zones');
    return await response.json();
}

/**
 * Fetch country boundary GeoJSON for displaying borders on the globe.
 */
async function getCountryBoundary(countryName) {
    try {
        const response = await fetch(`${API_BASE}/boundaries/country/${encodeURIComponent(countryName)}`);
        if (!response.ok) return null;
        return await response.json();
    } catch (error) {
        console.warn('Failed to fetch country boundary:', error);
        return null;
    }
}

// Legacy compatibility - these now call the API
const CHALLENGES = [];

function getChallengesByDifficulty(difficulty) {
    // This is now async - use fetchChallenges instead
    console.warn('getChallengesByDifficulty is deprecated. Use fetchChallenges() instead.');
    return [];
}
