# Databricks notebook source
# MAGIC %md
# MAGIC # PS Risk Assessment Tool - Generate Sample Data
# MAGIC 
# MAGIC This notebook populates the Delta tables with sample engagement data
# MAGIC for demonstration purposes.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

from pyspark.sql.functions import *
from pyspark.sql.types import *
from datetime import datetime, timedelta
import random
import uuid

# Configuration
CATALOG = "main"
SCHEMA = "ps_risk_assessment"

spark.sql(f"USE {CATALOG}.{SCHEMA}")
print(f"Using schema: {CATALOG}.{SCHEMA}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Generate Engagements

# COMMAND ----------

# Sample engagement data
today = datetime.now().date()

sample_engagements = [
    {
        "engagement_id": "eng-001",
        "customer_name": "Acme Financial Services",
        "industry": "Financial Services",
        "start_date": today - timedelta(days=60),
        "target_completion_date": today + timedelta(days=30),
        "scope_size": "large",
        "sa_assigned": "Sarah Chen",
        "sa_confidence_score": 2,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    },
    {
        "engagement_id": "eng-002",
        "customer_name": "TechCorp ML Platform",
        "industry": "Technology",
        "start_date": today - timedelta(days=30),
        "target_completion_date": today + timedelta(days=60),
        "scope_size": "medium",
        "sa_assigned": "Marcus Johnson",
        "sa_confidence_score": 3,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    },
    {
        "engagement_id": "eng-003",
        "customer_name": "HealthFirst Analytics",
        "industry": "Healthcare",
        "start_date": today - timedelta(days=15),
        "target_completion_date": today + timedelta(days=75),
        "scope_size": "small",
        "sa_assigned": "Emily Rodriguez",
        "sa_confidence_score": 5,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    },
    {
        "engagement_id": "eng-004",
        "customer_name": "RetailMax Data Lakehouse",
        "industry": "Retail",
        "start_date": today - timedelta(days=45),
        "target_completion_date": today + timedelta(days=45),
        "scope_size": "large",
        "sa_assigned": "David Kim",
        "sa_confidence_score": 3,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    },
    {
        "engagement_id": "eng-005",
        "customer_name": "EnergyGrid IoT Pipeline",
        "industry": "Energy",
        "start_date": today - timedelta(days=75),
        "target_completion_date": today + timedelta(days=15),
        "scope_size": "medium",
        "sa_assigned": "Lisa Wang",
        "sa_confidence_score": 2,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    },
]

# Convert to DataFrame and write
engagements_df = spark.createDataFrame(sample_engagements)

engagements_df.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("engagements")

print(f"✓ Inserted {len(sample_engagements)} engagements")
display(spark.table("engagements"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Generate Platform Signals

# COMMAND ----------

# Signal profiles for different risk scenarios
signal_profiles = {
    "eng-001": {"failure_rate": 0.25, "duration_trend": 1.4, "activity_gap": 5},
    "eng-002": {"failure_rate": 0.12, "duration_trend": 1.1, "activity_gap": 2},
    "eng-003": {"failure_rate": 0.05, "duration_trend": 0.9, "activity_gap": 0},
    "eng-004": {"failure_rate": 0.08, "duration_trend": 1.2, "activity_gap": 1},
    "eng-005": {"failure_rate": 0.30, "duration_trend": 1.5, "activity_gap": 8},
}

signals_data = []

for eng_id, profile in signal_profiles.items():
    base_duration = 120.0
    
    for i in range(14):  # 2 weeks of data
        signal_date = today - timedelta(days=13-i)
        
        # Calculate metrics based on profile
        total_jobs = random.randint(10, 30)
        failures = int(total_jobs * profile["failure_rate"] * random.uniform(0.7, 1.3))
        successes = total_jobs - failures
        
        # Duration increases over time for degrading engagements
        duration_factor = 1 + (i / 14) * (profile["duration_trend"] - 1)
        avg_duration = base_duration * duration_factor * random.uniform(0.9, 1.1)
        
        # Activity timestamp
        if i >= 14 - profile["activity_gap"]:
            last_activity = None
        else:
            last_activity = datetime.combine(
                signal_date,
                datetime.min.time()
            ) + timedelta(hours=random.randint(8, 18))
        
        signals_data.append({
            "signal_id": str(uuid.uuid4()),
            "engagement_id": eng_id,
            "signal_date": signal_date,
            "job_success_count": successes,
            "job_failure_count": failures,
            "avg_job_duration_seconds": round(avg_duration, 2),
            "notebook_execution_count": random.randint(5, 25),
            "sql_query_count": random.randint(20, 100),
            "last_activity_timestamp": last_activity,
            "collected_at": datetime.now(),
        })

# Convert to DataFrame and write
signals_df = spark.createDataFrame(signals_data)

signals_df.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("platform_signals")

print(f"✓ Inserted {len(signals_data)} platform signals")
display(spark.table("platform_signals").limit(10))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify Data

# COMMAND ----------

# Count records in each table
print("\nTable Record Counts:")
print("-" * 40)
print(f"engagements: {spark.table('engagements').count()}")
print(f"platform_signals: {spark.table('platform_signals').count()}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC 
# MAGIC Sample data has been generated:
# MAGIC 
# MAGIC | Engagement | Industry | Scope | Risk Profile |
# MAGIC |------------|----------|-------|--------------|
# MAGIC | Acme Financial | Financial Services | Large | High Risk |
# MAGIC | TechCorp ML | Technology | Medium | Medium Risk |
# MAGIC | HealthFirst | Healthcare | Small | Low Risk |
# MAGIC | RetailMax | Retail | Large | Medium Risk |
# MAGIC | EnergyGrid | Energy | Medium | High Risk |
# MAGIC 
# MAGIC Next: Run `03_risk_scoring_engine` to compute risk scores.
