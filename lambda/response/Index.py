import boto3
import datetime
import os
import json
import uuid
from mypy_boto3_bedrock_runtime import BedrockRuntimeClient

# create the DynamoDB resource
dynamo = boto3.client('dynamodb')

def handler(event, context):
    # get the message out of the SQS event
    message = event['Records'][0]['body']
    data: dict = json.loads(message)
    print(data)
    # write event data to DDB table
    user = data.get('user')
    transcript = data.get('transcription')
    response = generate_response(transcript)

    if os.environ.get('LOCAL_TEST', None) != None:
        tablename = os.environ['TABLE_TABLE_NAME']
        dynamo.put_item(
            TableName=tablename,
            Item={
                'id': {'S': str(uuid.uuid4())},
                'timestamp': {'S': datetime.datetime.now().isoformat()},
                #'transcript': {'N': str(transcript)}
            }
        )
    else:
        print(f"{user}: {transcript}")
        print(f"AI: {response}")

def generate_response(prompt: str):
    client: BedrockRuntimeClient = boto3.client("bedrock-runtime", region_name="eu-west-2")  

    response = client.converse( 
        modelId="global.amazon.nova-2-lite-v1:0", 
        messages=[ 
            { 
                "role": "user", 
                "content": [{"text": prompt}]
            } 
        ] 
    )  

    return response["output"]["message"]["content"][0]["text"]

if __name__ == "__main__":

    print(generate_response("hello there"))