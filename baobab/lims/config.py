from Products.Archetypes.public import DisplayList
from baobab.lims import bikaMessageFactory as _

PROJECTNAME = "BAOBAB"

GLOBALS = globals()

INVENTORY_TYPES = DisplayList((
    ('N', _('None')),
    ('g', _('Glassware')),
    ('a', _('Reagents Ambient Temperature')),
    ('t', _('Reagents Cold Temperature')),
    ('o', _('Other')),
))

DIMENSION_OPTIONS = DisplayList((
    ('N', _('None')),
    ('f', _('One Dimension\t')),
    ('s', _('Two Dimension\t')),
))

VOLUME_UNITS = [
    {'ResultValue': '1', 'ResultText': 'ml'},
    {'ResultValue': '2', 'ResultText': 'kg'}
]

PRICELIST_TYPES = DisplayList((
    ('AnalysisService', _('Analysis Services')),
    ('LabProduct', _('Lab Products')),
    ('KitTemplate', _('Kits')),
    ('StorageType', _('Sample Storage')),
))

INVOICE_SERVICES = DisplayList((
    ('Kit', _('Kit')),
    ('Storage', _('Sample Storage')),
    ('AnalysisRequest', _('Analysis Request')),
))
