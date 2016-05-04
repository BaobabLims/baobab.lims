from Products.CMFCore.utils import getToolByName
from Products.Archetypes import PloneMessageFactory as PMF
from Products.CMFPlone.utils import _createObjectByType, safe_unicode
from bika.lims.utils import t, tmpID
from bika.lims.idserver import renameAfterCreation
from bika.sanbi import bikaMessageFactory as _
from Products.Archetypes import public as atapi

import plone
import json
import string


def ajax_form_error(errors, field=None, message=None):

    if not message:
        message = t(PMF('Input is required but no input given.'))
    if field:
        error_key = '%s' % field
    else:
        error_key = 'Form error'
    errors[error_key] = message


class StorageManageSubmit:
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.errors = {}

    def __call__(self):
        form = self.request.form
        plone.protect.PostOnly(form)
        try:
            states = json.loads(form['state'])
        except Exception as e:
            message = t(_("Badely formed state: ${errmsg}",
                          mapping={"errmsg": e.message}))
            ajax_form_error(self.errors, message=message)

            return json.dumps({'errors': self.errors})

        values = {}
        for field, value in states.items():
            if field.endswith('_uid') and ',' in value:
                values[field] = value.split(',')
            else:
                values[field] = value

        storage, self.errors = self.create_storage(values)

        # used to redirect to view template (check it in js)
        storage_url = storage.absolute_url_path()
        message = _('Storage ${STO} was successfully created/updated.', mapping={'STO': safe_unicode(storage)})

        return json.dumps({'success': message, 'url': storage_url})

    # TODO: CHECK jsonapi/__init__.py LINE 59 TO FIND AN EXAMPLE HOW TO GET VALUES FOR FIELDS OF AN OBJECT
    # TODO: THIS IS VERY IMPORTANT. CHECK THAT THEY IGNORE VALUES IF FIELD TYPE IS FILE
    def context_to_dict(self):
        context_dict = {}
        for field in self.context.Schema().fields():
            name = field.getName()
            if not isinstance(field, atapi.ComputedField):
                value = field.getRaw(self.context)
                context_dict[name] = value

        return context_dict

    @staticmethod
    def update_children_parent_ref(context):
        for child in context.getChildren():
            child.edit(
                description="Child of " + context.Title()
            )
            # This is helpful for referenceField to not lose there value.
            child.reindexObject()

    def rename_children(self, child, values, index):
        title = self.context.getChildrenTitle() and self.context.getChildrenTitle() + ' ' + index or index
        child.edit(
            title=title,
        )
        # TODO: WE CAN USE HERE renameAfterCreation() method.
        if "Dimension" in values:
            self.context.manage_renameObject(child.id, index)
            child.reindexObject()
        self.update_children_parent_ref(child)

    def create_child(self, portal, values, index):
        """
        """
        title = self.context.getChildrenTitle() and self.context.getChildrenTitle() + ' ' + index or index
        child = _createObjectByType(portal, self.context, tmpID())
        child.edit(
            title=title,
            Type="Other",
            description="Child of " + self.context.Title(),
            StorageUnit=self.context,
            Shelves=0,
            Dimension="First",
            # TODO: MAY BE IS MORE TRUE TO PUT THE *Axis = 1?
            XAxis=1,
            YAxis=1,
            ZAxis=1
        )
        child.unmarkCreationFlag()
        renameAfterCreation(child)

    def create_child_as_location(self, portal, values, index):
        """
        """
        title = self.context.getHierarchy('.') + '.' + index
        location = _createObjectByType(portal, self.context, tmpID())
        # TODO: THINKS LATER TO IMPROVE THIS. 5 BECAUSE WE HAVE THIS HIERARCHY:
        # TODO: room > freezer > shelf > box > position
        assert len(location.getChain()) == 5
        position, box, shelf, freezer, room = [o.Title() for o in location.getChain()]
        if not position:
            position = index
        location.edit(
            title=title,
            Room=room,
            StorageType=freezer,
            Shelf=shelf,
            Box=box,
            Position=position
        )
        location.unmarkCreationFlag()
        renameAfterCreation(location)

    def dimension_representation(self, num_children_add, old_num_items, values, num_rows=1, num_cols=1,
                                 num_layers=1, create=False):

        alphabet = string.uppercase[:26]

        # TODO: THIS IS A REMARK. THE total_positions SHOULD BE EQUAL TO num_childs_add!
        # total_positions = num_rows * num_cols * num_layers
        total_positions = num_children_add
        num_pos_by_row = total_positions / (num_layers * num_rows)
        num_pos_by_col = total_positions / num_pos_by_row
        num_pos_by_layer = total_positions / num_layers
        children = self.context.getChildren()

        # TODO: THIS IS A REMARK. THE num_pos_by_row == num_cols AND num_pos_by_col == num_rows!
        for num in range(total_positions):
            x = num / num_pos_by_row % num_pos_by_col
            y = num % num_pos_by_row
            z = num / num_pos_by_layer

            if self.context.getDimension() == "First":
                x, z = '', ''
                index = str(y+1)
            elif self.context.getDimension() == "Second":
                z = ''
                index = alphabet[x] + str(y+1)
            elif self.context.getDimension() == "Third":
                index = alphabet[z] + str(x+1) + str(y+1)

            if create:
                if not self.context.getStorageLocation():
                    self.create_child('StorageManagement', values, index)
                else:
                    self.create_child_as_location('StorageLocation', values, index)
            else:
                self.rename_children(children[num], values, index)

        return self.context

    def number_children_add_sub(self, values):
        old_num_items = self.context.getShelves() and self.context.getShelves() or 0
        new_num_items = values.get('Shelves') and int(values['Shelves']) or 0

        if 'Shelves' not in values.keys():
            return 0, 0

        num_children_add = 0
        num_children_sub = 0
        if new_num_items > old_num_items:
            num_children_add = new_num_items - old_num_items
        elif new_num_items < old_num_items:
            num_children_sub = old_num_items - new_num_items

        return num_children_add, num_children_sub

    def create_storage(self, values):
        uid_catalog = getToolByName(self.context, 'uid_catalog')
        obj_exist = self.context.aq_parent.hasObject(self.context.getId())
        num_rows = values.has_key('XAxis') and values.get('XAxis') and int(values['XAxis']) or 1
        num_cols = values.has_key('YAxis') and values.get('YAxis') and int(values['YAxis']) or 1
        num_layers = values.has_key('ZAxis') and values.get('ZAxis') and int(values['ZAxis']) or 1
        old_num_items = 0
        if not obj_exist:
            num_add, num_sub = self.number_children_add_sub(values)
            brains = uid_catalog(UID=values['StorageUnit'])
            if len(brains):
                parent_unit = brains[0].getObject()

            # Create the current context in ZODB
            self.context = _createObjectByType('StorageManagement', parent_unit, tmpID())
            self.context.processForm(REQUEST=self.request, values=values)
            self.context.edit(
                Type=values.get('StorageType') and values['StorageType'] or "Freeze",
                Dimension=values.get('Dimension') and values['Dimension'] or "First",
                XAxis=values.get('XAxis') and values['XAxis'] or 1,
                YAxis=values.get('YAxis') and values['YAxis'] or 1,
                ZAxis=values.get('ZAxis') and values['ZAxis'] or 1
            )
            renameAfterCreation(self.context)
            # Increase by 1 the number of children for the parent.
            if parent_unit.portal_type == "StorageManagement":
                parent_unit.setShelves(parent_unit.getShelves() + 1)

            if num_add:
                self.dimension_representation(num_add, old_num_items, values, num_rows=num_rows,
                                              num_cols=num_cols, num_layers=num_layers, create=True)
        else:
            if not values.get('StorageUnit', ''):
                values['StorageUnit'] = self.context.aq_parent.UID()

            # context before processForm
            context_b = self.context_to_dict()
            num_add, num_sub = self.number_children_add_sub(values)
            self.context.processForm(REQUEST=self.request, values=values)
            if context_b['title'] != self.context.Title():
                self.update_children_parent_ref(self.context)

            if not num_add and (context_b['Dimension'] != self.context.getDimension() or \
               context_b['ChildrenTitle'] != self.context.getChildrenTitle()):
                self.dimension_representation(len(self.context.getChildren()), old_num_items, values, num_rows=num_rows,
                                             num_cols=num_cols, num_layers=num_layers, create=False)

            # In the form edit the type is a normal input element and processForm will not update Type field
            # for this reason we use here values instead of self.context.
            type = values.get('StorageType') and values['StorageType'] or ''
            if type and context_b['Type'] != type:
                self.context.edit(
                    Type=type
                )
                renameAfterCreation(self.context)

            # Create children for child. The case where the number of items to create pass from 0 to value > 0
            if num_add and context_b['Shelves'] != self.context.getShelves():
                self.dimension_representation(num_add, 0, values, num_rows=num_rows, num_cols=num_cols,
                                              num_layers=num_layers, create=True)


        return self.context, {}
