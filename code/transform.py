from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, date_format, year, month, dayofmonth, monotonically_increasing_id

spark = (
        SparkSession.builder
            .appName("ETL Staging → Warehouse")
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
staging_db = "staging"
warehouse_db = "warehouse"

spark.sql(f"CREATE DATABASE IF NOT EXISTS {warehouse_db}")

df_item = spark.table(f"{staging_db}.item") \
    .withColumnRenamed("item code", "item_code") \
    .withColumnRenamed("item name", "item_name") \
    .withColumnRenamed("category code", "category_code") \
    .withColumnRenamed("category name", "category_name") \
    .dropDuplicates(["item_code"]) \
    .withColumn("item_key", monotonically_increasing_id())

df_item.select(
    "item_key", "item_code", "item_name", "category_code", "category_name"
).write.mode("overwrite").saveAsTable(f"{warehouse_db}.dim_item")

df_dates = spark.table(f"{staging_db}.sale_record") \
    .select(to_date(col("date")).alias("dt"))
df_dates = df_dates.union(
    spark.table(f"{staging_db}.wholesale").select(to_date(col("date")).alias("dt"))
).dropDuplicates(["dt"]) \
 .withColumn("date_key", date_format(col("dt"), "yyyyMMdd").cast("int")) \
 .withColumn("year", year(col("dt"))) \
 .withColumn("month", month(col("dt"))) \
 .withColumn("day", dayofmonth(col("dt"))) \
 .withColumn("weekday", date_format(col("dt"), "E"))

from pyspark.sql.functions import col as _col, abs
spark.createDataFrame([], schema="date_key INT, date DATE, year INT, month INT, day INT, weekday STRING") 
df_dates.select(
    "date_key", col("dt").alias("date"), "year", "month", "day", "weekday"
).write.mode("overwrite").saveAsTable(f"{warehouse_db}.dim_date")

dim_tran = spark.createDataFrame(
    [(1, "sale"), (2, "return")],
    ["tran_type_key", "tran_type"]
)
dim_tran.write.mode("overwrite").saveAsTable(f"{warehouse_db}.dim_transaction_type")

dim_discount = spark.createDataFrame(
    [(1, "Yes"), (2, "No")],
    ["discount_flag_key", "discount_flag"]
)
dim_discount.write.mode("overwrite").saveAsTable(f"{warehouse_db}.dim_discount_flag")

df_sales = spark.table(f"{staging_db}.sale_record") \
    .withColumnRenamed("item code", "item_code") \
    .withColumnRenamed("quantity sold (kilo)", "quantity_kilo") \
    .withColumnRenamed("unit selling price (rmb/kg)", "unit_price") \
    .withColumnRenamed("sale or return", "tran_type") \
    .withColumnRenamed("discount (yes/no)", "discount_flag") \
    .withColumn("date", to_date(col("date"))) \
    .withColumn("quantity_kilo", abs(col("quantity_kilo"))) \
    .join(df_item, "item_code") \
    .join(df_dates.withColumnRenamed("dt", "date"), "date") \
    .join(dim_tran, "tran_type") \
    .join(dim_discount, "discount_flag") \
    .withColumn("sale_key", monotonically_increasing_id()) \
    .withColumn("total_amount", col("quantity_kilo") * col("unit_price"))

df_sales.select(
    "sale_key", "date_key", "item_key", "tran_type_key", "discount_flag_key", 
    "quantity_kilo", "unit_price", "total_amount"
).write.mode("overwrite").saveAsTable(f"{warehouse_db}.fact_sales")

from pyspark.sql.functions import to_date

df_wh = spark.table(f"{staging_db}.wholesale") \
    .withColumnRenamed("item code", "item_code") \
    .withColumnRenamed("wholesale price (rmb/kg)", "wholesale_price") \
    .withColumn("date", to_date(col("date"))) \
    .join(df_item, "item_code") \
    .join(df_dates.withColumnRenamed("dt", "date"), "date") \
    .withColumn("wholesale_key", monotonically_increasing_id())

df_wh.select(
    "wholesale_key", "date_key", "item_key", "wholesale_price"
).write.mode("overwrite").saveAsTable(f"{warehouse_db}.fact_wholesale")

df_loss = spark.table(f"{staging_db}.loss_rate") \
    .withColumnRenamed("item code", "item_code") \
    .withColumnRenamed("loss rate (%)", "loss_rate") \
    .join(df_item, "item_code") \
    .withColumn("loss_key", monotonically_increasing_id())

df_loss.select(
    "loss_key", "item_key", "loss_rate"
).write.mode("overwrite").saveAsTable(f"{warehouse_db}.fact_loss")

spark.stop()