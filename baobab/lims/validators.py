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
        instance = kwargs['instance']
        wftool = instance.portal_workflow
        translate = getToolByName(instance, 'translation_service').translate
        review_state = wftool.getInfoFor(instance, 'review_state')
        if review_state != 'created' and instance.getWillExtract() is True:
            msg = _("Validation failed: Must be on state Created to submitted")
            return to_utf8(translate(msg))
        return True

validation.register(ExtractGenomicMaterialValidator())
