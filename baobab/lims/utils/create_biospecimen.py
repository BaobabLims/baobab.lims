from bika.lims.utils import tmpID
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from baobab.lims.idserver import renameAfterCreation


def create_sample(context, request, values):
    obj = _createObjectByType('Sample', context, tmpID())

    # st_loc_list = pc(portal_type='StoragePosition', Title=values.get('StorageLocation'))
    # storage_location = st_loc_list and st_loc_list[0].getObject() or None

    obj.edit(
        title=values['title'],
        description=values['description'],
        Project=values['Project'],
        AllowSharing=values['AllowSharing'],
        SampleType=values['SampleType'],
        StorageLocation=values['StorageLocation'],
        SubjectID=values['SubjectID'],
        Barcode=values['Barcode'],
        Volume=values['Volume'],
        Unit=values['Unit'],
        LinkedSample=values['LinkedSample'],
        DateCreated=values['DateCreated'],
    )

    obj.unmarkCreationFlag()
    renameAfterCreation(obj)

    if values.has_key('APISource'):
        obj.api_source = values['APISource']

    from baobab.lims.subscribers.sample import ObjectInitializedEventHandler
    ObjectInitializedEventHandler(obj, None)

    return obj