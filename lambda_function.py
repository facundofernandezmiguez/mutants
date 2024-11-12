import logging
import json
import boto3
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('DnaVerificationTable')  # Table name for storing results

def is_mutant(dna):
    """
    Determines if a DNA sequence is mutant or not. To be considered mutant, the
    sequence must have at least two sequences of 4 equal characters, in any direction
    (horizontal, vertical or diagonal).

    Args:
        dna (list): List of DNA strings, where each string represents a row of the DNA matrix.

    Returns:
        bool: True if the DNA sequence is mutant, False otherwise.
    """
    dna_matrix = [list(row) for row in dna]
    n = len(dna_matrix)
    
    def check_sequence(i, j, di, dj):
        
        """
        Args:
            i (int): Row index in the DNA matrix.
            j (int): Column index in the DNA matrix.
            di (int): Row increment (1 for horizontal, 0 for vertical, -1 for diagonal).
            dj (int): Column increment (1 for horizontal, 1 for diagonal, 0 for vertical).

        Returns:
            bool: True if the sequence exists, False otherwise.
        """

        letter = dna_matrix[i][j]
        for k in range(4):
            ni, nj = i + di * k, j + dj * k
            if ni >= n or nj >= n or ni < 0 or nj < 0 or dna_matrix[ni][nj] != letter:
                return False
        return True

    sequence_count = 0
    for i in range(n):
        for j in range(n):
            if (j <= n - 4 and check_sequence(i, j, 0, 1)) or \
               (i <= n - 4 and check_sequence(i, j, 1, 0)) or \
               (i <= n - 4 and j <= n - 4 and check_sequence(i, j, 1, 1)) or \
               (i <= n - 4 and j >= 3 and check_sequence(i, j, 1, -1)):
                sequence_count += 1
                if sequence_count > 1:
                    return True
    return False

def store_dna_result(dna, is_mutant):
    """
    Stores the result of the DNA verification in a DynamoDB table.

    Args:
        dna (list): List of DNA strings, where each string represents a row of the DNA matrix.
        is_mutant (bool): Indicates if the DNA string is mutant.

    Stores the DNA sequence and its result (mutant or not) in the table, avoiding
    overwriting existing sequences. Logs a success message if the operation is
    completed successfully, and handles exceptions in case of errors.
    """
    dna_str = ''.join(dna)
    try:
        table.put_item(
            Item={
                'dna_sequence': dna_str,
                'mutant': is_mutant
            },
            ConditionExpression='attribute_not_exists(dna_sequence)'  # Prevents overwriting existing sequences
        )
        logger.info("DNA sequence stored successfully.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            logger.info("DNA sequence already exists in database.")
        else:
            logger.error(f"Error storing DNA sequence: %s", e)

def get_stats():
    """
    Retrieves statistics on DNA sequences stored in the DynamoDB table.

    Scans the table to count the number of mutant and human DNA sequences,
    and calculates the ratio of mutant to human DNA sequences.

    Returns:
        dict: A dictionary containing:
            - "count_mutant_dna" (int): The number of mutant DNA sequences.
            - "count_human_dna" (int): The number of human DNA sequences.
            - "ratio" (float): The ratio of mutant to human DNA sequences, rounded to two decimal places.
    """
    response = table.scan()
    mutant_count = sum(1 for item in response['Items'] if item['mutant'])
    human_count = sum(1 for item in response['Items'] if not item['mutant'])
    ratio = mutant_count / human_count if human_count > 0 else 1
    return {
        "count_mutant_dna": mutant_count,
        "count_human_dna": human_count,
        "ratio": round(ratio, 2)
    }

def lambda_handler(event, context):
    """
    AWS Lambda function handler for processing DNA verification requests.

    This function handles two main routes:
    1. /mutant: Verifies if the provided DNA sequence belongs to a mutant.
       - Accepts a JSON payload with a "dna" key containing the DNA sequence.
       - Returns status 200 if the sequence is mutant, 403 otherwise.
       - Stores the result in a DynamoDB table.

    2. /stats: Provides statistics on the number of mutant and human DNA sequences processed.
       - Returns a JSON with counts and the ratio of mutant to human DNA.

    If the path does not match any of the above, it returns a 404 error.

    Args:
        event (dict): Event data passed by AWS Lambda, expected to contain the HTTP request info.
        context (object): Context object provided by AWS Lambda, containing runtime information.
    
    Returns:
        dict: A response object with a statusCode and a JSON body.
    """
    path = event.get("rawPath")
    logger.info(f"Path recibido: %s", path)
    
    # Ruta /mutant
    if "/mutant" in path:  
        body = event.get("body", "{}")
        logger.info(f"Request body: %s", body)
        try:
            body_data = json.loads(body)
        except json.JSONDecodeError:
            return {"statusCode": 400, "body": json.dumps({"error": "Invalid JSON format"})}

        dna = body_data.get("dna", [])
        logger.info("Checking DNA sequence: %s", dna)
        if not dna:
            return {"statusCode": 400, "body": json.dumps({"error": "DNA sequence not provided"})}
        
        is_mutant_result = is_mutant(dna)
        store_dna_result(dna, is_mutant_result)

        if is_mutant_result:
            return {"statusCode": 200, "body": json.dumps({"isMutant": True})}
        else:
            return {"statusCode": 403, "body": json.dumps({"isMutant": False})}
    
    # Ruta /stats
    elif "/stats" in path:  
        stats = get_stats()
        return {"statusCode": 200, "body": json.dumps(stats)}
    
    # Ruta no encontrada
    return {"statusCode": 404, "body": json.dumps({"error": "Not Found"})}
