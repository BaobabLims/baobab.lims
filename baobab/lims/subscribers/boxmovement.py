# import time
# from utils import getLocalServerTime
from Products.CMFCore.utils import getToolByName
import pdb

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
    #pdb.set_trace()
    wf = getToolByName(instance, 'portal_workflow')

    oldlocation = instance.getStorageLocation()
    newlocation = instance.getNewLocation()

    box_samples = oldlocation.only_items_of_portal_type('Sample')
    free_positions = newlocation.get_free_positions()


    if len(box_samples) <= len(free_positions):
        for i, sample in enumerate(box_samples):
            sample.setStorageLocation(free_positions[i])
            wf.doActionFor(free_positions[i], 'occupy')
            wf.doActionFor(box_samples[i], 'available')
    else:
        for i, position in enumerate(free_positions):
            box_samples[i].setStorageLocation(position)
            wf.doActionFor(position, 'occupy')
            wf.doActionFor(box_samples[i], 'available')

        box_samples = box_samples[len(free_positions):]
