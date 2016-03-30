from bika.sanbi import bikaMessageFactory as _
from bika.lims.content.bikaschema import BikaSchema
from Products.Archetypes.public import *
from Products.CMFCore import permissions
from bika.lims.browser.widgets.datetimewidget import DateTimeWidget
from bika.lims.browser.widgets import ReferenceWidget
from AccessControl import ClassSecurityInfo
from bika.sanbi.config import PROJECTNAME
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.references import HoldingReference
from zope.interface import implements
from bika.sanbi.interfaces import IStorageOrder
from Products.CMFPlone.interfaces import IConstrainTypes
from Acquisition import aq_chain
import sys

schema = BikaSchema.copy() + Schema((
    StringField('StorageOrderID',
        required = 1,
        searchable = True,
        validators = ('uniquefieldvalidator', 'standard_id_validator'),
        widget = StringWidget(
            label=_("Storage ID"),
            placeholder='eg: FZ001, ...',
        ),
    ),
    ReferenceField(
        'StorageUnit',
        required=1,
        #vocabulary='getParentUnits',
        allowed_types=('StorageUnit', 'StorageOrder',),
        relationship='StorageUnitLevel',
        vocabulary_display_path_bound=sys.maxsize,
        referenceClass=HoldingReference,
        widget=ReferenceWidget(
            checkbox_bound=0,
            label=_("Level"),
            description=_("The Parent level"),
            size=50,
            showOn=True,
            visible={'view': 'visible', 'edit': 'visible'},
        ),
    ),
    IntegerField('Number',
        widget = IntegerWidget(
            label=_("Number of items"),
            default=0,
            size=15,
            description=_("The number of storage items to create"),
            visible={'view': 'visible', 'edit': 'visible'},
        ),
    ),
    StringField(
        'ChildTitle',
        searchable=True,
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=StringWidget(
            label = _("Children Title"),
            description=_("The common title shared by automatically created childs."),
            size=50,
        ),
    ),
    BooleanField(
        'Characters',
         default=False,
         widget=BooleanWidget(
             label=_("Characters [A..Z]"),
             description=_("Differentiate child's title by adding a letter at the end, e.g Box A, Box B, etc."),
         ),
    ),
    BooleanField(
        'TwoDimension',
        default=False,
        widget=BooleanWidget(
            label=_("Two Dimension"),
            description=_("2D storage representation like a 2D Grid."),
        ),
    ),
    IntegerField(
        'XAxis',
        widget = IntegerWidget(
            label=_("XAxis dimension"),
            default=0,
            size=15,
            description=_("The number of rows. Number of cols be computed automatically."),
            visible={'view': 'visible', 'edit': 'visible'},
        ),
    ),
    ComputedField(
        'Parent',
        expression='context.aq_parent.UID()',
        widget=ComputedWidget(
                visible=False,
        ),
    ),
    ComputedField(
        'Hierarchy',
        expression='context.getHierarchy()',
        widget=ComputedWidget(visible=False,),
    ),
    ComputedField('CategoryTitle',
          expression="context.getHierarchy().split('>')[1]",
          widget=ComputedWidget(
              visible=False,
          ),
    ),
))

schema['title'].required = True
schema['title'].widget.visible = {'view': 'visible', 'edit': 'visible'}
schema['description'].widget.visible = {'view': 'visible', 'edit': 'visible'}
#schema['description'].schemata = 'default'

class StorageOrder(BaseFolder):
    security = ClassSecurityInfo()
    #displayContentsTab = True
    implements(IStorageOrder, IConstrainTypes)
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    # This function is not used anywhere
    def getParentUnits(self):
        catalog = getToolByName(self.context, 'bika_setup_catalog')
        storage_units = []
        for unit in catalog(portal_type="StorageUnit", inactive_state='active'):
            storage_units.append((unit.UID, unit.Title))

        return DisplayList(storage_units)

    def getHierarchy(self):
        ancestors = []
        ancestor = self

        for obj in ancestor.aq_chain:
            ancestors.append(obj.Title())
            if obj.portal_type == "StorageUnit":
                break

        return '>'.join(reversed(ancestors))

    def getChildren(self):
        childs = []
        bsc = getToolByName(self, 'bika_setup_catalog')
        all_objects = bsc.searchResults(portal_type='StorageOrder')
        for obj in all_objects:
            obj = obj.getObject()
            if obj.getStorageUnit() == self:
                childs.append(obj)

        return childs

registerType(StorageOrder, PROJECTNAME)