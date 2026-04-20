from LambdaSrc.Response.Index import generate_response, handler

def test_generate_response():
    prompt: str = "this is a test prompt"
    response = generate_response(prompt)
    assert type(response) == str

event_test_data = {
    "Records": [
        {
            "messageId": "033275d9-4fc5-493e-94ec-a9544127e6de",
            "receiptHandle": "AQEBF2SQZQETISakK96XdRNxC8MNhjLSUZwW0aqzWLJmttP40XDaMCqPWJ2v4BSWZc1dY7dtd5mb2w/rCU3zSsJp5SV4LRwF4SoeXiXPu0exxWZp8StNphJPEIH3DclfOINXk31chS3N0MOqCOcaqwUKXnK8oqi3LJSLj1a+Jzy63AVfx42l338VgrGtBruPzNaAniZfjz9BsI8dyTIF4NahcKRAksNxTL9qSY645Bp1q/HbLKmpZyHb3Bj4FTrmeQOlo9dwyUNwhXib74O2agfRkJZR8YSbAa7KqTe0nkDXvfeIXKr6yQAi9YCMuzY+odmLSzKJat1QTY3DWcDxQDGsySgC/53QnavtvpzcABEnS6W9f6wbPcEnQE2qJwunfHbDv87dD6iAdSjuJRMFIUwp6w==",
            "body": '{"user": "test", "transcription": "Give me a series of Python interview questions."}',
            "attributes": {
                "ApproximateReceiveCount": "1",
                "AWSTraceHeader": "Root=1-69e61a45-41a85f322124961a0ed0b178;Parent=0aa04879a227ce3f;Sampled=0;Lineage=1:5d53ea41:0",
                "SentTimestamp": "1776687697356",
                "SenderId": "AROAVCGYG6IT52M4VXCMJ:SpeechToText_dev",
                "ApproximateFirstReceiveTimestamp": "1776687697361",
            },
            "messageAttributes": {},
            "md5OfBody": "b6469447f4f97c0b869a1b7cb921f1c6",
            "eventSource": "aws:sqs",
            "eventSourceARN": "arn:aws:sqs:eu-west-2:348345791015:AInterview_dev_queue",
            "awsRegion": "eu-west-2",
        }
    ]
}

def test_handler():
    result = handler(event=event_test_data, context=None)
    assert type(result['response']) == str