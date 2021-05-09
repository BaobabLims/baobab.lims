# -*- coding: utf-8 -*-

from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName


def upgrade(tool):
    portal = aq_parent(aq_inner(tool))

    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup

    # Update all tools in which changes have been made
    addMonitoringDeviceIndexes(portal)

    return True


def addMonitoringDeviceIndexes(portal):
    # TODO: move to latest upgrade script to avoid conflicts
    clear_and_rebuild = False
    bc = getToolByName(portal, 'bika_catalog', None)

    if 'getDatetimeRecorded' not in bc.indexes():
        bc.addIndex('getDatetimeRecorded', 'FieldIndex')
        clear_and_rebuild = True

    if clear_and_rebuild:
        bc.clearFindAndRebuild()
