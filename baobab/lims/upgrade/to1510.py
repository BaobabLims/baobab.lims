from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest
from Products.CMFCore import permissions


def upgrade(tool):
    portal = aq_parent(aq_inner(tool))

    setup = portal.portal_setup

    # Update all tools in which changes have been made
    setup.runImportStepFromProfile('profile-baobab.lims:default', 'jsregistry')
    setup.runImportStepFromProfile('profile-baobab.lims:default', 'cssregistry')
    setup.runImportStepFromProfile('profile-baobab.lims:default', 'plone.app.registry')

    return True