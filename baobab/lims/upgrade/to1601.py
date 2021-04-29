# -*- coding: utf-8 -*-

from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName


def upgrade(tool):
    portal = aq_parent(aq_inner(tool))

    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup

    # Update all tools in which changes have been made
    setup.runImportStepFromProfile('profile-baobab.lims:default', 'controlpanel')

    # Adding indexes - move to latest upgrade script to avoid conflicts
    clear_and_rebuild = False
    bc = getToolByName(portal, 'bika_catalog', None)
    if 'getMACAddress' not in bc.indexes():
        bc.addIndex('getMACAddress', 'FieldIndex')
        clear_and_rebuild = True
    if 'getMonitoringDeviceUID' not in bc.indexes():
        bc.addIndex('getMonitoringDeviceUID', 'FieldIndex')
        clear_and_rebuild = True
    if clear_and_rebuild:
        bc.clearFindAndRebuild()

    return True
