from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from baobab.lims.config import PROJECTNAME
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements
from baobab.lims.interfaces import ICollectionDevices

schema = ATFolderSchema.copy()

class CollectionDevices(ATFolder):
    implements(ICollectionDevices)
    displayContentsTab = False
    schema = schema

schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
atapi.registerType(CollectionDevices, PROJECTNAME)