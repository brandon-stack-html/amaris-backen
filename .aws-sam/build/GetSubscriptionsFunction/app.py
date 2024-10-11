import json
import boto3
import os
from decimal import Decimal

REGION = os.environ['REGION']
SUBSCRIPTIONS_TABLE = os.environ['SUBSCRIPTIONS_TABLE']
FUNDS_TABLE = os.environ['FUNDS_TABLE']

dynamodb = boto3.resource('dynamodb', region_name=REGION)
subscriptions_table = dynamodb.Table(SUBSCRIPTIONS_TABLE)  
funds_table = dynamodb.Table(FUNDS_TABLE)

def add_cors_headers(response):
    response['headers'] = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
    }
    return response

def decimal_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

def get_user_subscriptions(user_id):
    subscriptions = []
    try:
        response = subscriptions_table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('PK').eq(user_id)
        )
        for item in response.get('Items', []):
            subscriptions.append({
                'fundId': item['SK'],  
                'amount': item.get('Amount', 0),  
                'timestamp': item.get('Timestamp', ''), 
            })
    except Exception as e:
        print(f"Error al obtener suscripciones: {str(e)}")
    return subscriptions

def get_all_funds():
    funds = []
    try:
        response = funds_table.scan()
        for item in response.get('Items', []):
            funds.append({
                'fundId': item['PK'],  
                'name': item.get('Name', ''), 
                'MinimumInvestment': item.get('MinimumInvestment', 0),  
            })
    except Exception as e:
        print(f"Error al obtener fondos: {str(e)}")
    return funds

def main(event, context):
    user_id = event['pathParameters']['userId']
    
    user_subscriptions = get_user_subscriptions(user_id)
    all_funds = get_all_funds()
    
    subscribed_funds = {sub['fundId'] for sub in user_subscriptions}
    
    not_subscribed_funds = [fund for fund in all_funds if fund['fundId'] not in subscribed_funds]

    response = {
        'statusCode': 200,
        'body': json.dumps({
            'subscriptions': user_subscriptions,
            'notSubscribedFunds': not_subscribed_funds
        }, default=decimal_to_float)  
    }
    
    return add_cors_headers(response)
