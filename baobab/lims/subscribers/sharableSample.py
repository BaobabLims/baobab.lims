from zope.interface import alsoProvides
from baobab.lims.interfaces import ISharableSample

def ObjectInitializedEventHandler(instance, event):
    """
     Used to assign ISharableSample interface to Sample objects that user decided at
     the creation of the object to be sharable or accessible.
    """

    if instance.portal_type == 'Sample':

        if instance.getField('AllowSharing').get(instance):
            alsoProvides(instance, ISharableSample)
            instance.reindexObject()