import json

from route_individuals import route as route_individuals
from route_individuals_filtering_terms import route as route_individuals_filtering_terms
from route_individuals_id import route as route_individuals_id
from route_individuals_id_g_variants import route as route_individuals_id_g_variants
from route_individuals_id_biosamples import route as route_individuals_id_biosamples
from shared.apiutils.requests import RequestParams, parse_request


def lambda_handler(event, context):
    print("Event Received: {}".format(json.dumps(event)))
    request_params: RequestParams = parse_request(event)

    # if event['httpMethod'] == 'POST':
    #     try:
    #         body_dict = json.loads(event.get('body') or '{}')
    #     except ValueError:
    #         return bad_request(errorMessage='Error parsing request body, Expected JSON.')

    #     if event['resource'] == '/individuals/{id}/g_variants':
    #         schemaRequestBody['properties']['query']['properties']['requestParameters'] = schemaVariants

    #     validator = Draft202012Validator(schemaRequestBody)
    #     errors = []

    #     for error in sorted(validator.iter_errors(body_dict), key=lambda e: e.path):
    #         error_message = f'{error.message} '
    #         for part in list(error.path):
    #             error_message += f'/{part}'
    #         errors.append(error_message)

    #     if errors:
    #         return bad_request(errorMessage=', '.join(errors))

    # event_hash = hash_query(event)

    if event["resource"] == "/individuals":
        return route_individuals(request_params)

    elif event["resource"] == "/individuals/filtering_terms":
        return route_individuals_filtering_terms(request_params)

    elif event["resource"] == "/individuals/{id}":
        return route_individuals_id(
            request_params, event["pathParameters"].get("id", None)
        )

    elif event["resource"] == "/individuals/{id}/g_variants":
        return route_individuals_id_g_variants(
            request_params, event["pathParameters"].get("id", None)
        )

    elif event["resource"] == "/individuals/{id}/biosamples":
        return route_individuals_id_biosamples(
            request_params, event["pathParameters"].get("id", None)
        )


if __name__ == "__main__":
    pass
