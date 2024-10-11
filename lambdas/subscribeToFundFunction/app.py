import json
import boto3
from datetime import date, datetime, timezone
import uuid
import os
from mako.template import Template

REGION = os.environ['REGION']
SUBSCRIPTIONS_TABLE = os.environ['SUBSCRIPTIONS_TABLE']
FUNDS_TABLE = os.environ['FUNDS_TABLE']
CLIENTS_TABLE = os.environ['CLIENTS_TABLE']
TRANSACTION_HISTORY_TABLE = os.environ['TRANSACTION_HISTORY_TABLE']

dynamodb = boto3.resource('dynamodb', region_name=REGION)
subscriptions_table = dynamodb.Table(SUBSCRIPTIONS_TABLE)  
funds_table = dynamodb.Table(FUNDS_TABLE) 
clients_table = dynamodb.Table(CLIENTS_TABLE) 
ransaction_history_table = dynamodb.Table(TRANSACTION_HISTORY_TABLE) 
ses_client = boto3.client('ses', region_name=REGION)  


def update_client_balance(client_id, new_balance):
    try:
        clients_table.update_item(
            Key={'PK': client_id},
            UpdateExpression='SET Balance = :new_balance',
            ExpressionAttributeValues={':new_balance': new_balance}
        )
    except Exception as e:
        print(f"Error updating client balance: {str(e)}")

def send_email(subject, recipient, title, heading, message, userId, fundId):
    # Carga y renderiza la plantilla de Mako
    template = Template(filename='template.html.mako')
    body_html = template.render(
        title=title,
        heading=heading,
        message=message,
        userId=userId,
        fundId=fundId
    )

    # Envía el correo electrónico
    response = ses_client.send_email(
        Source='anarkigotic@gmail.com',  
        Destination={
            'ToAddresses': [recipient]
        },
        Message={
            'Subject': {
                'Data': subject,
                'Charset': 'UTF-8'
            },
            'Body': {
                'Html': {
                    'Data': body_html,
                    'Charset': 'UTF-8'
                }
            }
        }
    )

    return response

def get_fund_info(fund_id):
    try:
        response = funds_table.get_item(Key={'PK': fund_id})
        if 'Item' in response:
            return response['Item']
        else:
            print(f"Fund with id {fund_id} not found.")
            return {}  # or handle the missing item case as needed
    except Exception as e:
        print(f"Error retrieving fund info: {str(e)}")
        return {}


def get_client_balance(client_id):
    response = clients_table.get_item(Key={'PK': client_id})
    return response.get('Item', {}).get('Balance', 0)

def get_client_subscription(client_id, fund_id):
    try:
        response = subscriptions_table.get_item(
            Key={
                'PK': client_id,
                'SK': fund_id  # Ahora el SK es el fundId, que hace única la combinación cliente-fondo
            }
        )
        return response.get('Item')
    except Exception as e:
        print(f"Error retrieving subscription: {str(e)}")
        return None
    
    
def record_transaction(client_id, fund_id, amount, transaction_type):
    transaction_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()
    try:
        transaction_item = {
            'PK': client_id,
            'SK': transaction_id,
            'Type': transaction_type,
            'FundId': fund_id,
            'Amount': amount,
            'Timestamp': timestamp
        }
        ransaction_history_table.put_item(Item=transaction_item)
    except Exception as e:
        print(f"Error recording transaction: {str(e)}")

def add_cors_headers(response):
    response['headers'] = {
        'Access-Control-Allow-Origin': '*',  
        'Access-Control-Allow-Methods': 'POST',  
        'Access-Control-Allow-Headers': 'Content-Type',  
    }
    return response



def main(event, context):
    body_json = json.loads(event['body'])
    userId = body_json['userId']
    fundId = body_json['fundId']

    existing_subscription = get_client_subscription(userId, fundId)
    
    if existing_subscription:
        response = {
            'statusCode': 400,
            'body': json.dumps({
                'message': f"El cliente con ID {userId} ya está suscrito al fondo con ID {fundId}."
            })
        }
        return add_cors_headers(response)
    
    client_balance = get_client_balance(userId)
    fund_info = get_fund_info(fundId)
    
    if not fund_info:
        response = {
            'statusCode': 404,
            'body': json.dumps({
                'message': f"No se encontró información para el fondo con ID {fundId}."
            })
        }
        return add_cors_headers(response)
    
    if client_balance < fund_info['MinimumInvestment']:
        response = {
            'statusCode': 400,
            'body': json.dumps({
                'message': f"No tiene saldo disponible para vincularse al fondo {fund_info['Name']}"
            })
        }
        return add_cors_headers(response)
        
    amount = fund_info['MinimumInvestment']
    update_client_balance(userId,client_balance - fund_info['MinimumInvestment'])
    subscription_item = {
        'PK': userId,
        'SK': fundId, 
        'Amount': amount,
        'Timestamp': datetime.now(timezone.utc).isoformat()
    }
    
    subscriptions_table.put_item(Item=subscription_item)
    
    record_transaction(userId, fundId, amount, "subscription")
    # send_email("suscript a nueva cuenta", "anarkigotic@gmail.com", "titlle test", "heading", "message test", userId, fundId)

    response = {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Suscripción realizada con éxito',
            'userId': userId,
            'fundId': fundId,
            'amount': str(amount)
        })
    }
    
    return add_cors_headers(response)
