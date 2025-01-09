import requests


def get_external_ip():
    response = requests.get('https://api.ipify.org')
    return response.text.strip()
