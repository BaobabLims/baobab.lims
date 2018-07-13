from zope.interface import alsoProvides
from Products.Five.utilities.marker import erase
from bika.lims.workflow import doActionFor
from baobab.lims.interfaces import ISharableSample
from baobab.lims.browser.project import create_samplepartition


def ObjectInitializedEventHandler(instance, event):
    """called an object is created
    """
    if instance.portal_type == 'Sample':

        if instance.getField('AllowSharing').get(instance):
            alsoProvides(instance, ISharableSample)
            instance.reindexObject()

        if not instance.getField('Barcode').get(instance):
            instance.getField('Barcode').set(instance, instance.getId())

        create_samplepartition(instance, {'services': [], 'part_id': instance.getId() + "-P"})

        location = instance.getStorageLocation()

        # if hasattr(instance, 'api_source'):
        #     if instance.api_source == "odk":    #special case for field collecdted odk samples
        #         doActionFor(instance, 'sample_due')

        try:
            sample_state = instance.sample_state.lower()
        except:
            sample_state = None

        # sample state registered
        # sample state always starts in registered. do nothing but reserve location.
        if location:
            doActionFor(location, 'reserve')
            instance.update_box_status(location)

        # state due is cpgr requested default.
        # so set it unless it must remain in registered.  will need it later for receive.
        if sample_state not in ("register", "registered"):
            doActionFor(instance, 'sample_due')

        # sate received set it to this if so specified.
        if sample_state in ("receive", "received"):
            # if float(instance.getField('Volume').get(instance)) > 0:
            # does it makes sense to asume that only samples with volumes can be received?
            # taken out for now.
            doActionFor(instance, 'receive')
            if location:
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

