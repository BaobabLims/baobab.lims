import time


def getLocalServerTime(datetime_object):
    split_time = str(datetime_object).split('GMT')
    # print(split_time)

    new_time = split_time[0] + ' ' + getTimeZoneOffset()
    # print(new_time)

    return new_time



def getTimeZoneOffset():

    time_zone_offset = time.timezone / (60 * 60)
    if time_zone_offset < 0:
        time_gmt = 'GMT+' + str(-1 * time_zone_offset)
    elif time_zone_offset > 0:
        time_gmt = 'GMT-' + str(time_zone_offset)
    else:
        time_gmt = 'GMT+0'

    # print(time_gmt)
    return time_gmt