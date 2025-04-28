/**
 * validation.js - Handles client-side validation and AI processing feedback
 */
document.addEventListener('DOMContentLoaded', function() {
    // Document upload and AI validation process
    const documentForm = document.getElementById('documentUploadForm');
    const aiValidationStatus = document.getElementById('aiValidationStatus');
    
    if (documentForm && aiValidationStatus) {
        documentForm.addEventListener('submit', function(event) {
            // Show validation in progress status
            aiValidationStatus.innerHTML = `
                <div class="alert alert-info">
                    <div class="d-flex align-items-center">
                        <div class="spinner-border spinner-border-sm me-2" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <div>
                            <strong>AI Validation in Progress</strong><br>
                            <small>Please wait while we validate your document...</small>
                        </div>
                    </div>
                </div>
            `;
            
            // The actual validation happens on the server
            // This is just for UI feedback while the form is submitted
        });
    }
    
    // Social media profile analysis
    const analyzeButtons = document.querySelectorAll('.analyze-social-button');
    
    analyzeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const socialId = this.getAttribute('data-social-id');
            const platform = this.getAttribute('data-platform');
            const resultContainer = document.getElementById(`analysis-result-${socialId}`);
            
            if (!resultContainer) return;
            
            // Show loading state
            resultContainer.innerHTML = `
                <div class="d-flex align-items-center mt-2">
                    <div class="spinner-border spinner-border-sm me-2" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <div>Analyzing ${platform} profile...</div>
                </div>
            `;
            
            // Fetch analysis from server
            fetch(`/social/analyze/${platform}/${socialId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Display analysis results
                displaySocialAnalysis(data, resultContainer, platform);
            })
            .catch(error => {
                resultContainer.innerHTML = `
                    <div class="alert alert-danger mt-2">
                        <strong>Error:</strong> Failed to analyze profile. ${error.message}
                    </div>
                `;
            });
        });
    });
    
    // Esports profile validation feedback
    const esportsValidationResults = document.querySelectorAll('.esports-validation-result');
    
    esportsValidationResults.forEach(resultElement => {
        const relevanceScore = parseFloat(resultElement.getAttribute('data-relevance-score'));
        const fillElement = resultElement.querySelector('.relevance-score-fill');
        
        if (fillElement) {
            fillElement.style.width = `${relevanceScore * 100}%`;
            
            // Set color based on score
            if (relevanceScore >= 0.7) {
                fillElement.classList.add('bg-success');
            } else if (relevanceScore >= 0.4) {
                fillElement.classList.add('bg-warning');
            } else {
                fillElement.classList.add('bg-danger');
            }
        }
    });
});

// Helper function to display social media analysis
function displaySocialAnalysis(data, container, platform) {
    // Check for error
    if (data.error) {
        container.innerHTML = `
            <div class="alert alert-danger mt-2">
                <strong>Error:</strong> ${data.error}
            </div>
        `;
        return;
    }
    
    // Format esports teams
    const teams = Array.isArray(data.teams) ? data.teams : [];
    const teamsHtml = teams.length > 0 
        ? teams.map(team => `<span class="badge bg-secondary me-1">${team}</span>`).join(' ')
        : '<em>None detected</em>';
    
    // Format games
    const games = Array.isArray(data.games) ? data.games : [];
    const gamesHtml = games.length > 0
        ? games.map(game => `<span class="badge bg-secondary me-1">${game}</span>`).join(' ')
        : '<em>None detected</em>';
    
    // Set engagement score color
    let scoreClass = 'text-danger';
    if (data.esports_engagement_score >= 0.7) {
        scoreClass = 'text-success';
    } else if (data.esports_engagement_score >= 0.4) {
        scoreClass = 'text-warning';
    }
    
    // Build result HTML
    container.innerHTML = `
        <div class="card mt-3">
            <div class="card-header">
                <h5 class="mb-0">
                    <i class="fas fa-chart-line me-2"></i>
                    ${platform.charAt(0).toUpperCase() + platform.slice(1)} Analysis Results
                </h5>
            </div>
            <div class="card-body">
                <div class="mb-3">
                    <strong>Esports Engagement Score:</strong>
                    <span class="${scoreClass} fw-bold">${(data.esports_engagement_score * 100).toFixed(0)}%</span>
                    <div class="progress mt-1" style="height: 10px;">
                        <div class="progress-bar ${data.esports_engagement_score >= 0.7 ? 'bg-success' : data.esports_engagement_score >= 0.4 ? 'bg-warning' : 'bg-danger'}" 
                             role="progressbar" 
                             style="width: ${data.esports_engagement_score * 100}%" 
                             aria-valuenow="${data.esports_engagement_score * 100}" 
                             aria-valuemin="0" 
                             aria-valuemax="100"></div>
                    </div>
                </div>
                
                <div class="mb-3">
                    <strong>Esports Teams/Organizations:</strong>
                    <div class="mt-1">${teamsHtml}</div>
                </div>
                
                <div class="mb-3">
                    <strong>Games of Interest:</strong>
                    <div class="mt-1">${gamesHtml}</div>
                </div>
                
                <div>
                    <strong>Fan Authenticity Assessment:</strong>
                    <p>${data.authenticity_assessment || 'No assessment available.'}</p>
                </div>
            </div>
        </div>
    `;
}

// Helper function to get CSRF token
function getCsrfToken() {
    const csrfInput = document.querySelector('input[name="csrf_token"]');
    return csrfInput ? csrfInput.value : '';
}
