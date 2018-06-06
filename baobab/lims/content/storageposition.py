from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from zope.interface import implements

from bika.lims.content.bikaschema import BikaSchema

from baobab.lims.browser.storage import getStorageTypes
from baobab.lims.interfaces import IStoragePosition
from baobab.lims.config import PROJECTNAME
from baobab.lims import bikaMessageFactory as _

Hierarchy = ComputedField(
    'Hierarchy',
    expression="here.getHierarchy()"
)

schema = BikaSchema.copy() + Schema((
    Hierarchy,
))
schema['title'].widget.label = _('Address')
schema['description'].widget.visible = True


class StoragePosition(BaseContent):
    implements(IStoragePosition)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

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

    def getStoredItem(self):
        items = self.getBackReferences('ItemStorageLocation')
        wf_tool = getToolByName(self, 'portal_workflow')
        review_state = wf_tool.getInfoFor(self, 'review_state')
        if items:
            if review_state == 'available':
                wf_tool.doActionFor(self.aq_inner, 'occupy')
                self.reindexObject(idxs=["review_state", ])
            return items[0]
        elif review_state == 'occupied':
            wf_tool.doActionFor(self.aq_inner, 'liberate')
            self.reindexObject(idxs=["review_state", ])
        return None

    def guard_occupy_transition(self):
        """Occupy transition cannot proceed until StoredItem is set.

        If this position is available and StoredItem set,
        then we will prevent the occupy transition from becoming available.
        """

        wftool = self.portal_workflow
        review_state = wftool.getInfoFor(self, 'review_state')
        if (review_state == 'available' or review_state == 'reserved') \
                and self.getStoredItem():
            return True
        return False

    def guard_liberate_transition(self):
        """Liberate transition cannot proceed unless StoredItem is cleared.

        If this position is occupied and StoredItem still has a value,
        then we will prevent the liberate transition from becoming available.
        """
        wftool = self.portal_workflow
        review_state = wftool.getInfoFor(self, 'review_state')
        if review_state in ('occupied', 'reserved') \
                and not self.getStoredItem():
            return True
        return False

    def workflow_script_liberate(self):
        """If possible, liberate the parent storage.
        """
        wf = getToolByName(self, 'portal_workflow')
        tids = [t['id'] for t in wf.getTransitionsFor(self.aq_parent)]

        sample = self.getStoredItem()
        if sample:
            sample.setStorageLocation('')
            sample.reindexObject()

            storage_state = wf.getInfoFor(self, 'review_state')
            if storage_state != 'available':
                wf.doActionFor(self, 'liberate')

        if 'liberate' in tids:
            wf.doActionFor(self.aq_parent, 'liberate')

    def available(self):
        wf = getToolByName(self, 'portal_workflow')
        return wf.getInfoFor(self, 'review_state') == 'available'

    def at_post_create_script(self):
        """Execute once the object is created
        """
        wftool = self.portal_workflow
        if self.guard_occupy_transition():
            wftool.doActionFor(
                self, action='occupy', wf_id='bika_storage_workflow')

    def at_post_edit_script(self):
        """Execute once the object is edited
        """
        wftool = self.portal_workflow
        if self.guard_liberate_transition():
            wftool.doActionFor(
                self, action='liberate', wf_id='bika_storage_workflow')
        if self.guard_occupy_transition():
            wftool.doActionFor(
                self, action='occupy', wf_id='bika_storage_workflow')


registerType(StoragePosition, PROJECTNAME)

def ObjectModifiedEventHandler(instance, event):
    """Execute after each object modification?!
    """