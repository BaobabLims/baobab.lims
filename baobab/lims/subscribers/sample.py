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
        if hasattr(instance, 'api_source'):
            if instance.api_source == "odk":    #special case for field collecdted odk samples
                doActionFor(instance, 'sample_due')
                if location:
                    doActionFor(location, 'reserve')
                    instance.update_box_status(location)
            delattr(instance, 'api_source')
        else:
            if float(instance.getField('Volume').get(instance)) > 0:
                #set the state of the sample.  the default state is receive
                sample_state = None
                if hasattr(instance, "sample_state"):
                    sample_state = instance.sample_state

                # sample state registered: dont set state.  default is register and location to reserve
                if sample_state.lower() == "register" or sample_state.lower() == "registered":
                    if location:
                        doActionFor(location, 'reserve')
                        instance.update_box_status(location)
                #sample state due: set state to due and location to reserve
                if sample_state.lower() == "due":
                    doActionFor(instance, 'sample_due')
                    if location:
                        doActionFor(location, 'reserve')
                        instance.update_box_status(location)
                #state is received set sample state to receive and location to occupied
                #if no valid state in sample_state variable then also set it to received
                if not sample_state or sample_state.lower() == "receive" or sample_state.lower() == "received" or \
                        sample_state.lower() not in ("due", "receive", "received", "register", "registered"):
                    doActionFor(instance, 'sample_due')
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

