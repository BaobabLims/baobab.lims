# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from Products.validation import validation
from Products.validation.interfaces.IValidator import IValidator

from zope.interface import implements

from bika.lims import api
from bika.lims.utils import to_utf8
from bika.lims import bikaMessageFactory as _


class ExtractGenomicMaterialValidator:
    """
    """

    implements(IValidator)
    name = "extractgenomicmaterialvalidator"

    def __call__(self, value, *args, **kwargs):
        empty_line = [{'ExtractionBarcode': '',
            'orderindex_': 'template_row_marker',
            'HeatInactivated': '', 'VirusSample': '', 'WasKitUsed': '',
            'Notes': [], 'Volume': '', 'Unit': '', 'Method': '',
            'KitNumber': ''}]
        if value == empty_line:
            return True

        instance = kwargs['instance']
        review_state = instance.portal_workflow.getInfoFor(instance, 'review_state')
        if review_state == 'created':
            return True

        translate = getToolByName(instance, 'translation_service').translate
        if instance.getWillExtract() is False:
            msg = _("Validation failed: Extraction not part of the process")
            return to_utf8(translate(msg))
        return True

validation.register(ExtractGenomicMaterialValidator())
