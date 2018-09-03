from zope.interface import alsoProvides
from Products.Five.utilities.marker import erase
from bika.lims.workflow import doActionFor
from baobab.lims.interfaces import ISharableSample
from baobab.lims.browser.project import create_samplepartition


def ObjectInitializedEventHandler(instance, event):
    """called an object is created
    """
    print('----object initialized--------')
    if instance.portal_type == 'Sample':

        if instance.getField('AllowSharing').get(instance):
            alsoProvides(instance, ISharableSample)
            instance.reindexObject()

        if not instance.getField('Barcode').get(instance):
            instance.getField('Barcode').set(instance, instance.getId())

        create_samplepartition(instance, {'services': [], 'part_id': instance.getId() + "-P"})

        location = instance.getStorageLocation()
        print('location is -----')
        print(location)
        if hasattr(instance, 'api_source'):
            print('-----api source------')
            if instance.api_source == "odk":    #special case for field collecdted odk samples
                doActionFor(instance, 'sample_due')
                if location:
                    doActionFor(location, 'reserve')
                    instance.update_box_status(location)
            delattr(instance, 'api_source')
        else:
            print('----not api source-------')
            if float(instance.getField('Volume').get(instance)) > 0:
                doActionFor(instance, 'sample_due')
                doActionFor(instance, 'receive')

            print('before check location and after receive')
            print(location)

            if location:
                print('-------')
                print('occupy box in subscriber')
                doActionFor(location, 'occupy')
                instance.update_box_status(location)


def ObjectModifiedEventHandler(instance, event):
    """ Called if the object is modified
    """
    if instance.portal_type == 'Sample':

        if not ISharableSample.providedBy(instance) and \
                instance.getField('AllowSharing').get(instance):
            alsoProvides(instance, ISharableSample)
            instance.reindexObject()

        if ISharableSample.providedBy(instance) and \
            not instance.getField('AllowSharing').get(instance):
            erase(instance, ISharableSample)
            instance.reindexObject()

        if not instance.getField('Barcode').get(instance):
            instance.getField('Barcode').set(instance, instance.getId())

        if instance.getField('Barcode').get(instance) != instance.getId():
            instance.setId(instance.getField('Barcode').get(instance))

