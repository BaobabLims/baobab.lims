from Products.CMFCore.utils import getToolByName

from bika.lims.idserver import generateUniqueId as generate

import transaction


def generateUniqueId(context):
    """Id generation specific to Baoabab lims (overriding Bika lims)
    """
    if context.portal_type == "Sample":
        barcode = context.getField('Barcode')
        barcode_value = barcode.get(context)
        if barcode_value:
            return barcode_value
        else:
            return generate(context)

    elif context.portal_type == "SampleBatch":
        subject_id = context.getSubjectID()
        date_created = context.getDateCreated().strftime('%g%m%d')
        bc = getToolByName(context, 'bika_catalog')
        brains = bc(portal_type="SampleBatch", getSubjectID=subject_id)
        suffix = '1'
        prefix = subject_id + '-' + date_created
        suffixes = [int(brain.id.split('-')[-1]) for brain in brains if brain.id.startswith(prefix)]
        if suffixes:
            suffix = str(max(suffixes) + 1)

        id = prefix + '-' + suffix
        context.title = prefix + '-' + suffix

        return id

    # Analysis Request IDs
    elif context.portal_type == "AnalysisRequest":
        return generate(context)
    else:
        return generate(context)

def renameAfterCreation(obj):
    # Can't rename without a subtransaction commit when using portal_factory
    transaction.savepoint(optimistic=True)
    # The id returned should be normalized already
    new_id = generateUniqueId(obj)
    obj.aq_inner.aq_parent.manage_renameObject(obj.id, new_id)
    return new_id