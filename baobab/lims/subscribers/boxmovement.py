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

    oldlocation = instance.getStorageLocation()
    newlocation = instance.getNewLocation()

    box_samples = oldlocation.only_items_of_portal_type('Sample')
    free_positions = newlocation.get_free_positions()

    if len(box_samples) <= len(free_positions):
        for i, sample in enumerate(box_samples):
            newloc = free_positions[int(sample.getStorageLocation().id)]
            liberateBox(box_samples[i])
            sample.setStorageLocation(newloc)
            wf.doActionFor(free_positions[int(sample.getStorageLocation().id) - 1], 'occupy')

    oldlocation.reindexObject()
    newlocation.reindexObject()

def liberateBox(instance):
    wf = getToolByName(instance.getStorageLocation(), 'portal_workflow')
    wf.doActionFor(instance.getStorageLocation(), 'liberate')
    instance.setStorageLocation(None)
