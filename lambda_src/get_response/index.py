import boto3
import datetime
import os
import json
import uuid
from mypy_boto3_bedrock_runtime import BedrockRuntimeClient

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# get env variables
LOCAL_TEST = os.environ.get('LOCAL_TEST', None)
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', None)

# create the DynamoDB resource
dynamo = boto3.resource('dynamodb')
table = dynamo.Table(DYNAMODB_TABLE)

def handler(event, context):
    logger.info(f"Event: {event}")
    query_parameters: dict = event.get('queryStringParameters')
    jobId = query_parameters.get("jobId")
    logger.info(jobId)
    
    if LOCAL_TEST != None:
        # Get a single item by primary key
        response = table.get_item(
            Key={'id': jobId}
        )
        logger.info(response)
        item = response.get('response')
        logger.info(item)

    return {
        'statusCode': 200,
        'response': "testing"
    }
    