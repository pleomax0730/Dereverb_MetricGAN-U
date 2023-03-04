<div align="center">

# Dereverberation MetricGAN-U

</div>

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

<details>
  <summary>Reports</summary>

  ## GOP score table

  - Pick 5 users' records
  - Best score is marked in bold

  |          | Original | Loud Norm | MetricGAN (sup) | Reverb CLS + MetricGAN (sup) | MetricGAN (unsup) | MetricGAN (unsup) + Sync reverb|
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

  |          | Loud Norm | MetricGAN (sup) | Reverb CLS + MetricGAN (sup) | MetricGAN (unsup) | MetricGAN (unsup) + Sync reverb |
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

