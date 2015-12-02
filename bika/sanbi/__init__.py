import pkg_resources

__version__ = pkg_resources.get_distribution("bika.sanbi").version


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
