from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from plone.app.folder import folder
from zope.interface import implements

from bika.lims.interfaces import IHaveNoBreadCrumbs

from baobab.lims.config import PROJECTNAME
from baobab.lims.interfaces import IStorageUnits

schema = folder.ATFolderSchema.copy()


class StorageUnits(folder.ATFolder):
    implements(IStorageUnits, IHaveNoBreadCrumbs)
    displayContentsTab = False
    schema = schema
    security = ClassSecurityInfo()


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)

atapi.registerType(StorageUnits, PROJECTNAME)
