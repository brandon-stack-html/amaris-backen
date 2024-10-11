<%!
    # Plantilla Mako para confirmar la suscripción de un cliente a una cuenta
%>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Suscripción Exitosa</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            background-color: #f9fafc;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .container {
            background-color: #ffffff;
            border-radius: 16px;
            box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1);
            max-width: 450px;
            padding: 40px;
            text-align: center;
        }
        h1 {
            color: #2c3e50;
            font-size: 28px;
            margin-bottom: 15px;
        }
        p {
            font-size: 16px;
            color: #7f8c8d;
            line-height: 1.6;
            margin-bottom: 25px;
        }
        .highlight {
            font-weight: 500;
            color: #2980b9;
        }
        .button {
            display: inline-block;
            margin-top: 20px;
            padding: 12px 30px;
            background-color: #2980b9;
            color: #ffffff;
            text-decoration: none;
            border-radius: 50px;
            font-size: 18px;
            font-weight: 500;
            transition: background-color 0.3s ease, transform 0.3s ease;
            box-shadow: 0 4px 10px rgba(41, 128, 185, 0.2);
        }
        .button:hover {
            background-color: #1e6e98;
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(41, 128, 185, 0.3);
        }
        .icon {
            font-size: 60px;
            color: #27ae60;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">✔️</div>
        <h1>¡Suscripción Exitosa!</h1>
        
        <p>El cliente con ID <span class="highlight">${userId}</span> se ha suscrito exitosamente a la cuenta con ID <span class="highlight">${fundId}</span>.</p>
        <p>Gracias por confiar en nosotros. Si tienes alguna pregunta, no dudes en contactarnos.</p>
        <a href="#" class="button">Ir a la cuenta</a>
    </div>
</body>
</html>
