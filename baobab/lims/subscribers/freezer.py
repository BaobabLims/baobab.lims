from zope.interface import alsoProvides
from Products.Five.utilities.marker import erase
from bika.lims.workflow import doActionFor
from baobab.lims.browser.freezer_monitoring import add_device_to_freezer
from baobab.lims.interfaces import IFreezer


def ObjectInitializedEventHandler(instance, event):
    """called an object is created
    """
    if instance.portal_type == 'Freezer':
        alsoProvides(instance, IFreezer)

        if instance.getMonitoringDevice():
            add_device_to_freezer(instance)
