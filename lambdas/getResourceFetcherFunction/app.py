import json
from enum import Enum
import boto3
import os

REGION = os.environ['REGION']
FUNDS_TABLE = os.environ['FUNDS_TABLE']
CLIENTS_TABLE = os.environ['CLIENTS_TABLE']

dynamodb = boto3.resource('dynamodb', region_name=REGION)

class ResourceTypeEnum(Enum):
    FUNDS = 'funds'
    CLIENTS = 'clients'

def add_cors_headers(response):
    """Agrega encabezados CORS a la respuesta."""
    response['headers'] = {
        'Access-Control-Allow-Origin': '*',  
        'Access-Control-Allow-Methods': 'GET',  
        'Access-Control-Allow-Headers': 'Content-Type',  
    }
    return response

def get_funds():
    table = dynamodb.Table(FUNDS_TABLE)
    response = table.scan()
    items = response.get("Items", [])

    funds = [{
        **fund,  
        'MinimumInvestment': str(fund.get('MinimumInvestment', 0)) 
    } for fund in items]

    return add_cors_headers({
        'statusCode': 200,
        'body': json.dumps(funds)
    })

def get_clients():
    table = dynamodb.Table(CLIENTS_TABLE)
    response = table.scan()
    items = response.get("Items", [])

    clients = [{
        **client, 
        'Balance': str(client.get('Balance', 0))  
    } for client in items]

    return add_cors_headers({
        'statusCode': 200,
        'body': json.dumps(clients)
    })

def main(event, context):
    resource_type = event.get('queryStringParameters', {}).get('resource_type')

    if not resource_type:
        return add_cors_headers({
            'statusCode': 400,
            'body': 'Missing - resourceType parameter'
        })

    try:
        resource_type_enum = ResourceTypeEnum(resource_type)
        if resource_type_enum == ResourceTypeEnum.FUNDS:
            return get_funds()
        if resource_type_enum == ResourceTypeEnum.CLIENTS:
            return get_clients()

    except Exception as e:
        return add_cors_headers({
            'statusCode': 500,
            'body': f'Error: {str(e)}'
        })

    # Retorna la respuesta como JSON
    return add_cors_headers({
        'statusCode': 200,
        'body': json.dumps({'message': resource_type})
    })
