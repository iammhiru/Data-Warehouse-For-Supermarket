# Mini Project - Data Engineering - Viettel Digital Talent 2025

## Introduction

- Title: Build a ETL system and visualizing revenue in supermarket
- Project Objective
  - Transform data from raw sources to Data Warehouse
  - Query and visualizing data on Data Warehouse

## System pipeline

![Luồng xử lí dữ liệu](https://github.com/iammhiru/Data-Warehouse-For-Supermarket/blob/main/pic/Flow.png)

## Deploy

### 1. Install tools

#### 1.1  Docker  

<https://docs.docker.com/get-docker/>

### 2. Deploy

#### 2.1 Build Custom Image

```sh
docker build ./airflow -t airflow_vdt:1.2
```

```sh
docker build ./superset -t superset-trino:1.0
```

#### 2.2 Deploy service

```sh
docker-compose up -d
```

#### 2.3 Connect Superset with Trino through SQLAlchemy

```sh
trino://hive@trino:8080/hive
```

### 3. Result Sample

#### Doanh thu theo nhóm sản phẩm

<img style="width:70%" src="https://github.com/iammhiru/Data-Warehouse-For-Supermarket/blob/main/pic/doanh_thu_nhom.png">