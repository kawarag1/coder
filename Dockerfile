FROM python:3.11

WORKDIR /code

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:${PATH}"

COPY poetry.lock pyproject.toml ./

RUN poetry install --no-root

COPY ./src/coder .

#CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
CMD ["poetry", "run", "chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "80"]
