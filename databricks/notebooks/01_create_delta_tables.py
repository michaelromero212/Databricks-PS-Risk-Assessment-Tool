# Databricks notebook source
# MAGIC %md
# MAGIC # PS Risk Assessment Tool - Delta Table Creation
# MAGIC 
# MAGIC This notebook creates the required Delta Lake tables for the 
# MAGIC Databricks PS Risk Assessment Tool.
# MAGIC 
# MAGIC **Tables created:**
# MAGIC - `engagements` - Engagement metadata
# MAGIC - `platform_signals` - Daily platform telemetry
# MAGIC - `risk_scores` - Computed risk assessments
# MAGIC - `ai_explanations` - AI-generated insights
# MAGIC - `metrics` - Aggregate PS metrics

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

# Configuration - Update these values for your environment
CATALOG = "main"  # or your catalog name
SCHEMA = "ps_risk_assessment"
BASE_PATH = "/FileStore/delta/ps_risk_tool"

# Create full paths
engagements_path = f"{BASE_PATH}/engagements"
signals_path = f"{BASE_PATH}/platform_signals"
risk_scores_path = f"{BASE_PATH}/risk_scores"
explanations_path = f"{BASE_PATH}/ai_explanations"
metrics_path = f"{BASE_PATH}/metrics"

print(f"Catalog: {CATALOG}")
print(f"Schema: {SCHEMA}")
print(f"Base Path: {BASE_PATH}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Schema

# COMMAND ----------

# Create schema if not exists
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")
spark.sql(f"USE {CATALOG}.{SCHEMA}")
print(f"Using schema: {CATALOG}.{SCHEMA}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Engagements Table

# COMMAND ----------

from pyspark.sql.types import *

# Define engagements schema
engagements_schema = StructType([
    StructField("engagement_id", StringType(), False),
    StructField("customer_name", StringType(), False),
    StructField("industry", StringType(), False),
    StructField("start_date", DateType(), False),
    StructField("target_completion_date", DateType(), False),
    StructField("scope_size", StringType(), False),
    StructField("sa_assigned", StringType(), False),
    StructField("sa_confidence_score", IntegerType(), False),
    StructField("created_at", TimestampType(), True),
    StructField("updated_at", TimestampType(), True),
])

# Create empty DataFrame with schema
engagements_df = spark.createDataFrame([], engagements_schema)

# Write as Delta table
engagements_df.write \
    .format("delta") \
    .mode("ignore") \
    .option("path", engagements_path) \
    .saveAsTable("engagements")

print("✓ Created engagements table")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Platform Signals Table

# COMMAND ----------

# Define platform_signals schema
signals_schema = StructType([
    StructField("signal_id", StringType(), False),
    StructField("engagement_id", StringType(), False),
    StructField("signal_date", DateType(), False),
    StructField("job_success_count", IntegerType(), True),
    StructField("job_failure_count", IntegerType(), True),
    StructField("avg_job_duration_seconds", DoubleType(), True),
    StructField("notebook_execution_count", IntegerType(), True),
    StructField("sql_query_count", IntegerType(), True),
    StructField("last_activity_timestamp", TimestampType(), True),
    StructField("collected_at", TimestampType(), True),
])

# Create empty DataFrame with schema
signals_df = spark.createDataFrame([], signals_schema)

# Write as Delta table (partitioned by signal_date)
signals_df.write \
    .format("delta") \
    .mode("ignore") \
    .option("path", signals_path) \
    .partitionBy("signal_date") \
    .saveAsTable("platform_signals")

print("✓ Created platform_signals table")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Risk Scores Table

# COMMAND ----------

# Define risk_scores schema
risk_scores_schema = StructType([
    StructField("score_id", StringType(), False),
    StructField("engagement_id", StringType(), False),
    StructField("risk_score", DoubleType(), False),
    StructField("risk_level", StringType(), False),
    StructField("contributing_factors", StringType(), True),  # JSON string
    StructField("trend_direction", StringType(), False),
    StructField("computed_at", TimestampType(), True),
])

# Create empty DataFrame with schema
risk_scores_df = spark.createDataFrame([], risk_scores_schema)

# Write as Delta table
risk_scores_df.write \
    .format("delta") \
    .mode("ignore") \
    .option("path", risk_scores_path) \
    .saveAsTable("risk_scores")

print("✓ Created risk_scores table")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create AI Explanations Table

# COMMAND ----------

# Define ai_explanations schema
explanations_schema = StructType([
    StructField("explanation_id", StringType(), False),
    StructField("engagement_id", StringType(), False),
    StructField("model_name", StringType(), False),
    StructField("model_provider", StringType(), True),
    StructField("model_purpose", StringType(), True),
    StructField("risk_explanation", StringType(), False),
    StructField("mitigation_suggestions", StringType(), True),  # JSON string
    StructField("generation_status", StringType(), False),
    StructField("generated_at", TimestampType(), True),
    StructField("cached", BooleanType(), True),
])

# Create empty DataFrame with schema
explanations_df = spark.createDataFrame([], explanations_schema)

# Write as Delta table
explanations_df.write \
    .format("delta") \
    .mode("ignore") \
    .option("path", explanations_path) \
    .saveAsTable("ai_explanations")

print("✓ Created ai_explanations table")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Metrics Table

# COMMAND ----------

# Define metrics schema
metrics_schema = StructType([
    StructField("metric_id", StringType(), False),
    StructField("metric_date", DateType(), False),
    StructField("active_engagement_count", IntegerType(), True),
    StructField("high_risk_count", IntegerType(), True),
    StructField("medium_risk_count", IntegerType(), True),
    StructField("low_risk_count", IntegerType(), True),
    StructField("avg_risk_score", DoubleType(), True),
    StructField("ai_coverage_rate", DoubleType(), True),
    StructField("computed_at", TimestampType(), True),
])

# Create empty DataFrame with schema
metrics_df = spark.createDataFrame([], metrics_schema)

# Write as Delta table (partitioned by metric_date)
metrics_df.write \
    .format("delta") \
    .mode("ignore") \
    .option("path", metrics_path) \
    .partitionBy("metric_date") \
    .saveAsTable("metrics")

print("✓ Created metrics table")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify Tables

# COMMAND ----------

# List all tables in the schema
tables = spark.sql(f"SHOW TABLES IN {CATALOG}.{SCHEMA}").collect()
print(f"\nTables in {CATALOG}.{SCHEMA}:")
print("-" * 40)
for table in tables:
    print(f"  • {table.tableName}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Table Details

# COMMAND ----------

# Show table details
for table_name in ["engagements", "platform_signals", "risk_scores", "ai_explanations", "metrics"]:
    print(f"\n{table_name}:")
    print("-" * 40)
    spark.sql(f"DESCRIBE TABLE {table_name}").show(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC 
# MAGIC All Delta tables have been created successfully:
# MAGIC 
# MAGIC | Table | Description |
# MAGIC |-------|-------------|
# MAGIC | `engagements` | Engagement metadata |
# MAGIC | `platform_signals` | Daily Databricks platform telemetry |
# MAGIC | `risk_scores` | Computed risk assessments with factors |
# MAGIC | `ai_explanations` | AI-generated risk explanations |
# MAGIC | `metrics` | Aggregate PS metrics for leadership |
# MAGIC 
# MAGIC Next steps:
# MAGIC 1. Run `02_generate_sample_data` to populate with demo data
# MAGIC 2. Run `03_risk_scoring_engine` to compute risk scores
# MAGIC 3. Run `04_ai_explanation_generator` to generate AI explanations
