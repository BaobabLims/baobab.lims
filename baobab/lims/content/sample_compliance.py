# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFPlone.interfaces import IConstrainTypes
from zope.interface import implements

from baobab.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from baobab.lims.interfaces import ISampleCompliance
from Products.Archetypes.atapi import registerType
from baobab.lims import bikaMessageFactory as _


NonComplianceNumber = StringField(
    'NonComplianceNumber',
    widget=StringWidget(
        label=_('Non Compliance Number'),
        description=_('The Non Compliance Number.'),
        visible={'view': 'visible', 'edit': 'visible'}
    )
)

NonComplianceAction = StringField(
    'NonComplianceAction',
    widget=StringWidget(
        label=_('Non Compliance Action'),
        description=_('The Non Compliance Action.'),
        visible={'view': 'visible', 'edit': 'visible'}
    )
)

schema = BikaSchema.copy() + Schema((
    NonComplianceNumber,
    NonComplianceAction,
))
schema['title'].widget.visible = {'view': 'visible', 'edit': 'visible'}
schema['description'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}


class SampleCompliance(BaseContent):
    implements(ISampleCompliance, IConstrainTypes)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

registerType(SampleCompliance, PROJECTNAME)

# def SampleCompliances(self, instance=None, allow_blank=False):
#     instance = instance or self
#     bsc = getToolByName(instance, 'bika_setup_catalog')
#     items = []
#     for sm in bsc(portal_type='SampleCompliance',
#                   inactive_state='active',
#                   sort_on='sortable_title'):
#         items.append((sm.UID, sm.Title))
#     items = allow_blank and [['', '']] + list(items) or list(items)
#     return DisplayList(items)
