FROM python:3.11

RUN mkdir /fastapi_app

WORKDIR /fastapi_app

COPY requirements.txt .

RUN pip install -r requirements.txt && pip install "fastapi[all]" && pip install passlib && pip install PyJWT

COPY . .

EXPOSE 8000:8000

CMD [ "python", "./main.py" ]

#RUN chmod a+x docker/*.sh

#docker run --rm --network=host fastapi:latest

