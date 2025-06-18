import argparse
from pyspark.sql import SparkSession
from pyspark.sql.functions import regexp_replace, col, lit
from pyspark import SparkConf
from pyspark.sql.utils import AnalysisException

def path_exists(spark, hdfs_path):
    fs = spark._jvm.org.apache.hadoop.fs.FileSystem.get(spark._jsc.hadoopConfiguration())
    p  = spark._jvm.org.apache.hadoop.fs.Path(hdfs_path)
    return fs.exists(p)

def parse_args():
    parser = argparse.ArgumentParser(description="Ingest CSV by date into Hive staging tables")
    parser.add_argument(
        "--process-date", "-d",
        required=True,
        help="Ngày cần xử lý, định dạng YYYY-MM-DD (ví dụ: 2025-06-17)"
    )
    return parser.parse_args()

def main():
    args = parse_args()
    date = args.process_date
    spark = SparkSession.builder \
        .appName("CSV to Hive Tables - staging") \
        .enableHiveSupport() \
        .getOrCreate()
    spark = (
        SparkSession.builder
            .appName("CSV to Hive Tables - staging")
            .master("spark://spark-master:7077")
            .config(
                "spark.jars",
                ",".join([
                    "/opt/bitnami/spark/jars/iceberg-spark-runtime-3.3_2.12-1.7.2.jar",
                    "/opt/bitnami/spark/jars/iceberg-hive-runtime-1.7.2.jar"
                ])
            )
            .config("spark.sql.catalog.hadoop", "org.apache.iceberg.spark.SparkCatalog")
            .config("spark.sql.catalog.hadoop.type", "hive")
            .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000")
            .config("spark.sql.catalog.hadoop.uri", "thrift://hive-metastore:9083")
            .config("spark.sql.catalog.hadoop.warehouse", "/user/hive/warehouse")
            .enableHiveSupport()
            .getOrCreate()
    )
    database = "staging"
    spark.sql(f"CREATE DATABASE IF NOT EXISTS {database}")

    base_paths = {
        "item":        "hdfs://namenode:9000/landing/item",
        "sale_record": "hdfs://namenode:9000/landing/sale_record",
        "wholesale":   "hdfs://namenode:9000/landing/wholesale",
        "loss_rate":   "hdfs://namenode:9000/landing/loss_rate"
    }

    for table_name, base_path in base_paths.items():
        hdfs_path = f"{base_path}/{date}.csv"
        if not path_exists(spark, hdfs_path):
            print(f"[WARN] File không tồn tại: {hdfs_path}, sẽ bỏ qua.")
            continue
        df = spark.read \
            .option("header", "true") \
            .option("inferSchema", "true") \
            .csv(hdfs_path)

        for field, dtype in df.dtypes:
            if dtype == "string":
                df = df.withColumn(field, regexp_replace(col(field), "\u00A0", " "))

        df = df.withColumn("process_date", lit(date))

        full_table = f"{database}.{table_name}"
        (
            df.write
              .mode("overwrite")
              .saveAsTable(full_table)
        )
        print(f"[{date}] Đã append dữ liệu vào bảng {full_table}")

    spark.stop()

if __name__ == "__main__":
    main()