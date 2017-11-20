from AccessControl import ClassSecurityInfo

from Products.Archetypes.public import *
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from plone.app.folder.folder import ATFolder
from zope.interface import implements

from bika.lims.content.bikaschema import BikaFolderSchema

from baobab.lims.browser.storage import getStorageTypes
from baobab.lims.interfaces import IManagedStorage
from baobab.lims import bikaMessageFactory as _
from baobab.lims.config import PROJECTNAME

Containers = StringField(
    'Containers',
    widget=StringWidget(
        label=_('Containers'),
        description=_('If storage at this location is restricted to specific '
                      'containers, specify them here.'),
    )
)

FreePositions = ComputedField(
    'FreePositions',
    expression="len(here.get_free_positions())"
)

Hierarchy = ComputedField(
    'Hierarchy',
    expression="here.getHierarchy()"
)

# ____Shelves representation____ #
XAxis = IntegerField(
    'XAxis',
    widget=IntegerWidget(
        label=_("Number of rows"),
        description=_("Specify the number of rows in a layer."),
        visible=False
    )
)

YAxis = IntegerField(
    'YAxis',
    widget=IntegerWidget(
        label=_("Number of columns"),
        description=_("Specify the number of columns in a layer."),
        visible=False,
    )
)

schema = BikaFolderSchema.copy() + Schema((
    Containers,
    FreePositions,
    Hierarchy,
    XAxis,
    YAxis,
))


class ManagedStorage(ATFolder):
    implements(IManagedStorage)
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

    def available(self):
        wf = getToolByName(self, 'portal_workflow')
        return True if wf.getInfoFor(self, 'review_state') == 'available' \
            else False

    def get_positions(self):
        pc = getToolByName(self, 'portal_catalog')
        path = "/".join(self.getPhysicalPath())
        brains = pc.searchResults(
            portal_type='StoragePosition',
            inactive_state='active',
            sort_on='sortable_title',
            path={'query': path, 'level': 0})

        return [brain.getObject() for brain in brains]

    def get_free_positions(self):
        bsc = getToolByName(self, 'portal_catalog')
        path = "/".join(self.getPhysicalPath())
        brains = bsc.searchResults(
            portal_type='StoragePosition',
            inactive_state='active',
            sort_on='sortable_title',
            review_state='available',
            path={'query': path, 'level': 0}
        )

        return [brain.getObject() for brain in brains]

    def only_items_of_portal_type(self, portal_type):
        """ Return items of a @portal_type stored in this storage.
        """
        positions = self.get_positions()
        items = []
        for position in positions:
            item = position.getStoredItem()
            if item and item.portal_type == portal_type:
                items.append(item)

        return items
    
    def guard_occupy_transition(self):
        """Occupy transition signifies that this storage level cannot accept
        further items for storage.

        For managed storage levels, this transition is allowed when all
        available storage locations are occupied.
        """
        if not self.get_free_positions():
            return True
        return False

    def guard_liberate_transition(self):
        """Liberate transition means this storage can now be selected as
        an item's storage location.

        For managed storage levels, this transition is allowed when some
        available storage locations are available.
        """
        wf = getToolByName(self, 'portal_workflow')
        if self.get_free_positions():
            return True
        return False


registerType(ManagedStorage, PROJECTNAME)
