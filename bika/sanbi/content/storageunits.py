from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from plone.app.folder import folder
from zope.interface import implements

from bika.lims.interfaces import IHaveNoBreadCrumbs

from bika.sanbi.browser.storage import getStorageTypes
from bika.sanbi.config import PROJECTNAME
from bika.sanbi.interfaces import IStorageUnits

schema = folder.ATFolderSchema.copy()


class StorageUnits(folder.ATFolder):
    implements(IStorageUnits, IHaveNoBreadCrumbs)
    displayContentsTab = False
    schema = schema
    security = ClassSecurityInfo()

    def getStorageTypes(self, show_all=False):
        """Return a list of types of storage which are supported here.
        """
        types = getStorageTypes()
        if not show_all:
            types = [x for x in types if x['interface'].providedBy(self)]
        return types


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)

atapi.registerType(StorageUnits, PROJECTNAME)
