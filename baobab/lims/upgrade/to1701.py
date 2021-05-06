# -*- coding: utf-8 -*-

from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName


def upgrade(tool):
    portal = aq_parent(aq_inner(tool))

    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup

    # Update all tools in which changes have been made
    setup.runImportStepFromProfile('profile-baobab.lims:default',
                                   'propertiestool')
    setup.runImportStepFromProfile('profile-baobab.lims:default', 'typeinfo')
    setup.runImportStepFromProfile('profile-baobab.lims:default', 'workflow')
    setup.runImportStepFromProfile('profile-baobab.lims:default',
                                   'workflow-csv')
    setup.runImportStepFromProfile('profile-baobab.lims:default',
                                   'factorytool')
    setup.runImportStepFromProfile('profile-baobab.lims:default',
                                   'jsregistry')
    setup.runImportStepFromProfile('profile-baobab.lims:default', 'actions')
    addMonitoringDeviceIndexes(portal)

    return True


def addMonitoringDeviceIndexes(portal):
    # TODO: move to latest upgrade script to avoid conflicts
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
