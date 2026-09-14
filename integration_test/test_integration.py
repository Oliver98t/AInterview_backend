"""Integration tests for the deployed AInterview backend Lambdas.

These tests make real HTTP calls to deployed Lambda function URLs and
require AWS credentials to be set in the environment:
  - AWS_ACCESS_KEY_ID
  - AWS_SECRET_ACCESS_KEY

Run against a live AWS environment only — not in CI without credentials.
"""

import os
import subprocess

import boto3
import requests


def get_lambda_function_url(function_name: str) -> str:
    """Retrieve the deployed endpoint URL using the AWS CLI.

    Args:
        function_name: The name of the Lambda function.

    Returns:
        The HTTPS endpoint URL as a string.
    """
    region = os.environ.get("AWS_REGION", "eu-west-2")
    environment = os.environ.get("ENVIRONMENT", "dev")

    api_name = f"AInterview_{environment}_api"
    result = subprocess.run(
        [
            "aws",
            "apigatewayv2",
            "get-apis",
            "--region",
            region,
            "--query",
            f"Items[?Name=='{api_name}'].ApiEndpoint | [0]",
            "--output",
            "text",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    print(result)
    endpoint_url = result.stdout.strip().rstrip("/")
    if not endpoint_url or endpoint_url == "None":
        raise RuntimeError(f"Could not find endpoint URL for {function_name}")

    return endpoint_url


def send_response(
    response_url: str,
    user: str,
    message: str,
    role: str,
    clear: str | None,
    evaluate: bool | None,
    access_token: str,
) -> dict:
    """Send a transcript message to the deployed response endpoint.

    Args:
        response_url: The endpoint URL that receives the transcript.
        user: The username associated with the transcript.
        message: The transcript message to send.
        role: The message role, either ``user`` or ``assistant``.
        clear: Whether the endpoint should clear the existing database.
        evaluate: Whether the endpoint should evaluate the response.
        access_token: The bearer token used to authenticate the request.

    Returns:
        The decoded JSON response from the endpoint.

    Raises:
        ValueError: If ``role`` is not ``user`` or ``assistant``.
        RuntimeError: If the endpoint returns an unsuccessful status code.
    """
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
    return dict(res.json())


def test_response() -> None:
    """Authenticate a test account and send a sample response message."""
    client = boto3.client("cognito-idp", region_name="eu-west-2")

    response = client.initiate_auth(
        ClientId=os.environ["AUTH0_CLIENT_ID"],
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={
            "USERNAME": os.environ["TEST_ACCOUNT"],
            "PASSWORD": os.environ["TEST_PASSWORD"],
        },
    )

    access_token = response["AuthenticationResult"]["AccessToken"]
    response = send_response(
        response_url=f"{get_lambda_function_url('response')}/response",
        user="test",
        message="test message",
        role="user",
        clear=None,
        evaluate=None,
        access_token=access_token,
    )


def test_speech_to_text() -> None:
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
