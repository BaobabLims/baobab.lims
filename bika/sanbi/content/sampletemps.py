from Products.Archetypes import atapi
from bika.sanbi.config import PROJECTNAME
from bika.sanbi.interfaces import ISampletemps
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements

schema = ATFolderSchema.copy()


class Sampletemps(ATFolder):
    implements(ISampletemps)
    displayContentsTab = False
    schema = schema

# schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
atapi.registerType(Sampletemps, PROJECTNAME)
