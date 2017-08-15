from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode

from bika.lims.browser.analysisrequest.add import AnalysisServicesView as ASV
from bika.lims.browser.analysisrequest.add import AnalysisRequestAddView as ARAV
from bika.lims.browser.analysisrequest.add import ajax_form_error
from bika.lims.content.analysisrequest import schema as AnalysisRequestSchema
from baobab.lims.browser.analysisrequest.util import create_analysisrequest as crar
from bika.lims.utils import t

from baobab.lims import bikaMessageFactory as _

import plone
import json

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


class ajaxAnalysisRequestSubmit():
    """Overriding the one in bika.lims
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request
        # Errors are aggregated here, and returned together to the browser
        self.errors = {}

    def __call__(self):
        form = self.request.form
        plone.protect.CheckAuthenticator(self.request.form)
        plone.protect.PostOnly(self.request.form)
        uc = getToolByName(self.context, 'uid_catalog')
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        portal_catalog = getToolByName(self.context, 'portal_catalog')

        # Load the form data from request.state.  If anything goes wrong here,
        # put a bullet through the whole process.
        try:
            states = json.loads(form['state'])
        except Exception as e:
            message = t(_('Badly formed state: ${errmsg}',
                          mapping={'errmsg': e.message}))
            ajax_form_error(self.errors, message=message)
            return json.dumps({'errors': self.errors})

        # Validate incoming form data
        required = [field.getName() for field
                    in AnalysisRequestSchema.fields()
                    if field.required] + ["Analyses"]

        # First remove all states which are completely empty; if all
        # required fields are not present, we assume that the current
        # AR had no data entered, and can be ignored
        nonblank_states = {}
        for arnum, state in states.items():
            for key, val in state.items():
                if val \
                        and "%s_hidden" % key not in state \
                        and not key.endswith('hidden'):
                    nonblank_states[arnum] = state
                    break

        # in valid_states, all ars that pass validation will be stored
        valid_states = {}
        samples_volumes = {}
        for arnum, state in nonblank_states.items():
            # Secondary ARs are a special case, these fields are not required
            if state.get('Sample', ''):
                if 'SamplingDate' in required:
                    required.remove('SamplingDate')
                if 'SampleType' in required:
                    required.remove('SampleType')
            else:
                ajax_form_error(self.errors, field='Sample', arnum=arnum)
                continue

            # fields flagged as 'hidden' are not considered required because
            # they will already have default values inserted in them
            for fieldname in required:
                if fieldname + '_hidden' in state:
                    required.remove(fieldname)
            missing = [f for f in required if not state.get(f, '')]
            # If there are required fields missing, flag an error
            if missing:
                msg = t(_('Required fields have no values: '
                          '${field_names}',
                          mapping={'field_names': ', '.join(missing)}))
                ajax_form_error(self.errors, arnum=arnum, message=msg)
                continue

            # HOCINE: Verify Sample volume availability
            uc = getToolByName(self.context, 'uid_catalog')
            sample = uc(UID=state['Sample'])[0].getObject()
            total_volume = float(sample.getField('Volume').get(sample))
            sample_volume = samples_volumes.get(state['Sample'], 0.00)
            samples_volumes[state['Sample']] = sample_volume + float(state['Volume'])
            if total_volume < samples_volumes.get(state['Sample']):
                msg = t(_('The volume of sample ${sample} for this AR exceeds the sample volume available: '
                          '${total_volume}',
                           mapping={'sample': sample.getId(), 'total_volume': total_volume}))
                ajax_form_error(self.errors, arnum=arnum, message=msg)
                continue

            # This ar is valid!
            valid_states[arnum] = state

        # - Expand lists of UIDs returned by multiValued reference widgets
        # - Transfer _uid values into their respective fields
        for arnum in valid_states.keys():
            for field, value in valid_states[arnum].items():
                if field.endswith('_uid') and ',' in value:
                    valid_states[arnum][field] = value.split(',')
                elif field.endswith('_uid'):
                    valid_states[arnum][field] = value

        if self.errors:
            return json.dumps({'errors': self.errors})

        # Now, we will create the specified ARs.
        ARs = []
        for arnum, state in valid_states.items():
            # Create the Analysis Request
            ar = crar(
                self.context,
                self.request,
                state
            )
            field = ar.getField('Project')
            field.set(ar, self.context)
            # HOCINE: UPDATE SAMPLE VOLUME
            uc = getToolByName(self.context, 'uid_catalog')
            sample = uc(UID=state['Sample'])[0].getObject()
            field = sample.getField('Volume')
            total_volume = float(field.get(sample))
            volume = ar.getField('Volume').get(ar)
            field.set(sample, str(total_volume - float(volume)))
            ARs.append(ar.Title())

        # Display the appropriate message after creation
        if len(ARs) > 1:
            message = _('Analysis requests ${ARs} were successfully created.',
                        mapping={'ARs': safe_unicode(', '.join(ARs))})
        else:
            message = _('Analysis request ${AR} was successfully created.',
                        mapping={'AR': safe_unicode(ARs[0])})
        self.context.plone_utils.addPortalMessage(message, 'info')
        # Automatic label printing won't print "register" labels for Secondary. ARs
        new_ars = [ar for ar in ARs if ar[-2:] == '01']
        if 'register' in self.context.bika_setup.getAutoPrintStickers() \
                and new_ars:
            return json.dumps({
                'success': message,
                'stickers': new_ars,
                'stickertemplate': self.context.bika_setup.getAutoStickerTemplate()
            })
        else:
            return json.dumps({'success': message})