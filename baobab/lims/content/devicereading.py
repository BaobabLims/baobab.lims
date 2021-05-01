# -*- coding: utf-8 -*-

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import CalendarWidget
from Products.Archetypes.public import (
            BaseContent, DateTimeField, IntegerField, IntegerWidget, Schema,
            StringField, StringWidget, registerType)
from Products.CMFPlone.interfaces import IConstrainTypes
from zope.interface import implements
from DateTime import DateTime

from bika.lims.content.bikaschema import BikaSchema
from baobab.lims.interfaces import IDeviceReading
from baobab.lims import bikaMessageFactory as _
from baobab.lims.config import PROJECTNAME


schema = BikaSchema.copy() + Schema((
    StringField(
        'CurrentReading',
        searchable=True,
        widget=StringWidget(
            label=_("Current Reading"),
            description=_(""),
            visible={'edit': 'visible', 'view': 'visible'}
        )),

    StringField(
        'Label',
        default="Temperature",
        searchable=True,
        widget=StringWidget(
            label=_("Label"),
            description=_(""),
            visible={'edit': 'visible', 'view': 'visible'}
        )),

    IntegerField(
        'DecimalPlaces',
        required=1,
        default="0",
        widget=IntegerWidget(
            label=_("Decimal Places"),
            size=15,
            description=_(""),
            visible={'edit': 'visible', 'view': 'visible'}
        )),

    # Unit defaults degrees because when we get the request from easylogcloud
    # we ascii and not unicode and python 2 throws an error
    # please see browser/freezer_monitoring.py 
    StringField(
        'Unit',
        default="°", 
        widget=StringWidget(
            label=_("Unit"),
            visible={'edit': 'visible', 'view': 'visible'}
        )),

    DateTimeField(
        'DatetimeRecorded',
        default_method=DateTime,
        widget=CalendarWidget(
            label='Date and Time Recorded',
            description='',
            ampm=1,
            visible={'edit': 'visible', 'view': 'visible'}
        )
    ),
))

schema['title'].required = False
schema['title'].widget.visible = False
schema['description'].schemata = 'default'


class DeviceReading(BaseContent):
    implements(IDeviceReading, IConstrainTypes)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema


registerType(DeviceReading, PROJECTNAME)
