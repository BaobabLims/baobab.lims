from Products.Archetypes import atapi
from bika.sanbi.config import PROJECTNAME
from bika.sanbi.interfaces import IAliquots
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements

schema = ATFolderSchema.copy()


class Aliquots(ATFolder):
    implements(IAliquots)
    displayContentsTab = False
    schema = schema

# schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
atapi.registerType(Aliquots, PROJECTNAME)
