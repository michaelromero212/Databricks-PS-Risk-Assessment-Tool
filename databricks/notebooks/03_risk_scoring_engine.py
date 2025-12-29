# Databricks notebook source
# MAGIC %md
# MAGIC # PS Risk Assessment Tool - Risk Scoring Engine
# MAGIC 
# MAGIC This notebook computes risk scores for all engagements using 
# MAGIC rule-based heuristics with weighted signal aggregation.
# MAGIC 
# MAGIC **Scoring Weights:**
# MAGIC - Job Failure Rate: 25%
# MAGIC - Job Duration Trend: 15%
# MAGIC - Activity Recency: 20%
# MAGIC - SA Confidence: 20%
# MAGIC - Schedule Variance: 20%

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.window import Window
from datetime import datetime, timedelta
import json
import uuid

# Configuration
CATALOG = "main"
SCHEMA = "ps_risk_assessment"

# Scoring weights
WEIGHTS = {
    "job_failure_rate": 0.25,
    "job_duration_trend": 0.15,
    "activity_recency": 0.20,
    "sa_confidence": 0.20,
    "schedule_variance": 0.20,
}

# Risk thresholds
THRESHOLD_LOW = 35
THRESHOLD_HIGH = 65

spark.sql(f"USE {CATALOG}.{SCHEMA}")
print(f"Using schema: {CATALOG}.{SCHEMA}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Data

# COMMAND ----------

# Load engagements and signals
engagements_df = spark.table("engagements")
signals_df = spark.table("platform_signals")

print(f"Engagements: {engagements_df.count()}")
print(f"Signals: {signals_df.count()}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Compute Signal Aggregates

# COMMAND ----------

# Aggregate signals by engagement
signal_agg = signals_df.groupBy("engagement_id").agg(
    # Job failure metrics
    sum("job_success_count").alias("total_success"),
    sum("job_failure_count").alias("total_failure"),
    
    # Duration trend (compare first half to second half)
    avg("avg_job_duration_seconds").alias("avg_duration"),
    
    # Activity recency
    max("last_activity_timestamp").alias("last_activity"),
    max("signal_date").alias("latest_signal_date"),
    
    # Activity counts
    sum("notebook_execution_count").alias("total_notebooks"),
    sum("sql_query_count").alias("total_queries"),
)

# Calculate failure rate
signal_agg = signal_agg.withColumn(
    "failure_rate",
    when(col("total_success") + col("total_failure") > 0,
         col("total_failure") / (col("total_success") + col("total_failure")) * 100
    ).otherwise(0)
)

display(signal_agg)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Compute Risk Scores

# COMMAND ----------

# Join engagements with signal aggregates
risk_data = engagements_df.join(signal_agg, "engagement_id", "left")

# Current date for calculations
current_date = current_date()
current_timestamp_val = current_timestamp()

# Calculate individual risk factor scores
risk_scores = risk_data.withColumn(
    # Job Failure Rate Score (0-100)
    "job_failure_score",
    when(col("failure_rate") > 20, 100)
    .when(col("failure_rate") > 10, 60)
    .otherwise(20)
).withColumn(
    # Activity Recency Score (0-100)
    "days_since_activity",
    when(col("last_activity").isNotNull(),
         datediff(current_date, col("last_activity").cast("date"))
    ).otherwise(lit(14))
).withColumn(
    "activity_recency_score",
    when(col("days_since_activity") > 7, 100)
    .when(col("days_since_activity") > 3, 50)
    .otherwise(10)
).withColumn(
    # SA Confidence Score (0-100)
    "sa_confidence_score_factor",
    when(col("sa_confidence_score") <= 2, 100)
    .when(col("sa_confidence_score") == 3, 50)
    .otherwise(10)
).withColumn(
    # Schedule Variance Score (0-100)
    "total_days",
    datediff(col("target_completion_date"), col("start_date"))
).withColumn(
    "elapsed_days",
    datediff(current_date, col("start_date"))
).withColumn(
    "progress_pct",
    when(col("total_days") > 0, col("elapsed_days") / col("total_days") * 100).otherwise(100)
).withColumn(
    "schedule_score",
    when(col("progress_pct") > 100, 100)
    .when(col("progress_pct") > 80, 80)
    .when(col("progress_pct") > 50, 40)
    .otherwise(10)
).withColumn(
    # Duration trend score (simplified - using avg as proxy)
    "duration_score",
    when(col("avg_duration") > 150, 100)
    .when(col("avg_duration") > 100, 50)
    .otherwise(30)
)

# Calculate weighted total score
risk_scores = risk_scores.withColumn(
    "risk_score",
    (col("job_failure_score") * WEIGHTS["job_failure_rate"]) +
    (col("duration_score") * WEIGHTS["job_duration_trend"]) +
    (col("activity_recency_score") * WEIGHTS["activity_recency"]) +
    (col("sa_confidence_score_factor") * WEIGHTS["sa_confidence"]) +
    (col("schedule_score") * WEIGHTS["schedule_variance"])
)

# Determine risk level
risk_scores = risk_scores.withColumn(
    "risk_level",
    when(col("risk_score") <= THRESHOLD_LOW, "Low")
    .when(col("risk_score") <= THRESHOLD_HIGH, "Medium")
    .otherwise("High")
)

# Determine trend (simplified - would need historical data)
risk_scores = risk_scores.withColumn(
    "trend_direction",
    when(col("failure_rate") > 15, "degrading")
    .when(col("failure_rate") < 8, "improving")
    .otherwise("stable")
)

display(risk_scores.select(
    "engagement_id", "customer_name", "risk_score", "risk_level", "trend_direction",
    "job_failure_score", "activity_recency_score", "sa_confidence_score_factor", 
    "schedule_score", "duration_score"
))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Contributing Factors JSON

# COMMAND ----------

from pyspark.sql.functions import struct, to_json, array

# Create contributing factors as JSON
risk_with_factors = risk_scores.withColumn(
    "contributing_factors",
    to_json(array(
        struct(
            lit("Job Failure Rate").alias("factor_name"),
            col("failure_rate").alias("factor_value"),
            lit(WEIGHTS["job_failure_rate"]).alias("weight"),
            when(col("job_failure_score") > 50, "negative")
                .when(col("job_failure_score") < 30, "positive")
                .otherwise("neutral").alias("impact"),
            concat(lit("Failure rate: "), round(col("failure_rate"), 1), lit("%")).alias("description")
        ),
        struct(
            lit("Activity Recency").alias("factor_name"),
            col("days_since_activity").cast("double").alias("factor_value"),
            lit(WEIGHTS["activity_recency"]).alias("weight"),
            when(col("activity_recency_score") > 50, "negative")
                .when(col("activity_recency_score") < 30, "positive")
                .otherwise("neutral").alias("impact"),
            concat(lit("Days since activity: "), col("days_since_activity")).alias("description")
        ),
        struct(
            lit("SA Confidence").alias("factor_name"),
            col("sa_confidence_score").cast("double").alias("factor_value"),
            lit(WEIGHTS["sa_confidence"]).alias("weight"),
            when(col("sa_confidence_score_factor") > 50, "negative")
                .when(col("sa_confidence_score_factor") < 30, "positive")
                .otherwise("neutral").alias("impact"),
            concat(lit("SA confidence: "), col("sa_confidence_score"), lit("/5")).alias("description")
        ),
        struct(
            lit("Schedule Variance").alias("factor_name"),
            col("progress_pct").alias("factor_value"),
            lit(WEIGHTS["schedule_variance"]).alias("weight"),
            when(col("schedule_score") > 50, "negative")
                .when(col("schedule_score") < 30, "positive")
                .otherwise("neutral").alias("impact"),
            concat(lit("Timeline: "), round(col("progress_pct"), 0), lit("% elapsed")).alias("description")
        ),
        struct(
            lit("Job Duration Trend").alias("factor_name"),
            col("avg_duration").alias("factor_value"),
            lit(WEIGHTS["job_duration_trend"]).alias("weight"),
            when(col("duration_score") > 50, "negative")
                .when(col("duration_score") < 30, "positive")
                .otherwise("neutral").alias("impact"),
            concat(lit("Avg duration: "), round(col("avg_duration"), 1), lit("s")).alias("description")
        )
    ))
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Save Risk Scores

# COMMAND ----------

# Prepare final DataFrame for saving
final_scores = risk_with_factors.select(
    expr("uuid()").alias("score_id"),
    "engagement_id",
    round("risk_score", 2).alias("risk_score"),
    "risk_level",
    "contributing_factors",
    "trend_direction",
    current_timestamp().alias("computed_at")
)

# Write to Delta table
final_scores.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("risk_scores")

print(f"✓ Saved {final_scores.count()} risk scores")
display(spark.table("risk_scores"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Update Metrics

# COMMAND ----------

from pyspark.sql.functions import count, avg as spark_avg

# Calculate aggregate metrics
metrics_row = spark.table("risk_scores").agg(
    count("*").alias("active_engagement_count"),
    sum(when(col("risk_level") == "High", 1).otherwise(0)).alias("high_risk_count"),
    sum(when(col("risk_level") == "Medium", 1).otherwise(0)).alias("medium_risk_count"),
    sum(when(col("risk_level") == "Low", 1).otherwise(0)).alias("low_risk_count"),
    round(spark_avg("risk_score"), 2).alias("avg_risk_score")
).withColumn(
    "metric_id", expr("uuid()")
).withColumn(
    "metric_date", current_date()
).withColumn(
    "ai_coverage_rate", lit(0.0)  # Will be updated after AI explanations
).withColumn(
    "computed_at", current_timestamp()
)

# Reorder columns
metrics_row = metrics_row.select(
    "metric_id", "metric_date", "active_engagement_count",
    "high_risk_count", "medium_risk_count", "low_risk_count",
    "avg_risk_score", "ai_coverage_rate", "computed_at"
)

# Write to Delta table
metrics_row.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("metrics")

print("✓ Updated metrics")
display(spark.table("metrics"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC 
# MAGIC Risk scores have been computed for all engagements:
# MAGIC 
# MAGIC | Risk Level | Description |
# MAGIC |------------|-------------|
# MAGIC | Low (0-35) | On track, minimal concerns |
# MAGIC | Medium (36-65) | Some concerns, monitor closely |
# MAGIC | High (66-100) | Significant risk, action needed |
# MAGIC 
# MAGIC Next: Run `04_ai_explanation_generator` to generate AI explanations.
