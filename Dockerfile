FROM python:3.12
ENV PYTHONUNBUFFERED=1
WORKDIR /usr/src/
COPY . 51442_52661_54362
WORKDIR /usr/src/51442_52661_54362
RUN ls -la
RUN pip install --no-cache-dir -r minimal-requirements.txt

EXPOSE 8000