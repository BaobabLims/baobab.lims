# from Products.Archetypes.references import HoldingReference
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from zope.interface import implements
from Products.CMFCore import permissions

from bika.lims.content.bikaschema import BikaSchema
# from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from bika.lims.browser.widgets import DateTimeWidget
# from bika.lims.browser.widgets import SelectionWidget as BikaSelectionWidget

from baobab.lims.config import PROJECTNAME
from baobab.lims.interfaces import IAuditLog
from baobab.lims import bikaMessageFactory as _
# from baobab.lims.interfaces import ISampleStorageLocation
#
# from zope.component import queryUtility
# from Products.Archetypes.interfaces.vocabulary import IVocabulary
# from plone.registry.interfaces import IRegistry
# from Products.Archetypes.utils import DisplayList
#
# import sys

AuditDate = DateTimeField(
    'AuditDate',
    mode="rw",
    required=True,
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=DateTimeWidget(
        label=_("Audit Date"),
        description=_("Date that this audit entry was created."),
        show_time=True,
        visible={'edit': 'visible', 'view': 'visible'}
    )
)

AuditUser = StringField(
    'AuditUser',
    widget=StringWidget(
        label=_('Audit User'),
        description=_('User that was involved in the creation of this audit entry.'),
        visible={'view': 'visible', 'edit': 'visible'}
    )
)

ItemType = StringField(
    'ItemType',
    widget=StringWidget(
        label=_('Content Type'),
        description=_('The content type that was involved in this audit entry.'),
        visible={'view': 'visible', 'edit': 'visible'}
    )
)

ItemTitle = StringField(
    'ItemTitle',
    widget=StringWidget(
        label=_('Item Title'),
        description=_('The title of the item being changed.'),
        visible={'view': 'visible', 'edit': 'visible'}
    )
)

ItemUID = StringField(
    'ItemUID',
    widget=StringWidget(
        label=_('Item UID'),
        description=_('The UID of the item being changed.'),
        visible={'view': 'visible', 'edit': 'visible'}
    )
)

ChangedValue = StringField(
    'ChangedValue',
    widget=StringWidget(
        label=_('Changed Value'),
        description=_('The name of the field that was changed.  Or New if the record is new.'),
        visible={'view': 'visible', 'edit': 'visible'}
    )
)

OldValue  = StringField(
    'OldValue',
    widget=StringWidget(
        label=_('Old Value'),
        description=_('The old value of the field.  The value before the change.'),
        visible={'view': 'visible', 'edit': 'visible'}
    )
)

NewValue = StringField(
    'NewValue',
    widget=StringWidget(
        label=_('New Value'),
        description=_('The new value of the field after the change.'),
        visible={'view': 'visible', 'edit': 'visible'}
    )
)


schema = BikaSchema.copy() + Schema((
    AuditDate,
    AuditUser,
    ItemType,
    ItemTitle,
    ItemUID,
    ChangedValue,
    OldValue,
    NewValue,
))

schema['title'].widget.visible = {'view': 'visible', 'edit': 'visible'}
schema['description'].widget.visible = {'view': 'visible', 'edit': 'visible'}

class AuditLog(BaseContent):
    implements(IAuditLog)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from baobab.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

# def ObjectModifiedEventHandler(instance, event):
#     """ Called if the object is modified.
#         Note from QC 2018-11-05:  As far as I can see this change happens after the object is modified.
#         I tested by altering the Serum Colour and by the time it does a data dump here the object
#         already has the new colour.
#     """
#
#     if instance.portal_type == 'SampleBatch':
#         from baobab.lims.idserver import renameAfterEdit
#         renameAfterEdit(instance)

registerType(AuditLog, PROJECTNAME)

