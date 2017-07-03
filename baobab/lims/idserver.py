from zope.component import getUtility
from bika.lims.numbergenerator import INumberGenerator

from bika.lims.idserver import generateUniqueId as generate

import transaction


def generateUniqueId(context):

    def getLastCounter(context, config):
        if config.get('counter_type', '') == 'backreference':
            return len(context.getBackReferences(config['counter_reference']))-1
        elif config.get('counter_type', '') == 'contained':
            return len(context.objectItems(config['counter_reference']))-1
        else:
            raise RuntimeError('ID Server: missing values in configuration')

    number_generator = getUtility(INumberGenerator)

    if context.portal_type == "Sample":
        barcode = context.getField('Barcode')
        barcode_value = barcode.get(context)
        if barcode_value:
            return barcode_value
        else:
            return generate(context)

    # Analysis Request IDs
    if context.portal_type == "AnalysisRequest":
        return generate(context)

def renameAfterCreation(obj):
    # Can't rename without a subtransaction commit when using portal_factory
    transaction.savepoint(optimistic=True)
    # The id returned should be normalized already
    new_id = generateUniqueId(obj)
    obj.aq_inner.aq_parent.manage_renameObject(obj.id, new_id)
    return new_id