from zope.component import getUtility
from plone.i18n.normalizer.interfaces import IFileNameNormalizer

from bika.lims.idserver import generateUniqueId as generate

import transaction

def generateUniqueId(context):
    """ Generate pretty content IDs.
        - context is used to find portal_type; in case there is no
          prefix specified for the type, the normalized portal_type is
          used as a prefix instead.
    """
    fn_normalize = getUtility(IFileNameNormalizer).normalize

    if context.portal_type == "Sample":
        barcode = context.getField('Barcode')
        barcode_value = barcode.get(context)
        if barcode_value:
            return barcode_value
        else:
            return generate(context)

    # Analysis Request IDs
    if context.portal_type == "AnalysisRequest":
        '''
        sample = context.getSample()
        prefix = sample.getSampleType().getPrefix()
        sample_id = sample.getId()
        ar_number = sample.getLastARNumber()
        ar_number = ar_number and ar_number + 1 or 1
        separator = '-'
        return fn_normalize(
            ("%s-%s" + separator + "R%s") % (
                str(sample_id),
                str(prefix),
                str(ar_number).zfill(3))
        )
        '''
        return generate(context)

def renameAfterCreation(obj):
    # Can't rename without a subtransaction commit when using portal_factory
    transaction.savepoint(optimistic=True)
    # The id returned should be normalized already
    new_id = generateUniqueId(obj)
    obj.aq_inner.aq_parent.manage_renameObject(obj.id, new_id)
    return new_id