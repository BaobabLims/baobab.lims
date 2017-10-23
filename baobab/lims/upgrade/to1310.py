from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName


def upgrade(tool):

    portal = aq_parent(aq_inner(tool))
    bc = getToolByName(portal, 'bika_catalog')

    at = getToolByName(portal, 'archetype_tool')
    at.setCatalogsByType('Project', ['portal_catalog', ])

    brains = bc.searchResults(portal_type='Project')
    for brain in brains:
        obj = brain.getObject()
        obj.unmarkCreationFlag()
        obj.reindexObject()
    # for brain in brains:
    #     pc.reindexObject(brain.getObject())
    #     bc.uncatalog_object(brain.getPath())
