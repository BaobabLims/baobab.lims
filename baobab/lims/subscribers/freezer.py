# -*- coding: utf-8 -*-

from plone import api as ploneapi
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

        monitoring_device = instance.getMonitoringDevice()
        if monitoring_device:
            add_device_to_freezer(instance)
            tool = ploneapi.portal.get_tool('portal_workflow')
            review_state = tool.getInfoFor(monitoring_device, 'review_state')
            if review_state == 'available':
                doActionFor(monitoring_device, 'use')
            monitoring_device.reindexObject(idxs=["review_state", ])
