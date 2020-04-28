from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType

from bika.lims.utils import tmpID
from bika.lims.workflow import doActionFor
from bika.lims.utils.analysisrequest import get_sample_from_values, _resolve_items_to_service_uids

def create_analysisrequest(context, request, values, analyses=None,
                           partitions=None, specifications=None, prices=None):
    """Overrides the method one in bika.lims
    """

    # Gather neccesary tools
    workflow = getToolByName(context, 'portal_workflow')
    bc = getToolByName(context, 'bika_catalog')
    # Analyses are analyses services
    analyses_services = analyses
    analyses = []
    # It's necessary to modify these and we don't want to pollute the
    # parent's data
    values = values.copy()
    analyses_services = analyses_services if analyses_services else []
    anv = values['Analyses'] if values.get('Analyses', None) else []
    analyses_services = anv + analyses_services

    if not analyses_services:
        raise RuntimeError(
                "create_analysisrequest: no analyses services provided")

    # Baobab does not create a sample when the sample is not selected in AR
    if not values.get('Sample', False):
        raise RuntimeError(
            "create_analysisrequest: no sample selected for analysis request")
    else:
        secondary = True
        sample = get_sample_from_values(context, values)
        workflow_enabled = sample.getSamplingWorkflowEnabled()

    # Create the Analysis Request
    ar = _createObjectByType('AnalysisRequest', context, tmpID())

    # Set some required fields manually before processForm is called
    ar.setSample(sample)
    values['Sample'] = sample
    values['SampleType'] = sample.getSampleType()
    values['StorageLocation'] = sample.getField('StorageLocation').get(sample)
    ar.processForm(REQUEST=request, values=values)
    # Object has been renamed
    ar.edit(RequestID=ar.getId())

    # Set initial AR state
    action = '{0}sampling_workflow'.format('' if workflow_enabled else 'no_')

    workflow.doActionFor(ar, action)

    # Set analysis request analyses
    service_uids = _resolve_items_to_service_uids(analyses_services)
    # processForm already has created the analyses, but here we create the
    # analyses with specs and prices. This function, even it is called 'set',
    # deletes the old analyses, so eventually we obtain the desired analyses.
    ar.setAnalyses(service_uids, prices=prices, specs=specifications)
    # Gettin the ar objects
    analyses = ar.getAnalyses(full_objects=True)
    # Continue to set the state of the AR
    skip_receive = ['to_be_sampled', 'sample_due', 'sampled', 'to_be_preserved']
    if secondary:
        # Only 'sample_due' and 'sample_recieved' samples can be selected
        # for secondary analyses
        doActionFor(ar, 'sampled')
        doActionFor(ar, 'sample_due')
        sample_state = workflow.getInfoFor(sample, 'review_state')
        if sample_state not in skip_receive:
            doActionFor(ar, 'receive')

    # Set the state of analyses we created.
    for analysis in analyses:
        revers = analysis.getService().getNumberOfRequiredVerifications()
        analysis.setNumberOfRequiredVerifications(revers)

        analysis.updateDueDate(ar)

        doActionFor(analysis, 'sample_due')
        analysis_state = workflow.getInfoFor(analysis, 'review_state')
        if analysis_state not in skip_receive:
            doActionFor(analysis, 'receive')

    # Once the ar is fully created, check if there are rejection reasons
    reject_field = values.get('RejectionReasons', '')
    if reject_field and reject_field.get('checkbox', False):
        doActionFor(ar, 'reject')
    # Return the newly created Analysis Request

    return ar
