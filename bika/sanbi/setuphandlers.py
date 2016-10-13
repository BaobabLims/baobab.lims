""" Bika setup handlers. """

from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName

from bika.lims import logger
from bika.sanbi.permissions import *


class Empty:
    pass


class BikaCustomGenerator:
    def setupPortalContent(self, portal):
        # remove undesired content objects
        for obj_id in (
                'kits',
                'projects',
                'shipments',
                'aliquots',
                'biospecimens'):
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
                'bika_storagetypes'):

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
        # addIndex(bc, 'kit_project_uid', 'FieldIndex')
        # addIndex(bc, 'biospecimen_project_uid', 'FieldIndex')
        # addIndex(bc, 'biospecimen_kit_uid', 'FieldIndex')
        # addIndex(bc, 'aliquot_project_uid', 'FieldIndex')

        # _______________________________#
        #      BIKA_SETUP_CATALOG        #
        # _______________________________#
        bsc = getToolByName(portal, 'bika_setup_catalog', None)
        if bsc is None:
            logger.warning('Could not find the bika_setup_catalog tool.')
            return

        # Add indexes and metadata columns here
        at = getToolByName(portal, 'archetype_tool')
        at.setCatalogsByType('KitTemplate', ['bika_setup_catalog', ])
        at.setCatalogsByType('StorageManagement', ['bika_setup_catalog', ])
        at.setCatalogsByType('BiospecType', ['bika_setup_catalog', ])
        at.setCatalogsByType('Multimage', ['bika_setup_catalog', ])
        at.setCatalogsByType('StorageType', ['bika_setup_catalog', ])
        # addIndex(bsc, 'getISID', 'FieldIndex')

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
        mp(AddProject, ['Manager', 'LabManager', 'LabClerk'], 1)
        mp(ManageProjects, ['Manager', 'LabManager', 'Owner'], 1)

        # projects
        mp = portal.projects.manage_permission
        mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'Member', 'LabClerk', 'Analyst', 'Sampler', 'Preserver', 'SamplingCoordinator'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Member', 'Analyst', 'Sampler', 'Preserver', 'SamplingCoordinator', 'SamplingCoordinator'], 0)
        mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'LabClerk', 'Owner'], 0)
        mp('Access contents information', ['Manager', 'LabManager', 'Member', 'LabClerk', 'Analyst', 'Sampler', 'Preserver', 'Owner', 'SamplingCoordinator'], 0)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'LabClerk', 'Owner'], 0)
        portal.projects.reindexObject()

        # kits
        mp = portal.kits.manage_permission
        mp(AddKit, ['Manager', 'LabManager', 'Owner'], 0)
        mp(ManageKits, ['Manager', 'LabManager', 'Owner'], 0)
        mp(permissions.ListFolderContents, ['LabClerk', ''], 0)
        mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'LabClerk', 'Owner'], 0)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'Owner', 'LabClerk'], 0)
        mp(permissions.DeleteObjects, ['Manager', 'LabManager', 'Owner'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk'], 0)
        portal.kits.reindexObject()

        # shipments
        mp = portal.shipments.manage_permission
        mp(AddShipment, ['Manager', 'LabManager', 'Owner'], 0)
        mp(ManageShipments, ['Manager', 'LabManager', 'Owner'], 0)
        mp(permissions.ListFolderContents, ['LabClerk', ''], 0)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'Owner', 'LabClerk'], 0)
        mp(permissions.DeleteObjects, ['Manager', 'LabManager', 'Owner'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk'], 0)
        portal.shipments.reindexObject()

        # Biospecimens
        mp = portal.biospecimens.manage_permission
        mp(ManageAliquots, ['Manager', 'LabManager', 'Owner'], 0)
        mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'Owner'], 0)
        mp(permissions.ListFolderContents, ['LabClerk', ''], 0)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'Owner', 'LabClerk'], 0)
        mp(permissions.DeleteObjects, ['Manager', 'LabManager', 'Owner'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk'], 0)
        portal.biospecimens.reindexObject()

        # Aliquots
        mp = portal.aliquots.manage_permission
        mp(ManageAliquots, ['Manager', 'LabManager', 'Owner'], 0)
        mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'Owner'], 0)
        mp(permissions.ListFolderContents, ['LabClerk', ''], 0)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'Owner', 'LabClerk'], 0)
        mp(permissions.DeleteObjects, ['Manager', 'LabManager', 'Owner'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk'], 0)
        portal.aliquots.reindexObject()


def setupCustomVarious(context):
    """ Setup Bika site structure """

    if context.readDataFile('bika.sanbi.txt') is None:
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
              # 'invoices',
              'arimports', ]:
        obj = portal[x]
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
                          'supplyorders']):
        portal.moveObjectsToTop([item])
