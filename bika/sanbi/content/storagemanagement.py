import sys
from AccessControl import ClassSecurityInfo

from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IConstrainTypes
from zope.interface import implements

from bika.lims.browser.widgets import ReferenceWidget
from bika.lims.content.bikaschema import BikaSchema
from bika.sanbi import bikaMessageFactory as _
from bika.sanbi.config import PROJECTNAME
from bika.sanbi.interfaces import IStorageManagement

schema = BikaSchema.copy() + Schema((

    StringField('Type',
        required=1,
        searchable=True,
        widget=StringWidget(
            label=_('Storage type'),
            visible=False,
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

    def getChildren(self):
        return self.objectValues('StorageManagement')

    def getPositions(self):
        children = []
        bsc = getToolByName(self, 'bika_setup_catalog')
        brains = bsc.searchResults(
            portal_type='StorageLocation',
            inactive_state='active',
            sort_on='sortable_title',
            path={'query': "/".join(self.getPhysicalPath()), 'level': 0})

        return [brain.getObject() for brain in brains]

    def getHierarchy(self, char='>'):
        ancestors = []
        ancestor = self
        for obj in ancestor.aq_chain:
            ancestors.append(obj.getId())
            if obj.portal_type == 'StorageUnit':
                break

        return char.join(reversed(ancestors))

registerType(StorageManagement, PROJECTNAME)
