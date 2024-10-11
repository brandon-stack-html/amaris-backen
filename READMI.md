sam build

<!-- Para probar tu Lambda localmente con el evento API Gateway que definiste en template.yaml, usa el siguiente comando: -->
sam local start-api
<!-- Desplegar en AWS -->
sam deploy --guided
<!-- Eliminar recursos en AWS -->
sam delete
rm -rf .aws-sam



# cargar fondos
aws dynamodb batch-write-item --request-items file://data/batch_write_funds_item.json
aws dynamodb batch-write-item --request-items file://data/batch_write_clients_item.json

