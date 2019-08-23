from Acquisition import aq_inner
from Acquisition import aq_parent


def upgrade(tool):

    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup

    # Update changed tools
    setup.runImportStepFromProfile('profile-baobab.lims:default', 'actions')
