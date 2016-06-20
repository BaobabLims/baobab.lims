from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes.atapi import *
from zope.interface import implements
from bika.lims.content.bikaschema import BikaSchema, BikaFolderSchema
from bika.lims.browser.widgets import DateTimeWidget as bika_DateTimeWidget
from plone.app.folder.folder import ATFolder
from bika.sanbi import bikaMessageFactory as _
from bika.sanbi.interfaces import IBiospecimen
from bika.sanbi.config import PROJECTNAME
from Products.CMFCore.utils import getToolByName
from DateTime import DateTime
from plone.formwidget.datetime.at import DatetimeWidget

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
                          "Eg, SAT for satisfactory.")
        )),

    StringField('SubjectID',
        searchable=True,
        widget=StringWidget(
            label=_("Subject ID"),
            description=_("Human-subject ID the specimen is taken from.")
        )),

    # StringField('Volume',
    #     widget=StringWidget(
    #         label=_("Volume"),
    #     )),

    FixedPointField('Volume',
        required=1,
        default="0.00",
        widget=DecimalWidget(
            label=_("Volume"),
            size=15,
            description=_("The The volume of the biospecimen taken from the subject."),
        )),

    StringField('Unit',
        widget=StringWidget(
            label=_("Unit"),
        )),

    # DateTimeField('dateReceived',
    #     searchable=1,
    #     widget=bika_DateTimeWidget(
    #         label='Date Received'
    #     )),

    DateTimeField('datetimeReceived',
          default_method=DateTime,
          widget=CalendarWidget(
              label='Date and Time Received',
              description='Select the date and time the biospecimen is received.',
              ampm=1,
          )),

    ComputedField('VolumeUsed',
          expression='context.getVolumeUsed()',
          widget=ComputedWidget(
              label=_("VAT"),
              visible={'edit': 'hidden',}
          ))
))

schema['description'].widget.visible = True
schema['description'].schemata = 'default'

@indexer(IBioSpecimen)
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

    def getDocuments(self):
        """
        Return all the multifile objects related with the instrument
        """
        return self.objectValues('Multimage')

    def getVolumeUsed(self):
        catalog = getToolByName(self, 'bika_catalog')
        brains = catalog.searchResults(portal_type='Sampletemp',
                                       getBiospecimenID=self.id)
        total_volume = 0
        for brain in brains:
            obj = brain.getObject()
            quantity = int(obj.getQuantity()) if obj.getQuantity() else 0
            volume = float(obj.getVolume()) if obj.getVolume() else 0
            total_volume += float(quantity * volume)

        return total_volume

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
registerType(Biospecimen, PROJECTNAME)
