import plone
import json
from Products.CMFCore.utils import getToolByName
from Products.Archetypes import PloneMessageFactory as PMF
from Products.CMFPlone.utils import _createObjectByType
from bika.lims.utils import t, tmpID
from bika.lims.idserver import renameAfterCreation
from bika.sanbi.content.storageorder import schema as StorageOrderSchema
from bika.sanbi import bikaMessageFactory as _

from Products.CMFCore import permissions

import math
import string

def ajax_form_error(errors, field=None, message=None):
    if not message:
        message = t(PMF('Input is required but no input given.'))
    if field:
        error_key = '%s' % field
    else:
        error_key = 'Form error'
    errors[error_key] = message

class StorageOrderSubmit():
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
            message = t(_('Badly formed state: ${errmsg}',
                          mapping={'errmsg': e.message}))
            ajax_form_error(self.errors, message=message)
            return json.dumps({'errors': self.errors})

        # Validate incoming form data
        required = [field.getName() for field
                    in StorageOrderSchema.fields()
                    if field.required]

        # TODO: Check file add.py in browser/analysisrequest line 400. Do we need to
        # TODO: have nonblank_states here in this file?

        valid_states = {}
        for field, value in states.items():
            if field.endswith('_uid') and ',' in value:
                valid_states[field] = value.split(',')
            else:
                valid_states[field] = value

        if self.errors:
            return json.dumps({'errors': self.errors})

        storgeorder = create_storageorder(
            self.context,
            self.request,
            valid_states
        )
        return json.dumps({'success': 'salam1'})

def create_object(portal, context, values, l='', i=0):
    """
    """
    # case of an edit. If context has children and want to add after them then the
    # indice i should start from the next number of the indice of the item created.

    indice = l + str(i) if l else str(i)
    title = context.getChildTitle() and context.getChildTitle() or values.get('ChildTitle', '')
    if title:
        title = title + ' ' + indice
    else:
        title = indice
    obj = _createObjectByType(portal, context, tmpID())
    obj.edit(
        title=title,
        description="Child of " + context.Title(),
        StorageOrderID=indice,
        StorageUnit=context,
        Number=0,
    )
    obj.unmarkCreationFlag()
    renameAfterCreation(obj)

def number_items_add_sub(context, values):
    """
    """
    old_num_items = context.getNumber() and context.getNumber() or 0
    new_num_items = int(values.get('Number', 0))
    if old_num_items and not new_num_items:
        return 0, 0
    num_items_add = 0
    num_items_sub = 0
    if new_num_items > old_num_items:
        num_items_add = new_num_items - old_num_items
    elif new_num_items < old_num_items:
        num_items_sub = old_num_items - new_num_items

    return num_items_add, num_items_sub

def delete_childs(context, objs_delete):
    mt = getToolByName(context, 'portal_membership')
    if mt.checkPermission(permissions.DeleteObjects, context):
        for obj in objs_delete:
            context.manage_delObjects([obj.getId()])
    else:
        raise AssertionError("Permission Denied")

def child_update_ref(context):
    for child in context.getChildren():
        child.edit(
            description="Child of " + context.Title(),
        )
        child.reindexObject()

def rename_childs(context):
    title = context.getChildTitle()
    dim = context.getXAxis()
    for child in context.getChildren():
        new_title = ''
        lt = child.Title().split(' ')
        if len(lt) > 1 and title:
            new_title = title + ' ' + lt[1]
        elif len(lt) == 1 and title:
            new_title = title + ' ' + lt[0]
        elif len(lt) > 1 and not title:
            new_title = lt[1]
        elif len(lt) == 1 and not title:
            new_title = lt[0]
        else:
            # TODO: show this error message in the html page.
            print('error: title and the old title should be defined!')
        if new_title:
            child.edit(
                title = new_title
            )
            child.reindexObject()
            child_update_ref(child)

def rename_child_indices(context, l='', i=0):
    old_title = context.Title().split(' ')
    indice = l + str(i) if l else str(i)
    new_title = ''
    if len(old_title) >=1:
        new_title = old_title[0] + ' ' + indice
    elif len(old_title) == 1:
        new_title = indice
    else:
        # TODO: show this error message in the html page.
        print('error: title and the old title should be defined!')

    context.edit(
        title=new_title
    )
    context.reindexObject()
    child_update_ref(context)

def dimension_representation(num_items_add, num_rows, old_num_items, context, values, create=False):
    """Comments please!
    """
    num_cols = int(math.ceil(float(num_items_add) / float(num_rows))) if num_rows else 0
    alphabet = string.uppercase[:26]
    children = []
    if not create:
        children = context.getChildren()
    if num_cols:
        for i in range(int(num_rows)):
            for j in range(num_cols):
                if (i * num_cols) + j + 1 <= num_items_add: # this will return 1,2,3,4, ... <= numitems
                    if create:
                        create_object('StorageOrder', context, values, l=alphabet[i], i=j+old_num_items+1)
                    else:
                        rename_child_indices(children[(i * num_cols) + j], alphabet[i], j+1)
    else:
        for i in range(num_items_add):
            if create:
                create_object('StorageOrder', context, values, l='', i=i+old_num_items+1)
            else:
                rename_child_indices(children[i], '', i+1)

def create_storageorder(context, request, values):
    """This function create storageorder
    """
    storageorder = context
    uc = getToolByName(storageorder, 'uid_catalog')
    obj_exist = storageorder.aq_parent.hasObject(storageorder.getId())
    num_items = int(values.get('Number', 0))
    num_rows = values.has_key('XAxis') and int(values.get('XAxis', 0)) or 0
    num_items_add, num_items_sub = number_items_add_sub(storageorder, values)
    old_num_items = 0
    old_title = ''
    old_child_title = ''
    two_d = False
    x_dim = False
    if not obj_exist:
        # 'StorageUnit' here could be also 'StorageOrder'! This is just a key appellation.
        brains = uc(UID=values['StorageUnit'])
        if len(brains):
            context = brains[0].getObject()
        # Create the current context in ZODB
        storageorder = _createObjectByType('StorageOrder', context, tmpID())
        storageorder.processForm(REQUEST=request, values=values)
        # Increase by 1 the number of items of context.
        # At this point, context is the parent of storageorder.
        if context.portal_type == "StorageOrder":
            context.setNumber(context.getNumber() + 1)
    else:
        old_num_items = context.getNumber()
        old_title = context.Title()
        old_child_title = context.getChildTitle()
        two_d = context.getTwoDimension() != values.get('TwoDimension<', False)
        x_dim = num_rows != context.getXAxis()
        # In case of edit, when "StorageUnit", which is a referencefield, not changed
        # "values" will not contain "StorageUnit". This will cause it's value to be
        # replaced by None. For this reason we added this line to avoid this.
        # For more info check processForm() in referencewidget.py line 75.
        if not values.get('StorageUnit', ''):
            values['StorageUnit'] = storageorder.aq_parent.UID()
        storageorder.processForm(REQUEST=request, values=values)

    # if we change the title we've to make sure that the change is also done on the childs
    if old_title and old_title != values.get('Title', ''):
        child_update_ref(storageorder)

    if old_child_title and old_child_title != values.get('ChildTitle', ''):
        rename_childs(storageorder)

    if num_items_add:
        dimension_representation(num_items_add, num_rows, old_num_items, storageorder, values, create=True)

    if two_d:
        num_items_add = len(storageorder.getChildren())
        if values.get('TwoDimension', False) or x_dim:
            dimension_representation(num_items_add, num_rows, 0, storageorder, values)

    if num_items_sub:
        bsc = getToolByName(storageorder, 'bika_setup_catalog')
        objects = bsc.searchResults(portal_type='StorageOrder')
        delete_objects = []
        children = storageorder.getChildren()
        if len(children) >= num_items_sub:
            delete_objects = children[len(children)-num_items_sub:]
        else:
            #TODO: print it as a message on the front page.
            print('Error: Number of items to delete is greater than the objects found on DB')

        delete_childs(storageorder, delete_objects)

    return storageorder