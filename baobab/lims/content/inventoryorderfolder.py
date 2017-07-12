"""Order Folder contains Orders for Inventory
"""
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from baobab.lims.config import PROJECTNAME
from AccessControl import ClassSecurityInfo
from baobab.lims.interfaces import IInventoryOrderFolder
from bika.lims.interfaces import IHaveNoBreadCrumbs

from plone.app.folder import folder
from zope.interface import implements

schema = folder.ATFolderSchema.copy()


class InventoryOrderFolder(folder.ATFolder):
    implements(IInventoryOrderFolder, IHaveNoBreadCrumbs)
    schema = schema
    displayContentsTab = False
    security = ClassSecurityInfo()

schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)

atapi.registerType(InventoryOrderFolder, PROJECTNAME)
