# import time
# from utils import getLocalServerTime
from Products.CMFCore.utils import getToolByName

def ObjectInitializedEventHandler(instance, event):
    """called an object is created
    """
    if instance.portal_type == 'BoxMovement':
        boxMove(instance)

def ObjectModifiedEventHandler(instance, event):
    """ Called if the object is modified
    """
    if instance.portal_type == 'BoxMovement':
        boxMove(instance)

def boxMove(instance):
    wf = getToolByName(instance.getStorageLocation(), 'portal_workflow')

    old_loc = instance.getStorageLocation()
    new_loc = instance.getNewLocation()

    box_samples = old_loc.only_items_of_portal_type('Sample')
    free_positions = new_loc.get_free_positions()

    if len(box_samples) <= len(free_positions):
        for i, sample in enumerate(box_samples):
            loc_id = int(sample.getStorageLocation().id) - 1
            liberateBox(box_samples[i])
            sample.setStorageLocation(free_positions[loc_id])
            wf.doActionFor(free_positions[loc_id], 'occupy')

    old_loc.reindexObject()
    new_loc.reindexObject()

def liberateBox(instance):
    wf = getToolByName(instance.getStorageLocation(), 'portal_workflow')
    wf.doActionFor(instance.getStorageLocation(), 'liberate')
    instance.setStorageLocation(None)
