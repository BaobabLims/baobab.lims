from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements

from bika.sanbi.config import PROJECTNAME
from bika.sanbi.interfaces import IBiospecimens

schema = ATFolderSchema.copy()


class Biospecimens(ATFolder):
    implements(IBiospecimens)
    displayContentsTab = False
    schema = schema
    security = ClassSecurityInfo()


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
atapi.registerType(Biospecimens, PROJECTNAME)
