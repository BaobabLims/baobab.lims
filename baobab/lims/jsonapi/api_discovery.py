from bika.lims.jsonapi.api import fail
import json
import os

_marker = object()

DEFAULT_ENDPOINT = "baobab.lims.jsonapi.get"


class ApiDiscovery(object):

    valid_portal_types = [
        "Client",
        "Project",
        "SampleType",
        "StorageUnit",
        "ManagedStorage",
        "UnmanagedStorage",
        "Sample",
        "Contact"
    ]

    def __init__(self):

        directory =  os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        discovery_file = "discover_api.json"

        self.api_discovery_file = os.path.join(directory, discovery_file)

    def discover_api(self, portal_type):

        with open(self.api_discovery_file, 'r') as f:
            json_api = json.load(f)

        discovered_api = ""

        if portal_type:
            if portal_type in self.valid_portal_types:
                discovered_api = json_api['portal_types'][portal_type]
            else:
                fail(404, "%s is not a valid portal type or no discovery exists for it" % portal_type)
        else:
            discovered_api = json_api['portal_types']

        return discovered_api
