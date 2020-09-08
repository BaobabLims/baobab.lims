from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import (
    BaseContent, BooleanField, Schema, registerType)
from Products.Archetypes.Widget import SelectionWidget
from Products.CMFCore import permissions
from Products.CMFPlone.interfaces import IConstrainTypes
from Products.validation import validation
from Products.validation.interfaces.IValidator import IValidator
from Products.CMFCore.utils import getToolByName
from zope.interface import implements

from baobab.lims import bikaMessageFactory as _
from baobab.lims import config
from baobab.lims.interfaces import IResultValidation

from bika.lims.utils import to_utf8
from bika.lims.browser.fields import DateTimeField
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.content.bikaschema import BikaSchema


class ResultValidation_StringValidation_Validator:
    """
        Verifies that the when StrainValid is True, DateOfValidation must be
        required.
    """

    implements(IValidator)
    name = "resultvalidation_StrainValidation_validator"

    def __call__(self, value, *args, **kwargs):
        instance = kwargs['instance']
        request = kwargs.get('REQUEST', {})
        form = request.form
        date_validated = form.get('DateOfValidation', None)
        if value.lower() == 'true' and not date_validated:
            tool_by_name = getToolByName(instance, 'translation_service')
            translate = tool_by_name.translate
            msg = _(
                "Date of validaton is required if Strain validation is Yes")
            return to_utf8(translate(msg))
        return True


validation.register(ResultValidation_StringValidation_Validator())


class ResultValidation_DeliveryOfCertificate_Validator:
    """
        Verifies that the when DeliveryOfCerticate is True, DateDelivered must
        be required.
    """

    implements(IValidator)
    name = "resultvalidation_DeliveryOfCertificate_validator"

    def __call__(self, value, *args, **kwargs):
        instance = kwargs['instance']
        request = kwargs.get('REQUEST', {})
        form = request.form
        date_validated = form.get('DateDelivered', None)
        if value.lower() == 'true' and not date_validated:
            tool_by_name = getToolByName(instance, 'translation_service')
            translate = tool_by_name.translate
            msg = _(
                "Date delivered is required if Delivery of Certificate is Yes")
            return to_utf8(translate(msg))
        return True


validation.register(ResultValidation_DeliveryOfCertificate_Validator())


class ResultValidation_BiobankedStorage_Validator:
    """
        Verifies that the when BiobankedStorage is True, DateStored must
        be required.
    """

    implements(IValidator)
    name = "resultvalidation_BiobankedStorage_validator"

    def __call__(self, value, *args, **kwargs):
        instance = kwargs['instance']
        request = kwargs.get('REQUEST', {})
        form = request.form
        date_stored = form.get('DateStored', None)
        if value.lower() == 'true' and not date_stored:
            tool_by_name = getToolByName(instance, 'translation_service')
            translate = tool_by_name.translate
            msg = _("Date of storage is required if Biobanked storage is Yes")
            return to_utf8(translate(msg))
        return True


validation.register(ResultValidation_BiobankedStorage_Validator())

StrainValidation = BooleanField(
        'StrainValidation',
        required=1,
        validators=('resultvalidation_StrainValidation_validator',),
        format="select",
        widget=SelectionWidget(
            label=_("Strain validation"),
            description=_(''),
            visible={'view': 'visible', 'edit': 'visible'},
        )
    )
DateOfValidation = DateTimeField(
    'DateOfValidation',
    required=0,
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=DateTimeWidget(
        label=_("Date of Validation"),
        description=_(""),
        visible={'edit': 'visible', 'view': 'visible'},
    )
)
DeliveryOfCerticate = BooleanField(
        'DeliveryOfCerticate',
        required=1,
        validators=('resultvalidation_DeliveryOfCertificate_validator',),
        format="select",
        widget=SelectionWidget(
            label=_("Delivery of certificate"),
            description=_(''),
            visible={'view': 'visible', 'edit': 'visible'},
        )
    )
DateDelivered = DateTimeField(
    'DateDelivered',
    required=0,
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=DateTimeWidget(
        label=_("Date Delivered"),
        description=_(""),
        visible={'edit': 'visible', 'view': 'visible'},
    )
)

BiobankedStorage = BooleanField(
        'BiobankedStorage',
        required=1,
        validators=('resultvalidation_BiobankedStorage_validator',),
        format="select",
        widget=SelectionWidget(
            label=_("Biobanked storage"),
            description=_(''),
            visible={'view': 'visible', 'edit': 'visible'},
        )
    )
DateStored = DateTimeField(
    'DateStored',
    required=0,
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=DateTimeWidget(
        label=_("Date of storage"),
        description=_(""),
        visible={'edit': 'visible', 'view': 'visible'},
    )
)
schema = BikaSchema.copy() + Schema((
    StrainValidation,
    DateOfValidation,
    DeliveryOfCerticate,
    DateDelivered,
    BiobankedStorage,
    DateStored

))

schema['title'].required = True
schema['title'].widget.label = 'Biobank number'


class ResultValidation(BaseContent):
    security = ClassSecurityInfo()
    implements(IResultValidation, IConstrainTypes)
    displayContentsTab = False
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)


registerType(ResultValidation, config.PROJECTNAME)
