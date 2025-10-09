# To use this script, you need to install the requests library:
# pip install requests

import requests

def get_trending_topics(api_url, api_key):
    """Fetches trending topics from a social media API."""
    headers = {'Authorization': f'Bearer {api_key}'}
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {'error': f'Failed to fetch trends. Status code: {response.status_code}'}

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Get trending topics from a social media API.')
    parser.add_argument('api_url', type=str, help='The URL of the social media API.')
    parser.add_argument('api_key', type=str, help='Your API key for the social media API.')

    args = parser.parse_args()
    trends = get_trending_topics(args.api_url, args.api_key)
    print(trends)
