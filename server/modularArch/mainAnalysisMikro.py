import requests
import base64

def main():
    # Fetch images
    fetch_url = 'http://localhost:8001/fetch/'
    fetch_data = {'series_id': 'your_series_id'}
    fetch_response = requests.post(fetch_url, json=fetch_data)
    image_data = fetch_response.json()['image']

    # Analyse images
    analyse_url = 'http://localhost:8002/analyse/'
    analyse_data = {'image': base64.b64encode(image_data.encode('latin1')).decode('latin1')}
    analyse_response = requests.post(analyse_url, json=analyse_data)
    analysis_result = analyse_response.json()

    # Store results
    store_url = 'http://localhost:8003/store/'
    store_response = requests.post(store_url, json=analysis_result)
    print(store_response.json())

if __name__ == '__main__':
    main()