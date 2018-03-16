import requests
from requests.auth import HTTPBasicAuth

top_level_url = 'http://localhost:8080/Plone'
username = 'admin'
password = 'hocine'

auth = HTTPBasicAuth(username, password)

# Use parent_path instead of parent_uid
# parent_path can start with "/Plone/storage/Room-1/..."
# or remove "/Plone/" i.e., "storage/Room-1/..."

url = top_level_url + '/@@API/v3/create'
data = {'BODY':
    '[{ \
        "portal_type": "UnmanagedStorage", \
        "prefix": "Rack", \
        "leading_zeros": "0", \
        "seq_start": 1, \
        "number_items": 2, \
        "parent_path": "storage/Room-1" \
    }]'
}

request = requests.post(url, data=data, auth=auth)

# show the response content
print(request.content)
