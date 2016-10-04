# Imports
from Products.CMFCore.utils import getToolByName
from zope.schema import ValidationError

from bika.lims.interfaces import IManagedStorage, IUnmanagedStorage
from project import ProjectView


def get_storage_objects(context, storage_uids):
    """Take a list of UIDs from the form, and resolve to a list of Storages.
    Accepts ManagedStorage, UnmanagedStorage, or StoragePosition UIDs.
    """
    uc = getToolByName(context, 'uid_catalog')
    bio_storages = []
    for uid in storage_uids:
        brain = uc(UID=uid)[0]
        instance = brain.getObject()
        if IUnmanagedStorage.providedBy(instance) \
                or len(instance.get_free_positions()) > 0:
            bio_storages.append(instance)

    return bio_storages


def count_storage_positions(storages):
    """"Return the number of items that can be stored in storages.
    This method is called in case all the storages are of type Managed.
    """
    count = 0
    for storage in storages:
        # If storage is a ManagedStorage, increment count for each
        # available StoragePosition
        if IManagedStorage.providedBy(storage):
            count += storage.getFreePositions()
        else:
            raise ValidationError("Storage %s is not a valid storage type" %
                                  storage)
    return count


def objects_between_two_uids(context, uid_1, uid_2, portal_type, wf_1, wf_2, state):
    """Retrieve the objects of type portal_type between two ordered objects
    using their uids.
    """
    w_tool = getToolByName(context, 'portal_workflow')
    uc = getToolByName(context, 'uid_catalog')
    first_id = uc(UID=uid_1)[0].id
    last_id = uc(UID=uid_2)[0].id
    objects = context.objectValues(portal_type)
    # Filter objects by workflow state active
    items = []
    for obj in objects:
        st1 = w_tool.getStatusOf(wf_1, obj)
        st2 = w_tool.getStatusOf(wf_2, obj)
        if st1.get('review_state', None) == state and \
                        st2.get('inactive_state', None) == 'active' and \
                                first_id <= obj.getId() <= last_id:
            items.append(obj)

    return items


def assign_items_to_storages(context, items, storages):
    """ store items inside selected storages
    """
    wf = getToolByName(context, 'portal_workflow')
    for storage in storages:
        if IManagedStorage.providedBy(storage):
            free_positions = storage.get_free_positions()
            if len(items) <= len(free_positions):
                for i, item in enumerate(items):
                    item.setStorageLocation(free_positions[i])
                    wf.doActionFor(free_positions[i], 'occupy')
            else:
                for i, position in enumerate(free_positions):
                    items[i].setStorageLocation(position)
                    wf.doActionFor(position, 'occupy')
                items = items[len(free_positions):]
        elif IUnmanagedStorage.providedBy(storage):
            # Case of unmanaged storage there is no limit in storage until
            # user manually set the storage as full.
            for item in items:
                item.setStorageLocation(storage)