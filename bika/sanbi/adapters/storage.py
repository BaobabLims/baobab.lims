from bika.sanbi.interfaces import IBioSpecimenStorage, \
    IAliquotStorage, IKitStorage


def defaultStorageTypes(context):
    """Return the storage types provided directly by bika.sanbi
    """
    return [
        {'interface': IBioSpecimenStorage,
         'identifier': IBioSpecimenStorage.__identifier__,
         'title': 'Bio Specimen'},
        {'interface': IAliquotStorage,
         'identifier': IAliquotStorage.__identifier__,
         'title': 'Aliquot'},
        {'interface': IKitStorage,
         'identifier': IKitStorage.__identifier__,
         'title': 'Kit'}
    ]
