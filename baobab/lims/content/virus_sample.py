from Products.Archetypes.references import HoldingReference
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore import permissions
from Products.CMFPlone.interfaces import IConstrainTypes
from zope.interface import implements

# from baobab.lims.extenders.sample import Sample
from baobab.lims import bikaMessageFactory as _
from baobab.lims import config
from baobab.lims.interfaces import IVirusSample
# from bika.lims.interfaces import ISample, ISamplePrepWorkflow
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.browser.fields import AddressField
from bika.lims.browser.widgets import AddressWidget
from bika.lims.locales import COUNTRIES,STATES,DISTRICTS
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.public import BaseContent
from Products.CMFPlone.utils import safe_unicode
from bika.lims.workflow import doActionFor

import sys

Project = ReferenceField(
    'Project',
    # schemata='Baobab Data',
    required=True,
    allowed_types=('Project',),
    relationship='VirusSampleProject',
    referenceClass=HoldingReference,
    widget=bika_ReferenceWidget(
        label=_("Project"),
        visible={'edit': 'visible', 'view': 'visible'},
        size=30,
        showOn=True,
        description=_("Select the project of the sample."),
    )
)

ParentSample = ReferenceField(
    'ParentSample',
    allowed_types=('VirusSample'),
    relationship='SampleSample',
    referenceClass=HoldingReference,
    widget=bika_ReferenceWidget(
        label=_("Parent Biospecimen"),
        description=_("Create an Aliquot of the virus sample selected."),
        visible={'edit': 'visible',
                 'view': 'visible',
                 },
        showOn=True,
        render_own_label=False,
        base_query={
            'cancellation_state': 'active',
        },
    ),
)

Kit = ReferenceField(
    'Kit',
    allowed_types=('Kit',),
    relationship='VirusSampleKit',
    referenceClass=HoldingReference,
    widget=bika_ReferenceWidget(
        label=_("Kit"),
        visible={'edit': 'visible', 'view': 'visible'},
        size=30,
        showOn=True,
        description=_("Select the Kit."),
    )
)

SampleType = ReferenceField(
    'SampleType',
    required=True,
    allowed_types=('SampleType',),
    relationship='VirusSampleSampleType',
    referenceClass=HoldingReference,
    widget=bika_ReferenceWidget(
        label=_("Sample Type"),
        visible={'edit': 'visible', 'view': 'visible'},
        size=30,
        showOn=True,
        description=_("Select the specimen type."),
    )
)

StorageLocation = ReferenceField(
    'StorageLocation',
    allowed_types=('StoragePosition',),
    relationship='ItemStorageLocation',
    widget=bika_ReferenceWidget(
        label=_("Storage Location"),
        description=_("Location where item is kept"),
        size=40,
        visible={'edit': 'visible',
                 'view': 'visible',
                 },
        catalog_name='portal_catalog',
        base_query={'inactive_state': 'active',
                    'review_state': 'available',
                    },
        colModel=[{'columnName': 'UID', 'hidden': True},
                  {'columnName': 'Title', 'width': '50', 'label': _('Title')}
                  ],
    )
)

AllowSharing = BooleanField(
    'AllowSharing',
    # schemata='Baobab Data',
    default=False,
    # write_permission = ManageClients,
    widget=BooleanWidget(
        label=_("Allow Sharing"),
        description=_("Check to allow researchers to share sample freely."),
        visible={'edit': 'visible',
                 'view': 'visible',
                 'header_table': 'visible',
                 },
    ),
)

WillReturnFromShipment = BooleanField(
    'WillReturnFromShipment',
    default=False,
    widget=BooleanWidget(
        label=_("Will Return From Shipment"),
        description=_("Indicates if sample will return if shipped."),
        visible={'edit': 'visible',
                 'view': 'visible',
                 },
    ),
)

Barcode = StringField(
    'Barcode',
    required=True,
    widget=StringWidget(
        label=_("Barcode"),
        description="Virus Sample Barcode",
        visible={'edit': 'visible', 'view': 'visible'},
    )
)

Volume = FixedPointField(
    'Volume',
    required=1,
    default="0.00",
    widget=DecimalWidget(
        label=_("Volume"),
        size=15,
        description=_("The volume of the biospecimen taken from the subject."),
        visible={'edit': 'visible',
                 'view': 'visible',
                 },
    )
)

Unit = StringField(
    'Unit',
    # schemata='Baobab Data',
    default="ml",
    widget=StringWidget(
        label=_("Unit"),
        visible={'edit': 'visible',
                 'view': 'visible',
                 },
    )
)

AnatomicalSiteTerm = StringField(
    'AnatomicalSiteTerm',
    searchable=True,
    widget=StringWidget(
        label=_("Anatomical site term"),
        description=_('The ICD-O-3 topography code for describing the anatomical source of '
                      'the sampled material'),
        visible={'edit': 'visible',
                 'view': 'visible',
                 },
        render_own_label=False,
    )
)

AnatomicalSiteDescription = StringField(
    'AnatomicalSiteDescription',
    widget=TextAreaWidget(
        label=_("Anatomical site description"),
        description=_('The anatomical position of the body where the solid sample was taken from'),
        visible={'edit': 'visible',
                 'view': 'visible',
                },
        render_own_label=False,
    )
)

BioSampleAccession = StringField(
    'BioSampleAccession',
    schemata='Repository Accession Numbers',
    widget=StringWidget(
        label=_("Biosample Accession"),
        description="The identifier assigned to a BioSample in INSDC archives",
        visible={'edit': 'visible', 'view': 'visible'},
    )
)

SpecimenCollectorSampleID = StringField(
    'SpecimenCollectorSampleID',
    required=True,
    schemata='Sample Collection and Processing',
    widget=StringWidget(
        label=_("Specimen Collector Sample ID"),
        description="The user-defined name for the sample",
        visible={'edit': 'visible', 'view': 'visible'},
    )
)

SampleCollectedBy = StringField(
    'SampleCollectedBy',
    required=True,
    schemata='Sample Collection and Processing',
    widget=StringWidget(
        label=_("Sample Collected By"),
        description="The name of the agency that collected the original sample",
        visible={'edit': 'visible', 'view': 'visible'},
    )
)

SampleCollectionDate = DateTimeField(
    'SampleCollectionDate',
    schemata='Sample Collection and Processing',
    mode="rw",
    required=True,
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=DateTimeWidget(
        label=_("Sample Collection Date"),
        description=_("The date on which the sample was collection."),
        visible={'edit': 'visible', 'view': 'visible'}
    )
)

DateCreated = DateTimeField(
    'DateCreated',
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=DateTimeWidget(
        label=_("Date Created"),
        description=_("Define when the sample has been created."),
        show_time=True,
        visible={'edit': 'visible',
                 'view': 'visible',
                 },
        # render_own_label=False,
    ),
)

SampleReceivedDate = DateTimeField(
    'SampleReceivedDate',
    schemata='Sample Collection and Processing',
    mode="rw",
    required=True,
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=DateTimeWidget(
        label=_("Sample Received Date"),
        description=_("The date on which the sample was received."),
        # show_time=True,
        visible={'edit': 'visible', 'view': 'visible'}
    )
)

GeoLocCountry = StringField(
    'GeoLocCountry',
    schemata='Sample Collection and Processing',
    default="",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    vocabulary='getCountries',
    widget=SelectionWidget(
        format='select',
        label=_("Country Geo Location"),
        description=_("The country of origin of sample"),
        visible={'edit': 'visible', 'view': 'visible'},
        # render_own_label=True,
    )
)

GeoLocState = StringField(
    'GeoLocState',
    schemata='Sample Collection and Processing',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    # vocabulary='getStates',
    widget=SelectionWidget(
        format='select',
        label=_("State/Province Geo Location"),
        description=_("State/province/region of origin of the sample"),
        visible={'edit': 'visible', 'view': 'visible'},
        # render_own_label=True,
    )
)

Organism = ReferenceField(
    'Organism',
    schemata='Sample Collection and Processing',
    required=True,
    allowed_types=('Organism',),
    relationship='VirusSampleOrganism',
    referenceClass=HoldingReference,
    widget=bika_ReferenceWidget(
        label=_("Organism"),
        visible={'edit': 'visible', 'view': 'visible'},
        size=30,
        showOn=True,
        description=_("Taxonomic name of Organism."),
    )
)

Isolate = StringField(
    'Isolate',
    required=True,
    schemata='Sample Collection and Processing',
    # default="ml",
    widget=StringWidget(
        label=_("Isolate"),
        description="Identifier of the specific isolate",
        visible={'edit': 'visible', 'view': 'visible'},
        # render_own_label=True,
    )
)

PurposeOfSampling = StringField(
    'PurposeOfSampling',
    schemata='Sample Collection and Processing',
    default="",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    vocabulary='getPurposeOfSamplings',
    widget=SelectionWidget(
        format='select',
        label=_("Purpose Of Sampling"),
        description=_("The reason why the sample was collected"),
        visible={'edit': 'visible', 'view': 'visible'},
        # render_own_label=True,
    )
)

CollectionDevice = ReferenceField(
    'CollectionDevice',
    schemata='Sample Collection and Processing',
    allowed_types=('CollectionDevice',),
    relationship='VirusSampleCollectionDevice',
    referenceClass=HoldingReference,
    widget=bika_ReferenceWidget(
        label=_("Collection Device"),
        visible={'edit': 'visible', 'view': 'visible'},
        size=30,
        showOn=True,
        description=_("Select the Collection Device."),
    )
)

CollectionProtocol = StringField(
    'CollectionProtocol',
    schemata='Sample Collection and Processing',
    # default="ml",
    widget=StringWidget(
        label=_("Collection Protocol"),
        description="The name and version of a particular protocol used for sampling",
        visible={'edit': 'visible',
            'view': 'visible',
            # 'header_table': 'visible',
         },
        # render_own_label=True,
    )
)

ExposureEvent = StringField(
    'ExposureEvent',
    schemata='Host Exposure Information',
    default="",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    vocabulary='getExposureEvents',
    widget=SelectionWidget(
        format='select',
        label=_("Exposure Event"),
        description=_("Event leading to exposure"),
        visible={'edit': 'visible', 'view': 'visible'},
        render_own_label=True,
    )
)

SpecimenProcessing = StringField(
    'SpecimenProcessing',
    schemata='Sample Collection and Processing',
    default="",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    vocabulary='getSpecimenProcessings',
    widget=SelectionWidget(
        format='select',
        label=_("Specimen Processing"),
        description=_("Any processing applied to the sample during or after receiving"),
        visible={'edit': 'visible', 'view': 'visible'},
        render_own_label=True,
    )
)

LabHost = ReferenceField(
    'LabHost',
    schemata='Sample Collection and Processing',
    allowed_types=('LabHost',),
    relationship='VirusSampleLabHost',
    referenceClass=HoldingReference,
    widget=bika_ReferenceWidget(
        label=_("Lab Host"),
        visible={'edit': 'visible', 'view': 'visible'},
        size=30,
        showOn=True,
        description=_("Select the Lab Host."),
    )
)

PassageNumber = StringField(
    'PassageNumber',
    schemata='Sample Collection and Processing',
    # default="ml",
    widget=StringWidget(
        label=_("Passage Number"),
        description=_("Number of Passages."),
        visible={'edit': 'visible', 'view': 'visible'},
        # render_own_label=True,
    )
)

PassageMethod = TextField(
    'PassageMethod',
    schemata='Sample Collection and Processing',
    # default="ml",
    widget=TextAreaWidget(
        label=_("Passage Method"),
        description=_("Description of how the organism was passaged."),
        visible={'edit': 'visible', 'view': 'visible',},
        # render_own_label=True,
    )
)

AnatomicalMaterial = ReferenceField(
    'AnatomicalMaterial',
    schemata='Sample Collection and Processing',
    allowed_types=('AnatomicalMaterial',),
    relationship='VirusSampleAnatomicalMaterial',
    referenceClass=HoldingReference,
    widget=bika_ReferenceWidget(
        label=_("Anatomical Material"),
        visible={'edit': 'visible', 'view': 'visible'},
        size=30,
        showOn=True,
        description=_("Select the Anatomical Material."),
    )
)

# Host Information
HostSubjectID = StringField(
    'HostSubjectID',
    schemata='Host Information',
    # default="ml",
    widget=StringWidget(
        label=_("Host Subject ID"),
        description=_("A unique identifier by which each host can be referred to e.g. #131"),
        visible={'edit': 'visible', 'view': 'visible'},
        # render_own_label=True,
    )
)

Host = ReferenceField(
    'Host',
    schemata='Host Information',
    allowed_types=('Host',),
    relationship='VirusSampleHost',
    referenceClass=HoldingReference,
    widget=bika_ReferenceWidget(
        label=_("Host (scientific name)"),
        visible={'edit': 'visible', 'view': 'visible'},
        size=30,
        showOn=True,
        description=_("Select the Host."),
    )
)

HostDisease = ReferenceField(
    'HostDisease',
    schemata='Host Information',
    allowed_types=('HostDisease',),
    relationship='VirusSampleHostDisease',
    referenceClass=HoldingReference,
    widget=bika_ReferenceWidget(
        label=_("Host Disease"),
        visible={'edit': 'visible', 'view': 'visible'},
        size=30,
        showOn=True,
        description=_("Select the disease of the Host."),
    )
)

HostGender = StringField(
    'HostGender',
    schemata='Host Information',
    default="",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    vocabulary='getHostGenders',
    widget=SelectionWidget(
        format='select',
        label=_("Host Gender"),
        description=_("The gender of the host at the time of sample collection"),
        visible={'edit': 'visible', 'view': 'visible'},
        render_own_label=True,
    )
)

HostAge = FixedPointField(
    'HostAge',
    schemata='Host Information',
    default="0.00",
    widget=DecimalWidget(
        label=_("Host Age"),
        description=_("Age of host at the time of sampling"),
        visible={'edit': 'visible', 'view': 'visible'},
        # render_own_label=True,
    )
)

HostAgeUnit = StringField(
    'HostAgeUnit',
    schemata='Host Information',
    default="",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    vocabulary='getHostAgeUnits',
    widget=SelectionWidget(
        format='select',
        label=_("Host Age Unit"),
        description=_("The units used to measure the host's age"),
        visible={'edit': 'visible', 'view': 'visible'},
        render_own_label=True,
    )
)

# Host Exposure Information
ExposureCountry = StringField(
    'ExposureCountry',
    schemata='Host Exposure Information',
    default="",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    vocabulary='getCountries',
    widget=SelectionWidget(
        format='select',
        label=_("Exposure Country"),
        description=_("The country in which this exposure occurred"),
        visible={'edit': 'visible', 'view': 'visible'},
        # render_own_label=True,
    )
)

ExposureEvent = StringField(
    'ExposureEvent',
    schemata='Host Exposure Information',
    default="",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    vocabulary='getExposureEvents',
    widget=SelectionWidget(
        format='select',
        label=_("Exposure Event"),
        description=_("Event leading to exposure"),
        visible={'edit': 'visible', 'view': 'visible'},
        render_own_label=True,
    )
)

# Sequencing information
LibraryID = StringField(
    'LibraryID',
    schemata='Sequencing',
    # default="ml",
    widget=StringWidget(
        label=_("Library ID"),
        description=_("The user-specified identifier for the library prepared for sequencing"),
        visible={'edit': 'visible', 'view': 'visible'},
        # render_own_label=True,
    )
)

InstrumentType = ReferenceField(
    'InstrumentType',
    schemata = "Sequencing",
    required = True,
    vocabulary_display_path_bound = sys.maxint,
    vocabulary = 'getInstrumentTypes',
    allowed_types = ('InstrumentType',),
    relationship = 'VirusSampleInstrumentType',
    referenceClass = HoldingReference,
    widget = ReferenceWidget(
        checkbox_bound = 0,
        label=_("Instrument Type"),
        description=_("Select the type of instrument"),
    ),
)

Instrument = ReferenceField(
    'Instrument',
    schemata = "Sequencing",
    required = 0,
    vocabulary_display_path_bound = sys.maxint,
    vocabulary = 'getInstruments',
    allowed_types = ('Instrument',),
    relationship = 'VirusSampleInstrument',
    referenceClass = HoldingReference,
    widget = ReferenceWidget(
        checkbox_bound = 0,
        label=_("Instrument"),
        description=_("Select the preferred instrument"),
    ),
)

SequencingProtocolName = StringField(
    'SequencingProtocolName',
    schemata='Sequencing',
    # default="ml",
    widget=StringWidget(
        label=_("Sequencing Protocol Name"),
        description=_("The name and version number of the sequencing protocol used"),
        visible={'edit': 'visible', 'view': 'visible'},
        # render_own_label=True,
    )
)

schema = BikaSchema.copy() + Schema((
    Project,
    Kit,
    ParentSample,
    SampleType,
    StorageLocation,
    AllowSharing,
    WillReturnFromShipment,
    Barcode,
    Volume,
    Unit,
    AnatomicalSiteTerm,
    AnatomicalSiteDescription,
    BioSampleAccession,
    SpecimenCollectorSampleID,
    DateCreated,
    SampleCollectedBy,
    SampleCollectionDate,
    SampleReceivedDate,
    GeoLocCountry,
    GeoLocState,
    Organism,
    Isolate,
    PurposeOfSampling,
    CollectionDevice,
    CollectionProtocol,
    SpecimenProcessing,
    LabHost,
    PassageNumber,
    PassageMethod,
    AnatomicalMaterial,
    HostSubjectID,
    Host,
    HostDisease,
    HostGender,
    HostAge,
    HostAgeUnit,
    ExposureCountry,
    ExposureEvent,
    LibraryID,
    InstrumentType,
    Instrument,
    SequencingProtocolName,
))

schema['title'].widget.visible = False
schema['description'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}
schema['SampleType'].widget.render_own_label = False

class VirusSample(BaseContent):
    security = ClassSecurityInfo()
    implements(IVirusSample, IConstrainTypes)
    displayContentsTab = False
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        # from baobab.lims.idserver import renameAfterCreation
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def title(self):
        # return safe_unicode(self.getField('Barcode').get(self)).encode('utf-8')
        return self.getField('Barcode').get(self)

    def update_box_status(self, location):
        box = location.aq_parent
        state = self.portal_workflow.getInfoFor(box, 'review_state')
        free_pos = box.get_free_positions()
        if not free_pos and state == 'available':
            doActionFor(box, 'occupy')
        elif free_pos and state == 'occupied':
            doActionFor(box, 'liberate')


    def getInstruments(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [('', '')] + [(c.UID, c.Title) for c in bsc(portal_type='InstrumentType', inactive_state='active')]

        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(items)

    def getInstrumentTypes(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [('', '')] + [(c.UID, c.Title)
                 for c in bsc(portal_type='InstrumentType',
                              inactive_state='active')]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(items)

    def getCountries(self):
        items = [('', '')] + [(x['Country'], x['Country']) for x in COUNTRIES]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return items

    def getPurposeOfSamplings(self):
        return [
            '',
            'Cluster Investigation',
            'Diagnostic Testing',
            'Research',
            'Surveillance Testing',
            'Viral Passage Experiment',
            'Not Applicable',
            'Not Collected',
            'Not Provided',
            'Missing',
            'Restricted Access',
        ]

    def getSpecimenProcessings(self):
        return [
            '',
            'Virus Passage',
            'RNA Re-Extraction (Post RT-PCR)',
            'Specimens Pooled',
            'Not Applicable',
            'Not Collected',
            'Not Provided',
            'Missing',
            'Restricted Access',
        ]

    def getHostAgeUnits(self):
        return [
            '',
            'Days',
            'Months',
            'Years',
            'Not Applicable',
            'Not Collected',
            'Not Provided',
            'Missing',
            'Restricted Access',
        ]

    def getHostGenders(self):
        return [
            '',
            'Female',
            'Male',
            'Non-binary Gender',
            'Transgender (Male to Female)',
            'Transgender (Female to Male)',
            'Undeclared',
            'Unknown',
            'Not Applicable',
            'Not Collected',
            'Not Provided',
            'Missing',
            'Restricted Access',
        ]

    def getExposureEvents(self):
        return [
            '',
            'Mass Gathering (Convention)',
            'Mass Gathering (Religious)',
            'Mass Gathering (Social e.g. Funeral, Wedding etc)',
            'Mass Gathering (Office)',
            'Occupational Exposure (Hospital Worker)',
            'Occupational Exposure (Hospital Visit)',
            'Occupational Exposure (Frontline Response)',
            'Occupational Exposure (Healthcare Work with the Public)',
            'Occupational Exposure (Retail)',
            'Occupational Exposure (Restaurant)',
            'Not Applicable',
            'Not Collected',
            'Not Provided',
            'Missing',
            'Restricted Access',
        ]

registerType(VirusSample, config.PROJECTNAME)
