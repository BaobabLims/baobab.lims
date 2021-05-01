#!/usr/bin/python
# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from DateTime import DateTime


def add_device_to_freezer(context, review_state='available'):
    """ Create devicehistory object for freezer(context)
    """

    dh_id = context.generateUniqueId('DeviceHistory')
    devicehistory = _createObjectByType('DeviceHistory', context, dh_id)
    devicehistory.unmarkCreationFlag()
    devicehistory.setDateTimeIn(DateTime())
    devicehistory.setDateTimeOut(None)
    devicehistory.setMonitoringDevice(context.getMonitoringDevice())
    devicehistory.setFreezer(context)
    devicehistory.reindexObject()
