// Debug search functionality
function debugSearch() {
    console.log('=== DEBUG SEARCH START ===');
    
    // Check if user is authenticated
    if (!window.authManager || !window.authManager.isAuthenticated()) {
        console.error('User not authenticated');
        return;
    }
    
    // Test basic search
    window.authManager.authenticatedFetch('/api/v1/cve/search/advanced', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            query: 'apache',
            search_type: 'both',
            limit: 10
        })
    })
    .then(response => {
        console.log('Response status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('Search response data:', data);
        
        if (data.results && data.results.length > 0) {
            console.log('✅ Search returned', data.results.length, 'results');
            console.log('First result:', data.results[0]);
        } else {
            console.log('❌ No results in response');
        }
    })
    .catch(error => {
        console.error('❌ Search failed:', error);
    });
}

// Add to window for manual testing
window.debugSearch = debugSearch; 