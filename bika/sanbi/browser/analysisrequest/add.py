from bika.lims.browser.analysisrequest.add import AnalysisServicesView as ASV
from bika.lims.browser.analysisrequest.add import AnalysisRequestAddView as ARAV

class AnalysisServicesView(ASV):

    def __init__(self, context, request, poc, ar_count=None, category=None):
        ASV.__init__(self, context, request, poc, ar_count, category)
        self.context = context
        self.request = request
        self.show_categories = False

    def folderitems(self):
        # This folderitems acts slightly differently from others, in that it
        # saves it's results in an attribute, and prevents itself from being
        # run multiple times.  This is necessary so that AR Add can check
        # the item count before choosing to render the table at all.
        if not self.ar_add_items:
            client = self.context.aq_parent.aq_parent \
                if self.context.aq_parent.aq_parent.portal_type == 'Client' \
                else None
            items = ASV.folderitems(self)
            services = self.context.aq_parent.getService()
            out_items = []
            for x, item in enumerate(items):
                if 'obj' not in items[x]:
                    continue
                obj = items[x]['obj']
                if obj in services:
                    kw = obj.getKeyword()
                    for arnum in range(self.ar_count):
                        key = 'ar.%s' % arnum
                        # If AR Specification fields are enabled, these should
                        # not be allowed to wrap inside the cell:
                        items[x]['class'][key] = 'nowrap'
                        # checked or not:
                        selected = self._get_selected_items(form_key=key)
                        items[x][key] = item in selected
                        # always editable:
                        items[x]['allow_edit'].append(key)
                        # fields and controls after each checkbox
                        items[x]['after'][key] = ''
                        if self.context.bika_setup.getEnableARSpecs():
                            items[x]['after'][key] += '''
                                    <input class="min" size="3" placeholder="&gt;min"/>
                                    <input class="max" size="3" placeholder="&lt;max"/>
                                    <input class="error" size="3" placeholder="err%"/>
                                '''
                        items[x]['after'][key] += '<span class="partnr"></span>'

                        # Price and VAT percentage are cheats: There is code in
                        # bika_listing_table_items.pt which allows them to be
                        # inserted into as attributes on <TR>.  TAL has this flaw;
                        # that attributes cannot be dynamically inserted.
                        # XXX five.zpt should fix this.  we must test five.zpt!
                        items[x]['price'] = obj.getBulkPrice() \
                            if client and client.getBulkDiscount() \
                            else obj.getPrice()
                        items[x]['vat_percentage'] = obj.getVAT()

                        # place a clue for the JS to recognize that these are
                        # AnalysisServices being selected here (service_selector
                        # bika_listing):
                        # XXX five.zpt should fix this.  we must test five.zpt!
                        poc = items[x]['obj'].getPointOfCapture()
                        items[x]['table_row_class'] = \
                            'service_selector bika_listing ' + poc
                    out_items.append(item)

            self.ar_add_items = out_items

        return self.ar_add_items


class AnalysisRequestAddView(ARAV):
    def __init__(self, context, request):
        ARAV.__init__(self, context, request)
        self.context = context
        self.request = request

    def __call__(self):
        self.request.set('disable_border', 1)
        self.ShowPrices = self.context.bika_setup.getShowPrices()
        if 'ajax_category_expand' in self.request.keys():
            cat = self.request.get('cat')
            asv = AnalysisServicesView(self.context,
                                       self.request,
                                       self.request['form_id'],
                                       category=cat,
                                       ar_count=self.ar_count)
            return asv()
        else:
            return self.template()

    def services_widget_content(self, poc, ar_count=None):

        """Copied from bika.lims add.py
        """

        if not ar_count:
            ar_count = self.ar_count

        s = AnalysisServicesView(self.context, self.request, poc,
                                 ar_count=ar_count)
        s.form_id = poc
        s.folderitems()

        if not s.ar_add_items:
            return ''
        return s.contents_table()