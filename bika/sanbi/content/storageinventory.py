from bika.sanbi import bikaMessageFactory as _
from bika.lims.content.bikaschema import BikaSchema
from Products.Archetypes.public import *
from bika.lims.browser.widgets import ReferenceWidget
from AccessControl import ClassSecurityInfo
from bika.sanbi.config import PROJECTNAME
from Products.Archetypes.references import HoldingReference
from zope.interface import implements
from bika.sanbi.interfaces import IStorageInventory
from Products.CMFPlone.interfaces import IConstrainTypes
from Products.CMFCore.utils import getToolByName
from bika.sanbi.config import INVENTORY_TYPES, DIMENSION_OPTIONS
import sys

schema = BikaSchema.copy() + Schema((

    LinesField(
        'Type',
        required=1,
        vocabulary=INVENTORY_TYPES,
        widget=SelectionWidget(
            format='select',
            label=_("Type"),
            description=_("Select a storage type."),
            visible={'edit': 'visible', 'view': 'visible'},
        )),

    BooleanField(
        'LetterID',
        default=False,
        widget=BooleanWidget(
            label="Use letters for IDs",
            visible=False
        )),

    StringField(
        'FreezerID',
        searchable=True,
        mode='rw',
        widget=StringWidget(
            label=_("Freezer ID"),
            description=_("Select a Freezer ID"),
            visible={'edit': 'visible', 'view': 'visible'}
        )),

    StringField(
        'ShelfID',
        searchable=True,
        mode='rw',
        widget=StringWidget(
            label=_("Shelf ID"),
            description=_("Select a Shelf ID"),
            visible={'edit': 'visible', 'view': 'visible'}
        )),

    StringField(
        'BoxID',
        searchable=True,
        mode="rw",
        widget=StringWidget(
            label=_("Box ID"),
            description=_("Select a Box ID"),
            visible={'edit': 'visible', 'view': 'visible'}
        )),

    IntegerField(
        'NumPositions',
        required=True,
        widget=IntegerWidget(
            label=_("Number Positions"),
            default=0,
            size=20,
            description=_("Specify the number of storage positions in the box."),
            visible={'edit': 'visible', 'view': 'visible'},
        )),

    LinesField(
        'Dimension',
        required=1,
        vocabulary=DIMENSION_OPTIONS,
        widget=SelectionWidget(
            format='select',
            label=_("Graphical Representation"),
            description=_("Select a storage representation."),
            visible={'edit': 'visible', 'view': 'visible'},
        )),

    IntegerField(
        'XAxis',
        widget=IntegerWidget(
            label=_("Number of rows"),
            description=_("Specify the number of rows in a layer."),
            visible=False
        )),

    IntegerField(
        'YAxis',
        widget=IntegerWidget(
            label=_("Number of columns"),
            description=_("Specify the number of columns in a layer."),
            visible=False,
        )),

    BooleanField(
        'Location',
        default=False,
        widget=BooleanWidget(
            visible=False,
        )),

    BooleanField(
        'HasChildren',
        default=False,
        widget=BooleanWidget(
            visible=False,
        )),

    ComputedField(
        'UnitID',
        expression="context.aq_parent.getId()",
        widget=ComputedWidget(
            visible=False
        )),

    StringField(
        'StockItemID',
        widget=StringWidget(visible=False),
    ),
    BooleanField(
        'IsOccupied',
        default=0,
        widget=BooleanWidget(visible=False),
    ),
    IntegerField(
        'NumberOfAvailableChildren',
        default=0,
        widget=IntegerWidget(visible=False)
    ),
))

schema['title'].required = True
schema['title'].widget.visible = {'view': 'visible', 'edit': 'visible'}
#schema['title'].widget.size = 100
schema['description'].widget.visible = {'edit': 'visible', 'view': 'visible'}
schema['description'].widget.description = "Used in Listings and Searches"


class StorageInventory(BaseFolder):
    implements(IStorageInventory, IConstrainTypes)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    # def _renameAfterCreation(self, check_auto_id=False):
    #     from bika.lims.idserver import renameAfterCreation
    #
    #     renameAfterCreation(self)

    def getHierarchy(self):
        ancestors = []
        ancestor = self

        # TODO: Instead of looping indefinitely, use aq_chain
        for obj in ancestor.aq_chain:
            ancestors.append(obj.Title())
            if obj.portal_type == 'StorageUnit' or \
                            obj.portal_type == 'Plone Site':
                break

        return ' > '.join(reversed(ancestors))

    def getChildren(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        brains = bsc.searchResults(portal_type='StorageInventory',
                                   getUnitID=self.getId(),
                                   getLocation=True)

        return [brain.getObject() for brain in brains]

    def liberatePosition(self):
        if self.getLocation():
            self.setIsOccupied(0)
            self.setStockItemID('')
            num = self.aq_parent.getNumberOfAvailableChildren()
            self.aq_parent.setNumberOfAvailableChildren(num + 1)


registerType(StorageInventory, PROJECTNAME)
