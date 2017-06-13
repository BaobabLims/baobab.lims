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
                'aliquots',
                'biospecimens',
                'inventoryorders',
                'storage',):
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
        at.setCatalogsByType('Project', ['bika_catalog'])
        at.setCatalogsByType('Shipment', ['bika_catalog'])
        at.setCatalogsByType('Aliquot', ['bika_catalog'])
        at.setCatalogsByType('Biospecimen', ['bika_catalog'])

        addIndex(bc, 'getParentUID', 'FieldIndex')
        addIndex(bc, 'getProjectUID', 'FieldIndex')

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
        at.setCatalogsByType('StorageUnit', ['bika_setup_catalog'])
        at.setCatalogsByType('ManagedStorage', ['bika_setup_catalog'])
        at.setCatalogsByType('UnmanagedStorage', ['bika_setup_catalog'])
        at.setCatalogsByType('StoragePosition', ['bika_setup_catalog'])

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
        mp(AddMultimage, ['Manager', 'LabManager', 'LabClerk'], 1)
        mp(EditFieldBarcode, ['Manager', 'LabManager', 'LabClerk'], 1)
        mp(ViewBarcode, ['Manager', 'LabManager', 'LabClerk'], 1)
        mp(AddStorageType, ['Manager', 'LabManager', 'LabClerk'], 1)
        mp(AddKitTemplate, ['Manager', 'LabManager', 'LabClerk'], 1)
        mp(ManageProjects, ['Manager', 'LabManager', 'Owner'], 1)
        mp(ManageShipments, ['Manager', 'LabManager', 'Owner', 'Member'], 1)
        mp(ManageKits, ['Manager', 'LabManager', 'LabClerk'], 1)
        mp(ManageAliquots, ['Manager', 'LabManager', 'LabClerk'], 1)
        mp(AddProject, ['Manager', 'LabManager', 'LabClerk'], 1)
        mp(AddKit, ['Manager', 'LabManager', 'LabClerk'], 1)
        mp(AddShipment, ['Manager', 'LabManager', 'LabClerk'], 1)
        mp(AddStorageUnit, ['Manager', 'Owner', 'LabManager', ], 1)
        mp(AddManagedStorage, ['Manager', 'Owner', 'LabManager', ], 1)
        mp(AddUnmanagedStorage, ['Manager', 'Owner', 'LabManager', ], 1)
        mp(AddStoragePosition, ['Manager', 'Owner', 'LabManager', ], 1)

        # projects
        mp = portal.projects.manage_permission
        mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'Member', 'LabClerk', 'Analyst'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Member', 'Analyst'], 0)
        mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'LabClerk'], 0)
        mp('Access contents information', ['Manager', 'LabManager', 'Member', 'LabClerk', 'Analyst'], 0)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'LabClerk'], 0)
        portal.projects.reindexObject()

        # kits
        mp = portal.kits.manage_permission
        mp(AddKit, ['Manager', 'LabManager', 'LabClerk'], 0)
        mp(ManageKits, ['Manager', 'LabManager', 'LabClerk'], 0)
        mp(permissions.ListFolderContents, ['Manager', 'LabClerk'], 0)
        mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'LabClerk', 'Owner'], 0)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'Owner', 'LabClerk'], 0)
        mp(permissions.DeleteObjects, ['Manager', 'LabManager', 'Owner'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk'], 0)
        portal.kits.reindexObject()

        # shipments
        mp = portal.shipments.manage_permission
        mp(AddShipment, ['Manager', 'LabManager', 'LabClerk'], 0)
        mp(ManageShipments, ['Manager', 'LabManager', 'Member'], 0)
        mp(permissions.ListFolderContents, ['Manager', 'LabClerk'], 0)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'LabClerk'], 0)
        mp(permissions.DeleteObjects, ['Manager', 'LabManager', 'Owner'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk'], 0)
        portal.shipments.reindexObject()

        # Biospecimens
        mp = portal.biospecimens.manage_permission
        mp(ManageAliquots, ['Manager', 'LabManager', 'LabClerk'], 0)
        mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'Owner'], 0)
        mp(permissions.ListFolderContents, ['LabClerk', ''], 0)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'Owner', 'LabClerk'], 0)
        mp(permissions.DeleteObjects, ['Manager', 'LabManager', 'Owner'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk'], 0)
        portal.biospecimens.reindexObject()

        # Aliquots
        mp = portal.aliquots.manage_permission
        mp(ManageAliquots, ['Manager', 'LabManager', 'LabClerk'], 0)
        mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'Owner'], 0)
        mp(permissions.ListFolderContents, ['LabClerk', ''], 0)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'Owner', 'LabClerk'], 0)
        mp(permissions.DeleteObjects, ['Manager', 'LabManager', 'Owner'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk'], 0)
        portal.aliquots.reindexObject()

        # inventoryorders folder permissions
        mp = portal.inventoryorders.manage_permission
        mp(CancelAndReinstate, ['Manager', 'LabManager', 'LabClerk'], 0)
        mp(AddInventoryOrder,  ['Manager', 'LabManager', 'Owner', 'LabClerk'], 1)
        mp(DispatchInventoryOrder, ['Manager', 'LabManager', 'Owner', 'LabClerk'], 1)
        mp(ReceiveInventoryOrder, ['Manager', 'LabManager', 'Owner', 'LabClerk'], 1)
        mp(StoreInventoryOrder, ['Manager', 'LabManager', 'LabClerk', 'Owner'], 1)
        mp(permissions.ListFolderContents, ['Member'], 1)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'Owner', 'LabClerk'], 0)
        mp(permissions.DeleteObjects, ['Manager', 'LabManager', 'Owner', 'LabClerk'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk'], 0)
        portal.inventoryorders.reindexObject()

        # /storage folder permissions (StorageUnits)
        mp = portal.storage.manage_permission
        mp(CancelAndReinstate, ['Manager', 'LabManager', 'LabClerk'], 0)
        mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 0)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'Owner'], 0)
        mp(permissions.DeleteObjects, ['Manager', 'LabManager', 'Owner'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk'], 0)
        portal.invoices.reindexObject()


def setupCustomVarious(context):
    """ Setup Bika site structure """

    if context.readDataFile('baobab.lims.txt') is None:
        return

    portal = context.getSite()

    gen = BikaCustomGenerator()
    gen.setupCatalogs(portal)
    gen.setupPortalContent(portal)
    gen.setupPermissions(portal)

    # Hide some NAV folders that BioBank may not need.
    for x in ['samples',
              'referencesamples',
              'batches',
              'worksheets',
              'methods',
              'inventoryorders',
              'supplyorders',
              'arimports',
              'bika_setup',
              ]:
        obj = portal[x]
        obj.schema['excludeFromNav'].set(obj, True)
        obj.reindexObject()

    bika_setup = portal._getOb('bika_setup')
    for x in [
        'bika_analysiscategories',
        'bika_analysisspecs',
        'bika_arpriorities',
        'bika_artemplates',
        'bika_analysisprofiles',
        'bika_attachmenttypes',
        'bika_batchlabels',
        'bika_containers',
        'bika_containertypes',
        'bika_identifiertypes',
        'bika_instrumentlocations',
        'bika_instrumenttypes',
        'bika_labcontacts',
        'bika_departments',
        'bika_labproducts',
        'bika_manufacturers',
        'bika_preservations',
        'bika_referencedefinitions',
        'bika_sampleconditions',
        'bika_samplematrices',
        'bika_samplingdeviations',
        'bika_samplepoints',
        'bika_srtemplates',
        'bika_storagelocations',
        'bika_subgroups',
        'bika_worksheettemplates',
        'bika_samplingrounds',
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
                          'aliquots',
                          'analysisrequests',
                          'pricelists',
                          'invoices']):
        portal.moveObjectsToTop([item])
