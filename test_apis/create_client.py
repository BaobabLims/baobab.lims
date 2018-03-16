import requests
from requests.auth import HTTPBasicAuth

top_level_url = 'http://localhost:8080/Plone'
username = 'admin'
password = 'hocine'

auth = HTTPBasicAuth(username, password)
url = top_level_url + '/@@API/v3/create'

data = {
    "BODY": '[{ \
        "portal_type": "Client", \
        "Name": "james XI", \
        "ClientID": "CL100XI", \
        "parent_path": "clients" \
    }]'
}

request = requests.post(url, data=data, auth=auth)

# show the response content
print(request.content)
