from AccessControl import ClassSecurityInfo

from Products.Archetypes.public import *
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from plone.app.folder.folder import ATFolder
from zope.interface import implements

from bika.lims.content.bikaschema import BikaFolderSchema

from baobab.lims.browser.storage import getStorageTypes
from baobab.lims.interfaces import IUnmanagedStorage
from baobab.lims import bikaMessageFactory as _
from baobab.lims.config import PROJECTNAME

Containers = StringField(
    'Containers',
    widget=StringWidget(
        label=_('Containers'),
        description=_('If storage at this location is restricted to specific '
                      'containers, specify them here.'),
    ),
)

FreePositions = ComputedField(
    'FreePositions',
    expression="'Yes'"
)

Hierarchy = ComputedField(
    'Hierarchy',
    expression="here.getHierarchy()"
)

schema = BikaFolderSchema.copy() + Schema((
    Containers,
    FreePositions,
    Hierarchy,
))


class UnmanagedStorage(ATFolder):
    implements(IUnmanagedStorage)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema
    _at_rename_after_creation = False  # the viewlet handles this

    def Title(self):
        return safe_unicode(self.getField('title').get(self)).encode('utf-8')

    def getHierarchy(self, structure=False, separator='.', fieldname='id'):
        hierarchy = []
        item = self
        while (1):
            try:
                accessor = getattr(item, fieldname).getAccessor()
                val = accessor() if callable(accessor) else accessor
            except AttributeError:
                val = getattr(item, fieldname)
            # Don't report on the /storage folder
            if item.portal_type == 'StorageUnits':
                break
            url = "<a href='%s'>%s</a>" % (item.absolute_url(), val)
            hierarchy.append(url if structure else val)
            item = item.aq_parent
        return separator.join(reversed(hierarchy))

    def getStorageTypes(self, show_all=False):
        """Return a list of types of storage which are supported here.
        """
        types = getStorageTypes()
        if not show_all:
            types = [x for x in types if x['interface'].providedBy(self)]
        return types

    def guard_occupy_transition(self):
        """Occupy transition signifies that this storage level cannot accept
        further items for storage.

        For unmanaged storages, this transition is not invoked automatically,
        because we don't know how many items can be stored here.
        """
        return True

    def guard_liberate_transition(self):
        """Liberate transition means this level can now be selected as
        an item's storage location.

        For un-managed storage levels this transition is always available.
        """
        return True

    def available(self):
        wf = getToolByName(self, 'portal_workflow')
        return True if wf.getInfoFor(self, 'review_state') == 'available' \
            else False


registerType(UnmanagedStorage, PROJECTNAME)
