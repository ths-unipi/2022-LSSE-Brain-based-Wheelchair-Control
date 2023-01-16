from requests import post

if __name__ == '__main__':
    data = {'type': 'test'}
    response = post('http://localhost:5000/json', json=data)
    if response.status_code != 200:
        error_message = response.json()['error']
        print(f'[-] Error: {error_message}')