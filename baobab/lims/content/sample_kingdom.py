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
from baobab.lims.interfaces import ISampleKingdom
from Products.Archetypes.atapi import registerType
from Products.CMFCore import permissions
from bika.lims.browser.widgets import DateTimeWidget
from baobab.lims import bikaMessageFactory as _

# DateCreation = DateTimeField(
#     'DateCreated',
#     mode="rw",
#     read_permission=permissions.View,
#     write_permission=permissions.ModifyPortalContent,
#     widget=DateTimeWidget(
#         label=_("Date Created"),
#         description=_("Define when the centrifugation has been created."),
#         show_time=True,
#         visible={'edit': 'visible', 'view': 'visible'}
#     )
# )

Kingdom = StringField(
    'Kingdom',
    widget=StringWidget(
        label=_('Kingdom'),
        description=_('The technique used to centrifuged.'),
        visible={'view': 'visible', 'edit': 'visible'}
    )
)

IsMicroOrganism = BooleanField(
        'IsMicroOrganism',
        # schemata="Security",
        default=False,
        widget=BooleanWidget(
            label=_("This is micro organism."),
            description=_('Indicates if this sample kingdom is a micro organism.'),
            visible={'view': 'visible', 'edit': 'visible'}
        )
    )

schema = BikaSchema.copy() + Schema((
    IsMicroOrganism
    # DateCreation,
    # Kingdom,
))
schema['title'].widget.visible = {'view': 'visible', 'edit': 'visible'}
schema['description'].widget.visible = {'view': 'visible', 'edit': 'visible'}


class SampleKingdom(BaseContent):
    implements(ISampleKingdom, IConstrainTypes)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

registerType(SampleKingdom, PROJECTNAME)


# def SampleConditions(self, instance=None, allow_blank=False):
#     instance = instance or self
#     bsc = getToolByName(instance, 'bika_setup_catalog')
#     items = []
#     for sm in bsc(portal_type='SampleCondition',
#                   inactive_state='active',
#                   sort_on='sortable_title'):
#         items.append((sm.UID, sm.Title))
#     items = allow_blank and [['', '']] + list(items) or list(items)
#     return DisplayList(items)
