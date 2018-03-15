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




_marker = object()

#DEFAULT_ENDPOINT = "bika.lims.jsonapi.v2.get"
DEFAULT_ENDPOINT = "baobab.lims.jsonapi.get"


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


def resource_to_portal_type(resource):
    return bika_resource_to_portal_type(resource)


def url_for(endpoint, default=DEFAULT_ENDPOINT, **values):
    return bika_url_for(endpoint, default=DEFAULT_ENDPOINT, **values)


# CREATE
def create_items(portal_type=None, uid=None, endpoint=None, **kw):
    """ create items

    1. If the uid is given, get the object and create the content in there
       (assumed that it is folderish)
    2. If the uid is 0, the target folder is assumed the portal.
    3. If there is no uid given, the payload is checked for either a key
        - `parent_uid`  specifies the *uid* of the target folder
        - `parent_path` specifies the *physical path* of the target folder
    """

    # disable CSRF
    req.disable_csrf_protection()

    # destination where to create the content
    container = uid and api.get_object_by_uid(uid) or None

    # extract the data from the request
    records = req.get_request_data()

    results = []
    for record in records:

        # get the portal_type
        if portal_type is None:
            # try to fetch the portal type out of the request data
            portal_type = record.pop("portal_type", None)

        # check if it is allowed to create the portal_type
        if not is_creation_allowed(portal_type):
            fail(401, "Creation of '{}' is not allowed".format(portal_type))

        if container is None:
            # find the container for content creation
            container = find_target_container(portal_type, record)

        # Check if we have a container and a portal_type
        if not all([container, portal_type]):
            fail(400, "Please provide a container path/uid and portal_type")

        # create the object and pass in the record data
        obj = create_object(container, portal_type, **record)
        results.append(obj)

    if not results:
        fail(400, "No Objects could be created")

    return make_items_for(results, endpoint=endpoint)


def create_object(container, portal_type, **data):
    """Creates an object slug

    :returns: The new created content object
    :rtype: object
    """

    if "id" in data:
        # always omit the id as Bika LIMS generates a proper one
        id = data.pop("id")
        logger.warn("Passed in ID '{}' omitted! Bika LIMS "
                    "generates a proper ID for you" .format(id))

    if portal_type == "Sample":
        obj = create_sample(container, **data)
        return obj
    elif portal_type == "SampleType":
        obj = create_sample_type(container, portal_type, **data)
        return obj
    else:
        try:
            obj = bika_create_object(container, portal_type, **data)
            return obj
        except:
            raise


def create_sample(container, **data):
    """
    create a sample from here that doesnt go via api create
    :param container:
    :param data:
    :return: Sample object
    """
    container = get_object(container)
    request = req.get_request()
    # we need to resolve the SampleType to a full object
    sample_type = data.get("SampleType", None)
    if sample_type is None:
        fail(400, "Please provide a SampleType")

    # TODO We should handle the same values as in the DataManager for this field
    #      (UID, path, objects, dictionaries ...)
    sample_type_results = search(portal_type="SampleType", title=sample_type)
    if not sample_type_results:
        sample_type_results = search(portal_type="SampleType", uid=sample_type)

    # StorageLocation
    storage_location = data.get("StorageLocation", None)
    if storage_location is None:
        fail(400, "Please provide a StorageLocation")

    linked_sample_list = search(portal_type="Sample", Title=data.get('LinkedSample', ''))
    linked_sample = linked_sample_list and linked_sample_list[0].getObject() or None

    try:
        volume = str(data.get('Volume'))
        float_volume = float(volume)
        if not float_volume:
            fail(400, "Please provide a correct Volume")
    except:
        raise

    # TODO We should handle the same values as in the DataManager for this field
    #      (UID, path, objects, dictionaries ...)
    storage_location_results = search(portal_type='StoragePosition', Title=storage_location)
    if not storage_location_results:
        storage_location_results = search(portal_type='StoragePosition', uid=storage_location)

    # set the values and call the create function
    values = {
        "title": data.get('title', ''),
        "description": data.get("description", ""),
        "Project": container,     #because the container is in fact the project this sample belongs to.
        "AllowSharing": data.get('AllowSharing', 0),
        "StorageLocation": storage_location_results and get_object(storage_location_results[0]) or None,
        "SampleType": sample_type_results and get_object(sample_type_results[0]) or None,
        "SubjectID": data.get("SubjectID", ""),
        "Barcode": data.get("Barcode", ""),
        "Volume": volume,
        "Unit": data.get("Unit", ""),
        "LinkedSample": linked_sample,
        "DateCreated": data.get("DateCreated", ""),
    }

    api_source = data.get('APISource', None)
    if api_source:
        values['APISource'] = api_source

    return create_smp(container, request, values)


def create_sample_type(container, portal_type, **data):
    """
    create a sample type
    :param container:
    :param portal_type
    :param data:
    :return: sample type object
    """

    container = get_object(container)
    request = req.get_request()

    retention_days = int(data.pop('RetentionDays', '0'))
    retention_hours = int(data.pop('RetentionHours', '0'))
    retention_minutes = int(data.pop('RetentionMinutes', '0'))

    retention_period = {
        'days': retention_days,
        'hours': retention_hours,
        'minutes': retention_minutes}

    data['RetentionPeriod'] = retention_period

    values = {
        "title": data.get('title', ''),
        "description": data.get("description", ""),
        "RetentionPeriod": retention_period,
        "Hazardous": data.get("Hazardous"),
        "Prefix": data.get('Prefix'),
        "MinimumVolume": data.get('MinimumVolume'),
    }

    return create_smp_type(container, request, values)


def update_items(portal_type=None, uid=None, endpoint=None, **kw):
    return bika_update_items(portal_type, uid, endpoint, **kw)


def update_object_with_data(content, record):
    """Update the content with the record data

    :param content: A single folderish catalog brain or content object
    :type content: ATContentType/DexterityContentType/CatalogBrain
    :param record: The data to update
    :type record: dict
    :returns: The updated content object
    :rtype: object
    :raises:
        APIError,
        :class:`~plone.jsonapi.routes.exceptions.APIError`
    """

    # ensure we have a full content object
    content = get_object(content)

    # get the proper data manager
    dm = IDataManager(content)

    if dm is None:
        fail(400, "Update for this object is not allowed")

    if content.portal_type == 'Sample':
        content = update_sample(content, record)
        record = u.omit(record, "SampleType", "StorageLocation")

    # Iterate through record items
    for k, v in record.items():
        try:
            success = dm.set(k, v, **record)       #starting point
        except Unauthorized:
            fail(401, "Not allowed to set the field '%s'" % k)
        except ValueError, exc:
            fail(400, str(exc))

        if not success:
            logger.warn("update_object_with_data::skipping key=%r", k)
            continue

        logger.debug("update_object_with_data::field %r updated", k)

    # Validate the entire content object
    invalid = validate_object(content, record)
    if invalid:
        fail(400, u.to_json(invalid))

    # do a wf transition
    if record.get("transition", None):
        t = record.get("transition")
        logger.debug(">>> Do Transition '%s' for Object %s", t, content.getId())
        do_transition_for(content, t)

    # reindex the object
    content.reindexObject()
    return content


# TODO: MOVE TO BAOBAB (QUINTON)
def update_sample(content, record):
    """
    Custom code for updating a sample because of special requirements for storage location and sample type.
    :param content:  The sample object that has to be modified
    :param record:  This object has a dictionary, items, that has the values that are to be changed.
    :return: The updated sample object
    """
    # set and unset the storage locations
    for k, v in record.items():
        if k == 'StorageLocation':
            storage_location_results = search(portal_type='StoragePosition', Title=v)
            if not storage_location_results:
                storage_location_results = search(portal_type='StoragePosition', uid=v)
            storage_location = storage_location_results and get_object(storage_location_results[0]) or None

            wf_tool = get_tool("portal_workflow")
            location_status = wf_tool.getStatusOf('bika_storageposition_workflow', storage_location)
            if location_status and location_status.get("review_state", None) == "available":

                current_location = content.getStorageLocation()
                if current_location:
                    doActionFor(current_location, 'liberate')

                # assign the sample to the storage location
                content.setStorageLocation(storage_location)
                sample_status = wf_tool.getStatusOf('bika_sample_workflow', content)

                if sample_status and sample_status.get("review_state", None) == "sample_received":
                    doActionFor(storage_location, 'occupy')
                else:
                    doActionFor(storage_location, 'reserve')

        if k == 'SampleType':
            sample_type_results = search(portal_type="SampleType", title=v)
            if not sample_type_results:
                sample_type_results = search(portal_type="SampleType", uid=v)

            sample_type = sample_type_results and get_object(sample_type_results[0]) or None

            if isinstance(sample_type, tuple):
                sample_type = sample_type[0]
            content.setSampleType(sample_type)

    return content
