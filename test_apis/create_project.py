import requests
from requests.auth import HTTPBasicAuth

top_level_url = 'http://localhost:8080/Plone'
username = 'admin'
password = 'hocine'

auth = HTTPBasicAuth(username, password)
url = top_level_url + '/@@API/v3/create'

data = {"BODY": '[{"portal_type": "Project", "parent_path": "clients/client-1", "StudyType": "eclectic", "title": "White Goblin lvl 1", "description": "Cleaning up the side effects of Goblin serum", "NumParticipants": "412", "AgeHigh": "24", "AgeLow": "4", "DateCreated": "2018-02-22", "Service": ["400d67e0f61d4487a71f2174d4eed3f6","1c9fc9da29ca4d049dc74484cddd7799"]}]'}

request = requests.post(url, data=data, auth=auth)
# show the response content
print(request.content)
