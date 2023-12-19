from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
import audio_processing  # Updated import

app = FastAPI()

@app.post("/process-audio/")
async def process_audio(file: UploadFile = File(...)):
    audio_data = await file.read()
    response_text = audio_processing.process_audio(audio_data)
    audio_stream = audio_processing.synthesize_speech(response_text)
    return StreamingResponse(audio_stream, media_type="audio/mpeg")
