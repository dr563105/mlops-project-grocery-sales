FROM public.ecr.aws/lambda/python:3.9

RUN pip install -U pip
RUN pip install pipenv

COPY [ "Pipfile", "Pipfile.lock", "./" ]

RUN pipenv install --system --deploy

# COPY [ "lgb_preds.parquet" , "lgb_preds.parquet" ]
COPY [ "items.parquet" , "lambda_function.py", "./" ]

CMD [ "lambda_function.lambda_handler" ]
