from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest
from Products.CMFCore import permissions
import pdb

def upgrade(tool):
    portal = aq_parent(aq_inner(tool))

    at = getToolByName(portal, 'archetype_tool')
    # bsc = getToolByName(portal, 'bika_setup_catalog')
    # pc = getToolByName(portal, 'portal_catalog')
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup
    types_tool = getToolByName(portal, 'portal_types')
    # wf = getToolByName(portal, 'portal_workflow')

    # Update all tools in which changes have been made
    setup.runImportStepFromProfile('profile-baobab.lims:default', 'propertiestool')
    setup.runImportStepFromProfile('profile-baobab.lims:default', 'typeinfo')
    setup.runImportStepFromProfile('profile-baobab.lims:default', 'repositorytool')
    setup.runImportStepFromProfile('profile-baobab.lims:default', 'workflow')
    setup.runImportStepFromProfile('profile-baobab.lims:default', 'workflow-csv')
    setup.runImportStepFromProfile('profile-baobab.lims:default', 'factorytool')
    setup.runImportStepFromProfile('profile-baobab.lims:default', 'jsregistry')
    setup.runImportStepFromProfile('profile-baobab.lims:default', 'portlets', run_dependencies=False)
    setup.runImportStepFromProfile('profile-baobab.lims:default', 'viewlets')
    setup.runImportStepFromProfile('profile-plone.app.jquery:default', 'jsregistry')

    # Add the AuditLogs /auditlogs
    try:
        types_tool.constructContent(type_name="AuditLogs",
                                    container=portal,
                                    id='auditlogs',
                                    title='Audit Logs')
        obj = portal['auditlogs']
        obj.unmarkCreationFlag()
        obj.reindexObject()
    except BadRequest:
        pass

    # Allow authenticated users to see the contents of the auditlogger folder
    mp = portal.auditlogs.manage_permission
    mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'Analyst', ], 0)
    mp(permissions.View, ['Manager', 'LabManager', 'Analyst'], 0)
    mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'Analyst', 'Owner'], 0)
    mp('Access contents information', ['Manager', 'LabManager', 'Analyst', 'Owner'], 0)
    portal.auditlogs.reindexObject()

    return True