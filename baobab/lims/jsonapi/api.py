from bika.lims import api as bika_lims_api
from baobab.lims import logger
from baobab.lims.jsonapi import config

from bika.lims.jsonapi.api import fail, make_items_for, find_target_container, get_object, search, \
    resource_to_portal_type as bika_resource_to_portal_type, url_for as bika_url_for, \
    update_items as bika_update_items, validate_object, do_transition_for, get_tool

from bika.lims.jsonapi.api import create_object as bika_create_object
from bika.lims.jsonapi import request as req
from bika.lims.jsonapi import underscore as u
from bika.lims.jsonapi import api as bika_json_api
from baobab.lims.utils.create_biospecimen import create_sample as create_smp
from baobab.lims.utils.create_sample_type import create_sample_type as create_smp_type

from bika.lims.workflow import doActionFor
from bika.lims.jsonapi.interfaces import IDataManager

from AccessControl import Unauthorized
from zope.dottedname.resolve import resolve
from zope.interface import alsoProvides
from plone import api

from Products.CMFPlone.PloneBatch import Batch
from bika.lims.jsonapi.interfaces import IBatch
from bika.lims.jsonapi.interfaces import IInfo

from Products.CMFCore.utils import getToolByName
from baobab.lims.interfaces import ISharableSample


_marker = object()

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

# GET BATCHED
def get_batched(context, portal_type=None, uid=None, endpoint=None, **kw):
    """Get batched results
    """
    pm = getToolByName(context, 'portal_membership')
    roles = pm.getAuthenticatedMember().getRoles()
    if 'EMS' in roles or uid == "allowSharing":
        uid = None
        if portal_type == 'Sample':
            kw['object_provides'] = ISharableSample.__identifier__
            req.get_request().form["catalog"] = "portal_catalog"
        else:
            raise Unauthorized("You don't have access permission to {}".format(portal_type))

    # TODO: ------
    # fetch the catalog results
    results = get_search_results(portal_type=portal_type, uid=uid, **kw)

    # fetch the batch params from the request
    size = req.get_batch_size()
    start = req.get_batch_start()

    # check for existing complete flag
    complete = req.get_complete(default=_marker)
    if complete is _marker:
        # if the uid is given, get the complete information set
        complete = uid and True or False

    # return a batched record
    return get_batch(results, size, start, endpoint=endpoint,
                     complete=complete)

def get_search_results(portal_type=None, uid=None, **kw):
    """Search the catalog and return the results

    :returns: Catalog search results
    :rtype: iterable
    """

    # If we have an UID, return the object immediately
    if uid is not None:
        logger.info("UID '%s' found, returning the object immediately" % uid)
        return u.to_list(get_object_by_uid(uid))

    # allow to search search for the Plone Site with portal_type
    include_portal = False
    if u.to_string(portal_type) == "Plone Site":
        include_portal = True

    # The request may contain a list of portal_types, e.g.
    # `?portal_type=Document&portal_type=Plone Site`
    if "Plone Site" in u.to_list(req.get("portal_type")):
        include_portal = True

    # Build and execute a catalog query
    results = search(portal_type=portal_type, uid=uid, **kw)

    if include_portal:
        results = list(results) + u.to_list(get_portal())

    return results

def is_folderish(brain_or_object):
    return bika_lims_api.is_folderish(brain_or_object)

def get_portal():
    """Proxy to bika.lims.api.get_portal
    """
    return bika_lims_api.get_portal()

def get_parent(brain_or_object):
    return bika_lims_api.get_parent(brain_or_object)

def get_portal_type(brain_or_object):
    return bika_lims_api.get_portal_type(brain_or_object)

def get_object_by_uid(uid, default=None):
    """Proxy to bika.lims.api.get_object_by_uid
    """
    return bika_lims_api.get_object_by_uid(uid, default)

def get_contents(brain_or_object, depth=1):
    return bika_lims_api.get_contents(brain_or_object, depth)

def get_id(brain_or_object):
    """Proxy to bika.lims.api.get_id
    """
    return bika_lims_api.get_id(brain_or_object)

def get_uid(brain_or_object):
    """Proxy to bika.lims.api.get_uid
    """
    return bika_lims_api.get_uid(brain_or_object)

def resource_to_portal_type(resource):
    return bika_resource_to_portal_type(resource)

def portal_type_to_resource(portal_type):
    return bika_json_api.portal_type_to_resource(portal_type)

def get_workflow_info(brain_or_object, endpoint=None):
    return bika_lims_api.get_workflow_info(brain_or_object, endpoint)

def get_endpoint(brain_or_object, default=DEFAULT_ENDPOINT):
    return bika_json_api.get_endpoint(brain_or_object, default)

def get_url(brain_or_object):
    return bika_lims_api.get_url(brain_or_object)


def is_root(brain_or_object):
    return bika_json_api.is_root(brain_or_object)

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
    # import pdb;pdb.set_trace()
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
        if type(obj) is list:
            results.extend(obj)
        else:
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

    try :
        if portal_type == "Sample":
            obj = create_sample(container, **data)
            return obj
        elif portal_type == "SampleType":
            obj = create_sample_type(container, portal_type, **data)
            return obj
        elif portal_type == "Project":
            obj = create_project(container, portal_type, **data)
            return obj
        elif portal_type == "StorageUnit" or \
             portal_type == "ManagedStorage" or \
             portal_type == "UnmanagedStorage":
            obj = create_storage(container, portal_type, **data)
            return obj

    except Unauthorized:
        fail(401, "You are not allowed to create this content")

    obj = bika_create_object(container, portal_type, **data)

    return obj


def create_project(container, portal_type, **data):
    """
        Create a project via API
    """

    container = get_object(container)
    title = data.get("title", "")
    if not title:
        fail(404, "Title is required.")

    obj = bika_create_object(container, portal_type, **data)

    st_titles = data.get("SampleType", "")

    st_uids = []
    if st_titles and type(st_titles) is list:
        for st_title in st_titles:
            brains = search(portal_type="SampleType", title=st_title)
            if brains:
                st_uids.append(brains[0].UID)
        if st_uids:
            obj.setSampleType(st_uids)

    return obj



def create_storage(container, portal_type, **data):
    """
        Create a storage unit and (un-)managed storage via API
    """
    def set_inputs_into_schema(
            instance, temperature, department, unit_type):
        # Set field values across each object if possible
        schema = instance.Schema()
        if temperature and 'Temperature' in schema:
            instance.Schema()['Temperature'].set(instance, temperature)
        if department and 'Department' in schema:
            instance.Schema()['Department'].set(instance, department)
        if unit_type and 'UnitType' in schema:
            instance.Schema()['UnitType'].set(instance, unit_type)

    def set_storage_types(instance, storage_interfaces):
        schema = instance.Schema()
        if storage_interfaces and 'StorageTypes' in schema:
            instance.Schema()['StorageTypes'].set(instance, storage_interfaces)

        for storage_interface in storage_interfaces:
            inter = resolve(storage_interface)
            alsoProvides(instance, inter)

    container = get_object(container)

    # variables for storage unit
    department_title = data.get("department", "")
    temperature = data.get("temperature", "")
    unit_type = data.get("unit_type", "")

    department = None
    if container.portal_type == "StorageUnit":
        department = container.getDepartment()
        temperature = container.getTemperature()
    else:
        brains = search(portal_type="Department", title = department_title)
        if not brains:
            department = brains[0].getObject()

    # variables for managed storage
    if portal_type == "ManagedStorage":
        number_positions = data.get("number_positions", "")
        x_axis = data.get("x_axis", "")
        y_axis = data.get("y_axis", "")
        try:
            x_axis = x_axis and int(x_axis) or ''
            y_axis = y_axis and int(y_axis) or ''
            number_positions = number_positions and int(number_positions) or ''
        except ValueError:
            fail(401, "Number positions, X axis and Y axis must be integers.")

        if not number_positions or not x_axis or not y_axis:
            fail(400, "Number positions, X axis and Y axis are required to create storage positions.")

    # common variables
    prefix = data.get("prefix", "")
    leading_zeros = data.get("leading_zeros", "")
    if not prefix or not leading_zeros:
        fail(400, "Prefix and leading_zeros are required to construct storage unit title and Id.")

    number_items = data.get("number_items", "")
    try:
        number_items = number_items and int(number_items) or 1
    except ValueError:
        fail(401, "Number items must be integer.")

    seq_start = data.get("seq_start", "")
    try:
        seq_start = seq_start and int(seq_start) or 1
    except ValueError:
        fail(401, "Id sequence start must be integer.")

    sequence = range(seq_start, seq_start + number_items)

    units = []
    for x in sequence:
        id_obj = prefix + '-' + str(x).zfill(len(leading_zeros) + 1)
        title_obj = prefix + ' ' + str(x).zfill(len(leading_zeros) + 1)

        instance = api.content.create(
            container=container,
            type=portal_type,
            id=id_obj,
            title=title_obj)

        if instance.portal_type == "StorageUnit":
            set_inputs_into_schema(instance, temperature, department, unit_type)
        elif instance.portal_type == "UnmanagedStorage":
            set_storage_types(instance, ["baobab.lims.interfaces.IStockItemStorage"])
        elif instance.portal_type == "ManagedStorage":
            instance.setXAxis(x_axis)
            instance.setYAxis(y_axis)
            set_storage_types(instance, ["baobab.lims.interfaces.ISampleStorageLocation"])
            positions = storage_positions(instance, number_positions)
            for position in positions:
                set_storage_types(position, ["baobab.lims.interfaces.ISampleStorageLocation"])
                position.reindexObject()

        instance.reindexObject()

        units.append(instance)

    return units


def storage_positions(instance, number_positions):
    """ Create storage positions for a managed storage
    """
    positions = []
    for p in range(1, number_positions + 1):
        position = api.content.create(
            container=instance,
            type="StoragePosition",
            id="{id}".format(id=p),  # XXX hardcoded pos title and id
            title=instance.getHierarchy() + ".{id}".format(id=p))

        positions.append(position)

    return positions

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

    linked_sample_list = search(portal_type="Sample", title=data.get('LinkedSample', ''))
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
    storage_location_results = search(portal_type='StoragePosition', Title=storage_location, review_state='available')
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


def is_creation_allowed(portal_type):
    """Checks if it is allowed to create the portal type

    :param portal_type: The portal type requested
    :type portal_type: string
    :returns: True if it is allowed to create this object
    :rtype: bool
    """
    allowed_portal_types = config.ALLOWED_PORTAL_TYPES_TO_CREATE
    return portal_type in allowed_portal_types

# -----------------------------------------------------------------------------
#   Batching Helpers
# -----------------------------------------------------------------------------

def get_batch(sequence, size, start=0, endpoint=None, complete=False):
    """ create a batched result record out of a sequence (catalog brains)
    """

    batch = make_batch(sequence, size, start)

    return {
        "pagesize": batch.get_pagesize(),
        "next": batch.make_next_url(),
        "previous": batch.make_prev_url(),
        "page": batch.get_pagenumber(),
        "pages": batch.get_numpages(),
        "count": batch.get_sequence_length(),
        "items": make_items_for([b for b in batch.get_batch()],
                                endpoint, complete=complete),
    }

def make_batch(sequence, size=25, start=0):
    """Make a batch of the given size from the sequence
    """
    # we call an adapter here to allow backwards compatibility hooks
    return IBatch(Batch(sequence, size, start))

# Make the return items suitable for json return.  That is what the below functions are for.

def make_items_for(brains_or_objects, endpoint=None, complete=False):
    """Generate API compatible data items for the given list of brains/objects

    :param brains_or_objects: List of objects or brains
    :type brains_or_objects: list/Products.ZCatalog.Lazy.LazyMap
    :param endpoint: The named URL endpoint for the root of the items
    :type endpoint: str/unicode
    :param complete: Flag to wake up the object and fetch all data
    :type complete: bool
    :returns: A list of extracted data items
    :rtype: list
    """

    # check if the user wants to include children
    include_children = req.get_children(False)

    def extract_data(brain_or_object):
        info = get_info(brain_or_object, endpoint=endpoint, complete=complete)
        if include_children and is_folderish(brain_or_object):
            info.update(get_children_info(brain_or_object, complete=complete))
        return info

    return map(extract_data, brains_or_objects)

def get_info(brain_or_object, endpoint=None, complete=False):
    """Extract the data from the catalog brain or object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :param endpoint: The named URL endpoint for the root of the items
    :type endpoint: str/unicode
    :param complete: Flag to wake up the object and fetch all data
    :type complete: bool
    :returns: Data mapping for the object/catalog brain
    :rtype: dict
    """

    # extract the data from the initial object with the proper adapter
    info = IInfo(brain_or_object).to_dict()

    # update with url info (always included)
    url_info = get_url_info(brain_or_object, endpoint)
    info.update(url_info)

    # include the parent url info
    parent = get_parent_info(brain_or_object)
    info.update(parent)

    # add the complete data of the object if requested
    # -> requires to wake up the object if it is a catalog brain
    if complete:
        # ensure we have a full content object
        obj = bika_json_api.get_object(brain_or_object)
        # get the compatible adapter
        adapter = IInfo(obj)
        # update the data set with the complete information
        info.update(adapter.to_dict())

        # update the data set with the workflow information
        # -> only possible if `?complete=yes&workflow=yes`
        if req.get_workflow(False):
            info.update(get_workflow_info(obj))

        # # add sharing data if the user requested it
        # # -> only possible if `?complete=yes`
        # if req.get_sharing(False):
        #     sharing = get_sharing_info(obj)
        #     info.update({"sharing": sharing})

    return info
#
# def get_url_info(brain_or_object, endpoint=None):
#     return bika_lims_api.get_url_info(brain_or_object, endpoint)


def get_url_info(brain_or_object, endpoint=None):
    """Generate url information for the content object/catalog brain

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :param endpoint: The named URL endpoint for the root of the items
    :type endpoint: str/unicode
    :returns: URL information mapping
    :rtype: dict
    """

    # If no endpoint was given, guess the endpoint by portal type
    if endpoint is None:
        endpoint = get_endpoint(brain_or_object)

    uid = get_uid(brain_or_object)
    portal_type = get_portal_type(brain_or_object)
    resource = portal_type_to_resource(portal_type)

    return {
        "uid": uid,
        "url": get_url(brain_or_object),
        "api_url": url_for(endpoint, resource=resource, uid=uid),
    }


def get_parent_info(brain_or_object, endpoint=None):
    """Generate url information for the parent object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :param endpoint: The named URL endpoint for the root of the items
    :type endpoint: str/unicode
    :returns: URL information mapping
    :rtype: dict
    """

    # special case for the portal object
    if is_root(brain_or_object):
        return {}

    # get the parent object
    parent = get_parent(brain_or_object)
    portal_type = get_portal_type(parent)
    resource = portal_type_to_resource(portal_type)

    # fall back if no endpoint specified
    if endpoint is None:
        endpoint = get_endpoint(parent)

    return {
        "parent_id": get_id(parent),
        "parent_uid": get_uid(parent),
        "parent_url": url_for(endpoint, resource=resource, uid=get_uid(parent))
    }


def get_children_info(brain_or_object, complete=False):
    """Generate data items of the contained contents

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :param complete: Flag to wake up the object and fetch all data
    :type complete: bool
    :returns: info mapping of contained content items
    :rtype: list
    """

    # fetch the contents (if folderish)
    children = get_contents(brain_or_object)

    def extract_data(brain_or_object):
        return get_info(brain_or_object, complete=complete)
    items = map(extract_data, children)

    return {
        "children_count": len(items),
        "children": items
    }


