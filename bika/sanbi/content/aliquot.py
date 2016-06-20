from Products.Archetypes.public import *
from bika.lims.content.bikaschema import BikaSchema
from Products.Archetypes.references import HoldingReference
from bika.sanbi import bikaMessageFactory as _
from AccessControl import ClassSecurityInfo
from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from bika.sanbi.interfaces import IAliquot
from bika.sanbi import config
import sys
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from Products.CMFCore import permissions

schema = BikaSchema.copy() + Schema((
    ReferenceField('Biospecimen',
        required=1,
        allowed_types=('Biospecimen',),
        relationship='BiospecimenSample',
        vocabulary_display_path_bound=sys.maxsize,
        referenceClass=HoldingReference,
        widget=bika_ReferenceWidget(
           checkbox_bound=0,
           label=_("Biospecimen"),
           description=_("Select the biospecimen from where the sample is derived"),
           size=40,
           catalog_name='bika_setup_catalog',
           showOn=True,
           visible={'edit': 'visible', 'view': 'visible'},
        )),

    StringField('SubjectID',
        searchable=True,
        widget=StringWidget(
            label=_('Subject ID'),
            description=_("The ID of the person the biospecimen is taken from."),
            visible={'edit': 'visible', 'view': 'visible'},
        )),

    FixedPointField('Volume',
        required=1,
        default="0.00",
        widget=DecimalWidget(
            label=_("Volume"),
            size=15,
            description=_("The volume of the sample taken from the biospecimen."),
        )),

    IntegerField('Quantity',
        required=1,
        default=0,
        widget=IntegerWidget(
         label=_("Quantity"),
            size=15,
         description=_("The number of units that this sample represents."),
        )),

    ReferenceField('SampleType',
        required=1,
        allowed_types=('SampleType',),
        relationship='SampleTypeSample',
        vocabulary_display_path_bound=sys.maxsize,
        referenceClass=HoldingReference,
        widget=bika_ReferenceWidget(
           checkbox_bound=0,
           label=_("Sample Type"),
           description=_("Select the type of the sample."),
           size=40,
           catalog_name='bika_setup_catalog',
           showOn=True,
           visible={'edit': 'visible', 'view': 'visible'},
        )),

    ReferenceField(
        'StorageLocation',
        allowed_types=('StorageLocation',),
        relationship='AliquotStorageLocation',
        widget=bika_ReferenceWidget(
            label=_("Storage Location"),
            description=_("Location where sample is kept"),
            size=40,
            visible={'edit': 'visible', 'view': 'visible'},
            catalog_name='bika_setup_catalog',
            showOn=True,
            base_query={'inactive_state': 'active', 'review_state': 'position_free'},
            colModel=[{'columnName': 'UID', 'hidden': True},
                      {'columnName': 'Room', 'width': '15', 'label': _('Room')},
                      {'columnName': 'StorageType', 'width': '15', 'label': _('Type')},
                      {'columnName': 'Shelf', 'width': '13', 'label': _('Sh./Ca.')},
                      {'columnName': 'Box', 'width': '13', 'label': _('Box/Cane')},
                      {'columnName': 'Position', 'width': '13', 'label': _('Pos.')},
                      {'columnName': 'Title', 'width': '31', 'label': _('Address')},
                      ],
        ),
    ),

    ReferenceField('StorageUnits',
        vocabulary='getStorageUnits',
        allowed_types=('StorageUnit',),
        relationship='AliquotUnit',
        widget=SelectionWidget(
           format='select',
           label=_("Storage Units"),
           visible={'view': 'invisible', 'edit': 'invisible'}
        )),

    ReferenceField('Freezers',
        vocabulary='getFreezers',
        allowed_types=('StorageManagement',),
        relationship='AliquotStorage',
        widget=SelectionWidget(
           format='select',
           label=_("Freezers"),
           visible={'view': 'invisible', 'edit': 'invisible'}
        )),

    ReferenceField('Shelves',
        vocabulary='getShelves',
        allowed_types=('StorageManagement',),
        relationship='AliquotStorage',
        widget=SelectionWidget(
           format='select',
           label=_("Shelves"),
           visible={'view': 'invisible', 'edit': 'invisible'}
        )),

    ReferenceField('Boxes',
        vocabulary='getBoxes',
        allowed_types=('StorageManagement',),
        relationship='AliquotStorage',
        widget=SelectionWidget(
           format='select',
           label=_("Boxes"),
           visible={'view': 'invisible', 'edit': 'invisible'}
        )),
))

schema['title'].required = True
schema['title'].widget.visible = {'view': 'visible', 'edit': 'visible'}
schema['description'].widget.visible = {'edit': 'visible', 'view': 'visible'}

class Aliquot(BaseContent):
    implements(IAliquot)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getStorageUnits(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [(c.UID, c.Title)
                 for c in bsc(portal_type='StorageUnit',
                              inactive_state='active')]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(items)

    def getFreezers(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        brains = bsc.searchResults(portal_type='StorageManagement',
                                   inactive_state='active')

        items = [(c.UID, c.Title)
                 for c in brains if c.getObject().aq_parent.portal_type=='StorageUnit']
        items.sort(lambda x, y: cmp(x[1], y[1]))

        return DisplayList(items)

    def getShelves(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        brains = bsc.searchResults(portal_type='StorageManagement',
                                   inactive_state='active')
        items = [(c.UID, c.Title)
                 for c in brains if c.getObject()
                                     .aq_parent
                                     .aq_parent
                                     .portal_type == 'StorageUnit']
        items.sort(lambda x, y: cmp(x[1], y[1]))

        return DisplayList(items)

    def getBoxes(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        brains = bsc.searchResults(portal_type='StorageManagement',
                                   inactive_state='active')
        items = [(c.UID, c.Title)
                 for c in brains if c.getObject().aq_parent
                                                 .aq_parent
                                                 .aq_parent
                                                 .portal_type == 'StorageUnit']
        items.sort(lambda x, y: cmp(x[1], y[1]))

        return DisplayList(items)

    def getPositions(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [(c.UID, c.Title)
                 for c in bsc(portal_type='StorageLocation',
                              inactive_state='active')]
        items.sort(lambda x, y: cmp(x[1], y[1]))

        return DisplayList(items)

    def guard_store_transition(self):
        """Return True if object's storage location is referenced and the actual state
           is pending. This will show a button "store sample" and allow a transition
           to "Store" state.
        """
        wftool = self.portal_workflow
        review_state = wftool.getInfoFor(self, 'review_state')
        if self.getStorageLocation() and review_state == 'pending':
            return True

        return False

    def guard_pending_transition(self):
        """Return true if object reference to any storage location and it's actual state
           'store'. In this case we have to change state a button will be shown and allow
           a transition to 'pending' state.
        """
        wftool = self.portal_workflow
        review_state = wftool.getInfoFor(self, 'review_state')

        if self.getStorageLocation() and review_state == 'stored':
            return True

        return False

    def at_post_create_script(self):
        """Execute once the object is created
        """
        wftool = self.portal_workflow
        storage_location = self.getStorageLocation()
        if self.guard_store_transition():
            state = wftool.getInfoFor(storage_location, 'review_state')
            if state != 'position_reserved':
                wftool.doActionFor(storage_location, action='reserve', wf_id='bika_storageposition_workflow')

    def at_post_edit_script(self):
        """Execute once the object is updated
        """
        wftool = self.portal_workflow
        storage_location = self.getStorageLocation()
        if self.guard_store_transition():
            state = wftool.getInfoFor(storage_location, 'review_state')
            if state != 'position_reserved':
                wftool.doActionFor(storage_location, action='reserve', wf_id='bika_storageposition_workflow')

        #TODO: DO WE NEED THIS?
        if self.guard_pending_transition():
            state = wftool.getInfoFor(storage_location, 'review_state')
            if state != 'position_occupied':
                wftool.doActionFor(storage_location, action='occupy', wf_id="bika_storageposition_workflow")

    def workflow_script_store(self):
        """
        """
        wftool = self.portal_workflow
        if self.guard_pending_transition():
            storage_location = self.getStorageLocation()
            state = wftool.getInfoFor(storage_location, 'review_state')
            if state != 'position_occupied':
                #wftool.doActionFor(storage_location, action='reserve', wf_id='bika_storageposition_workflow')
                if not storage_location.getAliquot():
                    storage_location.setAliquot(self)
                wftool.doActionFor(storage_location, action='occupy', wf_id="bika_storageposition_workflow")

    def workflow_script_pend(self):
        """
        """
        wftool = self.portal_workflow
        if self.guard_store_transition():
            storage_location = self.getStorageLocation()
            state = wftool.getInfoFor(storage_location, 'review_state')
            if state == 'position_occupied':
                storage_location.setAliquot(None)
                wftool.doActionFor(storage_location, action='reserve', wf_id='bika_storageposition_workflow')


registerType(Aliquot, config.PROJECTNAME)
