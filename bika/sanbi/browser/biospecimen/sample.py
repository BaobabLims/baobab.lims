from bika.lims.browser.sample import SampleEdit as SE
from bika.sanbi import bikaMessageFactory as _
from bika.sanbi.interfaces import IAliquot, IBiospecimen


class SampleEdit(SE):
    """This overrides the edit and view of sample.
    """

    def __init__(self, context, request):
        SE.__init__(self, context, request)
        if IAliquot.providedBy(context):
            self.icon = self.portal_url + \
                        "/++resource++bika.sanbi.images/aliquot_big.png"
        elif IBiospecimen.providedBy(context):
            self.icon = self.portal_url + \
                        "/++resource++bika.sanbi.images/biospecimen_big.png"
        self.allow_edit = True

    def __call__(self):
        SE.__call__(self)
        return self.template()


class SampleView(SampleEdit):
    """
    The view of a single sample
    """
    def __call__(self):
        self.allow_edit = False
        return SampleEdit.__call__(self)