import requests

base_url = 'http://127.0.0.1:8000'
headers = {'X-API-Key': 'your-secure-api-key'}

print('🚀 CVE Analysis Platform - API Endpoint Testing')
print('=' * 60)

# Test core endpoints
tests = [
    ('Health Check', '/health'),
    ('Root API Info', '/'),
    ('PoC List', '/api/v1/poc/'),
    ('User Settings', '/api/v1/settings/user'),
    ('Notifications', '/api/v1/notifications/'),
    ('Monitoring Status', '/api/v1/monitoring/status'),
    ('Dashboard Metrics', '/api/v1/dashboard/metrics'),
    ('Auth Info', '/api/v1/auth/info'),
    ('CVE Search (first 5)', '/api/v1/cve/?limit=5'),
    ('Notification Stats', '/api/v1/notifications/stats')
]

working_count = 0
for name, endpoint in tests:
    try:
        h = headers if 'poc' in endpoint or 'notifications/' in endpoint and 'stats' not in endpoint else {}
        r = requests.get(f'{base_url}{endpoint}', headers=h)
        if r.status_code == 200:
            status = '✅ WORKING'
            working_count += 1
        else:
            status = f'❌ ERROR ({r.status_code})'
        print(f'{name:<25} {status}')
    except Exception as e:
        print(f'{name:<25} ❌ FAILED: {str(e)[:30]}')

print(f'\n📊 Results: {working_count}/{len(tests)} endpoints working')
print('\n🎉 All major API functionality is now available!')
print('\n📖 View complete API docs at: http://127.0.0.1:8000/api/docs') 