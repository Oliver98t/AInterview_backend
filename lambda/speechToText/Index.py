import json
import os
# TODO create modules for each lambda function
# TODO connect lambda functions via queue
# TODO create a way to test each lambda function locally
# TODO create a folder structure for each lambda 
def handler(event, context):
    # Get environment variables
    print(event)
    environment = os.environ.get('ENVIRONMENT', 'unknown')
    
    # Build response
    response_body = {
        "message": "Hello from index1",
        "environment": environment,
        "path": event.get('rawPath', '/'),
        "method": event.get('requestContext', {}).get('http', {}).get('method', 'UNKNOWN')
    }
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(response_body)
    }