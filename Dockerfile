FROM python:3.13-slim

WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY src /code/src
COPY app_rest_api.py /code/app_rest_api.py

CMD ["uvicorn", "app_rest_api:app", "--host", "0.0.0.0", "--port", "8000"]