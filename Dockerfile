FROM python:3.9.20
RUN mkdir -p /app
WORKDIR /app
ADD main.py egs_module.py sql_module.py requirements.txt var.yaml README.md ./
RUN pip install -r requirements.txt
RUN mkdir /app/db
CMD ["python3", "main.py"]