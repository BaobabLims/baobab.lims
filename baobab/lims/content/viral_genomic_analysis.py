from plone import api
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore import permissions
from Products.CMFPlone.interfaces import IConstrainTypes
from Products.CMFCore.utils import getToolByName
from Products.DataGridField import CheckboxColumn
from Products.DataGridField import Column
from Products.DataGridField import DataGridField
from Products.DataGridField import DataGridWidget
from Products.DataGridField import LinesColumn
from Products.DataGridField import SelectColumn
from zope.interface import implements

from baobab.lims import bikaMessageFactory as _
from baobab.lims import config
from baobab.lims.interfaces import IViralGenomicAnalysis
from baobab.lims.utils.create_biospecimen import create_virus_sample
from baobab.lims.utils.retrieve_objects import getRNAorDNASampleTypes
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.vocabularies import CatalogVocabulary


Project = ReferenceField(
    'Project',
    allowed_types=('Project',),
    relationship='ViralGenomicAnalysisProjects',
    referenceClass=HoldingReference,
    required=True,
    widget=bika_ReferenceWidget(
        label=_("Select Project"),
        size=30,
        showOn=True,
        description=_("Select the project for the viral genomic analysis."),
        visible={
         'edit': 'visible',
         'view': 'visible',
         'created': {'view': 'visible', 'edit': 'visible'},
     },
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
        visible={
         'edit': 'visible',
         'view': 'visible',
         'created': {'view': 'visible', 'edit': 'visible'},
         'extracted_genomic_material': {'view': 'invisible', 'edit': 'invisible'},
         'aliquoted': {'view': 'invisible', 'edit': 'invisible'},
         'genome_quantified': {'view': 'invisible', 'edit': 'invisible'},
         'viral_load_determined': {'view': 'invisible', 'edit': 'invisible'},
         'sequencing_library_preped': {'view': 'invisible', 'edit': 'invisible'},
     },
    )
)

WillExtract = BooleanField(
    'WillExtract',
    default=False,
    widget=BooleanWidget(
        label="Will Extract",
        description="Whether or not to Extract Genomic Material",
        visible={
         'edit': 'visible',
         'view': 'visible',
         'created': {'view': 'visible', 'edit': 'visible'},
         'extracted_genomic_material': {'view': 'invisible', 'edit': 'invisible'},
         'aliquoted': {'view': 'invisible', 'edit': 'invisible'},
         'genome_quantified': {'view': 'invisible', 'edit': 'invisible'},
         'viral_load_determined': {'view': 'invisible', 'edit': 'invisible'},
         'sequencing_library_preped': {'view': 'invisible', 'edit': 'invisible'},
     },
    )
)

WillAliquot = BooleanField(
    'WillAliquot',
    default=False,
    widget=BooleanWidget(
        label="Aliquoting",
        description="Whether new Aliquots will be created",
        visible={
         'edit': 'visible',
         'view': 'visible',
         'created': {'view': 'visible', 'edit': 'visible'},
         'extracted_genomic_material': {'view': 'invisible', 'edit': 'invisible'},
         'aliquoted': {'view': 'invisible', 'edit': 'invisible'},
         'genome_quantified': {'view': 'invisible', 'edit': 'invisible'},
         'viral_load_determined': {'view': 'invisible', 'edit': 'invisible'},
         'sequencing_library_preped': {'view': 'invisible', 'edit': 'invisible'},
     },
    )
)

WillQuantify = BooleanField(
    'WillQuantify',
    default=False,
    widget=BooleanWidget(
        label="Will Quantify",
        description="Whether Quantifying will occur",
        visible={
         'edit': 'visible',
         'view': 'visible',
         'created': {'view': 'visible', 'edit': 'visible'},
         'extracted_genomic_material': {'view': 'invisible', 'edit': 'invisible'},
         'aliquoted': {'view': 'invisible', 'edit': 'invisible'},
         'genome_quantified': {'view': 'invisible', 'edit': 'invisible'},
         'viral_load_determined': {'view': 'invisible', 'edit': 'invisible'},
         'sequencing_library_preped': {'view': 'invisible', 'edit': 'invisible'},
     },
    )
)

WillViralLoadDetermine = BooleanField(
    'WillViralLoadDetermine',
    default=False,
    widget=BooleanWidget(
        label="Confirm Viral Load Determine",
        description="Whether viral load will be determined",
        visible={
         'edit': 'visible',
         'view': 'visible',
         'created': {'view': 'visible', 'edit': 'visible'},
         'extracted_genomic_material': {'view': 'invisible', 'edit': 'invisible'},
         'aliquoted': {'view': 'invisible', 'edit': 'invisible'},
         'genome_quantified': {'view': 'invisible', 'edit': 'invisible'},
         'viral_load_determined': {'view': 'invisible', 'edit': 'invisible'},
         'sequencing_library_preped': {'view': 'invisible', 'edit': 'invisible'},
     },
    )
)

WillLibraryPrep = BooleanField(
    'WillLibraryPrep',
    default=False,
    widget=BooleanWidget(
        label="Confirm Sequence Library Prep",
        description="Confirm if there will be Sequence Library Prep",
        visible={
         'edit': 'visible',
         'view': 'visible',
         'created': {'view': 'visible', 'edit': 'visible'},
         'extracted_genomic_material': {'view': 'invisible', 'edit': 'invisible'},
         'aliquoted': {'view': 'invisible', 'edit': 'invisible'},
         'genome_quantified': {'view': 'invisible', 'edit': 'invisible'},
         'viral_load_determined': {'view': 'invisible', 'edit': 'invisible'},
         'sequencing_library_preped': {'view': 'invisible', 'edit': 'invisible'},
     },
    )
)

ExtractGenomicMaterial = DataGridField(
    'ExtractGenomicMaterial',
    schemata='Extract Genomic Material',
    validators=('extractgenomicmaterialvalidator'),
    allow_insert=True,
    allow_delete=True,
    allow_reorder=False,
    allow_empty_rows=False,
    allow_oddeven=True,
    columns=('VirusSample',
             'Method',
             'SampleType',
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
                'Virus Sample', 
                col_description='Virus Sample(s) of the selected Project',
                # vocabulary='Vocabulary_VirusSample_by_ProjectUID',
                vocabulary='Vocabulary_VirusSample_by_ProjectUID_and_RNADNA',
                ),
            'Method': SelectColumn('Method', vocabulary='Vocabulary_Method'),
            'SampleType': SelectColumn('SampleType',
                vocabulary='Vocabulary_RNAorDNA_SampleTypes'),
            'ExtractionBarcode': Column('Extraction Barcode'),
            'Volume': Column('Volume'),
            'Unit': Column('Unit'),
            'HeatInactivated': CheckboxColumn('Heat Inactivated'),
            'WasKitUsed': CheckboxColumn('Was Kit Used'),
            'KitNumber': Column('Kit Lot #'),
            'Notes': LinesColumn('Notes'),
        },
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
    columns=('VirusSampleRNAorDNA',
             'FluorimeterConc',
             'NanometerQuantity',
             'NanometerRatio',
             ),
    widget=DataGridWidget(
        label=_('Fluorimeter/Nanometer'),
        columns={
            'VirusSampleRNAorDNA': SelectColumn(
                'Virus Sample by RNA/DNA',
                vocabulary='Vocabulary_VirusSample_by_ProjectUID_NOT_RNADNA',
                # vocabulary='Vocabulary_VLD_Sample_RNA_or_DNA',
                visible={
                 'edit': 'visible',
                 'view': 'visible',
                 'created': {'view': 'visible', 'edit': 'visible'},
             },
                ),
            'FluorimeterConc': Column('Fluorimeter Conc (ng/ul)',
                visible={
                 'edit': 'visible',
                 'view': 'visible',
                 'created': {'view': 'visible', 'edit': 'visible'},
             },
                ),
            'NanometerQuantity': Column('Nanometer Conc (ng/ul)',
                visible={
                 'edit': 'visible',
                 'view': 'visible',
                 'created': {'view': 'visible', 'edit': 'visible'},
             },
                ),
            'NanometerRatio': Column('Nanometer Ratio (260/280)',
                visible={
                 'edit': 'visible',
                 'view': 'visible',
                 'created': {'view': 'visible', 'edit': 'visible'},
             },
                )
        }
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
        visible={
         'edit': 'visible',
         'view': 'visible',
         'created': {'view': 'visible', 'edit': 'visible'},
     },
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
    )
)

ReferenceSampleControl = StringField(
    'ReferenceSampleControl',
    schemata='Viral Load Determination',
    default="",
    vocabulary='Vocabulary_Control',
    widget=SelectionWidget(
        format='select',
        label=_("Reference Sample Control Options"),
        description=_("Reference Sample Control options(Positive or Negetive control)"),
    )
)

ReferenceSampleControlResult = StringField(
    'ReferenceSampleControlResult',
    schemata='Viral Load Determination',
    default="",
    vocabulary='Vocabulary_PassFail',
    widget=SelectionWidget(
        format='select',
        label=_("Reference Sample Control Result"),
        description=_("Reference Sample Control Result(Positive or Negetive control)"),
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
    columns=('VirusSampleRNAorDNA',
             'ctValue',
             'KitNumber',
             'Result',
             'Verification',
             'AddToReport',
             'Notes',
             ),
    widget=DataGridWidget(
        label=_('Viral Load Determination(RT-PCR)'),
        columns={
            'VirusSampleRNAorDNA': SelectColumn(
                'Virus Sample by RNA/DNA',
                vocabulary='Vocabulary_VirusSample_by_ProjectUID_NOT_RNADNA'),
                # vocabulary='Vocabulary_VLD_Sample_RNA_or_DNA'),
            'ctValue': Column('ct Value'),
            'KitNumber': Column('Kit Lot #'),
            'Result': SelectColumn(
                'Result',
                vocabulary='Vocabulary_VLD_Result'),
            'Verification': SelectColumn(
                'Verification',
                vocabulary='Vocabulary_VLD_Verification'),
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
    columns=('VirusSampleRNAorDNA',
             'Method',
             'LibraryID',
             'Notes',
             ),
    widget=DataGridWidget(
        label=_('Sequencing Library Prep'),
        columns={
            'VirusSampleRNAorDNA': SelectColumn(
                'Virus Sample by RNA/DNA',
                vocabulary='Vocabulary_VirusSample_by_ProjectUID_NOT_RNADNA',
                # vocabulary='Vocabulary_VLD_Sample_RNA_or_DNA',
                ),
            'Method': SelectColumn('Method', vocabulary='Vocabulary_Method'),
            'LibraryID': Column('Library ID'),
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
    ReferenceSampleControl,
    ReferenceSampleControlResult,
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

    def getProjectUID(self):
        return self.getProject().UID() if self.getProject() else None

    def setExtractGenomicMaterial(self, value, **kwargs):
        empty_line = [{'ExtractionBarcode': '',
            'orderindex_': 'template_row_marker',
            'HeatInactivated': '', 'VirusSample': '', 'WasKitUsed': '',
            'Notes': [], 'Volume': '', 'Unit': '', 'Method': '',
            'KitNumber': ''}]
        if value == empty_line or value == ({},):
            return 
        if empty_line[0] in value:
            value.pop(value.index(empty_line[0]))


        # TODO: do visible on the field and hide on extracted_genomic_material
        # then delete next 3 lines from the 3rd line
        workflow = getToolByName(self, 'portal_workflow')
        review_state = workflow.getInfoFor(self, 'review_state')
        if review_state == 'extracted_genomic_material':
            old_value = self.getField('ExtractGenomicMaterial').get(self)
            self.getField('ExtractGenomicMaterial').set(self, old_value)
        aline = False
        if review_state != 'extracted_genomic_material':
            # TODO: Check and delete existig Biospecimans related to this
            # extraction recreate from the new value
            # maybe change state here aswell if we will be using the workflow
            # set the values and call the create function
            for row in value:
                virus_sample = api.content.get(UID=row['VirusSample'])
                if virus_sample is None:
                    continue
                aline = True
                sample_type = api.content.get(UID=row['SampleType'])
                values = {
                }
                values = {
                    "title": '',
                    "description": None,
                    "Project": self.getProject(),
                    "AllowSharing": 0,
                    "StorageLocation": None,
                    "SampleType": sample_type,
                    "SubjectID": None,
                    "Barcode": row['ExtractionBarcode'],
                    "Volume": row['Volume'],
                    "Unit": row['Unit'],
                    "LinkedSample": virus_sample,
                    "DateCreated": DateTime,
                }
                # create_smp(self.getProject(), None, values)
                create_virus_sample(self.getProject(), values)
            if aline:
                # atlease 1 sample was created
                self.getField('ExtractGenomicMaterial').set(self, value)
                workflow.doActionFor(self, 'extract_genomic_material')


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
            date_created = aliquot.getField('DateCreated').get(aliquot)
            prepared_date_created = ''
            if date_created:
                prepared_date_created = date_created.strftime("%Y-%m-%d %H:%M:%S")
            prepared_extract = {
                "barcode": aliquot.getField('Barcode').get(aliquot),
                "volume": aliquot.getField('Volume').get(aliquot),
                "unit": aliquot.getField('Unit').get(aliquot),
                "sample_type": self.get_sample_type(aliquot),
                'date_created': prepared_date_created,
                # 'time_created': aliquot.getField('DateCreated').get(aliquot).strftime("%H:%M:%S"),
                # 'date_created': aliquot.getField('DateCreated').get(aliquot),
            }
            prepared_aliquots.append(prepared_extract)

        return prepared_aliquots

    def prepare_viral_load_data(self):
        viral_loads = self.getViralLoadDetermination()
        viral_loads_list = []
        for viral_load in viral_loads:
            if viral_load['AddToReport']:
                individual_viral_load = self.prepare_individual_viral_load(viral_load)
                viral_loads_list.append(individual_viral_load)
        return viral_loads_list

    def prepare_individual_viral_load(self, viral_load):
        return {
            'sample': self.getObjectTitleFromUID(viral_load['VirusSampleRNAorDNA']),
            'ct_value': viral_load['ctValue'],
            'kit_number': viral_load['KitNumber'],
            'result': viral_load['Result'],
            'verification': viral_load['Verification'],
            'notes': viral_load['Notes'],
        }

    def get_virus_sample(self, extract):
        try:
            virus_sample = extract.getField('VirusSample').get(extract)
            return virus_sample.Title()
        except:
            return ''

    def getObjectTitleFromUID(self, object_uid):

        try:
            pc = getToolByName(self, 'portal_catalog')

            brains = pc(UID=object_uid)
            return brains[0].getObject().Title()
        except Exception as e:
            # raise Exception('%s %s not found' % (obj_type, obj_title))
            return ''

    def get_parent_sample(self, virus_aliquot):
        try:
            parent_sample = virus_aliquot.getField('ParentSample').get(virus_aliquot)
            return parent_sample.getField('Barcode').get(parent_sample)
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

    def Vocabulary_PassFail(self):
        return DisplayList([('',''), ('Pass', 'Pass'), ('Fail', 'Fail')])

    def Vocabulary_Control(self):
        return DisplayList([
            ('',''),
            ('PositiveControl', 'Positive Control'),
            ('NegativeControl', 'Negative Control')])

    def Vocabulary_Sample(self):
        vocabulary = CatalogVocabulary(self)
        vocabulary.catalog = 'bika_catalog'
        return vocabulary(allow_blank=True, portal_type='VirusSample')

    def Vocabulary_VLD_Sample_RNA_or_DNA(self):
        pc = getToolByName(self, 'portal_catalog')

        # TODO: Add getProjectUID index or column instead,
        project_uid = self.getProjectUID()
        if not project_uid:
            items = [('','')]
            return DisplayList(items)

        rna_dna_sample_types = getRNAorDNASampleTypes(self)
        items = [('', '')]
        brains = pc(portal_type="Sample", getProjectUID=project_uid)
        for brain in brains:
            obj = brain.getObject()
            if obj.getField('SampleType').get(obj) in rna_dna_sample_types:
                items.append((obj.UID(), obj.Title()))

        return DisplayList(items)

    def Vocabulary_RNAorDNA_SampleTypes(self):
        rna_dna_sample_types = getRNAorDNASampleTypes(self)
        items = [('', '')] + [(c.UID(), c.title) for c in rna_dna_sample_types]
        return DisplayList(items)

    def Vocabulary_VirusSample_by_ProjectUID(self, project_uid=None):
        return DisplayList(self.getVirusSamplesByProjectUID())

    def Vocabulary_VirusSample_by_ProjectUID_and_RNADNA(self, project_uid=None):
        return DisplayList(self.getVirusSamplesByProjectUID(rna_dna=True))

    def Vocabulary_VirusSample_by_ProjectUID_NOT_RNADNA(self, project_uid=None):
        return DisplayList(self.getVirusSamplesByProjectUID(not_rna_dna=True))

    def Vocabulary_VirusSample(self):
        pc = getToolByName(self, 'portal_catalog')
        brains = pc(portal_type="VirusSample")
        items = [('', '')]
        for brain in brains:
            c = brain.getObject()
            items.append((c.UID(), c.getField('Barcode').get(c)))
        return DisplayList(items)

    def getVirusSamplesByProjectUID(self, project_uid=None, rna_dna=False, not_rna_dna=False):
        pc = getToolByName(self, 'portal_catalog')

        rna_dna_sample_types = []
        if rna_dna:
            rna_dna_sample_types = getRNAorDNASampleTypes(self)

        items = [('','')]
        if not project_uid:
            project_uid = self.getProjectUID()
        if not project_uid:
            return items

        brains = pc(portal_type="VirusSample", inactive_state='active', getProjectUID=project_uid)

        for brain in brains:
            try:
                virus_sample = brain.getObject()
                if virus_sample.getSampleType() not in rna_dna_sample_types:
                    items.append((virus_sample.UID(), virus_sample.getField('Barcode').get(virus_sample)))
                if len(items) == 1 and not_rna_dna == True:
                    if virus_sample.getSampleType() in rna_dna_sample_types:
                        items.append((virus_sample.UID(), virus_sample.getField('Barcode').get(virus_sample)))
            except:
                continue
        return items

    def Vocabulary_Method(self):
        pc = getToolByName(self, 'portal_catalog')
        brains = pc(portal_type="Method")
        items = [('', '')] + [(c.UID, c.Title) for c in brains]
        return DisplayList(items)

    def Vocabulary_VLD_Result(self):
        return DisplayList([('', ''), ('Positive', 'Positive'), ('Negative', 'Negative'), ('Not determined', 'Not determined')])

    def Vocabulary_VLD_Verification(self):
        return DisplayList([('', ''), ('Verified', 'Verified'), ('Retracted', 'Retracted')])

registerType(ViralGenomicAnalysis, config.PROJECTNAME)
