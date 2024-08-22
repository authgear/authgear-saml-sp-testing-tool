FROM python:3.11.9-slim

RUN pip install pipenv
WORKDIR /app
COPY ./Pipfile ./Pipfile.lock ./setup.py /app/
RUN pipenv install --system --dev --deploy
COPY . /app
ENV FLASK_APP=app
CMD ["flask", "run", "--host=0.0.0.0", "--port=5001"]
