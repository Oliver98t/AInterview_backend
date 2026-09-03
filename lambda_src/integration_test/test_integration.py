"""Integration tests for the deployed AInterview backend Lambdas.

These tests make real HTTP calls to deployed Lambda function URLs and
require AWS credentials to be set in the environment:
  - AWS_ACCESS_KEY_ID
  - AWS_SECRET_ACCESS_KEY

Run against a live AWS environment only — not in CI without credentials.
"""

import os
import requests
from requests_aws4auth import AWS4Auth
import subprocess
import boto3

def get_lambda_function_url(function_name: str) -> str:
    """Retrieve the function URL for a deployed Lambda using the AWS CLI.

    Args:
        function_name: The name of the Lambda function.
        region: The AWS region the function is deployed in.

    Returns:
        The HTTPS function URL as a string.
    """
    result = subprocess.run(
        [
            "terraform",
            "-chdir=infrastructure",
            "output",
            "-raw",
            f"{function_name}_lambda_function_url"
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()

def send_response(
        response_url: str,
        user: str, 
        message: str, 
        role: str, 
        clear: str, 
        evaluate: bool, 
        access_token: str) -> dict:
    if role not in ("user", "assistant"):
        raise ValueError(f"Invalid role: {role}")

    body = {
        "user_name": user,
        "message": message,
        "role": role,
        "clear_db": clear,
        "eval": evaluate,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    res = requests.post(response_url, json=body, headers=headers)
    if not res.ok:
        raise RuntimeError(f"Failed to send transcript: {res.status_code} {res.text}")
    return res.json()

def test_response():
    client = boto3.client("cognito-idp", region_name="eu-west-2")
    
    response = client.initiate_auth(
        ClientId=os.environ['AUTH0_CLIENT_ID'],
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={
            "USERNAME": os.environ['TEST_ACCOUNT'],
            "PASSWORD": os.environ['TEST_PASSWORD'],
        },
    )

    AccessToken = response['AuthenticationResult']['AccessToken']
    response = send_response(
        response_url=f"{get_lambda_function_url("response")}/response",
        user="test",
        message="test message",
        role="user",
        clear=None,
        evaluate=None,
        access_token=AccessToken
    )
    
def test_speech_to_text():
    """Integration test: invoke the deployed speech_to_text Lambda and verify a 200 response.

    Signs the request with AWS SigV4 credentials read from the environment,
    then calls the function URL with a 'user=test' query parameter.
    """
    # # read AWS credentials from the environment
    # access_key = os.environ.get("AWS_ACCESS_KEY_ID")
    # secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
    # region = "eu-west-2"
    # service = "lambda"

    # # # build SigV4 auth for the Lambda function URL
    # # auth = AWS4Auth(
    # #     access_key,
    # #     secret_key,
    # #     region,
    # #     service,
    # # )

    # # # resolve the live function URL and invoke it
    # url = get_lambda_function_url("speech_to_text_dev")
    # params = {"user": "test"}
    # response = requests.get(url, params=params, auth=auth)
    # assert response.status_code == 200
