from Products.Archetypes import atapi
from bika.lims.config import PROJECTNAME as BIKALIMS_PROJECTNAME
from bika.lims.interfaces import IStorageLocation
from zope.component import adapts
from archetypes.schemaextender.interfaces import ISchemaExtender
from bika.lims.fields import implements
from bika.lims.content.storagelocation import StorageLocation as BaseLocation
from bika.lims.fields import ExtComputedField, ComputedWidget
from bika.sanbi import bikaMessageFactory as _

class StorageLocationSchemaExtender(object):
    adapts(IStorageLocation)
    implements(ISchemaExtender)

    fields = [
        ExtComputedField(
            'isOccupied',
            expression='context.is_occupied()',
            widget=ComputedWidget(
                label=_("Position Free?"),
                description=_("Return if the position in stock is free, i.e, not reserved or "
                              "occupied"))
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

class StorageLocation(BaseLocation):
    """ Inherits from bika.lims.content.StorageLocation
    """
    def getChain(self):
        chain = []
        ancestor = self

        portal_types = []
        for o in ancestor.aq_chain:
            if hasattr(o, 'portal_type'):
                portal_types.append(o.portal_type)

        if not 'StorageUnit' in portal_types:
            return ''

        for obj in ancestor.aq_chain:
            chain.append(obj)
            if obj.portal_type == 'StorageUnit':
                break

        return chain

    def getHierarchy(self, char='>'):
        ancestors = []
        ancestor = self

        portal_types = []
        for o in ancestor.aq_chain:
            if hasattr(o, 'portal_type'):
                portal_types.append(o.portal_type)

        if not 'StorageUnit' in portal_types:
            return ''

        for obj in ancestor.aq_chain:
            ancestors.append(obj.getId())
            if obj.portal_type == 'StorageUnit':
                break

        return char.join(reversed(ancestors))

    def guard_occupy_transition(self):
        """
        """
        wftool = self.portal_workflow
        review_state = wftool.getInfoFor(self, 'review_state')
        if self.getSampletemp() and (review_state == 'position_free' or
                                     review_state == 'position_reserved'):
            return True

        return False

    def guard_free_transition(self):
        """
        Return true if object has no reference to any stock item and
        it is in 'position_occupied'. In this case we have to liberate
        the position.
        """
        wftool = self.portal_workflow
        review_state = wftool.getInfoFor(self, 'review_state')

        if not self.getSampletemp() and review_state in ('position_occupied', 'position_reserved'):
            return True

        return False

    def at_post_create_script(self):
        """Execute once the object is created
        """
        wftool = self.portal_workflow
        if self.guard_occupy_transition():
            wftool.doActionFor(self, action='occupy', wf_id='bika_storageposition_workflow')

    def at_post_edit_script(self):
        """Execute once the object is edited
        """
        wftool = self.portal_workflow

        if self.guard_free_transition():
            wftool.doActionFor(self, action='free', wf_id='bika_storageposition_workflow')

        if self.guard_occupy_transition():
            wftool.doActionFor(self, action='occupy', wf_id='bika_storageposition_workflow')

# overrides bika.lims.content.StorageLocation
atapi.registerType(StorageLocation, BIKALIMS_PROJECTNAME)