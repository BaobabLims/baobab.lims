from bika.sanbi.interfaces import IStockItemStorageLocation, \
    IBioSpecimenStorageLocation, IAliquotStorageLocation, IKitStorageLocation


def defaultStorageTypes(context):
    """Return the storage types provided directly by bika.sanbi
    """
    return [
        {'interface': IStockItemStorageLocation, 'title': 'Stock Item'},
        {'interface': IBioSpecimenStorageLocation, 'title': 'Bio Specimen'},
        {'interface': IAliquotStorageLocation, 'title': 'Aliquot'},
        {'interface': IKitStorageLocation, 'title': 'Kit'}
    ]
