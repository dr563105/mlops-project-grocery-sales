FROM public.ecr.aws/lambda/python:3.9

RUN pip install -U pip
RUN pip install pipenv

COPY [ "Pipfile", "Pipfile.lock", "./" ]

RUN pipenv install --system --deploy

COPY [ "lgb_predictions_wo_family.parquet" , "lgb_predictions_wo_family.parquet" ]
COPY [ "items.parquet" , "items.parquet" ]

COPY [ "lambda_function.py", "lambda_function.py" ]

EXPOSE 9696

CMD [ "lambda_function.lambda_handler" ]
