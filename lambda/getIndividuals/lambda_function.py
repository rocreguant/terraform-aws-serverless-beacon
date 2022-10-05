import json

from jsonschema import Draft202012Validator

from apiutils.api_response import bad_request
from route_individuals import route as route_individuals
from route_individuals_filtering_terms import route as route_individuals_filtering_terms
from route_individuals_id import route as route_individuals_id
from route_individuals_id_g_variants import route as route_individuals_id_g_variants
from route_individuals_id_biosamples import route as route_individuals_id_biosamples


schemaRequestBody = json.load(open('./schemas/requestBody.json'))
schemaVariants = json.load(open('./schemas/gVariantsRequestParameters.json'))


def lambda_handler(event, context):
    print('Event Received: {}'.format(json.dumps(event)))

    if event['httpMethod'] == 'POST':
        try:
            body_dict = json.loads(event.get('body') or '{}')
        except ValueError:
            return bad_request(errorMessage='Error parsing request body, Expected JSON.')
        
        if event['resource'] == '/individuals/{id}/g_variants':
            schemaRequestBody['properties']['query']['properties']['requestParameters'] = schemaVariants
        
        validator = Draft202012Validator(schemaRequestBody)
        errors = []
        
        for error in sorted(validator.iter_errors(body_dict), key=lambda e: e.path):
            error_message = f'{error.message} '
            for part in list(error.path):
                error_message += f'/{part}'
            errors.append(error_message)

        if errors:
            return bad_request(errorMessage=', '.join(errors))

    if event["resource"] == "/individuals":
        return route_individuals(event)

    elif event['resource'] == '/individuals/filtering_terms':
        return route_individuals_filtering_terms(event)

    elif event['resource'] == '/individuals/{id}':
        return route_individuals_id(event)

    elif event['resource'] == '/individuals/{id}/g_variants':
        return route_individuals_id_g_variants(event)

    elif event['resource'] == '/individuals/{id}/biosamples':
        return route_individuals_id_biosamples(event)


if __name__ == '__main__':
    pass
