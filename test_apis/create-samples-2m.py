import random
import requests
from requests.auth import HTTPBasicAuth

@profile
def create_first_sample(sample_id, sample_type, location, url, auth):
    data = {
      "BODY":
         '[{ \
            "portal_type": "Sample", \
            "SampleID": "'+ sample_id + '", \
            "title": "Biospecimen 1", \
            "SampleType": "'+ sample_type + '", \
            "Barcode": "'+ sample_id +'", \
            "StorageLocation": "' + location +'", \
            "Volume": "20.00", \
            "Unit": "ml", \
            "parent_path": "clients/client-1/project-1" \
          }]'
    }
    request = requests.post(url, data=data, auth=auth)

def create_samples(freezers, sample_types, nb_samples, url, auth):
    # for 2000000 samples we need 8 digits 
    x1 = slice(1, 8, 1)
    # for 2000 boxes per freezer we need 5 digits
    x2 = slice(1, 5, 1)
    k = 0
    for i in range(len(freezers)):
        bx = 'Box-0001'
        for j in range(1, int(nb_samples / len(freezers)) + 1):
            k += 1
            sample_type = sample_types[random.randint(0,4)]
            sample_id = 'id-' + str(nb_samples * 10 + (nb_samples / len(freezers)) * i + j)[x1]
            location = 'rm-1.' + freezers[i] + '.' + bx + '.' + str(k)
            if k == 0:
                create_first_sample(sample_id, sample_type, location, auth, url)
            else:
                data = {
                "BODY":
                  '[{ \
                    "portal_type": "Sample", \
                    "SampleID": "'+ sample_id + '", \
                    "title": "Biospecimen '+ str(i * (nb_samples / len(freezers)) + j) +'", \
                    "SampleType": "'+ sample_type + '", \
                    "Barcode": "'+ sample_id +'", \
                    "StorageLocation": "' + location +'", \
                    "Volume": "20.00", \
                    "Unit": "ml", \
                    "parent_path": "clients/client-1/project-1" \
                  }]'
                }
                request = requests.post(url, data=data, auth=auth)
                # print(request.content)
            if j % 100 == 0:
                k = 0           
                bx = 'Box-' + str(10000 + j / 100 + 1)[x2]

# create last sample 2000001
def create_last_sample(sample_id, sample_type, location, url, auth):
    data = {
      "BODY":
       '[{ \
         "portal_type": "Sample", \
         "SampleID": "' + sample_id + '", \
         "title": "Biospecimen 2000001", \
         "SampleType": "'+ sample_type + '", \
         "Barcode": "id-2000001", \
         "StorageLocation": "' + location +'", \
         "Volume": "20.00", \
         "Unit": "ml", \
         "parent_path": "clients/client-1/project-1" \
       }]'
    }

    request = requests.post(url, data=data, auth=auth)

def main():
    top_level_url = 'http://localhost:8080/Plone'
    username = 'admin'
    password = '123qwe'
    sample_types = ['Blood Plasma', 'Serum','Urine', 'Water', 'Whole Blood']
    freezers = ['fz-001', 'fz-002', 'fz-003', 'fz-004', 'fz-005',
                'fz-006', 'fz-007', 'fz-008', 'fz-009', 'fz-010']
    auth = HTTPBasicAuth(username, password)
    url = top_level_url + '/@@API/v3/create'
    nb_samples = 2000000

    create_samples(freezers, sample_types, nb_samples, url, auth)
    location = 'rm-1.fz-010.Box-2001.1'
    create_last_sample('id-2000001', sample_types[0], location, url, auth) 
    create_first_sample('id-0000001', sample_types[0], 'rm-1.fz-1.Box-0001.1', url, auth)

if __name__=="__main__":
    main()

