FROM apache/airflow:2.10.3
USER root
RUN apt update
RUN apt install -y default-jdk 
USER airflow
RUN pip install pyspark==3.3.4
USER root
RUN apt-get update \
    && apt-get install -y default-jdk wget ca-certificates \
    && wget https://repo1.maven.org/maven2/io/trino/trino-cli/403/trino-cli-403-executable.jar \
       -O /usr/local/bin/trino \
    && chmod +x /usr/local/bin/trino \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow