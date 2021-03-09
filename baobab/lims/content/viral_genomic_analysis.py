from Products.Archetypes.references import HoldingReference
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore import permissions
from Products.CMFPlone.interfaces import IConstrainTypes
from zope.interface import implements
from bika.lims.browser.widgets import DateTimeWidget

from bika.lims.content.bikaschema import BikaSchema
from baobab.lims import bikaMessageFactory as _
from baobab.lims import config
from baobab.lims.interfaces import IViralGenomicAnalysis
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from Products.CMFPlone.utils import safe_unicode

Project = ReferenceField(
    'Project',
    # schemata='General Info',
    allowed_types=('Project',),
    relationship='ViralGenomicAnalysisProjects',
    referenceClass=HoldingReference,
    widget=bika_ReferenceWidget(
        label=_("Select Project"),
        visible={'edit': 'visible', 'view': 'visible'},
        size=30,
        showOn=True,
        description=_("Select the project for the viral genomic analysis."),
    )
)

DateCreated = DateTimeField(
    'DateCreated',
    mode="rw",
    # schemata='General Info',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=DateTimeWidget(
        label=_("Date Created"),
        description=_("Define when the Viral Genomic Analysis has been created."),
        show_time=True,
        visible={'edit': 'visible', 'view': 'visible'}
    )
)

WillExtract = BooleanField(
    'WillExtract',
    # required=1,
    # schemata='General Info',
    default=False,
    widget=BooleanWidget(
        label="Will Extract",
        description="Whether or not to Extract Genomic Material",
        visible={'edit': 'visible', 'view': 'visible'}
    )
)

WillAliquot = BooleanField(
    'WillAliquot',
    # required=1,
    # schemata='General Info',
    default=False,
    widget=BooleanWidget(
        label="Aliquoting",
        description="Whether new Aliquots will be created",
        visible={'edit': 'visible', 'view': 'visible'}
    )
)

WillQuantify = BooleanField(
    'WillQuantify',
    # required=1,
    # schemata='General Info',
    default=False,
    widget=BooleanWidget(
        label="Will Quantify",
        description="Whether Quantifying will occur",
        visible={'edit': 'visible', 'view': 'visible'}
    )
)

WillViralLoadDetermine = BooleanField(
    'WillViralLoadDetermine',
    # required=1,
    # schemata='General Info',
    default=False,
    widget=BooleanWidget(
        label="Confirm Viral Load Determine",
        description="Whether viral load will be determined",
        visible={'edit': 'visible', 'view': 'visible'}
    )
)

WillLibraryPrep = BooleanField(
    'WillLibraryPrep',
    # schemata='General Info',
    # required=1,
    default=False,
    widget=BooleanWidget(
        label="Confirm Sequence Library Prep",
        description="Confirm if there will be Sequence Library Prep",
        visible={'edit': 'visible', 'view': 'visible'}
    )
)

ExtractGenomicMaterial = ReferenceField(
    'ExtractGenomicMaterial',
    schemata='Extract Genomic Material',
    multiValued=1,
    allowed_types=('ExtractGenomicMaterial',),
    relationship='ViralGenomicAnalysisExtractGenomicMaterial',
    referenceClass=HoldingReference,
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=bika_ReferenceWidget(
        label=_("Select Extract Genomic Material"),
        visible={'edit': 'visible', 'view': 'visible'},
        size=30,
        showOn=True,
        description=_("Select the Extract Genomic Material for the viral genomic analysis."),
    )
)

VirusAliquot = ReferenceField(
    'VirusAliquot',
    schemata='Virus Sample Aliquot',
    multiValued=1,
    allowed_types=('VirusAliquot',),
    relationship='ViralGenomicAnalysisVirusAliquot',
    referenceClass=HoldingReference,
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=bika_ReferenceWidget(
        label=_("Select Virus Aliquot"),
        visible={'edit': 'visible', 'view': 'visible'},
        size=30,
        showOn=True,
        description=_("Select the Virus Aliquot for the viral genomic analysis."),
    )
)


schema = BikaSchema.copy() + Schema((
    Project,
    DateCreated,
    WillExtract,
    WillAliquot,
    WillQuantify,
    WillViralLoadDetermine,
    WillLibraryPrep,
    ExtractGenomicMaterial,
    VirusAliquot,
))

schema['title'].widget.visible = {'view': 'visible', 'edit': 'visible'}
schema['description'].widget.visible = {'view': 'visible', 'edit': 'visible'}

class ViralGenomicAnalysis(BaseContent):
    security = ClassSecurityInfo()
    implements(IViralGenomicAnalysis, IConstrainTypes)
    displayContentsTab = False
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    # def prepare_extract_genomic_material(self):
    #
    #     extract_genomic_material_rows = self.getExtractGenomicMaterial()
    #     prepared_extracts = []
    #
    #     for extract in extract_genomic_material_rows:
    #         prepared_extract = {
    #             'title': extract.Title(),
    #             'virus_sample': self.get_virus_sample(extract),
    #             'heat_inactivated': extract.getField('HeatInactivated').get(extract),
    #             'method': self.get_method(extract),
    #             'extraction_barcode': extract.getField('ExtractionBarcode').get(extract),
    #             'volume': extract.getField('Volume').get(extract),
    #             'unit': extract.getField('Unit').get(extract),
    #             'was_kit_used': extract.getField('WasKitUsed').get(extract),
    #             'kit_number': extract.getField('KitNumber').get(extract),
    #             'notes': extract.getField('Notes').get(extract),
    #         }
    #         prepared_extracts.append(prepared_extract)
    #
    #     return prepared_extracts

    def prepare_virus_aliquots(self):
        virus_aliquots = self.getVirusAliquot()
        virus_aliquots_dict = {}

        for virus_aliquot in virus_aliquots:
            parent_sample = self.get_parent_sample(virus_aliquot)
            prepared_aliquot_list = self.get_prepared_aliquots(virus_aliquot.getAliquotSample())
            virus_aliquots_dict[parent_sample] = prepared_aliquot_list

        return virus_aliquots_dict

    def get_prepared_aliquots(self, aliquot_rows):
        prepared_aliquots = []

        for aliquot in aliquot_rows:
            prepared_extract = {
                "barcode": aliquot.getField('Barcode').get(aliquot),
                "volume": aliquot.getField('Volume').get(aliquot),
                "unit": aliquot.getField('Unit').get(aliquot),
                "sample_type": self.get_sample_type(aliquot),
                'date_created': aliquot.getField('DateCreated').get(aliquot).strftime("%Y-%m-%d"),
                'time_created': aliquot.getField('DateCreated').get(aliquot).strftime("%H:%M:%S"),
                # 'date_created': aliquot.getField('DateCreated').get(aliquot),
            }
            prepared_aliquots.append(prepared_extract)

        return prepared_aliquots

    def get_virus_sample(self, extract):
        try:
            virus_sample = extract.getField('VirusSample').get(extract)
            return virus_sample.Title()
        except:
            return ''

    def get_parent_sample(self, virus_aliquot):
        try:
            parent_sample = virus_aliquot.getField('ParentSample').get(virus_aliquot)
            return parent_sample.Title()
        except:
            return ''

    def get_sample_type(self, aliquot):
        try:
            sample_type = aliquot.getField('SampleType').get(aliquot)
            return sample_type.Title()
        except:
            return ''

    def get_method(self, extract):
        try:
            method = extract.getField('Method').get(extract)
            return method.Title()
        except:
            return ''

registerType(ViralGenomicAnalysis, config.PROJECTNAME)