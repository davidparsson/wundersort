"""
Usage:
  ./sort.py [options]

Options:
  --list-id=<id>
"""
import docopt
import requests
from flask.json import jsonify

from auth import client_id, get_access_token


def main():
    token = get_access_token()

    arguments = docopt.docopt(__doc__)
    list_id = arguments['--list-id']
    if list_id:
        response = requests.get(f'http://a.wunderlist.com/api/v1/tasks', {'list_id': list_id}, headers={'X-Access-Token': token, 'X-Client-ID': client_id})
        assert response.status_code == 200
        json = response.json()
        json.sort(key=lambda item: item['created_at'])
        json.reverse()
        
        response = requests.get(f'http://a.wunderlist.com/api/v1/task_positions', {'list_id': list_id}, headers={'X-Access-Token': token, 'X-Client-ID': client_id})
        assert response.status_code == 200
        positions_json = response.json()
        #print(positions_json)

        response = requests.put(f'http://a.wunderlist.com/api/v1/task_positions/{positions_json[0]["id"]}', json={'revision': positions_json[0]['revision'], 'values': [item['id'] for item in json]}, headers={'X-Access-Token': token, 'X-Client-ID': client_id})
        assert response.status_code == 200
        #print(response.json())
        print('Done!')
    else:
        response = requests.get('http://a.wunderlist.com/api/v1/lists', headers={'X-Access-Token': token, 'X-Client-ID': client_id})
        assert response.status_code == 200
        json = response.json()
        for item in json:
            print(f"{item['title']}: {item['id']}")


if __name__ == '__main__':
    main()
