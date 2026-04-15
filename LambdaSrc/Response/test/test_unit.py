from LambdaSrc.Response.Index import generate_response

def test_generate_response():
    prompt: str = "this is a test prompt"
    response = generate_response(prompt)
    assert type(response) == str