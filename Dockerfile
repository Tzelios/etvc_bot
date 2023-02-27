FROM python:3.9

WORKDIR /etvc

COPY requirments.txt .

COPY ./src ./src

RUN pip install -r requirments.txt

CMD ["python3.9", "./src/main.py"]