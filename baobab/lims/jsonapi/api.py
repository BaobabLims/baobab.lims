from bika.lims import api
from bika.lims import logger
from bika.lims.jsonapi.api import fail, make_items_for
from bika.lims.jsonapi import request as req
from bika.lims.jsonapi import underscore as u

_marker = object()

DEFAULT_ENDPOINT = "bika.lims.jsonapi.v2.get"


def is_id(id):
    """Checks if the passed in uid is a valid UID

    :param uid: The uid to check
    :type uid: string
    :return: True if the uid is a valid 32 alphanumeric uid or '0'
    :rtype: bool
    """
    #import pdb;pdb.set_trace()
    if not isinstance(id, basestring):
        return False
    if id != "0" and len(id) != 32:
        return False
    return True


def get_record(id=None):
    """Get a single record
    """
    obj = None

    if id is not None:
        obj = get_object_by_id(id)
    else:
        obj = get_object_by_request()
    if obj is None:
        fail(404, "No object found")
    complete = req.get_complete(default=_marker)
    if complete is _marker:
        complete = True
    items = make_items_for([obj], complete=complete)
    return u.first(items)


def get_object_by_id(id, default=None):
    """Find an object by a given ID

    :param id: The ID of the object to find
    :type id: string
    :returns: Found Object or None
    """

    # nothing to do here
    if not id:
        if default is not _marker:
            return default
        fail("get_object_by_id requires ID as first argument; got {} instead"
             .format(id))

    # we defined the portal object UID to be '0'::
    if id == '0':
        return api.get_portal()

    # we try to find the object with both catalogs
    pc = api.get_portal_catalog()
    # uc = api.get_tool("uid_catalog")

    # try to find the object with the reference catalog first
    brains = pc(id=id)
    if brains:
        return brains[0].getObject()

    # try to find the object with the portal catalog
    res = pc(ID=id)
    if not res:
        if default is not _marker:
            return default
        fail("No object found for UID {}".format(id))

    return api.get_object(res[0])


def get_object_by_request():
    """Find an object by request parameters

    Inspects request parameters to locate an object

    :returns: Found Object or None
    :rtype: object
    """
    data = req.get_form() or req.get_query_string()
    return get_object_by_record(data)


def get_object_by_record(record):
    """Find an object by a given record

    Inspects request the record to locate an object

    :param record: A dictionary representation of an object
    :type record: dict
    :returns: Found Object or None
    :rtype: object
    """

    # nothing to do here
    if not record:
        return None

    if record.get("id"):
        return get_object_by_id(record["id"])

    # TODO: import get_object_by_record from bika and call it if else
    return None