FROM python:3.9.14-slim

RUN pip install -U pip
RUN pip install pipenv

WORKDIR /app

COPY [ "Pipfile", "Pipfile.lock", "./" ]

RUN pipenv install --system --deploy

COPY [ "../input/df_test_preds_wo_family.parquet" , "df_test_preds_wo_family.parquet" ]
COPY [ "../input/df_items.parquet" , "df_items.parquet" ]

COPY ["sales_predictor.py", "sales_predictor.py"]

EXPOSE 9696

ENTRYPOINT [ "gunicorn", "--bind=0.0.0.0:9696", "sales_predictor:app" ]
#I want to start a lambda function


