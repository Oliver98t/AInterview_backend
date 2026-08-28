# Lambda: response
# Triggered by SQS messages or direct URL invocations.
# Calls Amazon Bedrock to generate an AI response for a given transcript,
# then persists the result to DynamoDB.

import boto3
import datetime
import time
import os
import json
import uuid
from mypy_boto3_dynamodb import DynamoDBServiceResource
from mypy_boto3_bedrock_runtime import BedrockRuntimeClient
from boto3.dynamodb.conditions import Key
from dataclasses import dataclass

# types
##################################################
@dataclass
class DbRecord:
    user_name: str 
    response: str 
    job_id: str
    role: str
    session_id: str

@dataclass
class ResponseResult:
    response: str
    response_num: int
##################################################

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

ddb_resource: DynamoDBServiceResource = boto3.resource('dynamodb')
LLM = "global.amazon.nova-2-lite-v1:0"
LOCAL_TEST = os.environ.get('LOCAL_TEST', None)
TABLENAME = os.environ.get('TABLE_NAME')

CHAT_WINDOW = 10

def handler(event, context):
    """Lambda entry point. Routes to the correct handler based on the event source.

    Args:
        event: The Lambda event dict. Contains 'Records' for SQS triggers
               or 'version' for Lambda function URL invocations.
        context: The Lambda context object (unused).

    Returns:
        The result from either sqs_event() or url_event().
    """
    logger.info(f"LOCAL_TEST: {LOCAL_TEST}")
    logger.info(f"Event: {event}")

    # Route to the appropriate handler based on the event source
    if event.get('Records'):
        logger.info("SQS trigger")
        data = sqs_event(event)
    elif event.get('version'):
        logger.info("url trigger")
        data = url_event(event)

    return data

def sqs_event(event):
    """Handle an SQS-triggered invocation.

    Parses the SQS message body, generates a Bedrock response for the
    transcript, and writes the result to DynamoDB.

    Args:
        event: The raw SQS event dict containing a 'Records' list.

    Returns:
        The generated AI response string.
    """
    # get the message out of the SQS event
    message = event['Records'][0]['body']
    data: dict = json.loads(message)
    # extract fields from the SQS message payload
    job_id = data.get('jobId')
    user_name = data.get('user_name')
    transcript = data.get('transcription')
    # generate an AI response for the transcript
    response = generate_response(prompt=transcript, user_name=user_name, clear_db=False)

    db_record = DbRecord(
    user_name=user_name,
    response=response,
    job_id=job_id)
    # write event data to DDB table
    result = write_to_db({"user": user_name, 
                          "transcript": transcript,
                          "response": response, 
                          "job_id": job_id})
    return result

def url_event(event) -> dict:
    """Handle a direct HTTP invocation via Lambda function URL or API Gateway.

    Reads 'user' and 'transcript' from the query string, generates a Bedrock
    response, persists it to DynamoDB, and returns an HTTP response dict.

    Args:
        event: The Lambda event dict containing 'queryStringParameters'.

    Returns:
        A dict with 'statusCode' (200 or 500) and a JSON 'body'.
    """
    # Handle a direct HTTP invocation via URL function URL or API Gateway
    try:
        query_parameters: dict = json.loads(event.get('body'))
        job_id = str(uuid.uuid4())

        # health status of lambda
        function_status = query_parameters.get('status')
        logger.info(f"status: {function_status}")
        if function_status:
            return {
                'statusCode': 200,
                'body': json.dumps({'status': 'true'})
            }
        
        user_name = query_parameters.get("user_name")
        message = query_parameters.get("message")
        role = query_parameters.get("role")
        session_id = query_parameters.get("session_id")
        clear_db = query_parameters.get("clear_db")
        eval = bool(query_parameters.get("eval"))
        logger.info(f"eval: {eval}")
        # generate an AI response for the provided transcript
        body = None
        response = None
        if role == "assistant":
            generate_response_result = generate_response(
                prompt=message,
                user_name=user_name,
            )
            response = generate_response_result.response
            response_num = generate_response_result.response_num
            body = json.dumps({"jobId": job_id, "response": response, 'response_num': response_num})
        elif role == "user":
            response = message
            body = json.dumps({"state": "succcess"})
        
        if clear_db != "clear":
            db_record = DbRecord(
                user_name=user_name,
                response=response,
                job_id=job_id,
                role=role,
                session_id=session_id)
            write_to_db(db_record)
        else:
            if eval:
                evaluation = evaluate_repsonses(user_name=user_name)
                body = json.dumps({"result": evaluation})
            clear_db_by_user(user_name=user_name)    
            
        
        status_code = 200
    except Exception as e:
        logger.error(f"Exception: {e}")
        status_code = 500
        body = None
    return {
        'statusCode': status_code,
        'body': body
    }

def read_db_by_user(user_name: str):
    response = None
    try:
        table = ddb_resource.Table(TABLENAME)
        # Use query instead of scan, assuming user_name is the partition key and timestamp is the sort key
        response = table.query(
            KeyConditionExpression=Key('user_name').eq(user_name),
            ScanIndexForward=False  # Descending order (newest first)
        )

    except Exception as e:
        logger.error(f"Exception: {e}")
        response = {"Items": []}
    
    return response

def clear_db_by_user(user_name: str):
    try:
        table = ddb_resource.Table(TABLENAME)
        # Use query instead of scan, assuming user_name is the partition key and timestamp is the sort key
        response = table.query(
            KeyConditionExpression=Key('user_name').eq(user_name),
            ScanIndexForward=False  # Descending order (newest first)
        )

        items = response.get("Items", [])
        with table.batch_writer() as batch:
            for item in items:
                batch.delete_item(
                    Key={
                        'user_name': item['user_name'],
                        'timestamp': item['timestamp']
                    }
                )

    except Exception as e:
        logger.error(f"Exception: {e}")

    return
        

def write_to_db(data: DbRecord):
    """Persist the response data to DynamoDB.

    Args:
        data: A dict containing 'job_id', 'user', 'transcript', and 'response'.

    Returns:
        The AI response string from data['response'].
    """
    result = data.response
    # only write to DynamoDB when running in a live environment (not local tests)
    if LOCAL_TEST != None:
        logger.info("writing to dynamodb")
        table = ddb_resource.Table(TABLENAME)
        table.put_item(
            Item={
                'user_name':    str(data.user_name),
                'timestamp':    int(time.time()),
                'date':         datetime.datetime.now().isoformat(),
                'job_id':       str(data.job_id),
                'response':     str(data.response),
                'role':         str(data.role),
                'session_id':   str(data.session_id)          
            }
        )
    return result

def create_message_history(history: dict)-> list:
    items = history.get('Items')
    # DynamoDB returns newest-first; reverse to chronological order for the model
    items = list(reversed(items))
    message_history = []
    for item in items:
        try:
            role = item.get('role')
            message_history.append(
                {
                    "role": role,
                    "content": [{"text": str(item.get('response'))}]
                })
        except Exception as error:
            logger.error(error)

    return message_history

def generate_response(prompt: str, user_name: str) -> ResponseResult:
    """Send a prompt to Amazon Bedrock and return the model's text response.

    Args:
        prompt: The input text (transcript) to send to the model.

    Returns:
        The generated response text as a string.
    """
    # Bedrock currently only supports the client API in boto3, not resource API.
    bedrock: BedrockRuntimeClient = boto3.client("bedrock-runtime", region_name="eu-west-2")
    
    history = read_db_by_user(user_name=user_name)
    response_num = len(history['Items'])
    logger.info(f"history {response_num} {history}")
    
    messages = create_message_history(history=history)
    logger.info(f"message_history {len(messages)} {messages}")
      
    messages.append({"role": "user",
                     "content": [{"text": prompt}]})

    system_prompt = (
        "You are an AI technical interviewer. "
        "Your job is to ask the candidate one interview question at a time. "
        "Review the full conversation history carefully and do NOT repeat or rephrase any question that has already been asked. "
        "Each question must cover a distinct topic or concept not yet explored in this conversation. "
        "Ask only one question per response."
    )

    #logger.info(f"messages {messages}")
    # send the transcript to the model and retrieve the generated text
    response = bedrock.converse(
        modelId=LLM,
        system=[{"text": system_prompt}],
        messages=messages
    )
    response_result = ResponseResult(response=response["output"]["message"]["content"][0]["text"],
                                     response_num=response_num)
    return response_result

def stringify_message_history(message_history: list) -> str:
    output = ""
    for message in message_history:
        output += f"{message.get('role')}: {message.get('content')[0].get('text')}\n"
    return output

def evaluate_repsonses(user_name: str):
    # Bedrock currently only supports the client API in boto3, not resource API.
    bedrock: BedrockRuntimeClient = boto3.client("bedrock-runtime", region_name="eu-west-2")
    
    history = read_db_by_user(user_name=user_name)
    response_num = len(history['Items'])
    logger.info(f"history {response_num} {history}")
    
    messages = create_message_history(history=history)
    logger.info(f"message_history {len(messages)} {messages}")

    message_history_str = stringify_message_history(messages)
    logger.info(message_history_str)
    output_format = "store the result in a json object in the exact form of { question_num: {expected_answer: , score:}, overall_evaluation: {comment: , score: } } only output ths json object and nothing else"
    prompt = f"Evaluate the responses from the user to the assistants questions in this interview transcript: {message_history_str}\n{output_format}"
    response = bedrock.converse(
        modelId=LLM,
        messages=[{"role": "user",
                   "content": [{"text": prompt}]}]
    )
    logger.info(response["output"]["message"]["content"][0]["text"])
    return response["output"]["message"]["content"][0]["text"]