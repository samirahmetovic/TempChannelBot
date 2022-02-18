FROM python:3.10

WORKDIR /arenabot
ADD main.py /

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .
RUN chmod +x main.py

CMD ["python", "main.py"]