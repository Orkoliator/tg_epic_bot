FROM python:3.9.20-slim
RUN mkdir -p /app
WORKDIR /app
ADD main.py egs_module.py sql_module.py requirements.txt var.yaml README.md ./
RUN pip install -r requirements.txt
CMD [“python”, “./main.py”]