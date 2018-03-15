from plone.jsonapi.core import router

from bika.lims import api
from baobab.lims import logger
from bika.lims.jsonapi.api import fail, make_items_for, is_creation_allowed, \
    find_target_container, get_object, search, resource_to_portal_type as bika_resource_to_portal_type, \
    url_for as bika_url_for, update_items as bika_update_items, validate_object, do_transition_for, get_tool, \
    get_search_results as bika_get_search_results
from bika.lims.jsonapi.api import create_object as bika_create_object
from bika.lims.jsonapi import request as req
from bika.lims.jsonapi import underscore as u
from baobab.lims.utils.create_biospecimen import create_sample as create_smp
from baobab.lims.utils.create_sample_type import create_sample_type as create_smp_type

from bika.lims.workflow import doActionFor
from bika.lims.jsonapi.interfaces import IDataManager
from AccessControl import Unauthorized

from xml.dom import minidom
import json
import os




_marker = object()

#DEFAULT_ENDPOINT = "bika.lims.jsonapi.v2.get"
DEFAULT_ENDPOINT = "baobab.lims.jsonapi.get"


class ApiDiscovery(object):

    valid_portal_types = [
        "client",
        "project",
        "sampletype",
        "storage",
        "managed_storage",
        "unmanaged_storage",
        "sample",
        "analysis_request",
        "product",
        "client_contact"
    ]

    def __init__(self):

        directory = "/home/quinton/Plone/zeocluster/src/baobab.lims/baobab/lims/jsonapi/"
        discovery_file = "discover_api.json"

        self.api_discovery_file = os.path.join(directory, discovery_file)

    def discover_api(self, portal_type, *kw):

        with open(self.api_discovery_file, 'r') as f:
            json_api = json.load(f)

        if portal_type:
            if portal_type.lower() in self.valid_portal_types:
                discovered_api = json_api['portal_types'][portal_type.lower()]
            else:
                fail(404, "%s is not a valid portal type or no discovery exists for it" % portal_type)
        else:
            discovered_api = json_api['portal_types']

        return discovered_api
