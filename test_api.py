import requests

base_url = 'http://127.0.0.1:5000'

print('=== API ENDPOINT DEMONSTRATION ===')

# Test crime data API
try:
    response = requests.get(f'{base_url}/api/crime-data?city=Mumbai&limit=2')
    if response.status_code == 200:
        data = response.json()
        print(f'Crime API: {len(data["data"])} records returned')
        if data['data']:
            print(f'  Sample: {data["data"][0]["city"]} - {data["data"][0]["crime_description"]}')
    else:
        print('Crime API: Server not running')
except Exception as e:
    print(f'Crime API Error: {e}')

# Test environmental data API
try:
    response = requests.get(f'{base_url}/api/environmental-data?limit=2')
    if response.status_code == 200:
        data = response.json()
        print(f'Environmental API: {len(data["data"])} records returned')
        if data['data']:
            print(f'  Sample: {data["data"][0]["city"]} - PM2.5: {data["data"][0]["pm25"]}')
    else:
        print('Environmental API: Server not running')
except Exception as e:
    print(f'Environmental API Error: {e}')

print('\n=== AVAILABLE API ENDPOINTS ===')
print('GET /api/crime-data?city=CityName&limit=10')
print('GET /api/environmental-data?city=CityName&limit=10')
print('GET /api/women-crime-stats?state=StateName&limit=10')
print('GET /api/cities')