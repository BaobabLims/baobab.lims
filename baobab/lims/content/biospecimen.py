from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes.atapi import *
from Products.CMFPlone.interfaces import IConstrainTypes
from plone.indexer import indexer
from zope.interface import implements
from Products.CMFCore import permissions
from plone.app.folder.folder import ATFolder
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.references import HoldingReference
from DateTime import DateTime

from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.content.bikaschema import BikaSchema, BikaFolderSchema
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from baobab.lims import bikaMessageFactory as _
from baobab.lims.interfaces import IBiospecimen, IBiospecimenStorage
from baobab.lims.config import PROJECTNAME

import sys

@indexer(IBiospecimen)
def get_biospecimen_kit_uid(instance):
    return instance.getKit().UID()

@indexer(IBiospecimen)
def get_biospecimen_project_uid(instance):
    return instance.getKit().getProject().UID()

schema = BikaFolderSchema.copy() + BikaSchema.copy() + Schema((

    ReferenceField(
        'Type',
        vocabulary_display_path_bound=sys.maxint,
        allowed_types=('BiospecType',),
        relationship='BiospecimenType',
        referenceClass=HoldingReference,
        widget=bika_ReferenceWidget(
            label=_("Biospecimen type"),
            catalog_name='bika_setup_catalog',
            size=30,
            showOn=True,
            description=_("Click and select a biospecimen type."),
            visible={'view': 'invisible', 'edit': 'visible'}
        )
    ),

    ReferenceField('Kit',
        vocabulary_display_path_bound=sys.maxint,
        allowed_types=('Kit',),
        relationship='BiospecimenKit',
        referenceClass=HoldingReference,
        widget=bika_ReferenceWidget(
            label=_("Kit"),
            catalog_name='bika_catalog',
            visible={'view': 'invisible', 'edit': 'visible'}
        )),

    StringField('SubjectID',
        searchable=True,
        widget=StringWidget(
            label=_("Subject ID"),
            description=_("Human-subject ID the specimen is taken from."),
            visible={'edit': 'visible', 'view': 'visible'}
        )),

    StringField('Barcode',
        searchable=True,
        widget=StringWidget(
            label=_("Barcode"),
            description=_("Biospecimen barcode."),
            visible={'edit': 'visible', 'view': 'visible'}
        )),

    FixedPointField('Volume',
        required=1,
        default="0.00",
        widget=DecimalWidget(
            label=_("Volume"),
            size=15,
            description=_("The The volume of the biospecimen taken from the subject."),
            visible={'edit': 'visible', 'view': 'visible'}
        )),

    StringField('Unit',
        widget=StringWidget(
            label=_("Unit"),
            visible={'edit': 'visible', 'view': 'visible'}
        )),

    ReferenceField(
        'StorageLocation',
        allowed_types=('UnmanagedStorage', 'StoragePosition'),
        relationship='ItemStorageLocation',
        widget=bika_ReferenceWidget(
            label=_("Storage Location"),
            description=_("Location where item is kept"),
            size=40,
            visible={'edit': 'visible', 'view': 'visible'},
            # catalog_name='bika_setup_catalog',
            showOn=True,
            render_own_label=True,
            base_query={'inactive_state': 'active',
                        'review_state': 'available',
                        'object_provides': IBiospecimenStorage.__identifier__},
            colModel=[{'columnName': 'UID', 'hidden': True},
                      {'columnName': 'Title', 'width': '50', 'label': _('Title')},
                      {"columnName": "Hierarchy", "align": "left", "label": "Hierarchy", "width": "50"}
                      ],
        )
    ),

    DateTimeField(
        'DatetimeReceived',
        default_method=DateTime,
        widget=CalendarWidget(
            label='Date and Time Received',
            description='Select the date and time the biospecimen is received.',
            ampm=1,
            visible={'edit': 'visible', 'view': 'visible'}
        )
    ),

    DateTimeField(
        'DateCreated',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=DateTimeWidget(
            label=_("Date Created"),
            visible={'edit': 'invisible', 'view': 'invisible'},
        )
    ),
))

schema['title'].widget.visible = {'edit': 'visible', 'view': 'visible'}
schema['description'].widget.visible = {'edit': 'visible', 'view': 'visible'}
schema['description'].schemata = 'default'


class Biospecimen(ATFolder):
    implements(IBiospecimen, IConstrainTypes)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getBiospecTypes(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [(c.UID, c.Title) \
                 for c in bsc(portal_type='BiospecType',
                              inactive_state='active')]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(items)

    def getKits(self):
        bc = getToolByName(self, 'bika_catalog')
        items = [(c.UID, c.Title) \
                 for c in bc(portal_type='Kit',
                             inactive_state='active',
                             kit_project_uid=self.aq_parent)]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(items)


    def getDocuments(self):
        """
        Return all the multifile objects related with the instrument
        """
        return self.objectValues('Multimage')

    def getStorageUnits(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [(c.UID, c.Title)
                 for c in bsc(portal_type='StorageUnit',
                              inactive_state='active')]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(items)

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
registerType(Biospecimen, PROJECTNAME)
