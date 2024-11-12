# DNA Mutant Checker API

Este proyecto proporciona una API en AWS Lambda que evalúa secuencias de ADN para determinar si son mutantes o no, y almacena los resultados en una tabla de DynamoDB. La API está conectada a dos API Gateways: uno para recibir secuencias de ADN a través de una solicitud `POST` y otro para obtener estadísticas de las solicitudes almacenadas en DynamoDB a través de una solicitud `GET`.

## Estructura del Proyecto

### 1. `lambda_function.py`
Este archivo contiene la función principal `is_mutant(dna)`, que recibe una secuencia de ADN en formato JSON y determina si es mutante o no. La función busca secuencias de 4 caracteres iguales en cualquier dirección (horizontal, vertical o diagonal). Si encuentra al menos dos secuencias de 4 caracteres iguales, se considera que el ADN es mutante.

### 2. API Gateway Endpoints

- **POST /mutant**: Este endpoint recibe una secuencia de ADN en formato JSON y llama a la función `is_mutant(dna)` para determinar si es mutante. El ADN debe enviarse en el siguiente formato:

  ```json
  {
    "dna": [
      "ATGCGA",
      "CAGHCC",
      "TTATGT",
      "AAAAGG",
      "CTCCTA",
      "TCACTG"
    ]
  }

- **GET /stats**: Este endpoint devuelve las estadísticas almacenadas en DynamoDB, como el número de secuencias mutantes, no mutantes y el ratio mutantes/no mutantes.

### 1. `test_lambda_function.py`
Este código contiene tests para ejecutar de manera local. Para poder ejecutarlo, se deben instalar las librerías (boto3 y unittest) presentes en en requirements.txt