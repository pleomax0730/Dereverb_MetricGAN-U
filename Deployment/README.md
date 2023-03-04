<div align="center">

# ML_web_dereverb

</div>

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
