import json

from jsonschema import Draft202012Validator

from apiutils.api_response import bad_request
from route_biosamples import route as route_biosamples
from route_biosamples_id import route as route_biosamples_id
from route_biosamples_id_g_variants import route as route_biosamples_id_g_variants
from route_biosamples_id_analyses import route as route_biosamples_id_analyses
from route_biosamples_id_runs import route as route_biosamples_id_runs
from route_biosamples_filtering_terms import route as route_biosamples_filtering_terms


schemaRequestBody = json.load(open('./schemas/requestBody.json'))
schemaVariants = json.load(open('./schemas/gVariantsRequestParameters.json'))


def lambda_handler(event, context):
    print('Event Received: {}'.format(json.dumps(event)))

    if event['httpMethod'] == 'POST':
        try:
            body_dict = json.loads(event.get('body') or '{}')
        except ValueError:
            return bad_request(errorMessage='Error parsing request body, Expected JSON.')
        
        if event['resource'] == '/biosamples/{id}/g_variants':
            schemaRequestBody['properties']['query']['properties']['requestParameters'] = schemaVariants
        
        validator = Draft202012Validator(schemaRequestBody)
        errors = []
        
        for error in sorted(validator.iter_errors(body_dict), key=lambda e: e.path):
            error_message = f'{error.message}'
            for part in list(error.path):
                error_message += f'/{part}'
            errors.append(error_message)

        if errors:
            return bad_request(errorMessage=', '.join(errors))

    if event["resource"] == "/biosamples":
        return route_biosamples(event)

    elif event['resource'] == '/biosamples/{id}':
        return route_biosamples_id(event)

    elif event['resource'] == '/biosamples/{id}/g_variants':
        return route_biosamples_id_g_variants(event)

    elif event['resource'] == '/biosamples/{id}/analyses':
        return route_biosamples_id_analyses(event)

    elif event['resource'] == '/biosamples/{id}/runs':
        return route_biosamples_id_runs(event)

    elif event['resource'] == '/biosamples/filtering_terms':
        return route_biosamples_filtering_terms(event)

if __name__ == '__main__':
    pass
