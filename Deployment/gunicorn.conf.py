import multiprocessing

bind = "0.0.0.0:8864"
workers = 1
# accesslog = "-"
# errorlog = "./error.log"
# loglevel = "error"
# worker_class = "egg:meinheld#gunicorn_worker"
max_requests = 1000
timeout = 30
pidfile = "gunicorn_pid"
