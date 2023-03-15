import json
import jsons


from athena.filter_functions import entity_search_conditions
from apiutils.requests import RequestParams, Granularity
from apiutils.schemas import DefaultSchemas
import apiutils.responses as responses
from athena.individual import Individual


def get_count_query(conditions=''):
    query = f'''
    SELECT COUNT(id) FROM "{{database}}"."{{table}}"
    {conditions};
    '''
    return query


def get_bool_query(conditions=''):
    query = f'''
    SELECT 1 FROM "{{database}}"."{{table}}"
    {conditions}
    LIMIT 1;
    '''
    return query


def get_record_query(skip, limit, conditions=''):
    query = f'''
    SELECT * FROM "{{database}}"."{{table}}"
    {conditions}
    ORDER BY id
    OFFSET {skip}
    LIMIT {limit};
    '''
    return query


def route(request: RequestParams):
    conditions, execution_parameters = entity_search_conditions(
        request.query.filters, 'individuals', 'individuals')

    if request.query.requested_granularity == Granularity.BOOLEAN:
        query = get_bool_query(conditions)
        count = 1 if Individual.get_existence_by_query(
            query, execution_parameters=execution_parameters) else 0
        response = responses.build_beacon_boolean_response(
            {}, count, request, {}, DefaultSchemas.INDIVIDUALS)
        print('Returning Response: {}'.format(json.dumps(response)))
        return responses.bundle_response(200, response)

    if request.query.requested_granularity == Granularity.COUNT:
        query = get_count_query(conditions)
        count = Individual.get_count_by_query(
            query, execution_parameters=execution_parameters)
        response = responses.build_beacon_count_response(
            {}, count, request, {}, DefaultSchemas.INDIVIDUALS)
        print('Returning Response: {}'.format(json.dumps(response)))
        return responses.bundle_response(200, response)

    if request.query.requested_granularity == Granularity.RECORD:
        query = get_record_query(
            request.query.pagination.skip, request.query.pagination.limit, conditions)
        individuals = Individual.get_by_query(
            query, execution_parameters=execution_parameters)
        response = responses.build_beacon_resultset_response(
            jsons.dump(individuals, strip_privates=True), len(individuals), request, {}, DefaultSchemas.INDIVIDUALS)
        print('Returning Response: {}'.format(json.dumps(response)))
        return responses.bundle_response(200, response)


if __name__ == '__main__':
    pass
