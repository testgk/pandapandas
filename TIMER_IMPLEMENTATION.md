# Challenge Timer Implementation

## Overview

A challenge timer infrastructure has been implemented to add time-based gameplay to GeoChallenge. Players have a configurable time limit to guess the location of a challenge before the time expires.

## Features

### 1. **Default Timer Duration**
- **Default Time Limit**: 15 seconds per challenge
- **Configurable**: Can be adjusted via `gameState.timer.duration`

### 2. **Timer Display**
- Shows remaining time in the challenge header (top-right of the challenge panel)
- Format: `⏱ Xs` (e.g., `⏱ 15s`)
- Three visual states:
  - **Normal** (> 7s): Blue text `#60a5fa`
  - **Warning** (3-7s): Orange text `#f59e0b`
  - **Critical** (≤ 3s): Red text with pulsing animation `#ef4444`

### 3. **Automatic Timer Start**
- Timer automatically starts when a challenge is loaded
- Starts in the `nextChallenge()` function after the challenge is displayed

### 4. **Time Expiration Handling**
- When time expires (elapsedTime ≥ duration):
  - Timer automatically stops
  - Auto-submits a random guess on the globe as a "timeout"
  - Displays "Time expired! Submitting random guess..." message
  - Calculates score normally based on the random guess location

### 5. **Timer Tracking**
- Captures elapsed time for each guess
- Accessible via `getElapsedTime()` function
- Returns time rounded to 1 decimal place

## Technical Architecture

### Game State Timer Object

```javascript
gameState.timer = {
    duration: 15,           // Time limit in seconds
    elapsedTime: 0,         // Current elapsed time
    intervalId: null,       // Timer interval ID
    isRunning: false,       // Timer status
    startTime: null         // Timestamp when started
}
```

### Core Timer Functions

#### `startTimer()`
- Initializes and starts the countdown timer
- Clears any existing timer first
- Updates display every 100ms for smooth animation
- Calls `handleTimeExpired()` when time runs out

```javascript
function startTimer() {
    stopTimer();  // Clear existing timer
    gameState.timer.isRunning = true;
    gameState.timer.elapsedTime = 0;
    gameState.timer.startTime = Date.now();
    
    updateTimerDisplay();
    gameState.timer.intervalId = setInterval(() => {
        // Update every 100ms
        const elapsed = (Date.now() - gameState.timer.startTime) / 1000;
        gameState.timer.elapsedTime = Math.min(elapsed, gameState.timer.duration);
        updateTimerDisplay();
        
        if (gameState.timer.elapsedTime >= gameState.timer.duration) {
            stopTimer();
            handleTimeExpired();
        }
    }, 100);
}
```

#### `stopTimer()`
- Stops the running timer
- Clears the interval
- Safely stops timer if one is running

```javascript
function stopTimer() {
    if (gameState.timer.intervalId) {
        clearInterval(gameState.timer.intervalId);
        gameState.timer.intervalId = null;
    }
    gameState.timer.isRunning = false;
}
```

#### `updateTimerDisplay()`
- Updates the timer text in the UI
- Applies color classes based on remaining time
- Updates text: `⏱ Xs`

```javascript
function updateTimerDisplay() {
    const timerText = document.getElementById('timer-text');
    const remaining = Math.max(0, gameState.timer.duration - gameState.timer.elapsedTime);
    const seconds = Math.ceil(remaining);
    
    timerText.textContent = `⏱ ${seconds}s`;
    
    timerText.classList.remove('timer-warning', 'timer-critical');
    if (remaining <= 3) {
        timerText.classList.add('timer-critical');  // Red + pulse
    } else if (remaining <= 7) {
        timerText.classList.add('timer-warning');   // Orange
    }
}
```

#### `handleTimeExpired()`
- Automatically submits a random guess when time expires
- Generates random coordinates on the globe
- Calls `handleGlobeClick()` to process the guess

```javascript
function handleTimeExpired() {
    if (!gameState.currentChallenge || gameState.guessSubmitted) {
        return;  // Already submitted
    }
    
    gameState.guessSubmitted = true;
    showLoading('Time expired! Submitting random guess...');
    
    const randomLat = Math.random() * 180 - 90;
    const randomLng = Math.random() * 360 - 180;
    
    setTimeout(() => {
        handleGlobeClick({ lat: randomLat, lng: randomLng });
    }, 500);
}
```

#### `getElapsedTime()`
- Returns the elapsed time for the current challenge
- Rounded to 1 decimal place
- Useful for logging or display

```javascript
function getElapsedTime() {
    return Math.round(gameState.timer.elapsedTime * 10) / 10;
}
```

## Timer Lifecycle

### When Challenge Loads
1. `nextChallenge()` fetches challenge
2. Challenge UI updates with location, difficulty, hints
3. **`startTimer()` called** → Timer begins countdown

### During Gameplay
- Timer counts down from `duration` to 0
- Display updates every 100ms
- Color changes at 7s and 3s thresholds
- User can click globe to submit guess anytime

### On Guess Submission
1. User clicks globe
2. **`stopTimer()` called** in `handleGlobeClick()`
3. Guess is processed and scored
4. Result displayed

### On Time Expiration
1. Timer reaches 0
2. **`stopTimer()` called**
3. **`handleTimeExpired()` called**
4. Random guess auto-submitted
5. Scoring processed normally
6. Result displayed

### On Game End
1. **`stopTimer()` called** in `endGame()`
2. Challenge panel hidden
3. Game state reset

## HTML Structure

The timer display is embedded in the challenge header:

```html
<div id="challenge-header">
    <span id="difficulty-badge" class="badge easy">Easy</span>
    <span id="challenge-number">Challenge 1</span>
    <div id="timer-display" class="timer-display">
        <span id="timer-text">⏱ 15s</span>
    </div>
</div>
```

## CSS Styling

### Normal State
```css
#timer-text {
    font-size: 0.95rem;
    font-weight: 600;
    color: #60a5fa;  /* Blue */
    font-family: 'Courier New', monospace;
    white-space: nowrap;
}
```

### Warning State (3-7 seconds)
```css
#timer-text.timer-warning {
    color: #f59e0b;  /* Orange */
}
```

### Critical State (≤ 3 seconds)
```css
#timer-text.timer-critical {
    color: #ef4444;  /* Red */
    animation: timer-pulse 0.6s ease-in-out infinite;
}

@keyframes timer-pulse {
    0%, 100% {
        opacity: 1;
        transform: scale(1);
    }
    50% {
        opacity: 0.7;
        transform: scale(1.05);
    }
}
```

## Configuration

### Change Default Duration

To change the default 15-second timer:

```javascript
// In gameState initialization
gameState.timer.duration = 30;  // 30 seconds
```

### Time Ranges

- **Normal display**: `remaining > 7 seconds`
- **Warning color**: `3 <= remaining <= 7 seconds`
- **Critical color + pulse**: `remaining < 3 seconds`

These thresholds can be adjusted in `updateTimerDisplay()`:

```javascript
if (remaining <= 3) {
    timerText.classList.add('timer-critical');
} else if (remaining <= 7) {
    timerText.classList.add('timer-warning');
}
```

## Integration Points

### Called From:
- `nextChallenge()` - Starts timer when challenge loads
- `handleGlobeClick()` - Stops timer when guess submitted
- `endGame()` - Stops timer when game ends
- `handleTimeExpired()` - Auto-submits on timeout

### Updates:
- `gameState.timer` object
- `#timer-text` element
- Challenge result panel with elapsed time

## Future Enhancements

Potential improvements to the timer system:

1. **Difficulty-based durations**: Different time limits per difficulty
   ```javascript
   const timeLimits = {
       'easy': 20,
       'medium': 15,
       'hard': 10,
       'expert': 5
   };
   gameState.timer.duration = timeLimits[difficulty];
   ```

2. **Bonus time for hints**: Reduce time penalty for hint usage
   ```javascript
   gameState.timer.duration -= gameState.hintIndex * 2;  // -2s per hint used
   ```

3. **Time-attack game mode**: Score multiplier based on speed
   ```javascript
   const speedBonus = 1 + (gameState.timer.duration - getElapsedTime()) / gameState.timer.duration * 0.5;
   finalScore = Math.floor(finalScore * speedBonus);
   ```

4. **Leaderboard integration**: Track average response times
   - Store `response_time_seconds` with each score
   - Display in leaderboard
   - Calculate speed statistics

5. **Pause functionality**: Allow pause/resume during gameplay
   ```javascript
   function pauseTimer() {
       stopTimer();
       gameState.timer.isPaused = true;
   }
   ```

6. **Sound effects**: Audio cues at thresholds
   - Warning beep at 5 seconds
   - Critical sound at 3 seconds
   - Time up sound

## Performance Considerations

- Timer interval set to 100ms (10 updates/second) for smooth display
- Uses `Date.now()` for accurate elapsed time calculation
- Properly cleans up intervals to prevent memory leaks
- Timer stops immediately on guess/game end to save resources

## Testing

### Manual Testing Checklist

- [ ] Timer starts when challenge loads
- [ ] Timer counts down correctly
- [ ] Display updates smoothly every 100ms
- [ ] Color changes at 7s threshold (orange)
- [ ] Color changes at 3s threshold (red + pulse)
- [ ] Timer stops when user clicks guess
- [ ] Timer stops when time expires
- [ ] Random guess submitted on timeout
- [ ] Score calculated correctly for timed-out guess
- [ ] Timer shows correct elapsed time
- [ ] Timer clears properly between challenges
- [ ] Multiple challenges don't have stacking timers

### Quick Test (15 seconds)
1. Click "Start Game"
2. Watch timer count from 15s to 0s
3. Observe color/animation changes
4. Let it expire and verify random guess auto-submits

## Browser Compatibility

Timer uses standard JavaScript APIs:
- `Date.now()` - All modern browsers
- `setInterval()` - All modern browsers
- `clearInterval()` - All modern browsers
- CSS animations - All modern browsers

Tested and working on:
- Chrome/Edge (Chromium)
- Firefox
- Safari
- Mobile browsers

