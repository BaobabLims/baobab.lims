from archetypes.schemaextender.interfaces import ISchemaExtender
from zope.interface import implements
from zope.component import adapts
from bika.lims.browser.widgets import RecordsWidget
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.public import *

from bika.lims.fields import ExtRecordsField, ExtensionField, ExtBooleanField
from bika.lims.interfaces import IBikaSetup
from baobab.lims import bikaMessageFactory as _
import plone.protect
from operator import itemgetter
import json


class ExtFixedPointField(ExtensionField, FixedPointField):
    "Field extender"

class BikaSetupSchemaExtender(object):
    adapts(IBikaSetup)
    implements(ISchemaExtender)

    fields = [
        ExtFixedPointField(
            'LevyAmount',
            schemata='Accounting',
            default='0.00',
            widget=DecimalWidget(
                label=_("Levy Amount"),
                description=_("The levy percentage the university or parent organisation raises on all invoiced amounts"),
            )
        ),
        ExtRecordsField(
            'StoragePricing',
            schemata='Storage',
            subfields=('storage_type', 'price', 'storage_type_uid'),
            subfield_hidden={'storage_type_uid': True},
            required_subfields=('storage_type', 'price', 'storage_type_uid'),
            subfield_sizes={'storage_type': 50, 'price': 5},
            subfield_labels={'storage_type': _('Storage Type'), 'price': _('Price')},
            widget=RecordsWidget(
                label=_("Storage Pricing"),
                description=_("Set Sample storage pricing depending on storage type."),
                allowDelete=False,
                combogrid_options={
                    'storage_type': {
                        'colModel': [{'columnName': 'storage_type', 'width': '30', 'label': _('Title')},
                                     {'columnName': 'Description', 'width': '70', 'label': _('Description')},
                                     {'columnName': 'storage_type_uid', 'hidden': True}],
                        'url': 'getstoragetypes',
                        'showOn': True,
                        'width': '550px'
                    },
                },
            )
        ),
        ExtBooleanField(
            'ShowPartitions',
            schemata="Analyses",
            default=False,
            widget=BooleanWidget(
                label=_("Display individual sample partitions "),
                description=_("Turn this on if you want to work with sample partitions")
            ),
        ),
        ExtBooleanField(
            'StoreKitBiospecimens',
            schemata="Storage",
            default=True,
            widget=BooleanWidget(
                label=_("Store biospecimens when kit creation"),
                description=_("Turn this off if you want create kits without storing its biospecimens in managed storages")
            ),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields


class ajaxGetStorageTypes:
    catalog_name = 'bika_setup_catalog'

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        searchTerm = 'searchTerm' in self.request and self.request[
            'searchTerm'].lower() or ''
        page = self.request['page']
        nr_rows = self.request['rows']
        sord = self.request['sord']
        sidx = self.request['sidx']
        rows = []

        # lookup objects from ZODB
        bsc = getToolByName(self.context, self.catalog_name)
        brains = bsc(portal_type='StorageType', inactive_state='active')
        if brains and searchTerm:
            brains = [brain for brain in brains if
                      brain.Title.lower().find(searchTerm) > -1]

        for brain in brains:
            rows.append({
                'storage_type': brain.Title,
                'storage_type_uid': brain.UID,
                'Description': brain.Description
            })

        rows = sorted(rows, cmp=lambda x, y: cmp(x.lower(), y.lower()),
                      key=itemgetter(sidx and sidx or 'storage_type'))

        if sord == 'desc':
            rows.reverse()
        pages = len(rows) / int(nr_rows)
        pages += divmod(len(rows), int(nr_rows))[1] and 1 or 0
        ret = {
            'page': page,
            'total': pages,
            'records': len(rows),
            'rows': rows[(int(page) - 1) * int(nr_rows): int(page) * int(nr_rows)]
        }

        return json.dumps(ret)
