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
from baobab.lims.interfaces import IConformity
from Products.Archetypes.atapi import registerType
from baobab.lims import bikaMessageFactory as _


NonConformityNumber = StringField(
    'NonConformityNumber',
    widget=StringWidget(
        label=_('Non Conformity Number'),
        description=_('The Non Conformity Number.'),
        visible={'view': 'visible', 'edit': 'visible'}
    )
)

NonConformityAction = StringField(
    'NonConformityAction',
    widget=StringWidget(
        label=_('Non Conformity Action'),
        description=_('The Non Conformity Action.'),
        visible={'view': 'visible', 'edit': 'visible'}
    )
)

schema = BikaSchema.copy() + Schema((
    NonConformityNumber,
    NonConformityAction,
))
schema['title'].widget.visible = {'view': 'visible', 'edit': 'visible'}
schema['description'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}


class Conformity(BaseContent):
    implements(IConformity, IConstrainTypes)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

registerType(Conformity, PROJECTNAME)

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
