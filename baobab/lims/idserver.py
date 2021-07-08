from zope.component import getUtility
#from bika.lims.numbergenerator import INumberGenerator

from bika.lims.idserver import generateUniqueId as generate

import transaction


def generateUniqueId(context):
    """Id generation specific to Baoabab lims (overriding Bika lims)
    """
    if context.portal_type in ["Sample"]:
    # if context.portal_type in ["Sample", "VirusSample"]:
        barcode = context.getField('Barcode')
        barcode_value = barcode.get(context)
        if barcode_value:
            return barcode_value
        else:
            return generate(context)

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
