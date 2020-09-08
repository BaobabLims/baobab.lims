from Products.Archetypes.references import HoldingReference
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore import permissions
from Products.CMFPlone.interfaces import IConstrainTypes
from zope.interface import implements

from bika.lims.content.bikaschema import BikaSchema
from baobab.lims import bikaMessageFactory as _
from baobab.lims import config
from baobab.lims.interfaces import ICulturing
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from bika.lims.browser.widgets import DateTimeWidget
from Products.CMFPlone.utils import safe_unicode

ProductionBatchNumber = StringField(
    'ProductionBatchNumber',
    # schemata='Transport Information',
    widget=StringWidget(
        label=_('Production Batch Number'),
        description=_('The Production Batch Number.'),
        visible={'view': 'visible', 'edit': 'visible'}
    )
)

BiobankNumber = StringField(
    'BiobankNumber',
    # schemata='Transport Information',
    widget=StringWidget(
        label=_('Biobank Number'),
        description=_('The Biobank Number.'),
        visible={'view': 'visible', 'edit': 'visible'}
    )
)

CultureMedium = ReferenceField(
    'CultureMedium',
    # schemata='Transport Information',
    allowed_types = ('CultureMedium',),
    relationship = 'CulturingCultureMedium',
    referenceClass=HoldingReference,
    widget = bika_ReferenceWidget(
        label=_("Culture Medium"),
        visible={'edit': 'visible', 'view': 'visible'},
        size=30,
        showOn=True,
        description=_("The Culture Medium."),
    )
)

Strain = ReferenceField(
    'Strain',
    # schemata='Transport Information',
    allowed_types=('Strain',),
    relationship='CulturingStrain',
    referenceClass=HoldingReference,
    widget=bika_ReferenceWidget(
        label=_("Select Strain"),
        visible={'edit': 'visible', 'view': 'visible'},
        size=30,
        showOn=True,
        description=_("Select the Strain of this culturing."),
    )
)


DateCollectionRequest = DateTimeField(
    'DateCollectionRequest',
    # schemata='Culture Appearance On Solid Medium',
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=DateTimeWidget(
        label=_("Date Of Collection Request"),
        description=_("Date Of Collection Request."),
        # show_time=True,
        visible={'edit': 'visible', 'view': 'visible'}
    )
)

# Culture properties in liquid
Living = StringField(
    'Living',
    schemata='Culture properties in liquid',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    vocabulary='getYesNoOptions',
    widget=SelectionWidget(
        format='select',
        label=_("Living"),
        description=_("Is the culture Living"),
        visible={'edit': 'visible', 'view': 'visible'},
    )
)

Spores = StringField(
    'Spores',
    schemata='Culture properties in liquid',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    vocabulary='getYesNoOptions',
    widget=SelectionWidget(
        format='select',
        label=_("Spores"),
        description=_("Is the culture Spores"),
        visible={'edit': 'visible', 'view': 'visible'},
    )
)

Contaminants = StringField(
    'Contaminants',
    schemata='Culture properties in liquid',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    vocabulary='getYesNoOptions',
    widget=SelectionWidget(
        format='select',
        label=_("Contaminants"),
        description=_("Is there Contaminants"),
        visible={'edit': 'visible', 'view': 'visible'},
    )
)

# Microscopic appearance of fresh culture
Mobile = StringField(
    'Mobile',
    schemata='Microscopic appearance of fresh culture',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    vocabulary='getYesNoOptions',
    widget=SelectionWidget(
        format='select',
        label=_("Mobile"),
        description=_("Is the culture Mobile"),
        visible={'edit': 'visible', 'view': 'visible'},
    )
)

PolarFlagella = BooleanField(
    'PolarFlagella',
    # schemata="Security",
    schemata='Microscopic appearance of fresh culture',
    default=False,
    widget=BooleanWidget(
        label=_("PolarFlagella"),
        description=_('Indicates if this culture is Polar Flagella.'),
        visible={'view': 'visible', 'edit': 'visible'}
    )
)

Lophotrichous = BooleanField(
    'Lophotrichous',
    # schemata="Security",
    schemata='Microscopic appearance of fresh culture',
    default=False,
    widget=BooleanWidget(
        label=_("Lophotrichous"),
        description=_('Indicates if this culture is Lophotrichous.'),
        visible={'view': 'visible', 'edit': 'visible'}
    )
)

Peritrichous = BooleanField(
    'Peritrichous',
    # schemata="Security",
    schemata='Microscopic appearance of fresh culture',
    default=False,
    widget=BooleanWidget(
        label=_("Peritrichous"),
        description=_('Indicates if this culturing is Peritrichous.'),
        visible={'view': 'visible', 'edit': 'visible'}
    )
)

Pure = StringField(
    'Pure',
    schemata='Microscopic appearance of fresh culture',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    vocabulary='getYesNoOptions',
    widget=SelectionWidget(
        format='select',
        label=_("Pure"),
        description=_("Is the culture Pure"),
        visible={'edit': 'visible', 'view': 'visible'},
    )
)

Contaminated = StringField(
    'Contaminated',
    schemata='Microscopic appearance of fresh culture',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    vocabulary='getYesNoOptions',
    widget=SelectionWidget(
        format='select',
        label=_("Contaminated"),
        description=_("Is the culture Contaminated"),
        visible={'edit': 'visible', 'view': 'visible'},
    )
)

# Microscopic appearance after straining
BaccillusStain = StringField(
    'BaccillusStain',
    schemata='Microscopic appearance after straining',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    vocabulary='getPositiveNegativeOptions',
    widget=SelectionWidget(
        format='select',
        label=_("Baccillus Stain"),
        description=_("Is the culture a Baccillus Stain"),
        visible={'edit': 'visible', 'view': 'visible'},
    )
)

CocciStain = StringField(
    'CocciStain',
    schemata='Microscopic appearance after straining',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    vocabulary='getYesNoOptions',
    widget=SelectionWidget(
        format='select',
        label=_("Cocci Stain"),
        description=_("Is the culture a Cocci Stain"),
        visible={'edit': 'visible', 'view': 'visible'},
    )
)

# Culture appearance on solid medium
ColonySize = StringField(
    'ColonySize',
    schemata='Culture Appearance On Solid Medium',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=StringWidget(
        label=_("Colony Size"),
        description=_("The size of the colony."),
        visible={'edit': 'visible', 'view': 'visible'},
    )
)

SurfaceOfColony = StringField(
    'SurfaceOfColony',
    schemata='Culture Appearance On Solid Medium',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=StringWidget(
        label=_("Surface Of Colony"),
        description=_("The Surface Of The Colony."),
        visible={'edit': 'visible', 'view': 'visible'},
    )
)

Regularity = StringField(
    'Regularity',
    schemata='Culture Appearance On Solid Medium',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=StringWidget(
        label=_("Regularity"),
        description=_("Regularity."),
        visible={'edit': 'visible', 'view': 'visible'},
    )
)

Analyst = ReferenceField(
    'Analyst',
    schemata='Culture Appearance On Solid Medium',
    allowed_types=('LabContact'),
    referenceClass=HoldingReference,
    relationship='CulturingLabContact',
    mode="rw",
    widget=bika_ReferenceWidget(
        label=_("Analyst"),
        description=_("The analyst doing the culturing."),
        size=40,
        # base_query={'review_state': 'sample_received', 'cancellation_state': 'active'},
        visible={'edit': 'visible', 'view': 'visible'},
        # catalog_name='bika_catalog',
        showOn=True
    )
)

DateOfControl = DateTimeField(
    'DateOfControl',
    schemata='Culture Appearance On Solid Medium',
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=DateTimeWidget(
        label=_("Date Of Control"),
        description=_("Date Of Control."),
        # show_time=True,
        visible={'edit': 'visible', 'view': 'visible'}
    )
)

#Non Conformance
Conformity = StringField(
    'Conformity',
    schemata='Non Conformance',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    vocabulary='getYesNoOptions',
    widget=SelectionWidget(
        format='select',
        label=_("Conformity"),
        description=_("Select the conformance of the culture"),
        visible={'edit': 'visible', 'view': 'visible'},
    )
)

NonConformities = ReferenceField(
    'NonConformities',
    schemata='Non Conformance',
    multiValued=1,
    allowed_types=('Conformity'),
    referenceClass=HoldingReference,
    relationship='TansportConformity',
    mode="rw",
    widget=bika_ReferenceWidget(
        label=_("Non Comformities"),
        description=_("Select non conformity"),
        size=40,
        visible={'edit': 'visible', 'view': 'visible'},
        catalog_name='portal_catalog',
    )
)

schema = BikaSchema.copy() + Schema((
    ProductionBatchNumber,
    BiobankNumber,
    CultureMedium,
    Strain,
    DateCollectionRequest,
    Living,
    Spores,
    Contaminants,
    Mobile,
    PolarFlagella,
    Lophotrichous,
    Peritrichous,
    Pure,
    Contaminated,
    BaccillusStain,
    CocciStain,
    ColonySize,
    SurfaceOfColony,
    Regularity,
    Analyst,
    DateOfControl,
    Conformity,
    NonConformities,
))

schema['title'].widget.visible = {'view': 'visible', 'edit': 'visible'}
schema['description'].widget.visible = {'view': 'visible', 'edit': 'visible'}

class Culturing(BaseContent):
    security = ClassSecurityInfo()
    implements(ICulturing, IConstrainTypes)
    displayContentsTab = False
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    # def Title(self):
    #     return safe_unicode(self.getField('ApplicationNumber').get(self)).encode('utf-8')

    def getYesNoOptions(self):
        return ['', 'Yes', 'No']

    def getPositiveNegativeOptions(self):
        return ['', 'Positive', 'Negative']

registerType(Culturing, config.PROJECTNAME)