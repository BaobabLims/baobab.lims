
def hide_actions_and_columns(context):
    """In our case we don't need some actions like to_be_preserved and also
    some of the columns in the listing table like batch.
    """
    cols = [
        'getDateSampled', 'getSampler', 'getDatePreserved',
        'getPreserver', 'getProfilesTitle', 'getTemplateTitle',
        'getDateSampled', 'AdHoc', 'SamplingDeviation',
        'getClientReference', 'getClientSampleID', 'BatchID'
    ]
    for col in context.columns.keys():
        if col in cols:
            del context.columns[col]

    ids = [
        'to_be_sampled', 'to_be_preserved', 'scheduled_sampling',
        'invalid', 'assigned', 'unassigned', 'rejected'
    ]
    j = 0
    for i in range(len(context.review_states)):
        if i - j > len(context.review_states): break
        if context.review_states[i - j]['id'] in ids:
            context.review_states.pop(i - j)
            j += 1
            continue
        k = 0
        for c in range(len(context.review_states[i - j]['columns'])):
            if c - k > len(context.review_states[i - j]['columns']):
                break
            if context.review_states[i - j]['columns'][c - k] in cols:
                context.review_states[i - j]['columns'].pop(c - k)
                k += 1

    return context