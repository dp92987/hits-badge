FROM dp92987/python_w_gcc_libpq-dev:3.9.1-slim-buster

WORKDIR /usr/hits-badge

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .

CMD gunicorn "hitsbadge:create_app()" --bind=0.0.0.0:5000 --workers=$WORKERS
