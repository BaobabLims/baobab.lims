# -*- coding: utf-8 -*-

from baobab.lims.jsonapi import api
from bika.lims.jsonapi import api as bika_api
from baobab.lims.jsonapi.routes import add_route
from bika.lims.jsonapi.exceptions import APIError
from baobab.lims.jsonapi.api_discovery import ApiDiscovery

ACTIONS = "create,update,delete"
ACTION = "discover"


# /<resource (portal_type)>
@add_route("/<string:resource>",
           "baobab.lims.jsonapi.get", methods=["GET"])
#
# /<resource (portal_type)>/<uid>
@add_route("/<string:resource>/<string(maxlength=32):uid>",
           "baobab.lims.jsonapi.get", methods=["GET"])
def get(context, request, resource=None, uid=None):
    """GET
    """
    if bika_api.is_uid(resource):
        return bika_api.get_record(resource)

    portal_type = api.resource_to_portal_type(resource)
    if portal_type is None:
        raise APIError(404, "Not Found")
    return api.get_batched(context, portal_type=portal_type, uid=uid, endpoint="baobab.lims.jsonapi.get")

# API discovery
@add_route("/discover",
           "baobab.lims.jsonapi.discover", methods=["GET"])
@add_route("/discover/<string:resource>",
           "baobab.lims.jsonapi.discover", methods=["GET"])
def api_discover(context, request, resource=None):

    api_discovery = ApiDiscovery()
    portal_type = ""
    if resource:
        portal_type = bika_api.resource_to_portal_type(resource)

    discovered = api_discovery.discover_api(portal_type)

    return discovered

# http://werkzeug.pocoo.org/docs/0.11/routing/#builtin-converters
# http://werkzeug.pocoo.org/docs/0.11/routing/#custom-converters
#
# /<uid>
@add_route("/<any(" + ACTIONS + "):action>",
           "baobab.lims.jsonapi.action", methods=["POST"])
#
# /<action (create,update,delete)>/<uid>
@add_route("/<any(" + ACTIONS + "):action>/<string(maxlength=32):uid>",
           "baobab.lims.jsonapi.action", methods=["POST"])
#
# /<resource (portal_type)>/<action (create,update,delete)>
@add_route("/<string:resource>/<any(" + ACTIONS + "):action>",
           "baobab.lims.jsonapi.action", methods=["POST"])
#
# /<resource (portal_type)>/<action (create,update,delete)>/<uid>
@add_route("/<string:resource>/<any(" + ACTIONS + "):action>/<string(maxlength=32):uid>",
           "baobab.lims.jsonapi.action", methods=["POST"])
def action(context, request, action=None, resource=None, uid=None):
    """Various HTTP POST actions

    Case 1: /<uid>
    -> Return the full object immediately in the root of the JSON API response
    <Bika-Site>/@@API/v2/<uid>

    Case 2: /<action>/<uid>
    -> The actions (update, delete) will performed on the object identified by <uid>
    -> The actions (create) will use the <uid> as the parent folder
    <Bika-Site>/@@API/v2/<action>/<uid>

    Case 3: <resource>/<action>
    -> The "target" object will be located by a location given in the request body (uid, path, parent_path + id)
    -> The actions (cut, copy, update, delete) will performed on the target object
    -> The actions (create) will use the target object as the container
    <Bika-Site>/@@API/v2/<resource>/<action>

    Case 4: <resource>/<action>/<uid>
    -> The actions (cut, copy, update, delete) will performed on the object identified by <uid>
    -> The actions (create) will use the <uid> as the parent folder
    <Bika-Site>/@@API/v2/<resource>/<action>
    """

    # Fetch and call the action function of the API
    func_name = "{}_items".format(action)
    action_func = getattr(api, func_name, None)
    if action_func is None:
        api.fail(500, "API has no member named '{}'".format(func_name))

    portal_type = api.resource_to_portal_type(resource)
    items = action_func(portal_type=portal_type, uid=uid)

    return {
        "count": len(items),
        "items": items,
        "url": api.url_for("baobab.lims.jsonapi.action", action=action),
    }

