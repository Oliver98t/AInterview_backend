from LambdaSrc.SpeechToText.Index import Transcribe

class TestSpeechToTextIndex:
    def test_transcribe(self):
        transcription = Transcribe(bucket="ainterviewupload", user="test").transcribe()
        test_trasncription = "Give me a series of Python interview questions."
        assert transcription == test_trasncription