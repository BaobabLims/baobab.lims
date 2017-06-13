from Products.Archetypes import atapi
from baobab.lims.config import PROJECTNAME
from baobab.lims.interfaces import IAliquots
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements

schema = ATFolderSchema.copy()


class Aliquots(ATFolder):
    implements(IAliquots)
    displayContentsTab = False
    schema = schema

# schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
atapi.registerType(Aliquots, PROJECTNAME)
