from Products.Archetypes.references import HoldingReference
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore import permissions
from Products.CMFPlone.interfaces import IConstrainTypes
from zope.interface import implements

from bika.lims.content.bikaschema import BikaSchema
from baobab.lims import bikaMessageFactory as _
from baobab.lims import config
from baobab.lims.interfaces import ITransport
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from bika.lims.browser.widgets import DateTimeWidget
from Products.CMFPlone.utils import safe_unicode

Client = ReferenceField('Client',
    schemata='Transport Information',
    allowed_types = ('Client',),
    relationship = 'TransportClient',
    referenceClass=HoldingReference,
    widget = bika_ReferenceWidget(
        label=_("Client"),
        visible={'edit': 'visible', 'view': 'visible'},
        size=30,
        showOn=True,
        description=_("The client this transport belongs to."),
    )
)

Project = ReferenceField(
    'Project',
    schemata='Transport Information',
    allowed_types=('Project',),
    relationship='TransportProject',
    referenceClass=HoldingReference,
    widget=bika_ReferenceWidget(
        label=_("Select Project"),
        visible={'edit': 'visible', 'view': 'visible'},
        size=30,
        showOn=True,
        description=_("Select the project of the sample donor."),
    )
)


NonConformityAction = StringField(
    'NonConformityAction',
    schemata='Transport Information',
    widget=StringWidget(
        label=_('Non Conformity Action'),
        description=_('The Non Conformity Action.'),
        visible={'view': 'visible', 'edit': 'visible'}
    )
)

Status = StringField(
    'Status',
    schemata='Transport Information',
    required=0,
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=StringWidget(
        label=_("Status"),
        description=_("The status of the transport."),
        visible={'edit': 'visible', 'view': 'visible'},
    )
)

ApplicationNumber = StringField(
    'ApplicationNumber',
    schemata='Transport Information',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=StringWidget(
        label=_("Application Number"),
        description=_("The application number."),
        visible={'edit': 'visible', 'view': 'visible'},
    )
)

DepositorName = StringField(
    'DepositorName',
    schemata='Transport Information',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=StringWidget(
        label=_("Depositor Name and Surname"),
        description=_("The Name and Last Name of the Depositor."),
        visible={'edit': 'visible', 'view': 'visible'},
    )
)

DepositorPhone = StringField(
    'DepositorPhone',
    schemata='Transport Information',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=StringWidget(
        label=_("Phone Number of Depositor"),
        description=_("The Phone Number of the Depositor."),
        visible={'edit': 'visible', 'view': 'visible'},
    )
)

DepartureDate = DateTimeField(
    'DepartureDate',
    schemata='Transport Information',
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=DateTimeWidget(
        label=_("Departure Date"),
        description=_("When this package was sent to the biobank."),
        show_time=True,
        visible={'edit': 'visible', 'view': 'visible'}
    )
)

ArrivalDate = DateTimeField(
    'ArrivalDate',
    schemata='Sample Deposit and Arrival',
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=DateTimeWidget(
        label=_("Arrival Date"),
        description=_("When this package arrived at the biobank."),
        show_time=True,
        # visible={'edit': 'visible', 'view': 'visible'}
        visible={'edit': 'visible',
                 'view': 'visible',
                 # 'header_table': 'visible',
                 'load_up': {'view': 'visible', 'edit': 'invisible'},
                 'arrived': {'view': 'visible', 'edit': 'visible'},
                 },
    )
)

NumberOfPackages = StringField(
    'NumberOfPackages',
    schemata='Transport Information',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=StringWidget(
        label=_("Number Of Packages"),
        description=_("The Number Of Packages."),
        visible={'edit': 'visible', 'view': 'visible'},
    )
)

DepartureTemperature = StringField(
    'DepartureTemperature',
    schemata='Transport Information',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=StringWidget(
        label=_("Departure Temperature"),
        description=_("The Temperature of the package when the transport left for the biobank."),
        visible={'edit': 'visible', 'view': 'visible'},
    )
)

ArrivalTemperature = StringField(
    'ArrivalTemperature',
    schemata='Sample Deposit and Arrival',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=StringWidget(
        label=_("Arrival Temperature"),
        description=_("The Temperature of the package when the transport arrived at the biobank."),
        # visible={'edit': 'visible', 'view': 'visible'},
        visible={
                 # 'edit': 'visible',
                 # 'view': 'visible',
                 # 'header_table': 'visible',
                 'load_up': {'view': 'visible', 'edit': 'invisible'},
                 'arrived': {'view': 'visible', 'edit': 'visible'},
                 },
    )
)

Conformance = StringField(
    'Conformance',
    schemata='Sample Deposit and Arrival',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    vocabulary='getConformances',
    widget=SelectionWidget(
        format='select',
        label=_("Conformances"),
        description=_("Select the conformance of the transport"),
        # visible={'edit': 'visible', 'view': 'visible'},
        visible={'edit': 'visible',
                 'view': 'visible',
                 # 'header_table': 'visible',
                 'load_up': {'view': 'visible', 'edit': 'invisible'},
                 'arrived': {'view': 'visible', 'edit': 'visible'},
                 },
    )
)

NonConformities = ReferenceField(
    'NonConformities',
    schemata='Sample Deposit and Arrival',
    multiValued=1,
    allowed_types=('Conformity'),
    referenceClass=HoldingReference,
    relationship='TansportConformity',
    mode="rw",
    widget=bika_ReferenceWidget(
        label=_("Non Comformities"),
        description=_("Select non conformity"),
        size=40,
        # visible={'edit': 'visible', 'view': 'visible'},
        visible={'edit': 'visible',
                 'view': 'visible',
                 # 'header_table': 'visible',
                 'load_up': {'view': 'visible', 'edit': 'invisible'},
                 'arrived': {'view': 'visible', 'edit': 'visible'},
                 },
        catalog_name='portal_catalog',
    )
)

schema = BikaSchema.copy() + Schema((
    Client,
    Project,
    Status,
    ApplicationNumber,
    DepositorName,
    DepositorPhone,
    DepartureDate,
    ArrivalDate,
    NumberOfPackages,
    DepartureTemperature,
    ArrivalTemperature,
    Conformance,
    NonConformities,
))

schema['title'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}
schema['description'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}

class Transport(BaseContent):
    security = ClassSecurityInfo()
    implements(ITransport, IConstrainTypes)
    displayContentsTab = False
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        return safe_unicode(self.getField('ApplicationNumber').get(self)).encode('utf-8')

    def getConformances(self):
        return ['', 'Yes', 'No']

registerType(Transport, config.PROJECTNAME)