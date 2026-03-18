/**
 * GeoChallenge Version Information
 * Update this file on each release/merge
 */
const APP_VERSION = 'v1.00';
const APP_COMMIT = '2a1bbb7';

// Update version display on page load
document.addEventListener('DOMContentLoaded', () => {
    const versionEl = document.getElementById('app-version');
    const commitEl = document.getElementById('app-commit');
    
    if (versionEl) versionEl.textContent = APP_VERSION;
    if (commitEl) commitEl.textContent = APP_COMMIT;
});
