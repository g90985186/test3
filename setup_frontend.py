#!/usr/bin/env python3
"""
CVE Analysis Platform - Frontend Setup
This script creates the frontend HTML, CSS, and JavaScript files.
"""

from pathlib import Path

def create_file(filepath, content):
    """Create a file with the given content"""
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Created: {filepath}")

def setup_frontend_files():
    """Create frontend files"""
    
    print("🎨 Setting up Frontend Files")
    print("=" * 30)
    
    files = {
        
        # Main HTML file
        "app/static/frontend/index.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CVE Analysis Platform</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link rel="stylesheet" href="styles.css">
</head>
<body class="bg-gray-100 min-h-screen">
    <!-- Navigation -->
    <nav class="bg-blue-800 text-white shadow-lg">
        <div class="max-w-7xl mx-auto px-4">
            <div class="flex justify-between h-16">
                <div class="flex items-center">
                    <i class="fas fa-shield-alt text-2xl mr-3"></i>
                    <h1 class="text-xl font-bold">CVE Analysis Platform</h1>
                </div>
                <div class="flex items-center space-x-4">
                    <button onclick="showDashboard()" class="nav-btn px-3 py-2 rounded-md text-sm font-medium hover:bg-blue-700">
                        <i class="fas fa-chart-line mr-2"></i>Dashboard
                    </button>
                    <button onclick="showCVESearch()" class="nav-btn px-3 py-2 rounded-md text-sm font-medium hover:bg-blue-700">
                        <i class="fas fa-search mr-2"></i>CVE Search
                    </button>
                    <button onclick="showAnalysis()" class="nav-btn px-3 py-2 rounded-md text-sm font-medium hover:bg-blue-700">
                        <i class="fas fa-brain mr-2"></i>AI Analysis
                    </button>
                </div>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto px-4 py-8">
        <!-- Dashboard Section -->
        <div id="dashboard-section" class="section">
            <div class="mb-8">
                <h2 class="text-3xl font-bold text-gray-900 mb-4">Security Dashboard</h2>
                <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    <div class="bg-white rounded-lg shadow p-6">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <i class="fas fa-exclamation-triangle text-red-500 text-2xl"></i>
                            </div>
                            <div class="ml-4">
                                <p class="text-sm font-medium text-gray-500">Critical CVEs</p>
                                <p class="text-2xl font-semibold text-gray-900" id="critical-count">-</p>
                            </div>
                        </div>
                    </div>
                    <div class="bg-white rounded-lg shadow p-6">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <i class="fas fa-chart-line text-blue-500 text-2xl"></i>
                            </div>
                            <div class="ml-4">
                                <p class="text-sm font-medium text-gray-500">Total CVEs</p>
                                <p class="text-2xl font-semibold text-gray-900" id="total-count">-</p>
                            </div>
                        </div>
                    </div>
                    <div class="bg-white rounded-lg shadow p-6">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <i class="fas fa-robot text-green-500 text-2xl"></i>
                            </div>
                            <div class="ml-4">
                                <p class="text-sm font-medium text-gray-500">AI Analyses</p>
                                <p class="text-2xl font-semibold text-gray-900" id="analysis-count">-</p>
                            </div>
                        </div>
                    </div>
                    <div class="bg-white rounded-lg shadow p-6">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <i class="fas fa-clock text-yellow-500 text-2xl"></i>
                            </div>
                            <div class="ml-4">
                                <p class="text-sm font-medium text-gray-500">Recent CVEs</p>
                                <p class="text-2xl font-semibold text-gray-900" id="recent-count">-</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Recent CVEs Table -->
                <div class="bg-white rounded-lg shadow">
                    <div class="px-6 py-4 border-b">
                        <h3 class="text-lg font-medium text-gray-900">Recent CVEs</h3>
                    </div>
                    <div class="overflow-x-auto">
                        <table class="min-w-full divide-y divide-gray-200">
                            <thead class="bg-gray-50">
                                <tr>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">CVE ID</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Severity</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">CVSS Score</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Published</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                                </tr>
                            </thead>
                            <tbody id="recent-cves-table" class="bg-white divide-y divide-gray-200">
                                <!-- Dynamic content -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <!-- CVE Search Section -->
        <div id="cve-search-section" class="section hidden">
            <div class="mb-8">
                <h2 class="text-3xl font-bold text-gray-900 mb-4">CVE Search</h2>
                
                <!-- Search Form -->
                <div class="bg-white rounded-lg shadow p-6 mb-6">
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Search CVEs</label>
                            <input type="text" id="cve-search-input" placeholder="Enter CVE ID or keywords" 
                                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Severity Filter</label>
                            <select id="severity-filter" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                                <option value="">All Severities</option>
                                <option value="CRITICAL">Critical</option>
                                <option value="HIGH">High</option>
                                <option value="MEDIUM">Medium</option>
                                <option value="LOW">Low</option>
                            </select>
                        </div>
                        <div class="flex items-end">
                            <button onclick="searchCVEs()" class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 w-full">
                                <i class="fas fa-search mr-2"></i>Search
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Search Results -->
                <div id="search-results" class="bg-white rounded-lg shadow hidden">
                    <div class="px-6 py-4 border-b">
                        <h3 class="text-lg font-medium text-gray-900">Search Results</h3>
                    </div>
                    <div class="p-6">
                        <div id="search-results-content">
                            <!-- Dynamic content -->
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- AI Analysis Section -->
        <div id="analysis-section" class="section hidden">
            <div class="mb-8">
                <h2 class="text-3xl font-bold text-gray-900 mb-4">AI-Powered CVE Analysis</h2>
                
                <!-- Analysis Form -->
                <div class="bg-white rounded-lg shadow p-6 mb-6">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">CVE ID</label>
                            <input type="text" id="analysis-cve-input" placeholder="Enter CVE ID (e.g., CVE-2024-1234)" 
                                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Analysis Type</label>
                            <select id="analysis-type" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                                <option value="comprehensive">Comprehensive Analysis</option>
                                <option value="quick">Quick Analysis</option>
                                <option value="technical">Technical Deep Dive</option>
                            </select>
                        </div>
                    </div>
                    <div class="flex space-x-4">
                        <button onclick="startAnalysis()" class="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700">
                            <i class="fas fa-brain mr-2"></i>Start AI Analysis
                        </button>
                    </div>
                </div>

                <!-- Analysis Results -->
                <div id="analysis-results" class="hidden">
                    <div class="bg-white rounded-lg shadow p-6">
                        <h3 class="text-lg font-medium text-gray-900 mb-4">Analysis Results</h3>
                        <div id="analysis-content">
                            <!-- Dynamic content -->
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Loading Spinner -->
    <div id="loading-spinner" class="fixed inset-0 bg-black bg-opacity-50 hidden flex items-center justify-center z-50">
        <div class="bg-white rounded-lg p-6 flex items-center">
            <i class="fas fa-spinner fa-spin text-blue-600 text-2xl mr-3"></i>
            <span class="text-gray-700">Processing...</span>
        </div>
    </div>

    <script src="app.js"></script>
</body>
</html>""",

        # JavaScript file
        "app/static/frontend/app.js": """// Global variables
let currentCVE = null;
let currentAnalysis = null;

// API base URL
const API_BASE = '/api/v1';

// Navigation functions
function showDashboard() {
    hideAllSections();
    document.getElementById('dashboard-section').classList.remove('hidden');
    loadDashboardData();
}

function showCVESearch() {
    hideAllSections();
    document.getElementById('cve-search-section').classList.remove('hidden');
}

function showAnalysis() {
    hideAllSections();
    document.getElementById('analysis-section').classList.remove('hidden');
}

function hideAllSections() {
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => section.classList.add('hidden'));
}

// Dashboard functions
async function loadDashboardData() {
    try {
        showLoading();
        
        // Load dashboard metrics
        const response = await fetch(`${API_BASE}/dashboard/metrics`);
        if (response.ok) {
            const data = await response.json();
            updateDashboardMetrics(data);
        }
        
        hideLoading();
    } catch (error) {
        console.error('Error loading dashboard:', error);
        hideLoading();
        showError('Failed to load dashboard data');
    }
}

function updateDashboardMetrics(data) {
    document.getElementById('critical-count').textContent = data.critical_count || 0;
    document.getElementById('total-count').textContent = data.total_count || 0;
    document.getElementById('analysis-count').textContent = data.analysis_count || 0;
    document.getElementById('recent-count').textContent = data.recent_count || 0;
}

// CVE Search functions
async function searchCVEs() {
    const query = document.getElementById('cve-search-input').value;
    const severity = document.getElementById('severity-filter').value;
    
    if (!query.trim()) {
        showError('Please enter a search query');
        return;
    }
    
    try {
        showLoading();
        
        let url = `${API_BASE}/cve/?`;
        if (severity) url += `severity=${severity}&`;
        
        const response = await fetch(url);
        if (response.ok) {
            const data = await response.json();
            displaySearchResults(data);
        } else {
            throw new Error('Search failed');
        }
        
        hideLoading();
    } catch (error) {
        console.error('Error searching CVEs:', error);
        hideLoading();
        showError('Search failed. Please try again.');
    }
}

function displaySearchResults(cves) {
    const resultsDiv = document.getElementById('search-results');
    const contentDiv = document.getElementById('search-results-content');
    
    if (cves.length === 0) {
        contentDiv.innerHTML = '<p class="text-gray-500">No CVEs found matching your criteria</p>';
    } else {
        contentDiv.innerHTML = cves.map(cve => `
            <div class="border rounded p-4 mb-4">
                <h4 class="font-bold text-lg">${cve.cve_id}</h4>
                <p class="text-gray-600 mt-2">${cve.description ? cve.description.substring(0, 200) + '...' : 'No description'}</p>
                <div class="mt-4 flex justify-between items-center">
                    <span class="px-2 py-1 rounded text-xs ${getSeverityColor(cve.severity_level)}">
                        ${cve.severity_level || 'Unknown'}
                    </span>
                    <button onclick="analyzeCVE('${cve.cve_id}')" class="bg-purple-600 text-white px-3 py-1 rounded text-sm hover:bg-purple-700">
                        Analyze
                    </button>
                </div>
            </div>
        `).join('');
    }
    
    resultsDiv.classList.remove('hidden');
}

// AI Analysis functions
async function startAnalysis() {
    const cveId = document.getElementById('analysis-cve-input').value.trim();
    const analysisType = document.getElementById('analysis-type').value;
    
    if (!cveId) {
        showError('Please enter a CVE ID');
        return;
    }
    
    try {
        showLoading();
        
        const response = await fetch(`${API_BASE}/analysis/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                cve_id: cveId,
                analysis_type: analysisType
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            displayAnalysisResults(data);
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Analysis failed');
        }
        
        hideLoading();
    } catch (error) {
        console.error('Error starting analysis:', error);
        hideLoading();
        showError(`Failed to start analysis: ${error.message}`);
    }
}

function displayAnalysisResults(data) {
    const resultsDiv = document.getElementById('analysis-results');
    const contentDiv = document.getElementById('analysis-content');
    
    contentDiv.innerHTML = `
        <div class="space-y-4">
            <div>
                <h4 class="font-medium text-gray-900">CVE ID</h4>
                <p class="text-gray-600">${data.cve_id}</p>
            </div>
            <div>
                <h4 class="font-medium text-gray-900">Model Used</h4>
                <p class="text-gray-600">${data.model_used}</p>
            </div>
            <div>
                <h4 class="font-medium text-gray-900">Analysis Results</h4>
                <pre class="bg-gray-100 p-4 rounded text-sm overflow-auto">${JSON.stringify(data.analysis, null, 2)}</pre>
            </div>
        </div>
    `;
    
    resultsDiv.classList.remove('hidden');
}

function analyzeCVE(cveId) {
    showAnalysis();
    document.getElementById('analysis-cve-input').value = cveId;
    startAnalysis();
}

// Utility functions
function getSeverityColor(severity) {
    switch (severity?.toUpperCase()) {
        case 'CRITICAL':
            return 'bg-red-100 text-red-800';
        case 'HIGH':
            return 'bg-orange-100 text-orange-800';
        case 'MEDIUM':
            return 'bg-yellow-100 text-yellow-800';
        case 'LOW':
            return 'bg-green-100 text-green-800';
        default:
            return 'bg-gray-100 text-gray-800';
    }
}

function showLoading() {
    document.getElementById('loading-spinner').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading-spinner').classList.add('hidden');
}

function showError(message) {
    alert('Error: ' + message);
}

function showSuccess(message) {
    alert('Success: ' + message);
}

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Show dashboard by default
    showDashboard();
    
    // Add event listeners
    document.getElementById('cve-search-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchCVEs();
        }
    });
    
    document.getElementById('analysis-cve-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            startAnalysis();
        }
    });
});
""",

        # CSS file
        "app/static/frontend/styles.css": """/* Custom styles for CVE Analysis Platform */

.section {
    transition: all 0.3s ease-in-out;
}

.nav-btn.active {
    background-color: rgba(59, 130, 246, 0.5);
}

.loading-animation {
    animation: spin 1s linear infinite;
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.vulnerability-card {
    transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}

.vulnerability-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.search-input {
    transition: all 0.2s ease;
}

.search-input:focus {
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.button-primary {
    background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
}

.button-primary:hover {
    background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
    transform: translateY(-1px);
}
""",

        # README file
        "README.md": """# CVE Analysis Platform

A comprehensive AI-powered platform for CVE analysis and vulnerability assessment using local AI models.

## 🚀 Features

- **AI-Powered Analysis**: Advanced vulnerability analysis using local Ollama models
- **CVE Management**: Search, import, and manage CVE data
- **Risk Assessment**: Intelligent risk scoring and prioritization
- **Interactive Dashboard**: Real-time metrics and visualization
- **RESTful API**: Complete API for integration

## 📋 Prerequisites

- Python 3.11+
- Docker & Docker Compose
- 16GB+ RAM (32GB recommended)
- Ollama with AI models (Llama 3.1, Gemma 2, CodeLlama)

## 🚀 Quick Start

1. **Setup Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

2. **Start Services**:
   ```bash
   docker-compose up -d
   ```

3. **Initialize Database**:
   ```bash
   python scripts/init_db.py
   ```

4. **Verify AI Models**:
   ```bash
   python scripts/load_models.py
   ```

5. **Access Platform**:
   - Web Interface: http://localhost
   - API Documentation: http://localhost:8000/docs

## 🔧 Development

### Local Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Application**:
   ```bash
   python run.py
   ```

## 📖 Usage

### Web Interface

1. **Dashboard**: View metrics and system status
2. **CVE Search**: Search existing CVEs
3. **AI Analysis**: Generate AI-powered vulnerability analysis

### API Examples

```python
import requests

# Analyze a CVE
response = requests.post("http://localhost:8000/api/v1/analysis/analyze", json={
    "cve_id": "CVE-2024-1234",
    "analysis_type": "comprehensive"
})
```

## 🔒 Security

- Local AI processing (no external API calls)
- Input validation and sanitization
- Secure database connections

## 📄 License

MIT License
"""
    }
    
    # Create all files
    for filepath, content in files.items():
        create_file(filepath, content)
    
    print(f"\n✅ Created {len(files)} frontend and documentation files")
    print("🎨 Frontend interface is ready!")

if __name__ == "__main__":
    setup_frontend_files()
