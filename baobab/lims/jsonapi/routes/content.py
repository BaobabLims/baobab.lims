# -*- coding: utf-8 -*-

from baobab.lims.jsonapi import api
from bika.lims.jsonapi.api import resource_to_portal_type, get_batched
from baobab.lims.jsonapi.routes import add_route
from bika.lims.jsonapi.exceptions import APIError


# /<resource (portal_type)>
@add_route("/<string:resource>",
           "baobab.lims.jsonapi.get", methods=["GET"])
#
# /<resource (portal_type)>/<id>
@add_route("/<string:resource>/<string(maxlength=32):id>",
           "baobab.lims.jsonapi.get", methods=["GET"])
def get(context, request, resource=None, id=None):
    """GET
    """
    # we have a UID as resource, return the record
    if api.is_id(resource):
        return api.get_record(resource)

    portal_type = resource_to_portal_type(resource)
    if portal_type is None:
        raise APIError(404, "Not Found")
    return get_batched(portal_type=portal_type, id=id, endpoint="baobab.lims.jsonapi.get")

