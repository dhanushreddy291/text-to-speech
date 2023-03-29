import os
import json
import requests
import soundfile as sf
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from fairseq.checkpoint_utils import load_model_ensemble_and_task_from_hf_hub
from fairseq.models.text_to_speech.hub_interface import TTSHubInterface

app = FastAPI()


class Text(BaseModel):
    text: str


@app.get("/")
async def root():
    return {"message": "Hello from Docker 🐳"}


@app.post("/tts")
async def tts(text: Text):
    try:
        models, cfg, task = load_model_ensemble_and_task_from_hf_hub(
            "facebook/fastspeech2-en-ljspeech",
            arg_overrides={"vocoder": "hifigan", "fp16": False},
        )
        model = models[0]
        TTSHubInterface.update_cfg_with_data_cfg(cfg, task.data_cfg)
        generator = task.build_generator([model], cfg)

        sample = TTSHubInterface.get_model_input(task, text.text)
        wav, rate = TTSHubInterface.get_prediction(task, model, generator, sample)

        # Store wav file locally at /tmp
        sf.write("/tmp/output.wav", wav, rate)
        wavURL = requests.post(
            "https://tmpfiles.org/api/v1/upload",
            files={"file": open("/tmp/output.wav", "rb")},
        ).json()["data"]["url"].replace("tmpfiles.org", "tmpfiles.org/dl")

        # Delete wav file from /tmp
        os.remove("/tmp/output.wav")
        # return an HTML page with the audio player and the text
        return HTMLResponse(
            f"""<html>
        <head>
            <title>Text to Speech</title>
        </head>
        <body>
            <h1>Text to Speech</h1>
            <p>{text.text}</p>
            <audio controls>
                <source src="{wavURL}" type="audio/wav">
            </audio>
        </body>
        </html>"""
        )
    except:
        return {"error": "Error in TTS"}
