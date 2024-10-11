import json
import boto3
from datetime import datetime, timezone
import uuid
import os
from mako.template import Template
from decimal import Decimal


REGION = os.environ['REGION']
SUBSCRIPTIONS_TABLE = os.environ['SUBSCRIPTIONS_TABLE']
FUNDS_TABLE = os.environ['FUNDS_TABLE']
CLIENTS_TABLE = os.environ['CLIENTS_TABLE']
TRANSACTION_HISTORY_TABLE = os.environ['TRANSACTION_HISTORY_TABLE']

dynamodb = boto3.resource('dynamodb', region_name=REGION)
subscriptions_table = dynamodb.Table(SUBSCRIPTIONS_TABLE)
clients_table = dynamodb.Table(CLIENTS_TABLE)
transaction_history_table = dynamodb.Table(TRANSACTION_HISTORY_TABLE)
ses_client = boto3.client('ses', region_name=REGION)


def send_email(subject, recipient, title, heading, message, userId, fundId):
    template = Template(filename='template.html.mako')
    body_html = template.render(
        title=title,
        heading=heading,
        message=message,
        userId=userId,
        fundId=fundId
    )

    response = ses_client.send_email(
        Source='anarkigotic@gmail.com',
        Destination={'ToAddresses': [recipient]},
        Message={
            'Subject': {'Data': subject, 'Charset': 'UTF-8'},
            'Body': {'Html': {'Data': body_html, 'Charset': 'UTF-8'}}
        }
    )
    return response

def get_client_balance(client_id):
    response = clients_table.get_item(Key={'PK': client_id})
    return response.get('Item', {}).get('Balance', 0)

def get_client_subscription(client_id, fund_id):
    try:
        response = subscriptions_table.get_item(
            Key={'PK': client_id, 'SK': fund_id}
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
        transaction_history_table.put_item(Item=transaction_item)
    except Exception as e:
        print(f"Error recording transaction: {str(e)}")

def add_cors_headers(response):
    response['headers'] = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    }
    return response

def unsubscribe_fund(userId, fundId):
    existing_subscription = get_client_subscription(userId, fundId)
    
    if not existing_subscription:
        response = {
            'statusCode': 400,
            'body': json.dumps({
                'message': f"El cliente con ID {userId} no está suscrito al fondo con ID {fundId}."
            })
        }
        return add_cors_headers(response)
    
    amount = Decimal(existing_subscription.get('Amount', 0))
    client_balance = Decimal(get_client_balance(userId))
    new_balance = client_balance + amount

    try:
        clients_table.update_item(
            Key={'PK': userId},
            UpdateExpression="SET Balance = :new_balance",
            ExpressionAttributeValues={':new_balance': new_balance}
        )
    except Exception as e:
        response = {
            'statusCode': 500,
            'body': json.dumps({
                'message': "Error al actualizar el balance del cliente."
            })
        }
        return add_cors_headers(response)

    record_transaction(userId, fundId, amount, "unsubscription")
    
    try:
        subscriptions_table.delete_item(
            Key={
                'PK': userId,
                'SK': fundId
            }
        )
    except Exception as e:
        print(f"Error deleting subscription: {str(e)}")
        response = {
            'statusCode': 500,
            'body': json.dumps({
                'message': "Error al eliminar la suscripción."
            })
        }
        return add_cors_headers(response)

    # send_email(
    #     subject="Desuscripción confirmada",
    #     recipient="anarkigotic@gmail.com",
    #     title="Desuscripción de Fondo",
    #     heading="Has sido desuscrito exitosamente",
    #     message=f"Has sido desuscrito del fondo con ID {fundId} y el monto de {amount} ha sido devuelto a tu balance.",
    #     userId=userId,
    #     fundId=fundId
    # )
    
    
    response = {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Desuscripción realizada con éxito',
            'userId': userId,
            'fundId': fundId,
            'amount': float(amount),  
            'new_balance': float(new_balance)  
        })
    }
    
    return add_cors_headers(response)

def main(event, context):
    body_json = json.loads(event['body'])
    userId = body_json['userId']
    fundId = body_json['fundId']

    return unsubscribe_fund(userId, fundId)
