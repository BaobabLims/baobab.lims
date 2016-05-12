""" Bika setup handlers. """

from Products.CMFCore.utils import getToolByName
from bika.lims import logger

from bika.sanbi.permissions import *


class Empty:
    pass


class BikaCustomGenerator:

    def setupPortalContent(self, portal):
        # remove undesired content objects
        for obj_id in ('kits','projectreg', 'shipments'):
            try:
                obj = portal._getOb(obj_id)
                obj.unmarkCreationFlag()
                obj.reindexObject()
            except:
                pass

        bika_setup = portal._getOb('bika_setup')
        for obj_id in ('bika_kittemplates',
                       'bika_storagemanagements',
                       'bika_biospecimens',
                       'bika_labanalyses',):
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
        at.setCatalogsByType('Kit', ['bika_catalog', 'portal_catalog'])
        at.setCatalogsByType('Project', ['bika_catalog', 'portal_catalog'])
        at.setCatalogsByType('Shipment', ['bika_catalog', 'portal_catalog'])

        # _______________________________#
        #      BIKA_SETUP_CATALOG        #
        # _______________________________#
        bsc = getToolByName(portal, 'bika_setup_catalog', None)
        if bsc is None:
            logger.warning('Could not find the bika_setup_catalog tool.')
            return
        # Add indexes and metadata columns here
        at = getToolByName(portal, 'archetype_tool')
        at.setCatalogsByType('KitTemplate', ['bika_setup_catalog',])
        at.setCatalogsByType('StorageManagement', ['bika_setup_catalog', 'portal_catalog', ])
        at.setCatalogsByType('BioSpecimen', ['bika_setup_catalog', 'portal_catalog', ])
        at.setCatalogsByType('LabAnalysis', ['bika_setup_catalog', 'portal_catalog', ])

        bac = getToolByName(portal, 'bika_analysis_catalog', None)
        if bsc is None:
            logger.warning('Could not find the bika_analysis_catalog tool.')
            return
        # Add indexes and metadata columns here

    def setupPermissions(self, portal):
        """ Set up some suggested role to permission mappings.
        """

        # Root permissions
        mp = portal.kits.manage_permission
        mp(AddKit, ['Manager', 'Owner'], 1)
        mp(ManageKits, ['Manager', 'Owner'], 1)
        portal.kits.reindexObject()

        mp = portal.shipments.manage_permission
        mp(AddShipment, ['Manager', 'Owner'], 1)
        mp(ManageShipments, ['Manager', 'Owner'], 1)
        portal.shipments.reindexObject()

def setupCustomVarious(context):
    """ Setup Bika site structure """

    if context.readDataFile('bika.sanbi.txt') is None:
        return

    portal = context.getSite()

    gen = BikaCustomGenerator()
    gen.setupCatalogs(portal)
    gen.setupPortalContent(portal)
    gen.setupPermissions(portal)
