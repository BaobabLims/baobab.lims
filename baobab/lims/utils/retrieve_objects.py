from bika.lims.utils import tmpID
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from baobab.lims.idserver import renameAfterCreation


def get_object_from_title(context, portal_type, object_title, catalog='portal_catalog'):
    if not object_title:
        return None
    catalog = get_catalog(context, catalog)
    try:
        brains = catalog(portal_type=portal_type, Title=str(object_title))
        return brains[0].getObject()
    except Exception as e:
        return None


def get_object_from_uid(context, object_uid, catalog='portal_catalog'):
    catalog = get_catalog(context, catalog)
    try:
        brains = catalog(UID=object_uid)
        return brains[0].getObject()
    except Exception as e:
        raise ObjectNotFoundException('No object matching the supplied UID has been found.')


def get_catalog(context, catalog_name='portal_catalog'):
    if catalog_name in ['portal_catalog', 'bika_catalog', 'bika_setup_catalog']:
        return getToolByName(context, catalog_name)

    raise InvalidCatalogException('No valid catalog has been found')


def getRNAorDNASampleTypes(context):
    bsc = getToolByName(context, 'bika_setup_catalog')
    brains = bsc(portal_type='SampleType', inactive_state='active')
    dna_rna_sample_types = []

    for brain in brains:
        obj = brain.getObject()
        if obj.getField('Prefix').get(obj).lower() in ('rna', 'dna'):
            dna_rna_sample_types.append(obj)

    return dna_rna_sample_types


class InvalidCatalogException(Exception):
    pass


class ObjectNotFoundException(Exception):
    pass
