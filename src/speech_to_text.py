from openai import OpenAI
import io

#placeholder for api keys and initalize the client


def speech_to_text(audio_data: bytes) -> str:
    # Convert bytes data to a file-like object
    audio_file = io.BytesIO(audio_data)

    audio_file.seek(0)

    with open('output.wav', 'wb') as f:
        f.write(audio_file.getvalue())

    print("File saved")
    audio_file= open('output.wav', "rb")
    # Use the file-like object directly with the OpenAI API
    transcription = client.audio.transcriptions.create(
    model="whisper-1", 
    file=audio_file
    )
    return transcription.text


