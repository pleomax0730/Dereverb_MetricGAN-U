import base64
import io
import tempfile
import os
import torch
import torchaudio
import soundfile as sf
from flask import Flask, jsonify, request
from flask_apiexceptions import (
    ApiError,
    ApiException,
    JSONExceptionHandler,
    api_exception_handler,
)
from speechbrain.pretrained import SpectralMaskEnhancement


app = Flask(__name__)
ext = JSONExceptionHandler(app)
ext.register(code_or_exception=ApiException, handler=api_exception_handler)

new_freq = 16000
input_limit = 20  # only accept audio with less than 20s.


base64_error = ApiError(code="base64", message="Unable to process the base64 entity.")
base64_save_error = ApiError(
    code="base64_save", message="Unable to save the processed audio to base64 format."
)
length_error = ApiError(
    code="length", message="Unable to process entity longer than 10s."
)
predict_error = ApiError(code="predict", message="Unable to predict the entity.")

cwd = os.getcwd()
model_path = os.path.join(cwd, "metricgan-u5000sync")
hparams_file = "hyperparams.yml"


def transform_audio(tensor, samplerate):
    # Stereo to Mono
    if tensor.shape[0] != 1:
        tensor = torch.mean(tensor, dim=0, keepdim=True)

    # Resample
    if samplerate != new_freq:
        resampler = torchaudio.transforms.Resample(
            orig_freq=samplerate, new_freq=new_freq
        )
        tensor = resampler(tensor)
    if tensor.shape[-1] > new_freq * input_limit:
        raise ApiException(status_code=422, error=length_error)

    return tensor


def get_b64_result(tensor):

    model = SpectralMaskEnhancement.from_hparams(
        source=model_path, hparams_file=hparams_file, savedir=model_path
    )

    try:
        enhanced = model.enhance_batch(tensor, lengths=torch.tensor([1.0]))
    except Exception as e:
        raise ApiException(status_code=422, error=predict_error)

    try:
        with tempfile.NamedTemporaryFile() as tmp:
            tmp_filename = tmp.name

            sf.write(
                f"{tmp_filename}.wav",
                enhanced.squeeze().numpy(),
                samplerate=new_freq,
                subtype="PCM_16",
                format="WAV",
            )

            with open(f"{tmp_filename}.wav", "rb") as base64_file:
                b64str = base64.b64encode(base64_file.read()).decode("UTF-8")
                os.rename(f"{tmp_filename}.wav", tmp_filename)
    except Exception as e:
        raise ApiException(status_code=422, error=base64_save_error)

    if os.path.exists(f"{tmp_filename}.wav"):
        try:
            os.remove(f"{tmp_filename}.wav")
        except Exception as e:
            pass

    return b64str


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/predict", methods=["POST"])
def predict():
    request_json = request.get_json()
    audio_base64 = request_json.get("base64", "")

    # Empty input check
    if not audio_base64:
        raise ApiException(status_code=422, error=base64_error)

    # Validate base64
    try:
        audio_base64 = base64.b64decode(audio_base64, validate=True)
        tensor, samplerate = torchaudio.load(io.BytesIO(audio_base64))
    except Exception as e:
        raise ApiException(status_code=422, error=base64_error)

    tensor = transform_audio(tensor, samplerate)

    b64str = get_b64_result(tensor)

    return jsonify({"base64": b64str})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8864, debug=True)
