FROM python:3.12.0
WORKDIR /app
ENV DEBIAN_FRONTEND="noninteractive"
RUN apt-get update && apt-get -y install python3-sklearn \
    python3-sklearn-lib python3-pandas build-essential \
    libpoppler-cpp-dev pkg-config python3-dev && \
    apt-get clean
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
COPY requirements.txt /app
COPY app.py /app
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["flask","run"]
