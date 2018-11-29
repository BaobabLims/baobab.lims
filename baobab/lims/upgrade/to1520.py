from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest
from Products.CMFCore import permissions


def upgrade(tool):
    portal = aq_parent(aq_inner(tool))
    bc = getToolByName(portal, 'bika_catalog')

    setup = portal.portal_setup
    setup.runImportStepFromProfile('profile-baobab.lims:default', 'baobab.lims.various')

    brains = bc(portal_type='ManagedStorage')
    for brain in brains:
        obj = brain.getObject()
        obj.reindexObject()

