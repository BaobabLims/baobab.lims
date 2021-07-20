from zope.interface import alsoProvides
from Products.Five.utilities.marker import erase
from bika.lims.workflow import doActionFor
from baobab.lims.interfaces import ISharableSample
from baobab.lims.browser.project import create_samplepartition


def ObjectInitializedEventHandler(instance, event):
    """called an object is created
    """
    if instance.portal_type in ['VirusSample']:

        location = instance.getStorageLocation()
        if location:
            doActionFor(location, 'occupy')
            instance.update_box_status(location)