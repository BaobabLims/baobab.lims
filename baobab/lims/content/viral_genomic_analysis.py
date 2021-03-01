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
from Products.CMFCore.utils import getToolByName

from Products.DataGridField import CheckboxColumn
from Products.DataGridField import Column
from Products.DataGridField import DataGridField
from Products.DataGridField import DataGridWidget
from Products.DataGridField import DateColumn
from Products.DataGridField import DatetimeColumn
from Products.DataGridField import LinesColumn
from Products.DataGridField import SelectColumn
from Products.DataGridField import TimeColumn
from bika.lims.vocabularies import CatalogVocabulary, BikaContentVocabulary

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

# ExtractGenomicMaterial = ReferenceField(
#     'ExtractGenomicMaterial',
#     schemata='Extract Genomic Material',
#     multiValued=1,
#     allowed_types=('ExtractGenomicMaterial',),
#     relationship='ViralGenomicAnalysisExtractGenomicMaterial',
#     referenceClass=HoldingReference,
#     mode="rw",
#     read_permission=permissions.View,
#     write_permission=permissions.ModifyPortalContent,
#     widget=bika_ReferenceWidget(
#         label=_("Select Extract Genomic Material"),
#         visible={'edit': 'visible', 'view': 'visible'},
#         size=30,
#         showOn=True,
#         description=_("Select the Extract Genomic Material for the viral genomic analysis."),
#     )
# )

ExtractGenomicMaterial = DataGridField(
    'ExtractGenomicMaterial',
    schemata='Extract Genomic Material',
    allow_insert=True,
    allow_delete=True,
    allow_reorder=False,
    allow_empty_rows=False,
    allow_oddeven=True,
    columns=('VirusSample',
             'HeatInactivated',
             'Method',
             'ExtractionBarcode',
             'Volume',
             'Unit',
             'WasKitUsed',
             'KitNumber',
             'Notes',
             ),
    widget=DataGridWidget(
        label=_('Extract Genomic Materials'),
        columns={
            'VirusSample': SelectColumn(
                'VirusSample', vocabulary='Vocabulary_Sample'),
            'HeatInactivated': Column('Hide Inactivated'),
            'Method': SelectColumn('Method', vocabulary='Vocabulary_Method'),
            'ExtractionBarcode': Column('Extraction Barcode'),
            'Volume': Column('Volume'),
            'Unit': Column('Unit'),
            'WasKitUsed': CheckboxColumn('Was Kit Used'),
            'KitNumber': Column('Kit Number'),
            'Notes': LinesColumn('Notes'),
        }
    )
)

Fluorimeter = DataGridField(
    'Fluorimeter',
    schemata='Genome Quantification',
    allow_insert=True,
    allow_delete=True,
    allow_reorder=False,
    allow_empty_rows=False,
    allow_oddeven=True,
    columns=('FlurometerSample',
             'FlurometerConc',
             'NanometerSample',
             'NanometerQuantity',
             'NanometerRation',
             ),
    widget=DataGridWidget(
        label=_('Fluorimeter/Nanometer'),
        columns={
            'FluorimeterSample': SelectColumn(
                'Sample', vocabulary='Vocabulary_Sample'),
            'CFluorimeteronc': Column('Conc (ng/ul)'),
            'NanometerSample': SelectColumn('Sample', vocabulary='Vocabulary_Sample'),
            'NanometerQuantity': Column('Conc (ng/ul)'),
            'NanometerRatio': Column('260/280'),
        }
    )
)

VirusAliquot = ReferenceField(
    'VirusAliquot',
    schemata='Virus Sample Aliquot',
    multiValued=1,
    allowed_types=('VirusAliquot',),
    relationship='ViralGenomicAnalysisExtractGenomicMaterial',
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
    VirusAliquot,
    ExtractGenomicMaterial,
    Fluorimeter,
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

    def Vocabulary_Sample(self):
        vocabulary = CatalogVocabulary(self)
        vocabulary.catalog = 'bika_catalog'
        return vocabulary(allow_blank=True, portal_type='Sample')

    def Vocabulary_Method(self):
        vocabulary = CatalogVocabulary(self)
        vocabulary.catalog = 'portal_catalog'
        pc = getToolByName(self, 'portal_catalog')
        brains = pc(portal_type="Method")
        items = [('', '')] + [(c.UID, c.Title) for c in brains]
        return DisplayList(items)

registerType(ViralGenomicAnalysis, config.PROJECTNAME)
