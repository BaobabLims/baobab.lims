from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes.atapi import *
from plone.indexer import indexer
from zope.interface import implements
from bika.lims.content.bikaschema import BikaSchema, BikaFolderSchema
from plone.app.folder.folder import ATFolder
from bika.sanbi import bikaMessageFactory as _
from bika.sanbi.interfaces import IBiospecimen
from bika.sanbi.config import PROJECTNAME
from Products.CMFCore.utils import getToolByName
from DateTime import DateTime
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget


schema = BikaFolderSchema.copy() + BikaSchema.copy() + Schema((
    ReferenceField('Type',
        vocabulary='getBiospecTypes',
        allowed_types=('BiospecType',),
        relationship='BiospecimenBiospecType',
        required=1,
        widget=SelectionWidget(
           format='select',
           label=_("Biospecimen type"),
           visible={'view': 'invisible', 'edit': 'visible'}
        )),

    StringField('Condition',
        searchable=True,
        widget=StringWidget(
            label=_("Specimen condition"),
            description=_("A specimen condition is a 3-letter code that indicates the status of a specimen. "
                          "Eg, SAT for satisfactory."),
            visible={'edit': 'visible', 'view': 'visible'}
        )),

    ReferenceField('kit',
        vocabulary='getKits',
        allowed_types=('Kit',),
        relationship='BiospecimenKit',
        required=1,
        widget=SelectionWidget(
            format='select',
            label=_("Kit"),
            visible={'view': 'invisible', 'edit': 'visible'}
        )),

    StringField('SubjectID',
        searchable=True,
        widget=StringWidget(
            label=_("Subject ID"),
            description=_("Human-subject ID the specimen is taken from."),
            visible={'edit': 'visible', 'view': 'visible'}
        )),

    StringField('KitStockItem',
        searchable=True,
        widget=StringWidget(
            label=_("Kit Stock Item"),
            description=_("Kit corresponding stock item."),
            visible={'edit': 'visible', 'view': 'visible'}
        )),

    StringField('Barcode',
        searchable=True,
        widget=StringWidget(
            label=_("Barcode"),
            description=_("Biospecimen barcode."),
            visible={'edit': 'visible', 'view': 'visible'}
        )),

    FixedPointField('Volume',
        required=1,
        default="0.00",
        widget=DecimalWidget(
            label=_("Volume"),
            size=15,
            description=_("The The volume of the biospecimen taken from the subject."),
            visible={'edit': 'visible', 'view': 'visible'}
        )),

    StringField('Unit',
        widget=StringWidget(
            label=_("Unit"),
            visible={'edit': 'visible', 'view': 'visible'}
        )),

    ComputedField('VolumeUsed',
          expression='context.getVolumeUsed()',
          widget=ComputedWidget(
              label=_("Volume Used"),
              visible={'edit': 'invisible', 'view': 'invisible'}
          )),

    ReferenceField('StorageUnits',
        vocabulary='getStorageUnits',
        allowed_types=('StorageUnit',),
        relationship='AliquotUnit',
        widget=SelectionWidget(
            format='select',
            label=_("Rooms"),
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
            render_own_label=True,
            base_query={'inactive_state': 'active', 'review_state': 'position_free'},
            colModel=[{'columnName': 'UID', 'hidden': True},
                      {'columnName': 'Room', 'width': '15', 'label': _('Room')},
                      {'columnName': 'StorageType', 'width': '15', 'label': _('Type')},
                      {'columnName': 'Shelf', 'width': '13', 'label': _('Sh./Ca.')},
                      {'columnName': 'Box', 'width': '13', 'label': _('Box/Cane')},
                      {'columnName': 'Position', 'width': '13', 'label': _('Pos.')},
                      {'columnName': 'Title', 'width': '31', 'label': _('Address')},
                      ],
        )),

    DateTimeField(
        'DatetimeReceived',
        default_method=DateTime,
        widget=CalendarWidget(
            label='Date and Time Received',
            description='Select the date and time the biospecimen is received.',
            ampm=1,
            visible={'edit': 'visible', 'view': 'visible'}
        )),

    IntegerField(
        'Quantity',
        required=1,
        default=1,
        widget=IntegerWidget(
            label=_("Quantity"),
            size=15,
            description=_("The number of units that this sample represents."),
            visible={'edit': 'invisible', 'view': 'invisible'}
        )),
))

schema['title'].widget.visible = {'edit': 'visible', 'view': 'visible'}
schema['description'].widget.visible = {'edit': 'visible', 'view': 'visible'}
schema['description'].schemata = 'default'


@indexer(IBiospecimen)
def getBiospecimenID(instance):
    return instance.id


class Biospecimen(ATFolder):
    implements(IBiospecimen)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getBiospecTypes(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [(c.UID, c.Title) \
                 for c in bsc(portal_type='BiospecType',
                              inactive_state='active')]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(items)

    def getKits(self):
        bc = getToolByName(self, 'bika_catalog')
        items = [(c.UID, c.Title) \
                 for c in bc(portal_type='Kit',
                             inactive_state='active',
                             kit_project_uid=self.aq_parent)]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(items)


    def getDocuments(self):
        """
        Return all the multifile objects related with the instrument
        """
        return self.objectValues('Multimage')

    def getVolumeUsed(self):
        catalog = getToolByName(self, 'bika_catalog')
        # TODO: WE ARE USING AN INDEX WE CREATED, getBiospecimen. AS WE EXPERIENCED, SOMETIMES THIS NOT
        # TODO: WORKING. THEN BECARFUL.
        brains = catalog.searchResults(portal_type='Aliquot', getBiospecimen=self)
        total_volume = 0
        for brain in brains:
            obj = brain.getObject()
            quantity = int(obj.getQuantity()) if obj.getQuantity() else 0
            volume = float(obj.getVolume()) if obj.getVolume() else 0
            total_volume += float(quantity * volume)

        return total_volume

    def getStorageUnits(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [(c.UID, c.Title)
                 for c in bsc(portal_type='StorageUnit',
                              inactive_state='active')]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(items)

    def at_post_create_script(self):
        """Execute once the project is created
        """
        wftool = self.portal_workflow
        location = self.getStorageLocation()
        if location:
            wftool.doActionFor(location, action='reserve', wf_id='bika_storageposition_workflow')
            location.edit(
                IsReserved=True,
                IsOccupied=False
            )
            location.setSample(self)
            location.reindexObject()

    def workflow_script_receive(self):
        self.setDatetimeReceived(DateTime())

    def workflow_script_store(self):
        """
        """
        wftool = self.portal_workflow
        storage_location = self.getStorageLocation()
        if storage_location:
            state = wftool.getInfoFor(storage_location, 'review_state')
            if state == 'position_reserved':
                if not storage_location.getSample():
                    storage_location.setSample(self)

                storage_location.edit(
                    IsReserved=False,
                    IsOccupied=True
                )
                storage_location.reindexObject()
                wftool.doActionFor(storage_location, action='occupy', wf_id="bika_storageposition_workflow")

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
registerType(Biospecimen, PROJECTNAME)
