from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.app.layout.viewlets import ViewletBase
from zope.schema import ValidationError
from Products.ATContentTypes.lib import constraintypes


class AddKitsViewlet(ViewletBase):
    index = ViewPageTemplateFile("templates/add_kits_viewlet.pt")

    def render(self):
        return self.index()


class AddKitsSubmitHandler(BrowserView):
    """
    """
    def __call__(self):

        if "viewlet_submitted" in self.request.form:
            try:
                self.validate_form_inputs()
            except ValidationError as e:
                self.form_error(e.message)

            # Validation is complete, now set local variables from form inputs.
            form = self.request.form
            title_template = form.get('titletemplate', None)
            id_template = form.get('idtemplate', None)
            seq_start = int(form.get('seq_start', None))
            kit_count = int(form.get('kit_count', None))
            project_uid = form.get('Project_uid', None)
            kit_template_uid = form.get('KitTemplate_uid', None)

            self.context.setConstrainTypesMode(constraintypes.DISABLED)
            kits = self.create_kits(title_template, id_template, seq_start, kit_count, project_uid, kit_template_uid)

            msg = u'%s Kit assembled.' % len(kits)
            self.context.plone_utils.addPortalMessage(msg)
            self.request.response.redirect(self.context.absolute_url())

    def create_kits(self, title_template, id_template, seq_start, kit_count, project_uid, kit_template_uid):
        """Create the new kits
        """
        kits = []
        for x in range(seq_start, seq_start + kit_count):
            obj = api.content.create(
                container=self.context,
                type='Kit',
                id=id_template.format(id=x),
                title=title_template.format(id=x),
                Project=project_uid,
                KitTemplate=kit_template_uid
            )
            self.context.manage_renameObject(obj.id, id_template.format(id=x), )
            kits.append(obj)

        return kits

    def validate_form_inputs(self):

        form = self.request.form

        title_template = form.get('titletemplate', None)
        id_template = form.get('idtemplate', None)
        if not (title_template and id_template):
            raise ValidationError(u'ID and Title template are both required.')
        if not ('{id}' in title_template and '{id}' in id_template):
            raise ValidationError(u'ID and Title templates must contain {id} '
                                  u'for ID sequence substitution')

        try:
            seq_start = int(form.get('seq_start', None))
            kit_count = int(form.get('kit_count', None))
        except:
            raise ValidationError(
                u'Sequence start and all counts must be integers')

        # verify ID sequence start
        if seq_start < 1:
            raise ValidationError(u'Sequence Start may not be < 1')

        # verify number of kits
        if kit_count < 1:
            raise ValidationError(u'Kit count must not be < 1')

        # Check that none of the IDs conflict with existing items
        ids = [x.id for x in self.context.objectValues('Kit')]
        for x in range(kit_count):
            check = id_template.format(id=seq_start + x)
            if check in ids:
                raise ValidationError(
                    u'The ID %s exists, cannot be created.' % check)

    def form_error(self, msg):
        self.context.plone_utils.addPortalMessage(msg)
        self.request.response.redirect(self.context.absolute_url())