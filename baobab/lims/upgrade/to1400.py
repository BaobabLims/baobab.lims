from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest
from Products.CMFCore import permissions


def upgrade(tool):
    portal = aq_parent(aq_inner(tool))

    at = getToolByName(portal, 'archetype_tool')
    bsc = getToolByName(portal, 'bika_setup_catalog')
    pc = getToolByName(portal, 'portal_catalog')
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

    # Add the SampleBatches /samplebatches
    try:
        types_tool.constructContent(type_name="SampleBatches",
                                   container=portal,
                                   id='samplebatches',
                                   title='Batch Samples')
        obj = portal['samplebatches']
        obj.unmarkCreationFlag()
        obj.reindexObject()
    except BadRequest:
        # folder already exists
        pass

    # /samplebatches folder permissions
    mp = portal.samplebatches.manage_permission
    mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'Analyst', ], 0)
    mp(permissions.View, ['Manager', 'LabManager', 'Analyst'], 0)
    mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'Analyst', 'Owner'], 0)
    mp('Access contents information', ['Manager', 'LabManager', 'Analyst', 'Owner'], 0)
    portal.supplyorders.reindexObject()

    # Add the SampleDonors /donors
    try:
        types_tool.constructContent(type_name="SampleDonors",
                                    container=portal,
                                    id='donors',
                                    title='Sample Donors')
        obj = portal['donors']
        obj.unmarkCreationFlag()
        obj.reindexObject()
    except BadRequest:
        # folder already exists
        pass

    # /donors folder permissions
    mp = portal.donors.manage_permission
    mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'Analyst', ], 0)
    mp(permissions.View, ['Manager', 'LabManager', 'Analyst'], 0)
    mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'Analyst', 'Owner'], 0)
    mp('Access contents information', ['Manager', 'LabManager', 'Analyst', 'Owner'], 0)
    portal.supplyorders.reindexObject()

    # Add the DiseaseOntologies /disease_ontologies
    try:
        types_tool.constructContent(type_name="DiseaseOntologies",
                                    container=portal,
                                    id='disease_ontologies',
                                    title='Disease Ontology')
        obj = portal['disease_ontologies']
        obj.unmarkCreationFlag()
        obj.reindexObject()
    except BadRequest:
        # folder already exists
        pass

    # Set catalogs for SampleBatch, SampleDonor and DiseaseOntology
    at.setCatalogsByType('SampleBatch', ['bika_catalog', 'portal_catalog'])
    at.setCatalogsByType('SampleDonor', ['bika_catalog', 'portal_catalog'])
    at.setCatalogsByType('DiseaseOntology', ['bika_catalog', 'portal_catalog'])

    # Set to None; Batch, Donor and DiseaseOntology to all Sample objects
    proxies = pc(portal_type="Sample")
    samples = (proxy.getObject() for proxy in proxies)
    for sample in samples:
        sample.getField('Batch').set(sample, None)
        sample.getField('Donor').set(sample, None)
        sample.getField('DiseaseOntology').set(sample, None)

    # change objects catalog from bsc to pc
    at.setCatalogsByType('ManagedStorage', ['portal_catalog', ])
    at.setCatalogsByType('UnmanagedStorage', ['portal_catalog', ])
    at.setCatalogsByType('StorageUnit', ['portal_catalog', ])
    at.setCatalogsByType('StoragePosition', ['portal_catalog', ])

    for content_type in ['ManagedStorage', 'UnmanagedStorage', 'StorageUnit', 'StoragePosition']:
        proxies = bsc(portal_type=content_type)
        storages = (proxy.getObject() for proxy in proxies)
        for storage in storages:
            storage.unmarkCreationFlag()
            storage.reindexObject()

    return True