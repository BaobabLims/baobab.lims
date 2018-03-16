import requests
from requests.auth import HTTPBasicAuth

top_level_url = 'http://localhost:8080/Plone'
username = 'admin'
password = 'hocine'

auth = HTTPBasicAuth(username, password)

url = top_level_url + '/@@API/v3/create'

data = {
"BODY":
    '[{ \
        "portal_type": "Sample", \
        "SampleID": "id1000602", \
        "title": "def007001", \
        "SampleType": "Urine", \
        "Barcode": "bar00602", \
        "StorageLocation": "Room-1.Box-01.2", \
        "Volume": "20.00", \
        "Unit": "ml", \
        "parent_path": "clients/client-1/project-1" \
    }]'
}

request = requests.post(url, data=data, auth=auth)

# show the response content
print(request.content)
