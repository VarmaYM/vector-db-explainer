FROM python:3.11.2-slim

WORKDIR /project
COPY . .

CMD ["python3", "tools/check_doc.py"]
