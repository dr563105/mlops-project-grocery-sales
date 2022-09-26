FROM python:3.9.14-slim

RUN pip install -U pip
RUN pip install pipenv

WORKDIR /app

COPY [ "Pipfile", "Pipfile.lock", "./" ]

RUN pipenv install --system --deploy

COPY [ "lgb_preds.parquet" , "lgb_preds.parquet" ]
COPY [ "items.parquet" , "items.parquet" ]

COPY ["flask_sales_predictor.py", "flask_sales_predictor.py"]

EXPOSE 9696

ENTRYPOINT [ "gunicorn", "--bind=0.0.0.0:9696", "flask_sales_predictor:app" ]
