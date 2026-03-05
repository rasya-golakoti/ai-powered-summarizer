// DOM Elements
const uploadForm = document.getElementById('uploadForm');
const submitBtn = document.getElementById('submitBtn');
const clearBtn = document.getElementById('clearBtn');
const resultsContentDiv = document.getElementById('resultsContent');
const loadingDiv = document.getElementById('loading');
const metricsDisplay = document.getElementById('metricsDisplay');
const summaryText = document.getElementById('summaryText');
const emotionDisplay = document.getElementById('emotionDisplay');
const keywordsDisplay = document.getElementById('keywordsDisplay');
const highlightsDisplay = document.getElementById('highlightsDisplay');
const tasksDisplay = document.getElementById('tasksDisplay');
const chaptersDisplay = document.getElementById('chaptersDisplay');
const speakerSummaryText = document.getElementById('speakerSummaryText');
const timelineDisplay = document.getElementById('timelineDisplay');
const exportPdfBtn = document.getElementById('exportPdfBtn');
const exportCsvBtn = document.getElementById('exportCsvBtn');
const exportTxtBtn = document.getElementById('exportTxtBtn');

// Global variable to store current results
let currentResults = null;
let currentResultId = null;

// Format metrics for display
function formatMetrics(metrics) {
    const formatted = {};
    
    if (metrics['ROUGE-L'] !== undefined) {
        formatted['ROUGE-L'] = (metrics['ROUGE-L'] * 100).toFixed(1) + '%';
    }
    if (metrics['BLEU'] !== undefined) {
        formatted['BLEU'] = (metrics['BLEU'] * 100).toFixed(1) + '%';
    }
    if (metrics['BERT-F1'] !== undefined) {
        formatted['BERT-F1'] = (metrics['BERT-F1'] * 100).toFixed(1) + '%';
    }
    if (metrics['Compression'] !== undefined) {
        formatted['Compression'] = (metrics['Compression'] * 100).toFixed(1) + '%';
    }
    
    return formatted;
}

// Display comprehensive metrics
function displayComprehensiveMetrics(metrics) {
    if (!metricsDisplay) return;
    
    metricsDisplay.innerHTML = '';
    
    const metricConfig = {
        'ROUGE-L': { label: 'ROUGE-L Score', lowerBetter: false },
        'BLEU': { label: 'BLEU Score', lowerBetter: false },
        'BERT-F1': { label: 'BERTScore F1', lowerBetter: false },
        'Compression': { label: 'Compression Ratio', lowerBetter: true }
    };
    
    for (const [key, config] of Object.entries(metricConfig)) {
        if (metrics[key] !== undefined) {
            const value = metrics[key].replace('%', '');
            const numValue = parseFloat(value);
            
            let colorClass = 'metric-box';
            if (config.lowerBetter) {
                colorClass += numValue < 30 ? ' success' : numValue < 60 ? ' warning' : ' error';
            } else {
                colorClass += numValue > 70 ? ' success' : numValue > 50 ? ' warning' : ' error';
            }
            
            const metricBox = document.createElement('div');
            metricBox.className = colorClass;
            metricBox.innerHTML = `${value}%<span>${config.label}</span>`;
            metricsDisplay.appendChild(metricBox);
        }
    }
}

// Display results
function displayResults(data) {
    if (!resultsContentDiv || !loadingDiv) return;
    
    resultsContentDiv.style.display = 'block';
    loadingDiv.style.display = 'none';
    
    // Store results for export
    currentResults = data.results;
    currentResultId = data.result_id;
    
    // Display statistics if available
    if (data.stats) {
        console.log('Stats:', data.stats);
        // You could display stats in a separate div if you want
    }
    
    // Update all display elements
    safeSetText(summaryText, data.results?.summary || 'No summary generated');
    safeSetText(emotionDisplay, data.results?.emotion || 'Emotion not detected');
    safeSetText(keywordsDisplay, data.results?.keywords || 'No keywords detected');
    safeSetText(highlightsDisplay, data.results?.highlights || 'No highlights detected');
    safeSetText(tasksDisplay, data.results?.tasks || 'No tasks identified');
    safeSetText(chaptersDisplay, data.results?.chapters || 'No chapters generated');
    safeSetText(speakerSummaryText, data.results?.speaker_summary || 'No speaker summaries available');
    safeSetText(timelineDisplay, data.results?.timeline || 'No timeline generated');
    
    // Display metrics
    if (data.results?.metrics) {
        const formattedMetrics = formatMetrics(data.results.metrics);
        displayComprehensiveMetrics(formattedMetrics);
    } else {
        safeSetText(metricsDisplay, 'Metrics not available');
    }
    
    // Enable CSV export if speaker analysis is available
    if (exportCsvBtn) {
        exportCsvBtn.disabled = !(data.results?.speaker_summary && 
                                  data.results.speaker_summary !== 'No speaker summaries available');
    }
}

// Helper function to safely set text content
function safeSetText(element, text) {
    if (element) {
        element.textContent = text;
    } else {
        console.warn('Element not found for text:', text.substring(0, 50));
    }
}

// Form submission handler
uploadForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const urlInput = document.querySelector('input[name="url"]');
    const fileInput = document.querySelector('input[name="file"]');
    
    if (!urlInput || !fileInput) {
        alert('Form inputs not found');
        return;
    }
    
    const url = urlInput.value;
    const file = fileInput.files[0];
    
    if (!url && !file) {
        alert('Please provide a file or a valid URL.');
        return;
    }
    
    if (url && !url.match(/^https?:\/\//)) {
        alert('Invalid URL. Must start with http:// or https://');
        return;
    }
    
    // Show loading animation
    if (loadingDiv) loadingDiv.style.display = 'block';
    if (resultsContentDiv) resultsContentDiv.style.display = 'none';
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Processing...';
    }
    
    try {
        const formData = new FormData(uploadForm);
        
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Run Full Pipeline';
        }
        
        if (data.error) {
            if (loadingDiv) loadingDiv.style.display = 'none';
            alert('Error: ' + data.error);
        } else {
            displayResults(data);
        }
    } catch (error) {
        if (loadingDiv) loadingDiv.style.display = 'none';
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Run Full Pipeline';
        }
        alert('Error processing request: ' + error.message);
    }
});

// Clear form and results
clearBtn.addEventListener('click', function() {
    uploadForm.reset();
    if (resultsContentDiv) resultsContentDiv.style.display = 'none';
    if (loadingDiv) loadingDiv.style.display = 'none';
    
    // Clear all displays
    const displays = [
        metricsDisplay, summaryText, emotionDisplay, keywordsDisplay,
        highlightsDisplay, tasksDisplay, chaptersDisplay, 
        speakerSummaryText, timelineDisplay
    ];
    
    displays.forEach(el => {
        if (el) el.innerHTML = '';
    });
    
    if (exportCsvBtn) exportCsvBtn.disabled = true;
    currentResults = null;
    currentResultId = null;
});

// Export text file
exportTxtBtn.addEventListener('click', async function() {
    if (!currentResultId) {
        alert('No results to export. Please run an analysis first.');
        return;
    }
    
    try {
        const response = await fetch(`/export/${currentResultId}/txt`);
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `analysis_${Date.now()}.txt`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } else {
            const error = await response.json();
            alert('Export failed: ' + (error.error || 'Unknown error'));
        }
    } catch (error) {
        alert('Export failed: ' + error.message);
    }
});

// Export CSV (speaker diarization)
exportCsvBtn.addEventListener('click', async function() {
    if (!currentResultId) {
        alert('No results to export. Please run an analysis first.');
        return;
    }
    
    if (exportCsvBtn.disabled) {
        alert('CSV export is only available when speaker analysis is enabled and speakers are detected.');
        return;
    }
    
    try {
        const response = await fetch(`/export/${currentResultId}/csv`);
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `speakers_${Date.now()}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } else {
            const error = await response.json();
            alert('Export failed: ' + (error.error || 'Unknown error'));
        }
    } catch (error) {
        alert('Export failed: ' + error.message);
    }
});

// Export PDF (placeholder)
exportPdfBtn.addEventListener('click', function() {
    alert('PDF export feature is coming soon! Currently in development.');
});

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎙️ AI Audio Summarizer Web Interface loaded');
    
    // Check if all required elements exist
    const requiredElements = {
        uploadForm, submitBtn, clearBtn, resultsContentDiv, loadingDiv,
        metricsDisplay, summaryText, emotionDisplay, keywordsDisplay,
        highlightsDisplay, tasksDisplay, chaptersDisplay, 
        speakerSummaryText, timelineDisplay
    };
    
    const missing = Object.entries(requiredElements)
        .filter(([name, el]) => !el)
        .map(([name]) => name);
    
    if (missing.length > 0) {
        console.warn('Missing elements:', missing);
    } else {
        console.log('✅ All required elements found');
    }
});