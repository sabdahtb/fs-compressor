FROM python:3-alpine

WORKDIR /dct-server

# Install app dependencies
# COPY requirements.txt ./

# RUN pip3 install -r requirements.txt

# Bundle app source
COPY . .

RUN . .venv/bin/activate

EXPOSE 5000

CMD [ "flask", "run","--host","0.0.0.0","--port","5000"]