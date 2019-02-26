import requests
from requests.auth import HTTPBasicAuth

def create_boxes(freezers, nb_boxes, url, auth):
    location = ''
    for i in range(len(freezers)):
       location = 'storage/rm-1/'+ freezers[i]
       for j in range(nb_boxes / len(freezers)):
       
           data = {'BODY':
            '[{ \
              "portal_type": "ManagedStorage", \
              "prefix": "Box", \
              "leading_zeros": "0", \
              "seq_start": ' + str(j+1) + ', \
              "number_items": 1, \
              "parent_path": "'+ location +'", \
              "number_positions": 100, \
              "x_axis": 10, \
              "y_axis": 10 \
            }]'
           }
          
           request = requests.post(url, data=data, auth=auth)
          # print(request.content)
        
    # create additional one box for sample 2000001
    data = {
      'BODY':
       '[{ \
         "portal_type": "ManagedStorage", \
         "prefix": "Box", \
         "leading_zeros": "0", \
         "seq_start": 11, \
         "number_items": 1, \
         "parent_path": "'+ location +'", \
         "number_positions": 100, \
         "x_axis": 10, \
         "y_axis": 10 \
       }]'
    }

    request = requests.post(url, data=data, auth=auth)

def main():
    top_level_url = 'http://localhost:8080/Plone'
    username = 'admin'
    password = 'hocine'
    auth = HTTPBasicAuth(username, password)
    url = top_level_url + '/@@API/v3/create'

    nb_boxes = 20000
    freezers = ['fz-001', 'fz-002', 'fz-003', 'fz-004', 'fz-005',
                'fz-006', 'fz-007', 'fz-008', 'fz-009', 'fz-010']
    create_boxes(freezers, nb_boxes, url, auth)

if __name__=="__main__":
    main()

