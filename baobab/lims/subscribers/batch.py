from zope.interface import alsoProvides
from Products.Five.utilities.marker import erase
from bika.lims.workflow import doActionFor
from baobab.lims.interfaces import ISharableSample
from baobab.lims.browser.project import create_samplepartition
import time
from time import gmtime, strftime


def ObjectInitializedEventHandler(instance, event):
    """called an object is created
    """

    updateLocalServerTime(instance)

def ObjectModifiedEventHandler(instance, event):
    """ Called if the object is modified
    """

    updateLocalServerTime(instance)

def updateLocalServerTime(instance):

    if instance.portal_type == 'SampleBatch':
        date_created = instance.getField('DateCreated').get(instance)
        cfg_date_time = instance.getField('CfgDateTime').get(instance)

        print('-------------------')
        print(cfg_date_time)
        print(type(cfg_date_time))

        new_date_created = getLocalServerTime(date_created)
        new_cfg_date_time = getLocalServerTime(cfg_date_time)
        instance.getField('DateCreated').set(instance, new_date_created)
        instance.getField('CfgDateTime').set(instance, new_cfg_date_time)

def getLocalServerTime(datetime_object):
    split_time = str(datetime_object).split('GMT')
    print(split_time)

    new_time = split_time[0] + ' ' + getTimeZoneOffset()
    print(new_time)

    return new_time



def getTimeZoneOffset():

    time_zone_offset = time.timezone / (60 * 60)
    if time_zone_offset < 0:
        time_gmt = 'GMT+' + str(-1 * time_zone_offset)
    elif time_zone_offset > 0:
        time_gmt = 'GMT-' + str(time_zone_offset)
    else:
        time_gmt = 'GMT+0'

    print(time_gmt)
    return time_gmt

