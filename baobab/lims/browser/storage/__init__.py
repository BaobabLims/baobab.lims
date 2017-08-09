from plone import api
from zope.component import getAdapters

from baobab.lims.interfaces import IStorageTypeRegistration, IStockItemStorage
from baobab.lims.interfaces import ISampleStorageLocation


def getStorageTypes():
    """Return interfaces and titles for all registered storage types.
    """

    output_types = []
    adapters = getAdapters((api.portal.get(),), IStorageTypeRegistration)
    for name, storagetypes in adapters:
        output_types.extend(storagetypes)
    return output_types


def getStorageTypesByName(name_adapter):
    """Return interfaces and titles for all registered storage types.
    """
    output_types = []
    adapters = getAdapters((api.portal.get(),), IStorageTypeRegistration)
    for name, storagetypes in adapters:
        if name == name_adapter:
            output_types.extend(storagetypes)
    return output_types


def defaultUnmanagedStorageTypes(context):
    """Return the storage types provided directly by bika.lims
    """
    return [
        {'interface': IStockItemStorage,
         'identifier': IStockItemStorage.__identifier__,
         'title': 'Stock Item'}]

def defaultManagedStorageTypes(context):
    """Return the storage types provided directly by bika.lims
    """
    return [
        {'interface': ISampleStorageLocation,
         'identifier': ISampleStorageLocation.__identifier__,
         'title': 'Samples'}]
