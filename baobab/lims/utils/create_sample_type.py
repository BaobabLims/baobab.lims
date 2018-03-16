from bika.lims.utils import tmpID
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from baobab.lims.idserver import renameAfterCreation


def create_sample_type(context, request, values):

    obj = _createObjectByType('SampleType', context, tmpID())

    # st_loc_list = pc(portal_type='StoragePosition', Title=values.get('StorageLocation'))
    # storage_location = st_loc_list and st_loc_list[0].getObject() or None

    obj.edit(
        title=values['title'],
        description=values['description'],
        RetentionPeriod=values['RetentionPeriod'],
        Hazardous=to_bool(values['Hazardous']),
        #SampleMatrix=samplematrix,
        Prefix=values['Prefix'],
        MinimumVolume=values['MinimumVolume'],
        #ContainerType=containertype
    )

    obj.unmarkCreationFlag()
    renameAfterCreation(obj)

    return obj


def to_bool(value):
    """ Converts a sheet string value to a boolean value.
        Needed because of utf-8 conversions
    """

    try:
        value = value.lower()
    except:
        pass
    try:
        value = value.encode('utf-8')
    except:
        pass
    try:
        value = int(value)
    except:
        pass
    if value in ('true', 1):
        return True
    else:
        return False
