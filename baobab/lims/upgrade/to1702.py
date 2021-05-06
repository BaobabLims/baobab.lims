# -*- coding: utf-8 -*-

from Acquisition import aq_inner
from Acquisition import aq_parent


def upgrade(tool):
    portal = aq_parent(aq_inner(tool))

    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup

    # Update all tools in which changes have been made
    setup.runImportStepFromProfile('profile-baobab.lims:default', 'typeinfo')
    setup.runImportStepFromProfile('profile-baobab.lims:default', 'workflow')

    return True
