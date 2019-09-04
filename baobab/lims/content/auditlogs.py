from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements

from baobab.lims.config import PROJECTNAME
from baobab.lims.interfaces import IAuditLogs

schema = ATFolderSchema.copy()


class AuditLogs(ATFolder):
    implements(IAuditLogs)
    displayContentsTab = False
    schema = schema
    # security = ClassSecurityInfo()


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
atapi.registerType(AuditLogs, PROJECTNAME)
