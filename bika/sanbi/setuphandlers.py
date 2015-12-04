""" Bika setup handlers. """

from Products.CMFCore.utils import getToolByName
from bika.lims import logger

from bika.sanbi.permissions import AddKitTemplates


class Empty:
    pass


class BikaCustomGenerator:
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

        bsc = getToolByName(portal, 'bika_catalog', None)
        if bsc is None:
            logger.warning('Could not find the bika_catalog tool.')
            return
        # Add indexes and metadata colums here

        bsc = getToolByName(portal, 'bika_setup_catalog', None)
        if bsc is None:
            logger.warning('Could not find the bika_setup_catalog tool.')
            return
        # Add indexes and metadata colums here

        bsc = getToolByName(portal, 'bika_analysis_catalog', None)
        if bsc is None:
            logger.warning('Could not find the bika_analysis_catalog tool.')
            return
        # Add indexes and metadata colums here

    def setupPermissions(self, portal):
        """ Set up some suggested role to permission mappings.
        """

        # Root permissions
        mp = portal.manage_permission

        mp(AddKitTemplates, ['Manager'], 0)

def setupCustomVarious(context):
    """ Setup Bika site structure """

    if context.readDataFile('bika.sanbi.txt') is None:
        return

    portal = context.getSite()

    gen = BikaCustomGenerator()
    gen.setupCatalogs(portal)
    gen.setupPermissions(portal)
