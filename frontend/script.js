const API_BASE = 'http://localhost:8000';

let currentPage = 1;
let currentFilters = {
    status: '',
    role_applied: '',
    skill: '',
    keyword: ''
};

// Fetch candidates with filters
async function fetchCandidates(page = 1) {
    const params = new URLSearchParams({
        limit: 20,
        offset: (page - 1) * 20,
        ...currentFilters
    });
    
    // Remove empty filters
    for (let [key, value] of params.entries()) {
        if (!value) params.delete(key);
    }
    
    try {
        const response = await fetch(`${API_BASE}/candidates?${params}`);
        const candidates = await response.json();
        displayCandidates(candidates);
        updatePagination(page, candidates.length);
        updateTotalCount();
    } catch (error) {
        console.error('Error fetching candidates:', error);
        document.getElementById('candidates-list').innerHTML = 
            '<div class="loading"><i class="fas fa-exclamation-circle"></i> Error loading candidates</div>';
    }
}

// Display candidates in grid
function displayCandidates(candidates) {
    const container = document.getElementById('candidates-list');
    
    if (!candidates.length) {
        container.innerHTML = '<div class="loading"><i class="fas fa-info-circle"></i> No candidates found</div>';
        return;
    }
    
    container.innerHTML = candidates.map(candidate => `
        <div class="candidate-card" onclick="showCandidateDetails(${candidate.id})">
            <div class="candidate-header">
                <div class="candidate-name">${escapeHtml(candidate.name)}</div>
                <div class="status-badge status-${candidate.status}">${candidate.status}</div>
            </div>
            <div class="candidate-role">
                <i class="fas fa-briefcase"></i> ${escapeHtml(candidate.role_applied)}
            </div>
            <div class="candidate-info">
                <span><i class="fas fa-map-marker-alt"></i> ${escapeHtml(candidate.location)}</span>
                <span><i class="fas fa-calendar"></i> ${candidate.experience_years} years</span>
            </div>
            <div class="candidate-skills">
                ${candidate.skills.slice(0, 3).map(skill => 
                    `<span class="skill-tag">${escapeHtml(skill)}</span>`
                ).join('')}
                ${candidate.skills.length > 3 ? `<span class="skill-tag">+${candidate.skills.length - 3}</span>` : ''}
            </div>
        </div>
    `).join('');
}

// Show candidate details modal
async function showCandidateDetails(candidateId) {
    try {
        const response = await fetch(`${API_BASE}/candidates/${candidateId}`);
        const candidate = await response.json();
        
        const modal = document.getElementById('candidate-modal');
        const modalBody = document.getElementById('modal-body');
        const modalTitle = document.getElementById('modal-title');
        
        modalTitle.textContent = candidate.name;
        
        modalBody.innerHTML = `
            <div class="candidate-details">
                <div class="info-section">
                    <h3><i class="fas fa-info-circle"></i> Basic Information</h3>
                    <p><strong>Email:</strong> ${escapeHtml(candidate.email)}</p>
                    <p><strong>Role Applied:</strong> ${escapeHtml(candidate.role_applied)}</p>
                    <p><strong>Status:</strong> <span class="status-badge status-${candidate.status}">${candidate.status}</span></p>
                    <p><strong>Experience:</strong> ${candidate.experience_years} years</p>
                    <p><strong>Location:</strong> ${escapeHtml(candidate.location)}</p>
                    <p><strong>Skills:</strong> ${candidate.skills.map(s => `<span class="skill-tag">${escapeHtml(s)}</span>`).join('')}</p>
                </div>
                
                ${candidate.ai_summary ? `
                <div class="ai-summary">
                    <h4><i class="fas fa-robot"></i> AI Summary</h4>
                    <div class="summary-text">${escapeHtml(candidate.ai_summary)}</div>
                    <button onclick="regenerateAISummary(${candidate.id})" class="btn-secondary" style="margin-top: 0.5rem;">
                        <i class="fas fa-sync-alt"></i> Regenerate Summary
                    </button>
                </div>
                ` : `
                <div class="ai-summary">
                    <h4><i class="fas fa-robot"></i> AI Summary</h4>
                    <div class="summary-text">No AI summary available.</div>
                    <button onclick="generateAISummary(${candidate.id})" class="btn-primary" style="margin-top: 0.5rem;">
                        <i class="fas fa-magic"></i> Generate AI Summary
                    </button>
                </div>
                `}
                
                <div class="score-section">
                    <h3><i class="fas fa-star"></i> Scores</h3>
                    ${candidate.scores.length ? candidate.scores.map(score => `
                        <div class="score-card">
                            <div class="score-header">
                                <span class="score-category">${escapeHtml(score.category)}</span>
                                <span class="score-value">${score.score}/5</span>
                            </div>
                            ${score.note ? `<div class="score-note">${escapeHtml(score.note)}</div>` : ''}
                            <small>Submitted by ${escapeHtml(score.submitted_by)} on ${new Date(score.submitted_at).toLocaleDateString()}</small>
                        </div>
                    `).join('') : '<p>No scores yet.</p>'}
                    
                    <div class="add-score-form">
                        <h4>Add New Score</h4>
                        <div class="form-group">
                            <label>Category</label>
                            <select id="score-category">
                                <option value="technical">Technical</option>
                                <option value="communication">Communication</option>
                                <option value="problem_solving">Problem Solving</option>
                                <option value="leadership">Leadership</option>
                                <option value="culture_fit">Culture Fit</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Score (1-5)</label>
                            <input type="number" id="score-value" min="1" max="5">
                        </div>
                        <div class="form-group">
                            <label>Note (optional)</label>
                            <textarea id="score-note" rows="2"></textarea>
                        </div>
                        <button onclick="submitScore(${candidate.id})" class="btn-primary">
                            <i class="fas fa-paper-plane"></i> Submit Score
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        modal.style.display = 'block';
        
        // Close modal functionality
        const closeBtn = modal.querySelector('.close');
        closeBtn.onclick = () => modal.style.display = 'none';
        window.onclick = (event) => {
            if (event.target === modal) modal.style.display = 'none';
        };
        
    } catch (error) {
        console.error('Error fetching candidate details:', error);
        alert('Error loading candidate details');
    }
}

// Submit score
async function submitScore(candidateId) {
    const category = document.getElementById('score-category').value;
    const score = parseInt(document.getElementById('score-value').value);
    const note = document.getElementById('score-note').value;
    
    if (!score || score < 1 || score > 5) {
        alert('Please enter a valid score between 1 and 5');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/candidates/${candidateId}/scores`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ category, score, note })
        });
        
        if (response.ok) {
            alert('Score submitted successfully!');
            showCandidateDetails(candidateId); // Refresh modal
            fetchCandidates(currentPage); // Refresh list
        } else {
            alert('Error submitting score');
        }
    } catch (error) {
        console.error('Error submitting score:', error);
        alert('Error submitting score');
    }
}

// Generate AI summary
async function generateAISummary(candidateId) {
    try {
        const response = await fetch(`${API_BASE}/candidates/${candidateId}/generate-summary`, {
            method: 'POST'
        });
        
        if (response.ok) {
            alert('AI summary generation started. Please wait a moment and refresh the candidate details.');
            setTimeout(() => showCandidateDetails(candidateId), 2000);
        } else {
            alert('Error generating AI summary');
        }
    } catch (error) {
        console.error('Error generating AI summary:', error);
        alert('Error generating AI summary');
    }
}

// Regenerate AI summary
async function regenerateAISummary(candidateId) {
    await generateAISummary(candidateId);
}

// Update total candidates count
async function updateTotalCount() {
    try {
        const response = await fetch(`${API_BASE}/candidates`);
        const candidates = await response.json();
        document.getElementById('total-candidates').textContent = candidates.length;
    } catch (error) {
        console.error('Error fetching total count:', error);
    }
}

// Update pagination controls
function updatePagination(page, resultsCount) {
    const prevBtn = document.getElementById('prev-page');
    const nextBtn = document.getElementById('next-page');
    const pageInfo = document.getElementById('page-info');
    
    prevBtn.disabled = page === 1;
    nextBtn.disabled = resultsCount < 20;
    pageInfo.textContent = `Page ${page}`;
}

// Apply filters
function applyFilters() {
    currentFilters = {
        status: document.getElementById('filter-status').value,
        role_applied: document.getElementById('filter-role').value,
        skill: document.getElementById('filter-skill').value,
        keyword: document.getElementById('filter-keyword').value
    };
    currentPage = 1;
    fetchCandidates(currentPage);
}

// Reset filters
function resetFilters() {
    document.getElementById('filter-status').value = '';
    document.getElementById('filter-role').value = '';
    document.getElementById('filter-skill').value = '';
    document.getElementById('filter-keyword').value = '';
    currentFilters = { status: '', role_applied: '', skill: '', keyword: '' };
    currentPage = 1;
    fetchCandidates(currentPage);
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Event listeners
document.getElementById('apply-filters').addEventListener('click', applyFilters);
document.getElementById('reset-filters').addEventListener('click', resetFilters);
document.getElementById('prev-page').addEventListener('click', () => {
    if (currentPage > 1) {
        currentPage--;
        fetchCandidates(currentPage);
    }
});
document.getElementById('next-page').addEventListener('click', () => {
    currentPage++;
    fetchCandidates(currentPage);
});

// Initial load
fetchCandidates();

// Add enter key support for filters
['filter-role', 'filter-skill', 'filter-keyword'].forEach(id => {
    document.getElementById(id).addEventListener('keypress', (e) => {
        if (e.key === 'Enter') applyFilters();
    });
});