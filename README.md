<div align="center">

# Dereverberation MetricGAN-U

</div>

<details>
  <summary>Experiment</summary>
  
## Step0: Pre-Work

In the training phase of Dereverberation, Pairs of Clean audio stream and
Reverberated audio stream need to be prepare in advance.

The audio streams with the same basename are viewed as a pair in the training
phase

```bash
/path/to/ane/aaa.wav
/path/to/ane/bbb.wav

/path/to/rev/aaa.wav
/path/to/rev/bbb.wav

# in train_list
aaa.wav
bbb.wav
```

## Step1: Data Generator

### Data Path

The data is stored in `/media/ponddy/DATA2/ponddy_dereverb/weak_reverb` , and `dereverb/dataset/ponddy_dereverb/mix`.
You can skip this section by directly using these dataset.

### Implementation

It is expensive to collect the reverberated and clean wild data at the same
time. The most common way is to synthesize the reverb audio streams.

```bash
cd reverb_generator
```

The dataset rir_noise is used for reverberation generation, the dataset is
stored at `/media/ponddy/DATA2/dereverb/Dataset/RIRS_NOISES` and `dereverb/dataset/RIRS_NOISES` or it can be directly downloaded by the link.

```bash
wget http://www.openslr.org/resources/28/rirs_noises.zip
```

Then set the path in the gernerator.py to the corresponding one.

```bash
vim reverb_generator/generator.py

# change the path to the correct path if not running in the provided system.
ps_path = 
rir_path =
```

The script generate point source reverberation and RIR into a clean audio
stream.

```bash
Usage:

python main.py --input_path /media/DATA/dayiData/VCTK/wavs \
               --output_path /media/ponddy/DATA2/ponddy_dereverb \
               --mode split \
               --generate \
               --mklist
'''
input_path:  the path of the clean audio files 
output_path: the path to output reverb and clean wav
/path/of/the/output_path　─── rev # reverb 16k Hz wave
                          ├── ane # clean 16k Hz wave

mode:        use data of train, dev, or test. set split can automatically
             seperate the dataset to these three parts
generate:    set this flag to generate the reverb data
mklist:      output a list of training and develop audio files (may used in
             some training)
'''
```

### Other dataset

VoiceBank Datset can be downloaded from `http://140.109.21.234:5000/fsdownload/xuC7hkiDg/reverb-vctk-16k`. It is stored in `dereverb/dataset/reverb-vctk-16k`
It will be used for the training of speechbrain.

## Step2 Train (MetricGAN-U)

### Code preparation

The implementation of MetricGAN-U takes advantage of the open-sorce project `speechbrain`.

To start with Cloning the script from `speechbrain`.

```bash
git clone https://github.com/speechbrain/speechbrain.git
```

### Train

- Find the target repo

```bash
cd dereverb/speechbrain/recipes/Voicebank/dereverb/MetricGAN-U
```

#### Train with voicebank dataset

```bash
python train.py hparams/train_dereverb.yaml --data_folder dereverb/dataset/reverb-vctk-16k
```

#### Train with ponddy data

```bash
# ponddy_reverb_prepare.py 和 README.md 同目錄，複製到 speechbrain/recipes/Voicebank/dereverb/MetricGAN-U 底下
cp tool/ponddy_reverb_prepare.py /path/to/speechbrain/recipes/Voicebank/dereverb/MetricGAN-U/ponddy_reverb_prepare.py

cd /path/to/speechbrain/recipes/Voicebank/dereverb/MetricGAN-U/ 
vim train.py 
# from voicebank_revb_prepare import prepare_voicebank  # noqa (line 719)
from ponddy_reverb_prepare import prepare_voicebank  # noqa
```

- Train with ponddy dataset

```bash
python train.py hparams/train_dereverb.yaml --data_folder dereverb/dataset/ponddy_dereverb/mix
```

- inference (evaluation)
  - Test phase follow the completion of the training phase. Commenting the training code leads to access the evaluation part directly.
  - 將train.py 裡面的 se_brain.fit(...) 註解掉，即可跑驗證

- inference (單筆音檔 evaluation)

  - 訓練完成後，會在 `speechbrain/recipes/Voicebank/dereverb/spectral_mask/results/spectral_mask/<訓練設定的seed>/save` 資料夾底下，找到你的模型 checkpoint 資料夾。

  - 將checkpoint資料夾內的 generator.ckpt 重新命名為 enhance_model.ckpt。

  - 接著請參考 `/home/vincent0730/chinese-voice-scoring-widget/English/metricgan_inference.py`，其中`7-10`行設定成你的 `enhance_model.ckpt` 保存位置，資料夾內還須附上 `hyperparams.yaml`，`hyperparams.yaml` 直接沿用即可。

### Result

- MetricGanU
pesq = 2.03 for Voicebank, pesq = 1.74 for ponddy dataset.
- spectral-mask
pesq = 2.35 for Voicebank, pesq = 2.03 for ponddy dataset.

</details>

<details>
  <summary>Deployment</summary>
  
## Gunicorn

```bash=
git clone https://github.com/ponddy-edu/ML_web_dereverb.git
cd ML_web_dereverb/
python3.8 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
gunicorn app:app 或是 python app.py

# Reloads the configuration, starts the new worker processes, and gracefully shutdowns older workers
# 通常使用這個指令重啟即可
kill -SIGHUP $(cat gunicorn_pid)

# 強制關閉所有名為gunicorn的服務 (可能會關閉其他的gunicorn，謹慎使用)
pkill -f gunicorn 
```

- Open your browser and navigate to <http://192.168.1.27:8864>

## Docker Deployment

```bash=
sudo docker build --no-cache -t "ponddy/dereverb" -f Dockerfile .
sudo docker run -it -d --rm --name ponddy_dereverb_web_flask -p 8864:8864 ponddy/dereverb:latest
sudo docker tag image_id ponddy/dereverb:v1.2
sudo docker push ponddy/dereverb:v1.2
sudo docker push ponddy/dereverb:latest
```

- Open your browser and navigate to <http://192.168.1.27:8864>

</details>

<details open>
  <summary>Report</summary>

## GOP score table

- Pick 5 users' records
- Best score is marked in bold

|          | Original | Loud Norm | MetricGAN (sup) | Reverb CLS + MetricGAN (sup) | MetricGAN (unsup) | MetricGAN (unsup) + Synthesized reverb|
|----------|:----------:|:-----------:|:-----------------:|:------------------------------:|:-------------------:|:-------------------:|
| 4405語者 | 79       | **90**        | 88              | 80                           | **90**                | 84       |
| 4420語者 | 73       | 85        | 79              | 71                           | **86**                | 80       |
| 4451語者 | 62       | **72**        | 68              | 62                           | **72**                | 73         |
| 4479語者 | 70       | 79        | 76              | 69                           | **86**                | 78          |
| 4516語者 | 69       | 77        | 74              | 78                           | **82**                | 76            |

## Kullback–Leibler(KL) divergence table

- A measure of how one probability distribution *Q* is different from a second, reference probability distribution *P*.
- KL divergence 用來量測兩個分布之間的距離，0為最小值，表示兩分布相同
- Reverb CLS + MetricGAN (sup) 和 Original 的分布相差最遠，同時 Reverb CLS + MetricGAN (sup) 的分布更靠左一些

|          | Loud Norm | MetricGAN (sup) | Reverb CLS + MetricGAN (sup) | MetricGAN (unsup) | MetricGAN (unsup) + Synthesized reverb |
|----------|:-----------:|:-----------------:|:------------------------------:|:-------------------:|:-------------------:|
| Original | 0.00206   | 0.00383         | 0.01041                      | 0.00328           |0.0030       |

## 分布圖說明

- 圖內有兩個分布重和，分別是Original(偏橘色)，以及測試的方法(藍色)，而重疊部分為紫色
- 當測試的方法(藍色)在分布右邊(高分)出現越多，代表分數的分布提升
- 當測試的方法(藍色)在分布左邊(低分)出現越多，代表分數的分布降低

## Loudness normalization

- Thoughts
  - Can be easily integrated into our current system
  - Lowest latency compared to other deep learning solution
  - GOP 訓練資料並無進行 loudness normalization 預處理，可列入考慮

![LN](https://i.imgur.com/xFzJZ6B.png)

## MetricGAN (supervised) - 人工殘響進行訓練

- Thoughts
  - 有些許成效，但訓練資料不易取得，需準備大量乾淨音檔(困難)以及近似使用者的迴響情境(困難)

![MetricGAN (supervised)](https://i.imgur.com/fjMPdeA.png)

## Reverb classification & MetricGAN (supervised) - 人工殘響進行訓練

- Thoughts
  - 效果不佳，多數使用者音檔均被歸類為有迴響情境

![Reverb classification & MetricGAN (supervised)](https://i.imgur.com/qykUGDD.png)

## MetricGAN (unsupervised) - 真實5000筆殘響進行訓練

- Thoughts
  - 真實使用者音檔資料易取得，不需要人工合成殘響即可訓練
  - 長遠使用來看，使用非監督式模型效果較佳

![MetricGAN (unsupervised)](https://i.imgur.com/Q7MNgsu.png)

## MetricGAN (unsupervised) - 真實5000筆殘響 + 人工殘響進行訓練

- Thoughts
  - 效果和單純使用 MetricGAN (unsupervised) 差不多，但加入多種殘響能增加泛化能力

![](https://i.imgur.com/Xpxjw4g.png)

</details>

```bibtex
@misc{speechbrainV1,
  title={Open-Source Conversational AI with {SpeechBrain} 1.0},
  author={Mirco Ravanelli and Titouan Parcollet and Adel Moumen and Sylvain de Langen and Cem Subakan and Peter Plantinga and Yingzhi Wang and Pooneh Mousavi and Luca Della Libera and Artem Ploujnikov and Francesco Paissan and Davide Borra and Salah Zaiem and Zeyu Zhao and Shucong Zhang and Georgios Karakasidis and Sung-Lin Yeh and Pierre Champion and Aku Rouhe and Rudolf Braun and Florian Mai and Juan Zuluaga-Gomez and Seyed Mahed Mousavi and Andreas Nautsch and Xuechen Liu and Sangeet Sagar and Jarod Duret and Salima Mdhaffar and Gaelle Laperriere and Mickael Rouvier and Renato De Mori and Yannick Esteve},
  year={2024},
  eprint={2407.00463},
  archivePrefix={arXiv},
  primaryClass={cs.LG},
  url={https://arxiv.org/abs/2407.00463},
}

@misc{speechbrain,
  title={{SpeechBrain}: A General-Purpose Speech Toolkit},
  author={Mirco Ravanelli and Titouan Parcollet and Peter Plantinga and Aku Rouhe and Samuele Cornell and Loren Lugosch and Cem Subakan and Nauman Dawalatabad and Abdelwahab Heba and Jianyuan Zhong and Ju-Chieh Chou and Sung-Lin Yeh and Szu-Wei Fu and Chien-Feng Liao and Elena Rastorgueva and François Grondin and William Aris and Hwidong Na and Yan Gao and Renato De Mori and Yoshua Bengio},
  year={2021},
  eprint={2106.04624},
  archivePrefix={arXiv},
  primaryClass={eess.AS},
  note={arXiv:2106.04624}
}
