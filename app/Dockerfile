FROM python:3.11-slim

WORKDIR /app
COPY ./requirements.txt /app/
RUN pip install --no-cache-dir -r ./requirements.txt
COPY . /app

# Compile translations
RUN pybabel compile -d translations

ENV FLASK_APP=app
CMD ["flask", "run", "--host=0.0.0.0", "--port=5001"]
