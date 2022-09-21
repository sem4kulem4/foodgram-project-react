FROM python:3.7-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --requirement requirements.txt

COPY ./ /app

RUN pip3 install -r requirements.txt --no-cache-dir

CMD ["python", "manage.py", "runserver", "0:8000"]