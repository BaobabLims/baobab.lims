from bika.sanbi.interfaces import IBiospecimenStorage, \
    IAliquotStorage, IKitStorage


def defaultStorageTypes(context):
    """Return the storage types provided directly by bika.sanbi
    """
    return [
        {'interface': IKitStorage,
         'identifier': IKitStorage.__identifier__,
         'title': 'Kits'}
    ]
