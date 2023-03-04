import base64
import io
import tempfile

import torch
import torchaudio
from speechbrain.pretrained import SpectralMaskEnhancement

file = "奧萬大吊橋.mp3"

enhance_model = SpectralMaskEnhancement.from_hparams(
    source="metricgan-u5000sync/", savedir="metricgan-u5000sync/"
)

noisy = enhance_model.load_audio(file).unsqueeze(0)
enhanced = enhance_model.enhance_batch(noisy, lengths=torch.tensor([1.0]))

with tempfile.NamedTemporaryFile() as tmp:
    print(tmp.name)
    tmp_filename = f"{tmp.name}"
    torchaudio.save(tmp_filename, enhanced, 16000, format="wav")

    with open(tmp_filename, "rb") as base64_file:
        b64str = base64.b64encode(base64_file.read()).decode("UTF-8")

with open("b64.txt", "wt", encoding="UTF-8") as f:
    f.write(b64str)

with open("b64.txt", "r", encoding="UTF-8") as f:
    audio_base64 = f.read()

audio_base64 = base64.b64decode(audio_base64, validate=True)
torchaudio.load(io.BytesIO(audio_base64))
