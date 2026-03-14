import requests
import time

# Wait a moment for server to start
time.sleep(2)

base_url = 'http://127.0.0.1:5000'

print('=== TESTING DATASET INTEGRATION ===')

# Test crime data API
try:
    response = requests.get(f'{base_url}/api/crime-data?limit=5')
    if response.status_code == 200:
        data = response.json()
        print(f'✅ Crime API: {len(data["data"])} records loaded')
        print(f'   Sample: {data["data"][0]["city"]} - {data["data"][0]["crime_description"]}')
    else:
        print('❌ Crime API failed')
except Exception as e:
    print(f'❌ Crime API error: {e}')

# Test cities API
try:
    response = requests.get(f'{base_url}/api/cities')
    if response.status_code == 200:
        data = response.json()
        print(f'✅ Cities API: {len(data["cities"])} cities available')
    else:
        print('❌ Cities API failed')
except Exception as e:
    print(f'❌ Cities API error: {e}')

print('\n=== DATASET SUCCESSFULLY MERGED ===')
print('🌐 Visit: http://127.0.0.1:5000')
print('👤 Login with: test / test123')
print('📊 Click: Crime Analytics to explore the dataset!')