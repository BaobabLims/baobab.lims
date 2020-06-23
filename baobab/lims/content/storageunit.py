from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.content import schemata
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.utils import getToolByName
from plone.app.folder.folder import ATFolder
from zope.interface import implements

from bika.lims.content.bikaschema import BikaFolderSchema

from baobab.lims import bikaMessageFactory as _
from baobab.lims.config import PROJECTNAME
from baobab.lims.browser.storage import getStorageTypesByName
from baobab.lims.interfaces import IStorageUnit

schema = BikaFolderSchema.copy() + Schema((
    StringField(
        'Temperature',
        widget=StringWidget(
            label=_('Temperature'),
        )
    ),
    ReferenceField(
        'Department',
        allowed_types=('Department',),
        relationship='StorageUnitDepartment',
        vocabulary='getDepartments',
        referenceClass=HoldingReference,
        widget=ReferenceWidget(
            checkbox_bound=0,
            label=_('Department'),
            description=_('The laboratory department'),
        ),
    ),
    ReferenceField(
        'UnitType',
        allowed_types=('StorageType',),
        relationship='StorageUnitType',
        vocabulary='getUnitTypes',
        referenceClass=HoldingReference,
        widget=ReferenceWidget(
            checkbox_bound=0,
            label=_('Storage Type'),
            description=_('Select the type of the storage units.'),
        ),
    ),
))

schema['description'].schemata = 'default'
schema['description'].widget.visible = True


class StorageUnit(ATFolder):
    security = ClassSecurityInfo()
    implements(IStorageUnit)
    schema = schema

    # _at_rename_after_creation = True
    #
    # def _renameAfterCreation(self, check_auto_id=False):
    #     from bika.lims.idserver import renameAfterCreation
    #     renameAfterCreation(self)

    def getDepartments(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        result = []
        for r in bsc(portal_type='Department',
                     inactive_state='active'):
            result.append((r.UID, r.Title))
        return DisplayList(result)

    def getDepartmentTitle(self):
        return self.getDepartment() and self.getDepartment().Title() or ''

    def getStorageTypes(self, name_adapter, show_all=False):
        """Return a list of types of storage which are supported here.
        """
        types = getStorageTypesByName(name_adapter)
        if not show_all:
            types = [x for x in types if x['interface'].providedBy(self)]
        return types

    def getUnitTypes(self):
        """Return the unit storage types
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        result = []
        for r in bsc(portal_type='StorageType',
                     inactive_state='active'):
            result.append((r.UID, r.Title))
        return DisplayList(result)

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

    def getBoxes(self):
        available_boxes = []

        storage_positions = self.get_positions()
        for position in storage_positions:
            if position.aq_parent not in available_boxes:
                available_boxes.append(position.aq_parent)

        return available_boxes

    def get_positions(self):
        available_storage_positions = []

        pc = getToolByName(self, 'portal_catalog')
        brains = pc(portal_type='StoragePosition')

        for brain in brains:

            storage_position = brain.getObject()

            if self.is_ancestor_of(storage_position):
                available_storage_positions.append(storage_position)

        return available_storage_positions

    def is_ancestor_of(self, storage_position):
        '''
        Determine if the current storage unit is an ancestor of the storage position
        being passed in as an argument
        :param storage_position:
        :return: boolean
        '''

        is_ancestor = False
        item = storage_position
        while True:

            if item.UID() == self.UID():
                is_ancestor = True
                break

            # Don't report on the /storage folder
            if item.portal_type == 'StorageUnits':
                break

            item = item.aq_parent

        return is_ancestor

    def workflow_script_deactivate(self):
        # Deactivate all sub objects in the hierarchy
        catalog = getToolByName(self, 'portal_catalog')
        unit_path = '/'.join(self.getPhysicalPath())
        units = catalog(portal_type=['StorageUnit', 'UnmanagedStorage', 'ManagedStorage'],
                        path={'query': unit_path, 'level': 0})
        for unit in units:
            obj = unit.getObject()
            review_state = self.portal_workflow.getInfoFor(obj, 'inactive_state')
            if review_state == 'active':
                self.portal_workflow.doActionFor(obj, 'deactivate')

schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
registerType(StorageUnit, PROJECTNAME)
