import LambdaSrc.SpeechToText.Index as stt
from LambdaSrc.SpeechToText.Index import Transcribe, handler
import json

def test_transcribe():
    transcribe = Transcribe(bucket="ainterviewupload", user="test")
    transcription = transcribe.transcribe()
    test_trasncription = "Give me a series of Python interview questions."
    assert transcription == test_trasncription

event_test_data = {
        "version": "2.0",
        "routeKey": "$default",
        "rawPath": "/",
        "rawQueryString": "user=test",
        "headers": {
            "x-amzn-tls-version": "TLSv1.3",
            "x-amz-date": "20260420T122125Z",
            "x-forwarded-proto": "https",
            "postman-token": "ab03b80a-a27b-486d-8ebf-1e0f42351d78",
            "x-forwarded-port": "443",
            "x-forwarded-for": "213.120.89.156",
            "accept": "*/*",
            "x-amzn-tls-cipher-suite": "TLS_AES_128_GCM_SHA256",
            "x-amzn-trace-id": "Root=1-69e61a45-41a85f322124961a0ed0b178",
            "host": "crje4j5cnd2yyhgbgpautdxrxm0qofor.lambda-url.eu-west-2.on.aws",
            "cache-control": "no-cache",
            "accept-encoding": "gzip, deflate, br",
            "user-agent": "PostmanRuntime/7.53.0",
        },
        "queryStringParameters": {"user": "test"},
        "requestContext": {
            "accountId": "348345791015",
            "apiId": "crje4j5cnd2yyhgbgpautdxrxm0qofor",
            "authorizer": {
                "iam": {
                    "accessKey": "AKIAVCGYG6ITSJW4JKVE",
                    "accountId": "348345791015",
                    "callerId": "AIDAVCGYG6IT6WHIS63FU",
                    "cognitoIdentity": None,
                    "principalOrgId": None,
                    "userArn": "arn:aws:iam::348345791015:user/oli-work",
                    "userId": "AIDAVCGYG6IT6WHIS63FU",
                }
            },
            "domainName": "crje4j5cnd2yyhgbgpautdxrxm0qofor.lambda-url.eu-west-2.on.aws",
            "domainPrefix": "crje4j5cnd2yyhgbgpautdxrxm0qofor",
            "http": {
                "method": "GET",
                "path": "/",
                "protocol": "HTTP/1.1",
                "sourceIp": "136.226.167.104",
                "userAgent": "PostmanRuntime/7.53.0",
            },
            "requestId": "a441f224-f797-4ec5-a0c8-f673a3cd49d7",
            "routeKey": "$default",
            "stage": "$default",
            "time": "20/Apr/2026:12:21:25 +0000",
            "timeEpoch": 1776687685938,
        },
        "isBase64Encoded": False,
    }

def test_handler(monkeypatch):
    monkeypatch.setattr(stt, "S3_BUCKET", "ainterviewupload")
    result = handler(event=event_test_data, context=None)
    body = json.loads(result['body'])
    assert result['statusCode'] == 200
    assert body == "transcription: Give me a series of Python interview questions."