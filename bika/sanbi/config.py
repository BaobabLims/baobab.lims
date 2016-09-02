from Products.Archetypes.public import DisplayList
from bika.sanbi import bikaMessageFactory as _

PROJECTNAME = "bika.sanbi"

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
