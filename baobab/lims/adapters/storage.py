from baobab.lims.interfaces import IBiospecimenStorage, \
    IAliquotStorage, IKitStorage


def defaultStorageTypes(context):
    """Return the storage types provided directly by baobab.lims
    """
    return [
        {'interface': IKitStorage,
         'identifier': IKitStorage.__identifier__,
         'title': 'Kits'}
    ]
