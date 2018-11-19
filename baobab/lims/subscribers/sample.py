# from zope.interface import alsoProvides
# from Products.Five.utilities.marker import erase
from bika.lims.workflow import doActionFor
# from baobab.lims.interfaces import ISharableSample
from baobab.lims.browser.project import create_samplepartition
from utils import getLocalServerTime


def ObjectInitializedEventHandler(instance, event):
    """called an object is created
    """
    if instance.portal_type == 'Sample':

        if not instance.getField('Barcode').get(instance):
            instance.getField('Barcode').set(instance, instance.getId())

        create_samplepartition(instance, {'services': [], 'part_id': instance.getId() + "-P"})

        location = instance.getStorageLocation()
        if hasattr(instance, 'api_source'):
            if instance.api_source == "odk":    #special case for field collecdted odk samples
                doActionFor(instance, 'sample_due')
                if location:
                    doActionFor(location, 'reserve')
                    instance.update_box_status(location)
            delattr(instance, 'api_source')
        else:
            if float(instance.getField('Volume').get(instance)) > 0:
                doActionFor(instance, 'sample_due')
                doActionFor(instance, 'receive')

            if location:
                doActionFor(location, 'occupy')
                instance.update_box_status(location)

        updateLocalServerTime(instance)


def ObjectModifiedEventHandler(instance, event):
    """ Called if the object is modified
    """
    if instance.portal_type == 'Sample':

        if not instance.getField('Barcode').get(instance):
            instance.getField('Barcode').set(instance, instance.getId())

        if instance.getField('Barcode').get(instance) != instance.getId():
            instance.setId(instance.getField('Barcode').get(instance))

        updateLocalServerTime(instance)

def updateLocalServerTime(instance):

    sampling_date = instance.getField('SamplingDate').get(instance)
    frozen_time = instance.getField('FrozenTime').get(instance)

    new_sampling_date = getLocalServerTime(sampling_date)
    new_frozen_time = getLocalServerTime(frozen_time)
    instance.getField('SamplingDate').set(instance, new_sampling_date)
    instance.getField('FrozenTime').set(instance, new_frozen_time)