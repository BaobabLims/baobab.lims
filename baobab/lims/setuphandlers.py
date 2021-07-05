""" Bika setup handlers. """

from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName

from bika.lims import logger
from baobab.lims.permissions import *
from bika.lims.permissions import CancelAndReinstate

class Empty:
    pass


class BikaCustomGenerator:

    def setupPortalContent(self, portal):

        for obj_id in (
                'kits',
                'projects',
                'shipments',
                'biospecimens',
                'inventoryorders',
                'samplebatches',
                'storage',
                'donors',
                'disease_ontologies',
                'sampleshipments',
                'auditlogs',
                'virus_samples',
                'organisms',
                'collection_devices',
                'anatomical_materials',
                'lab_hosts',
                'hosts',
                'host_diseases',
                'freezers',
                'monitoring_devices',
                'viral_genomic_analyses',
                'virus_aliquots',
        ):
            try:
                obj = portal._getOb(obj_id)
                obj.unmarkCreationFlag()
                obj.reindexObject()
            except:
                pass

        bika_setup = portal._getOb('bika_setup')
        for obj_id in (
                'bika_kittemplates',
                'bika_biospectypes',
                'bika_storagetypes',
                'bika_products',
                'bika_stockitems'):

            obj = bika_setup._getOb(obj_id)
            obj.unmarkCreationFlag()
            obj.reindexObject()

    def setupGroups(self, portal):
        """
            Remove some undesired groups
        """
        groups = ["Samplers", "Preservers", "RegulatoryInspectors", "SamplingCoordinators"]

        portal_groups = portal.portal_groups

        for group_id in portal_groups.listGroupIds():
            if group_id in groups:
                portal_groups.removeGroup(group_id)

        if 'EMSystems' not in portal_groups.listGroupIds():
            portal_groups.addGroup('EMSystems', title="EMSystems", roles = ['EMS'])

    def setupCatalogs(self, portal):

        def addIndex(cat, *args):
            try:
                cat.addIndex(*args)
            except:
                logger.warning("Could not create index %s in catalog %s" %
                               (args, cat))

        def addColumn(cat, col):
            try:
                cat.addColumn(col)
            except:
                logger.warning("Could not create metadata %s in catalog %s" %
                               (col, cat))

        # _______________________________#
        #          BIKA_CATALOG          #
        # _______________________________#
        bc = getToolByName(portal, 'bika_catalog', None)
        if bc is None:
            logger.warning('Could not find the bika_catalog tool.')
            return
        # Add indexes and metadata columns here
        at = getToolByName(portal, 'archetype_tool')
        at.setCatalogsByType('Kit', ['bika_catalog'])
        at.setCatalogsByType('Project', ['bika_catalog', 'portal_catalog'])
        at.setCatalogsByType('Shipment', ['bika_catalog'])
        at.setCatalogsByType('Biospecimen', ['bika_catalog'])
        at.setCatalogsByType('SampleBatch', ['bika_catalog'])
        at.setCatalogsByType('SampleDonor', ['bika_catalog'])
        at.setCatalogsByType('DiseaseOntology', ['bika_catalog'])
        at.setCatalogsByType('SampleShipment', ['bika_catalog'])
        at.setCatalogsByType('AuditLog', ['bika_catalog', 'portal_catalog'])
        at.setCatalogsByType('VirusSample', ['bika_catalog', 'portal_catalog'])
        at.setCatalogsByType('Organism', ['bika_catalog', 'portal_catalog'])
        at.setCatalogsByType('AnatomicalMaterial', ['bika_catalog', 'portal_catalog'])
        at.setCatalogsByType('CollectionDevice', ['bika_catalog', 'portal_catalog'])
        at.setCatalogsByType('LabHost', ['bika_catalog', 'portal_catalog'])
        at.setCatalogsByType('Host', ['bika_catalog', 'portal_catalog'])
        at.setCatalogsByType('HostDisease', ['bika_catalog', 'portal_catalog'])
        at.setCatalogsByType('Freezer', ['bika_catalog'])
        at.setCatalogsByType('MonitoringDevice', ['bika_catalog'])
        at.setCatalogsByType('DeviceReading', ['bika_catalog'])
        at.setCatalogsByType('DeviceHistory', ['bika_catalog'])
        at.setCatalogsByType('ViralGenomicAnalyses', ['bika_catalog', 'portal_catalog'])
        at.setCatalogsByType('VirusAliquots', ['bika_catalog', 'portal_catalog'])

        addIndex(bc, 'getParentUID', 'FieldIndex')
        addIndex(bc, 'getProjectUID', 'FieldIndex')
        addIndex(bc, 'getMACAddress', 'FieldIndex')
        addIndex(bc, 'getMonitoringDeviceUID', 'FieldIndex')
        addIndex(bc, 'getDatetimeRecorded', 'FieldIndex')

        # _______________________________#
        #      BIKA_SETUP_CATALOG        #
        # _______________________________#
        bsc = getToolByName(portal, 'bika_setup_catalog', None)
        if bsc is None:
            logger.warning('Could not find the bika_setup_catalog tool.')
            return

        # Add indexes and metadata columns here
        at = getToolByName(portal, 'archetype_tool')
        at.setCatalogsByType('KitTemplate', ['bika_setup_catalog'])
        at.setCatalogsByType('InventoryOrder', ['bika_setup_catalog'])
        at.setCatalogsByType('StorageType', ['bika_setup_catalog'])
        at.setCatalogsByType('Product', ['bika_setup_catalog'])
        at.setCatalogsByType('StockItem', ['bika_setup_catalog', ])
        at.setCatalogsByType('StorageLocation', ['bika_setup_catalog'])
        # at.setCatalogsByType('StorageUnit', ['bika_setup_catalog'])
        # at.setCatalogsByType('ManagedStorage', ['bika_setup_catalog'])
        # at.setCatalogsByType('UnmanagedStorage', ['bika_setup_catalog'])
        # at.setCatalogsByType('StoragePosition', ['bika_setup_catalog'])

        addIndex(bsc, 'getProductUID', 'FieldIndex')

        bac = getToolByName(portal, 'bika_analysis_catalog', None)
        if bsc is None:
            logger.warning('Could not find the bika_analysis_catalog tool.')
            return
            # Add indexes and metadata columns here

    def setupPermissions(self, portal):
        """ Set up some suggested role to permission mappings.
        """

        # Root permissions
        mp = portal.manage_permission
        mp(ManageProjects, ['Manager', 'LabManager'], 1)
        mp(ManageKits, ['Manager', 'LabManager', 'LabClerk'], 1)
        mp(AddProject, ['Manager', 'LabManager'], 1)
        mp(AddStorageUnit, ['Manager', 'LabManager', 'LabClerk'], 1)
        mp(AddManagedStorage, ['Manager', 'LabManager', 'LabClerk'], 1)
        mp(AddUnmanagedStorage, ['Manager', 'LabManager', 'LabClerk'], 1)
        mp(AddStoragePosition, ['Manager', 'LabManager', 'LabClerk'], 1)

        mp(AddInventoryOrder, ['Manager', 'LabManager'], 1)
        mp(DispatchInventoryOrder, ['Manager', 'LabManager'], 1)
        mp(ReceiveInventoryOrder, ['Manager', 'LabManager', 'LabClerk'], 1)
        mp(StoreInventoryOrder, ['Manager', 'LabManager', 'LabClerk'], 1)

        # monitoring_devices
        mp = portal.monitoring_devices.manage_permission

        # Allow authenticated users to see the contents of the project folder
        mp(permissions.View, ['Authenticated'], 0)
        mp(permissions.AccessContentsInformation, ['Authenticated'], 0)
        mp(permissions.ListFolderContents, ['Authenticated'], 0)

        mp(permissions.ListFolderContents, ['Manager'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner', 'EMS'], 0)
        mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'Owner'], 0)
        mp('Access contents information', ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner', 'EMS'], 0)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager'], 0)
        portal.monitoring_devices.reindexObject()

        # freezers
        mp = portal.freezers.manage_permission
        # Allow authenticated users to see the contents of the project folder
        mp(permissions.View, ['Authenticated'], 0)
        mp(permissions.AccessContentsInformation, ['Authenticated'], 0)
        mp(permissions.ListFolderContents, ['Authenticated'], 0)

        mp(permissions.ListFolderContents, ['Manager'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner', 'EMS'], 0)
        mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'Owner'], 0)
        mp('Access contents information', ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner', 'EMS'], 0)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager'], 0)

        portal.freezers.reindexObject()

        # virus_aliquots
        mp = portal.virus_aliquots.manage_permission
        # Allow authenticated users to see the contents of the project folder
        mp(permissions.View, ['Authenticated'], 0)
        mp(permissions.AccessContentsInformation, ['Authenticated'], 0)
        mp(permissions.ListFolderContents, ['Authenticated'], 0)

        mp(permissions.ListFolderContents, ['Manager'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner', 'EMS'], 0)
        mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'Owner'], 0)
        mp('Access contents information', ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner', 'EMS'], 0)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager'], 0)
        portal.virus_aliquots.reindexObject()

        # lab_hosts
        mp = portal.lab_hosts.manage_permission

        # Allow authenticated users to see the contents of the project folder
        mp(permissions.View, ['Authenticated'], 0)
        mp(permissions.AccessContentsInformation, ['Authenticated'], 0)
        mp(permissions.ListFolderContents, ['Authenticated'], 0)

        mp(permissions.ListFolderContents, ['Manager'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner', 'EMS'], 0)
        mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'Owner'], 0)
        mp('Access contents information', ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner', 'EMS'], 0)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager'], 0)
        portal.lab_hosts.reindexObject()

        # viral_genomic_analyses
        mp = portal.viral_genomic_analyses.manage_permission

        # Allow authenticated users to see the contents of the project folder
        mp(permissions.View, ['Authenticated'], 0)
        mp(permissions.AccessContentsInformation, ['Authenticated'], 0)
        mp(permissions.ListFolderContents, ['Authenticated'], 0)

        mp(permissions.ListFolderContents, ['Manager'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner', 'EMS'], 0)
        mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'Owner'], 0)
        mp('Access contents information', ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner', 'EMS'], 0)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager'], 0)
        portal.viral_genomic_analyses.reindexObject()

        # hosts
        mp = portal.hosts.manage_permission

        # Allow authenticated users to see the contents of the project folder
        mp(permissions.View, ['Authenticated'], 0)
        mp(permissions.AccessContentsInformation, ['Authenticated'], 0)
        mp(permissions.ListFolderContents, ['Authenticated'], 0)

        mp(permissions.ListFolderContents, ['Manager'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner', 'EMS'], 0)
        mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'Owner'], 0)
        mp('Access contents information', ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner', 'EMS'], 0)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager'], 0)
        portal.hosts.reindexObject()

        # host_diseases
        mp = portal.host_diseases.manage_permission

        # Allow authenticated users to see the contents of the project folder
        mp(permissions.View, ['Authenticated'], 0)
        mp(permissions.AccessContentsInformation, ['Authenticated'], 0)
        mp(permissions.ListFolderContents, ['Authenticated'], 0)

        mp(permissions.ListFolderContents, ['Manager'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner', 'EMS'], 0)
        mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'Owner'], 0)
        mp('Access contents information', ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner', 'EMS'], 0)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager'], 0)
        portal.host_diseases.reindexObject()

        # anatomical_materials
        mp = portal.anatomical_materials.manage_permission

        # Allow authenticated users to see the contents of the project folder
        mp(permissions.View, ['Authenticated'], 0)
        mp(permissions.AccessContentsInformation, ['Authenticated'], 0)
        mp(permissions.ListFolderContents, ['Authenticated'], 0)

        mp(permissions.ListFolderContents, ['Manager'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner', 'EMS'], 0)
        mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'Owner'], 0)
        mp('Access contents information', ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner', 'EMS'], 0)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager'], 0)
        portal.anatomical_materials.reindexObject()

        # collection_devices
        mp = portal.collection_devices.manage_permission

        # Allow authenticated users to see the contents of the project folder
        mp(permissions.View, ['Authenticated'], 0)
        mp(permissions.AccessContentsInformation, ['Authenticated'], 0)
        mp(permissions.ListFolderContents, ['Authenticated'], 0)

        mp(permissions.ListFolderContents, ['Manager'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner', 'EMS'], 0)
        mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'Owner'], 0)
        mp('Access contents information', ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner', 'EMS'], 0)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager'], 0)
        portal.collection_devices.reindexObject()

        # organisms
        mp = portal.organisms.manage_permission

        # Allow authenticated users to see the contents of the project folder
        mp(permissions.View, ['Authenticated'], 0)
        mp(permissions.AccessContentsInformation, ['Authenticated'], 0)
        mp(permissions.ListFolderContents, ['Authenticated'], 0)

        mp(permissions.ListFolderContents, ['Manager'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner', 'EMS'], 0)
        mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'Owner'], 0)
        mp('Access contents information', ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner', 'EMS'], 0)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager'], 0)
        portal.organisms.reindexObject()

        # virus samples
        mp = portal.virus_samples.manage_permission

        # Allow authenticated users to see the contents of the project folder
        mp(permissions.View, ['Authenticated'], 0)
        mp(permissions.AccessContentsInformation, ['Authenticated'], 0)
        mp(permissions.ListFolderContents, ['Authenticated'], 0)

        mp(permissions.ListFolderContents, ['Manager'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner', 'EMS'], 0)
        mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'Owner'], 0)
        mp('Access contents information', ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner', 'EMS'], 0)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager'], 0)
        portal.virus_samples.reindexObject()

        # audit logger
        mp = portal.auditlogs.manage_permission

        # Allow authenticated users to see the contents of the project folder
        mp(permissions.View, ['Authenticated'], 0)
        mp(permissions.AccessContentsInformation, ['Authenticated'], 0)
        mp(permissions.ListFolderContents, ['Authenticated'], 0)

        mp(permissions.ListFolderContents, ['Manager'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner', 'EMS'], 0)
        mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'Owner'], 0)
        mp('Access contents information', ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner', 'EMS'], 0)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager'], 0)
        portal.auditlogs.reindexObject()

        # projects
        mp = portal.projects.manage_permission

        # Allow authenticated users to see the contents of the project folder
        mp(permissions.View, ['Authenticated'], 0)
        mp(permissions.AccessContentsInformation, ['Authenticated'], 0)
        mp(permissions.ListFolderContents, ['Authenticated'], 0)

        mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner', 'EMS'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner', 'EMS'], 0)
        mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'Owner'], 0)
        mp('Access contents information', ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner', 'EMS'], 0)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager'], 0)
        portal.projects.reindexObject()

        # kits
        mp = portal.kits.manage_permission

        mp(permissions.View, ['Authenticated'], 0)
        mp(permissions.AccessContentsInformation, ['Authenticated'], 0)
        mp(permissions.ListFolderContents, ['Authenticated'], 0)

        mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
        # mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'LabClerk'], 0)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'LabClerk'], 0)
        mp(permissions.DeleteObjects, ['Manager', 'LabManager'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
        portal.kits.reindexObject()

        # shipments
        mp = portal.shipments.manage_permission

        # Allow authenticated users to see the contents of the client folder
        mp(permissions.View, ['Authenticated'], 0)
        mp(permissions.AccessContentsInformation, ['Authenticated'], 0)
        mp(permissions.ListFolderContents, ['Authenticated'], 0)

        mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'LabClerk'], 0)
        mp(permissions.DeleteObjects, ['Manager', 'LabManager'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
        portal.shipments.reindexObject()

        # Biospecimens
        mp = portal.biospecimens.manage_permission

        # Allow authenticated users to see the contents of the client folder
        mp(permissions.View, ['Authenticated'], 0)
        mp(permissions.AccessContentsInformation, ['Authenticated'], 0)
        mp(permissions.ListFolderContents, ['Authenticated'], 0)

        mp(CancelAndReinstate, ['Manager', 'LabManager', 'LabClerk'], 0)
        mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
        mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
        mp(permissions.DeleteObjects, ['Manager', 'LabManager'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'EMS'], 0)
        mp('Access contents information', ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'EMS'], 0)
        portal.biospecimens.reindexObject()

        # inventoryorders folder permissions
        mp = portal.inventoryorders.manage_permission
        mp(CancelAndReinstate, ['Manager', 'LabManager', 'LabClerk'], 0)
        mp(AddInventoryOrder,  ['Manager', 'LabManager', 'LabClerk'], 0)
        mp(DispatchInventoryOrder, ['Manager', 'LabManager', 'LabClerk'], 0)
        mp(ReceiveInventoryOrder, ['Manager', 'LabManager', 'LabClerk'], 0)
        mp(StoreInventoryOrder, ['Manager', 'LabManager', 'LabClerk'], 0)
        mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'LabClerk'], 0)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'LabClerk'], 0)
        mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
        mp(permissions.DeleteObjects, ['Manager', 'LabManager', 'LabClerk'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk'], 0)
        portal.inventoryorders.reindexObject()

        # /storage folder permissions (StorageUnits)
        mp = portal.storage.manage_permission

        # Allow authenticated users to see the contents of the storage folder
        mp(permissions.View, ['Authenticated'], 0)
        mp(permissions.AccessContentsInformation, ['Authenticated'], 0)
        mp(permissions.ListFolderContents, ['Authenticated'], 0)

        mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'LabClerk'], 0)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'LabClerk'], 0)
        mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'LabClerk'], 0)
        mp(permissions.DeleteObjects, ['Manager', 'LabManager'], 0)
        mp('Access contents information', ['Manager', 'LabManager', 'LabClerk'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk'], 0)
        portal.storage.reindexObject()


def setupCustomVarious(context):
    """ Setup Bika site structure """

    if context.readDataFile('baobab.lims.txt') is None:
        return

    portal = context.getSite()

    gen = BikaCustomGenerator()
    gen.setupGroups(portal)
    gen.setupCatalogs(portal)
    gen.setupPortalContent(portal)
    gen.setupPermissions(portal)

    # Hide some NAV folders that BioBank may not need.
    for x in ['samples',
              'referencesamples',
              'batches',
              'worksheets',
              'inventoryorders',
              'supplyorders',
              'arimports',
              'bika_setup',
              # 'virus_samples',
              'virus_aliquots',
              ]:
        obj = portal[x]
        obj.schema['excludeFromNav'].set(obj, True)
        obj.reindexObject()

    bika_setup = portal._getOb('bika_setup')
    for x in [
        'bika_artemplates',
        'bika_analysisprofiles',
        'bika_batchlabels',
        'bika_containers',
        'bika_containertypes',
        'bika_identifiertypes',
        'bika_instrumentlocations',
        'bika_instrumenttypes',
        'bika_labproducts',
        'bika_manufacturers',
        'bika_preservations',
        'bika_referencedefinitions',
        'bika_sampleconditions',
        'bika_samplematrices',
        'bika_samplepoints',
        'bika_srtemplates',
        'bika_storagelocations',
        'bika_subgroups',
        'bika_worksheettemplates',
        'bika_samplingrounds',
        'bika_clientdepartments',
        'bika_clienttypes',
        'bika_biospectypes'
    ]:
        obj = bika_setup._getOb(x)
        obj.schema['excludeFromNav'].set(obj, True)
        obj.reindexObject()

    # Set the order of the nav folders that are still visible
    for item in reversed(['clients',
                          'projects',
                          'kits',
                          'shipments',
                          'biospecimens',
                          'samplebatches',
                          'analysisrequests',
                          'pricelists',
                          'invoices',
                          'virus_samples',
                          'donors']):
        portal.moveObjectsToTop([item])
