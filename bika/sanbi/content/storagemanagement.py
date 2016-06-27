from bika.sanbi import bikaMessageFactory as _
from bika.lims.content.bikaschema import BikaSchema
from Products.Archetypes.public import *
from bika.lims.browser.widgets import ReferenceWidget
from AccessControl import ClassSecurityInfo
from bika.sanbi.config import PROJECTNAME
from Products.Archetypes.references import HoldingReference
from zope.interface import implements
from bika.sanbi.interfaces import IStorageManagement
from Products.CMFPlone.interfaces import IConstrainTypes
from Products.CMFCore.utils import getToolByName
from plone.indexer import indexer
import sys

@indexer(IStorageManagement)
def get_storage_room_id(instance):
    return instance.getStorageUnit().UID()

schema = BikaSchema.copy() + Schema((

    StringField('Type',
        required=1,
        searchable=True,
        widget=StringWidget(
            label=_('Storage type'),
            visible=False,
        )),

    ReferenceField('StorageUnit',
        required=1,
        allowed_types=('StorageUnit',),
        relationship='StorageManageUnit',
        vocabulary_display_path_bound=sys.maxsize,
        referenceClass=HoldingReference,
        widget=ReferenceWidget(
            checkbox_bound=0,
            label=_("Storage Unit"),
            description=_("Select the enclosure containing the new storage."),
            size=50,
            showOn=True,
            visible={'edit': 'visible', 'view': 'visible'},
        )),

    IntegerField('Shelves',
        widget=IntegerWidget(
            label=_("Shelves Number"),
            default=0,
            size=20,
            description=_("Specify the number of shelves for the new storage."),
            visible={'edit': 'visible', 'view': 'visible'},
        )),

    StringField(
        'ChildrenTitle',
        searchable=True,
        mode="rw",
        widget=StringWidget(
            label = _("Children Title"),
            description=_("Provide a common prefix for the children created. The title for a child will be the prefix "
                          "followed by its id, eg. 'Shelf 1'"),
            size=50,
            visible={'edit': 'visible', 'view': 'visible'}
        )),

    BooleanField(
        'StorageLocation',
        default=False,
        widget=BooleanWidget(
            label='Storage Location',
            visible=False,
        )),

    BooleanField(
        'LetterID',
        default=False,
        widget=BooleanWidget(
            label='Use letters for IDs',
            visible=False,
        )),

    # ____Shelves representation____ #
    StringField('Dimension',
                widget=StringWidget(
                    label=_("Dimension"),
                    description=_("Select a storage representation."),
                    visible=False,
                )),

    IntegerField('XAxis',
                 widget=IntegerWidget(
                     label=_("Number of rows"),
                     description=_("Specify the number of rows in a layer."),
                     visible=False
                 )),

    IntegerField('YAxis',
                widget=IntegerWidget(
                    label=_("Number of columns"),
                    description=_("Specify the number of columns in a layer."),
                    visible=False,
                )),

    IntegerField('ZAxis',
                widget=IntegerWidget(
                    label=_("Number of layers"),
                    description=_("Use number interval to encode the the layers."),
                    visible=False,
                )),
    TextField('Remarks',
        searchable = True,
        default_content_type = 'text/plain',
        allowed_content_types= ('text/plain', ),
        default_output_type = "text/html",
        widget = TextAreaWidget(
            macro = "bika_widgets/remarks",
            label=_("Remarks"),
            append_only = True,
        ),
    ),
))

schema['title'].required = True
schema['title'].widget.visible = {'view': 'visible', 'edit': 'visible'}
schema['description'].widget.visible = {'edit': 'visible', 'view': 'visible'}
schema.moveField('ChildrenTitle', before="Dimension")


class StorageManagement(BaseFolder):
    security = ClassSecurityInfo()
    implements(IStorageManagement, IConstrainTypes)
    schema = schema

    '''
    # The call to the renameAfterCreation() is in ajax.py
    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)
    '''

    def getChildren(self):
        children = []
        bsc = getToolByName(self, 'bika_setup_catalog')
        all_objects = bsc.searchResults(portal_type='StorageManagement')
        for obj in all_objects:
            obj = obj.getObject()
            if obj.getStorageUnit() == self:
                children.append(obj)

        return children

    def getPositions(self):
        children = []
        bsc = getToolByName(self, 'bika_setup_catalog')
        all_objects = bsc.searchResults(portal_type='StorageLocation', sort_on='sortable_title')
        for obj in all_objects:
            obj = obj.getObject()
            if obj.aq_parent == self:
                children.append(obj)

        return children

    def getHierarchy(self, char='>'):
        ancestors = []
        ancestor = self
        for obj in ancestor.aq_chain:
            ancestors.append(obj.getId())
            if obj.portal_type == 'StorageUnit':
                break

        return char.join(reversed(ancestors))

registerType(StorageManagement, PROJECTNAME)
