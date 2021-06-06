FROM python:3.9-alpine
COPY . .
RUN apk --update add gcc build-base \
    && pip install --no-cache-dir -r requirements.txt
CMD kopf run operator_logic.py --verbose