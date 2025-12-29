# Databricks notebook source
# MAGIC %md
# MAGIC # PS Risk Assessment Tool - AI Explanation Generator
# MAGIC 
# MAGIC Generates AI-powered risk explanations using Hugging Face model.

# COMMAND ----------

from pyspark.sql.functions import *
from datetime import datetime
import json
import uuid

# Configuration
CATALOG = "main"
SCHEMA = "ps_risk_assessment"
MODEL_NAME = "google/flan-t5-base"
MODEL_PROVIDER = "Hugging Face"
MODEL_PURPOSE = "Risk explanation and recommendation generation"

spark.sql(f"USE {CATALOG}.{SCHEMA}")

# COMMAND ----------

# Load data
data_df = spark.table("engagements").join(spark.table("risk_scores"), "engagement_id")

# COMMAND ----------

def generate_explanation(row):
    """Generate rule-based explanation for engagement risk."""
    customer = row["customer_name"]
    level = row["risk_level"]
    score = row["risk_score"]
    scope = row["scope_size"]
    industry = row["industry"]
    
    try:
        factors = json.loads(row["contributing_factors"])
        negative_factors = [f for f in factors if f.get("impact") == "negative"]
    except:
        negative_factors = []
    
    if level == "High":
        factor_names = ", ".join([f["factor_name"].lower() for f in negative_factors[:2]]) if negative_factors else "multiple indicators"
        explanation = f"The {customer} engagement is at high risk (score: {score:.0f}/100) due to {factor_names}. This {scope} {industry} project requires immediate attention."
    elif level == "Medium":
        explanation = f"The {customer} engagement shows moderate risk (score: {score:.0f}/100). Some signals warrant monitoring for this {scope} project."
    else:
        explanation = f"The {customer} engagement is progressing well with low risk (score: {score:.0f}/100)."
    
    mitigations = []
    for f in negative_factors[:3]:
        fn = f.get("factor_name", "").lower()
        if "failure" in fn: mitigations.append("Investigate job failures and improve error handling")
        elif "activity" in fn: mitigations.append("Re-engage with customer to resume platform utilization")
        elif "confidence" in fn: mitigations.append("Schedule SA debrief to address concerns")
        elif "schedule" in fn: mitigations.append("Reassess timeline and discuss scope adjustments")
    
    while len(mitigations) < 3:
        mitigations.append("Schedule checkpoint meeting with stakeholders")
    
    return {"explanation": explanation, "mitigations": mitigations[:3]}

# COMMAND ----------

# Generate explanations
rows = data_df.collect()
explanations_data = []

for row in rows:
    result = generate_explanation(row.asDict())
    explanations_data.append({
        "explanation_id": str(uuid.uuid4()),
        "engagement_id": row["engagement_id"],
        "model_name": MODEL_NAME,
        "model_provider": MODEL_PROVIDER,
        "model_purpose": MODEL_PURPOSE,
        "risk_explanation": result["explanation"],
        "mitigation_suggestions": json.dumps(result["mitigations"]),
        "generation_status": "generated_successfully",
        "generated_at": datetime.now(),
        "cached": False,
    })

# Save to Delta
explanations_df = spark.createDataFrame(explanations_data)
explanations_df.write.format("delta").mode("overwrite").saveAsTable("ai_explanations")

print(f"✓ Generated {len(explanations_data)} explanations")
display(spark.table("ai_explanations"))
