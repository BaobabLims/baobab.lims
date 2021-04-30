# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.Archetypes.public import Schema, StringField, StringWidget
from Products.ATContentTypes.content import schemata
from Products.Archetypes.public import registerType
from Products.CMFPlone.interfaces import IConstrainTypes
from Products.CMFCore.utils import getToolByName
from plone.app.folder.folder import ATFolder
from zope.interface import implements

from bika.lims.content.bikaschema import BikaFolderSchema
from baobab.lims.interfaces import IMonitoringDevice
from baobab.lims import bikaMessageFactory as _
from baobab.lims import config

schema = BikaFolderSchema.copy() + Schema((
    StringField(
        'MACAddress',
        required=1,
        searchable=True,
        validators=('uniquefieldvalidator',),
        widget=StringWidget(
            label=_("MAC Address"),
            description=_("Monitoring Device MAC Address"),
            visible={'edit': 'visible', 'view': 'visible'}
        )),

))

schema['description'].schemata = 'default'
schema['description'].widget.visible = True


class MonitoringDevice(ATFolder):
    security = ClassSecurityInfo()
    implements(IMonitoringDevice, IConstrainTypes)
    displayContentsTab = False
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def guard_occupy_transition(self):
        """Use transition cannot proceed until is added to a Freezer.

        If this monitoring device is available and is on freezer,
        then we will prevent the use transition from becoming available.
        """

        wftool = self.portal_workflow
        review_state = wftool.getInfoFor(self, 'review_state')
        pc = getToolByName(self, 'bika_catalog')

        on_freezer = pc(portal_type='Freezer', MonitoringDevice=self)

        if (review_state == 'available') and on_freezer:
            return True
        return False

    def guard_liberate_transition(self):
        """Liberate transition cannot proceed unless Freezer is cleared.

        If this monitoring device is used and Freezer still has a value,
        then we will prevent the liberate transition from becoming available.
        """
        wftool = self.portal_workflow
        review_state = wftool.getInfoFor(self, 'review_state')
        pc = getToolByName(self, 'bika_catalog')
        on_freezer = pc(portal_type='Freezer', MonitoringDevice=self)
        if review_state in ('used') and not on_freezer:
            return True
        return False


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
registerType(MonitoringDevice, config.PROJECTNAME)
