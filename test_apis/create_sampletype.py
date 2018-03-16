import requests
from requests.auth import HTTPBasicAuth

top_level_url = 'http://localhost:8080/Plone'
username = 'admin'
password = 'hocine'

auth = HTTPBasicAuth(username, password)

url = top_level_url + '/@@API/v3/create'

data = {
    "BODY": '[{ \
        "portal_type": "SampleType", \
        "RetentionDays": "42", \
        "title": "Brain Fluid Kuel", \
        "description": "Fluids of the brain Kuels", \
        "Prefix": "BFK", \
        "MinimumVolume": "24 ml", \
        "Hazardous": "1", \
        "parent_path": "bika_sampletypes" \
    }]'
}

request = requests.post(url, data=data, auth=auth)

# show the response content
print(request.content)
