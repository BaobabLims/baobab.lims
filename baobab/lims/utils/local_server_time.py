import time


def getLocalServerTime(datetime_object):
    sliced_time = str(datetime_object)[:16]
    new_time = sliced_time + ' ' + getTimeZoneOffset()

    return new_time


def getTimeZoneOffset():

    time_zone_offset = time.timezone / (60 * 60)
    if time_zone_offset > 0:
        time_gmt = 'GMT-' + str(time_zone_offset)
    elif time_zone_offset < 0:
        time_gmt = 'GMT+' + str(-1 * time_zone_offset)
    else:
        time_gmt = 'GMT+0'

    return time_gmt