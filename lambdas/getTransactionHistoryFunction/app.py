import json
import boto3
from boto3.dynamodb.conditions import Key
import os
from decimal import Decimal

REGION = os.environ['REGION']
TRANSACTION_HISTORY_TABLE = os.environ['TRANSACTION_HISTORY_TABLE']

dynamodb = boto3.resource('dynamodb')
transactions_table = dynamodb.Table(TRANSACTION_HISTORY_TABLE)  


def convert_decimals_to_floats(item):
    """Convierte recursivamente los Decimals en un diccionario a floats."""
    if isinstance(item, dict):
        return {k: convert_decimals_to_floats(v) for k, v in item.items()}
    elif isinstance(item, list):
        return [convert_decimals_to_floats(i) for i in item]
    elif isinstance(item, Decimal):
        return float(item)
    return item

def get_client_transactions(cliente_id):
    response = transactions_table.query(
        KeyConditionExpression=Key('PK').eq(cliente_id)
    )
    
    transactions = response.get('Items', [])
    
    return transactions

def main(event, context):
    
    path_parameters = event.get('pathParameters', {})
    cliente_id = path_parameters.get('userId', '0')  
    
    transactions = get_client_transactions(cliente_id)
    
    if not transactions:
        response = {
            'statusCode': 404,
            'body': json.dumps({'message': 'No se encontraron transacciones para este cliente.'})
        }
    else:
        transactions = [convert_decimals_to_floats(t) for t in transactions]
        
        response = {
            'statusCode': 200,
            'body': json.dumps(transactions)
        }

    return add_cors_headers(response) 

def add_cors_headers(response):
    response['headers'] = {
        'Access-Control-Allow-Origin': '*', 
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'OPTIONS,GET'
    }
    return response
