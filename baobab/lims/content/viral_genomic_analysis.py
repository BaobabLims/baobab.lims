from Products.Archetypes.references import HoldingReference
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore import permissions
from Products.CMFPlone.interfaces import IConstrainTypes
from Products.CMFCore.utils import getToolByName
from zope.interface import implements
from bika.lims.browser.widgets import DateTimeWidget

from bika.lims.content.bikaschema import BikaSchema
from baobab.lims import bikaMessageFactory as _
from baobab.lims import config
from baobab.lims.interfaces import IViralGenomicAnalysis
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget

from Products.DataGridField import CheckboxColumn
from Products.DataGridField import Column
from Products.DataGridField import DataGridField
from Products.DataGridField import DataGridWidget
from Products.DataGridField import LinesColumn
from Products.DataGridField import SelectColumn
from bika.lims.vocabularies import CatalogVocabulary

Project = ReferenceField(
    'Project',
    allowed_types=('Project',),
    relationship='ViralGenomicAnalysisProjects',
    referenceClass=HoldingReference,
    required=True,
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
    default=False,
    widget=BooleanWidget(
        label="Will Extract",
        description="Whether or not to Extract Genomic Material",
        visible={'edit': 'visible', 'view': 'visible'}
    )
)

WillAliquot = BooleanField(
    'WillAliquot',
    default=False,
    widget=BooleanWidget(
        label="Aliquoting",
        description="Whether new Aliquots will be created",
        visible={'edit': 'visible', 'view': 'visible'}
    )
)

WillQuantify = BooleanField(
    'WillQuantify',
    default=False,
    widget=BooleanWidget(
        label="Will Quantify",
        description="Whether Quantifying will occur",
        visible={'edit': 'visible', 'view': 'visible'}
    )
)

WillViralLoadDetermine = BooleanField(
    'WillViralLoadDetermine',
    default=False,
    widget=BooleanWidget(
        label="Confirm Viral Load Determine",
        description="Whether viral load will be determined",
        visible={'edit': 'visible', 'view': 'visible'}
    )
)

WillLibraryPrep = BooleanField(
    'WillLibraryPrep',
    default=False,
    widget=BooleanWidget(
        label="Confirm Sequence Library Prep",
        description="Confirm if there will be Sequence Library Prep",
        visible={'edit': 'visible', 'view': 'visible'}
    )
)

ExtractGenomicMaterial = DataGridField(
    'ExtractGenomicMaterial',
    schemata='Extract Genomic Material',
    allow_insert=True,
    allow_delete=True,
    allow_reorder=False,
    allow_empty_rows=False,
    allow_oddeven=True,
    columns=('VirusSample',
             'Method',
             'ExtractionBarcode',
             'Volume',
             'Unit',
             'HeatInactivated',
             'WasKitUsed',
             'KitNumber',
             'Notes',
             ),
    widget=DataGridWidget(
        label=_('Extract Genomic Materials'),
        columns={
            'VirusSample': SelectColumn(
                'Virus Sample', vocabulary='Vocabulary_Sample'),
            'Method': SelectColumn('Method', vocabulary='Vocabulary_Method'),
            'ExtractionBarcode': Column('Extraction Barcode'),
            'Volume': Column('Volume'),
            'Unit': Column('Unit'),
            'HeatInactivated': CheckboxColumn('Heat Inactivated'),
            'WasKitUsed': CheckboxColumn('Was Kit Used'),
            'KitNumber': Column('Kit Lot #'),
            'Notes': LinesColumn('Notes'),
        }
    )
)

GenomeQuantification = DataGridField(
    'GenomeQuantification',
    schemata='Genome Quantification',
    allow_insert=True,
    allow_delete=True,
    allow_reorder=False,
    allow_empty_rows=False,
    allow_oddeven=True,
    columns=('VirusSample',
             'FluorimeterConc',
             'NanometerQuantity',
             'NanometerRatio',
             ),
    widget=DataGridWidget(
        label=_('Fluorimeter/Nanometer'),
        columns={
            'VirusSample': SelectColumn('Virus Sample', vocabulary='Vocabulary_Sample'),
            'FluorimeterConc': Column('Fluorimeter Conc (ng/ul)'),
            'NanometerQuantity': Column('Nanometer Conc (ng/ul)'),
            'NanometerRatio': Column('Nanometer Ratio (260/280)')
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

ViralLoadDeterminationTitle = StringField(
    'ViralLoadDeterminationTitle',
    schemata='Viral Load Determination',
    widget=StringWidget(
        label=_("Title"),
        size=30,
    )
)

ViralLoadDeterminationDescription = TextField(
    'ViralLoadDeterminationDescription',
    schemata='Viral Load Determination',
    widget=TextAreaWidget(
        label=_("Description"),
    )
)

ViralLoadDeterminationGeneName = StringField(
    'ViralLoadDeterminationGeneName',
    schemata='Viral Load Determination',
    widget=StringWidget(
        label=_("Gene name"),
    )
)
ViralLoadDeterminationDate = DateTimeField(
    'ViralLoadDeterminationDate',
    schemata='Viral Load Determination',
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=DateTimeWidget(
        label=_("Date"),
        description=_("Viral Load Determination date."),
        show_time=False,
        visible={'edit': 'visible', 'view': 'visible'}
    )
)

ViralLoadDetermination = DataGridField(
    'ViralLoadDetermination',
    schemata='Viral Load Determination',
    allow_insert=True,
    allow_delete=True,
    allow_reorder=False,
    allow_empty_rows=False,
    allow_oddeven=True,
    columns=('PCR',
             'ctValue',
             'KitNumber',
             'Result',
             'AddToReport',
             'Notes',
             ),
    widget=DataGridWidget(
        label=_('Viral Load Determination(RT-PCR)'),
        columns={
            'PCR': Column('PCR'),
            'ctValue': Column('ct Value'),
            'KitNumber': Column('Kit Lot #'),
            'Result': CheckboxColumn('Result'),
            'AddToReport': CheckboxColumn('Add to report'),
            'Notes': LinesColumn('Notes')
        }
    )
)
SequencingLibraryPrep = DataGridField(
    'SequencingLibraryPrep',
    schemata='Sequencing Library Prep',
    allow_insert=True,
    allow_delete=True,
    allow_reorder=False,
    allow_empty_rows=False,
    allow_oddeven=True,
    columns=('VirusSample',
             'Method',
             'LibraryID',
             'KitNumber',
             'Notes',
             ),
    widget=DataGridWidget(
        label=_('Sequencing Library Prep'),
        columns={
            'VirusSample': SelectColumn(
                'Virus Sample', vocabulary='Vocabulary_Sample'),
            'Method': SelectColumn('Method', vocabulary='Vocabulary_Method'),
            'LibraryID': Column('Library ID'),
            'KitNumber': Column('Kit Lot #'),
            'Notes': LinesColumn('Notes'),
        }
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
    GenomeQuantification,
    ViralLoadDeterminationTitle,
    ViralLoadDeterminationDescription,
    ViralLoadDeterminationGeneName,
    ViralLoadDeterminationDate,
    ViralLoadDetermination,
    SequencingLibraryPrep,
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
        return vocabulary(allow_blank=True, portal_type='VirusSample')

    def Vocabulary_Method(self):
        vocabulary = CatalogVocabulary(self)
        vocabulary.catalog = 'portal_catalog'
        pc = getToolByName(self, 'portal_catalog')
        brains = pc(portal_type="Method")
        items = [('', '')] + [(c.UID, c.Title) for c in brains]
        return DisplayList(items)


registerType(ViralGenomicAnalysis, config.PROJECTNAME)
