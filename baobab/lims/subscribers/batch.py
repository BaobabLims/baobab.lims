# import time
from utils import getLocalServerTime

def ObjectInitializedEventHandler(instance, event):
    """called an object is created
    """
    if instance.portal_type == 'SampleBatch':
        updateLocalServerTime(instance)

def ObjectModifiedEventHandler(instance, event):
    """ Called if the object is modified
    """
    if instance.portal_type == 'SampleBatch':
        updateLocalServerTime(instance)

def updateLocalServerTime(instance):

    date_created = instance.getField('DateCreated').get(instance)
    cfg_date_time = instance.getField('CfgDateTime').get(instance)

    new_date_created = getLocalServerTime(date_created)
    new_cfg_date_time = getLocalServerTime(cfg_date_time)

    # print('------batch date and time--------------')
    # print(new_date_created)
    # print(new_cfg_date_time)
    # print('-------')

    instance.getField('DateCreated').set(instance, new_date_created)
    instance.getField('CfgDateTime').set(instance, new_cfg_date_time)

