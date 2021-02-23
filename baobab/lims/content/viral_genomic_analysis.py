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

# Genus = StringField(
#     'Genus',
#     schemata='Extract Genomic Material',
#     mode="rw",
#     read_permission=permissions.View,
#     write_permission=permissions.ModifyPortalContent,
#     widget=StringWidget(
#         label=_("Genus"),
#         description=_("The genus of the organism"),
#         visible={'edit': 'visible', 'view': 'visible'},
#     )
# )
#
# ExtractGenomicMaterial = ReferenceField(
#     'ExtractGenomicMaterial',
#     multiValued=1,
#     allowed_types=('ExtractGenomicMaterial',),
#     referenceClass=HoldingReference,
#     relationship='ExtractGenomicMaterialViralGenomicAnalysis',
#     mode="rw",
#     read_permission=permissions.View,
#     write_permission=permissions.ModifyPortalContent,
#     widget=ComputedWidget(
#         visible={'edit': 'invisible', 'view': 'invisible'},
#     )
# )



# # Aliquoting
# # ExtractGenomicMaterial = ReferenceField(
# #     'ExtractGenomicMaterial',
# #     required=True,
# #     allowed_types=('ExtractGenomicMaterial',),
# #     relationship='ExtractGenomicMaterialViralGenomicAnalysis',
# #     referenceClass=HoldingReference,
# #     widget=bika_ReferenceWidget(
# #         label=_("Extract Genomic Material"),
# #         # catalog_name='bika_catalog',
# #         visible={'edit': 'visible', 'view': 'visible'},
# #         size=30,
# #         showOn=True,
# #         render_own_label=True,
# #         description=_("Select the ExtractGenomic MaterialViral GenomicAnalysis."),
# #     )
# # )
#
# GenomicQuantification = ReferenceField(
#     'GenomicQuantification',
#     required=True,
#     allowed_types=('GenomicQuantification',),
#     relationship='GenomicQuantificationViralGenomicAnalysis',
#     referenceClass=HoldingReference,
#     widget=bika_ReferenceWidget(
#         label=_("Genomic Quantification"),
#         # catalog_name='bika_catalog',
#         visible={'edit': 'visible', 'view': 'visible'},
#         size=30,
#         showOn=True,
#         render_own_label=True,
#         description=_("The Genomic Quantification."),
#     )
# )
#
# ViralLoadDetermination = ReferenceField(
#     'ViralLoadDetermination',
#     required=True,
#     allowed_types=('ViralLoadDetermination',),
#     relationship='ViralLoadDeterminationViralGenomicAnalysis',
#     referenceClass=HoldingReference,
#     widget=bika_ReferenceWidget(
#         label=_("Determination Viral Load"),
#         # catalog_name='bika_catalog',
#         visible={'edit': 'visible', 'view': 'visible'},
#         size=30,
#         showOn=True,
#         render_own_label=True,
#         description=_("Specify viral load determination."),
#     )
# )
#
# SequenceLibraryPrep = ReferenceField(
#     'SequenceLibraryPrep',
#     required=True,
#     allowed_types=('SequenceLibraryPrep',),
#     relationship='SequenceLibraryPrepViralGenomicAnalysis',
#     referenceClass=HoldingReference,
#     widget=bika_ReferenceWidget(
#         label=_("Sequence Library Prep"),
#         # catalog_name='bika_catalog',
#         visible={'edit': 'visible', 'view': 'visible'},
#         size=30,
#         showOn=True,
#         render_own_label=True,
#         description=_("Sequencing the library preparation."),
#     )
# )

# ExtractGenomicMaterial = ReferenceField(
#     'ExtractGenomicMaterial',
#     required=True,
#     allowed_types=('ExtractGenomicMaterial',),
#     relationship='ExtractGenomicMaterialViralGenomicAnalysis',
#     referenceClass=HoldingReference,
#     widget=bika_ReferenceWidget(
#         label=_("Extract Genomic Material"),
#         # catalog_name='bika_catalog',
#         visible={'edit': 'visible', 'view': 'visible'},
#         size=30,
#         showOn=True,
#         render_own_label=True,
#         description=_("Select the ExtractGenomic MaterialViral GenomicAnalysis."),
#     )
# )

schema = BikaSchema.copy() + Schema((
    Project,
    DateCreated,
    WillExtract,
    WillAliquot,
    WillQuantify,
    WillViralLoadDetermine,
    WillLibraryPrep,
    ExtractGenomicMaterial,
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

registerType(ViralGenomicAnalysis, config.PROJECTNAME)