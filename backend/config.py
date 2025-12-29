"""
Configuration loader for Databricks PS Risk Assessment Tool.
Loads settings from environment variables with validation.
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class DatabricksConfig:
    """Databricks workspace configuration."""
    host: str
    token: str
    sql_warehouse_id: str
    
    @classmethod
    def from_env(cls) -> "DatabricksConfig":
        """Load Databricks config from environment variables."""
        host = os.getenv("DATABRICKS_HOST", "")
        token = os.getenv("DATABRICKS_TOKEN", "")
        warehouse_id = os.getenv("DATABRICKS_SQL_WAREHOUSE_ID", "")
        
        return cls(
            host=host,
            token=token,
            sql_warehouse_id=warehouse_id
        )
    
    def is_configured(self) -> bool:
        """Check if Databricks is properly configured."""
        return bool(self.host and self.token)


@dataclass
class HuggingFaceConfig:
    """Hugging Face model configuration."""
    api_key: Optional[str]
    model_name: str = "google/flan-t5-base"
    model_provider: str = "Hugging Face"
    model_purpose: str = "Risk explanation and recommendation generation"
    use_local: bool = True  # Use local model by default (no API key needed)
    
    @classmethod
    def from_env(cls) -> "HuggingFaceConfig":
        """Load Hugging Face config from environment variables."""
        api_key = os.getenv("HUGGINGFACE_API_KEY")
        return cls(
            api_key=api_key,
            use_local=not bool(api_key)  # Use local if no API key
        )


@dataclass
class DeltaTableConfig:
    """Delta Lake table paths configuration."""
    base_path: str
    engagements_table: str
    signals_table: str
    risk_scores_table: str
    explanations_table: str
    metrics_table: str
    
    @classmethod
    def from_env(cls) -> "DeltaTableConfig":
        """Load Delta table config from environment variables."""
        base_path = os.getenv("DELTA_BASE_PATH", "/FileStore/delta/ps_risk_tool")
        return cls(
            base_path=base_path,
            engagements_table=os.getenv("DELTA_ENGAGEMENTS_TABLE", "engagements"),
            signals_table=os.getenv("DELTA_SIGNALS_TABLE", "platform_signals"),
            risk_scores_table=os.getenv("DELTA_RISK_SCORES_TABLE", "risk_scores"),
            explanations_table=os.getenv("DELTA_EXPLANATIONS_TABLE", "ai_explanations"),
            metrics_table=os.getenv("DELTA_METRICS_TABLE", "metrics")
        )
    
    def get_full_path(self, table_name: str) -> str:
        """Get full path for a table."""
        return f"{self.base_path}/{table_name}"


@dataclass
class AppConfig:
    """Application configuration."""
    flask_env: str
    flask_debug: bool
    backend_port: int
    frontend_port: int
    dashboard_port: int
    api_url: str
    
    # Sub-configurations
    databricks: DatabricksConfig
    huggingface: HuggingFaceConfig
    delta_tables: DeltaTableConfig
    
    @classmethod
    def from_env(cls) -> "AppConfig":
        """Load complete application config from environment variables."""
        return cls(
            flask_env=os.getenv("FLASK_ENV", "development"),
            flask_debug=os.getenv("FLASK_DEBUG", "true").lower() == "true",
            backend_port=int(os.getenv("BACKEND_PORT", "5000")),
            frontend_port=int(os.getenv("FRONTEND_PORT", "3000")),
            dashboard_port=int(os.getenv("DASHBOARD_PORT", "8050")),
            api_url=os.getenv("REACT_APP_API_URL", "http://localhost:5000"),
            databricks=DatabricksConfig.from_env(),
            huggingface=HuggingFaceConfig.from_env(),
            delta_tables=DeltaTableConfig.from_env()
        )


# Global configuration instance
config = AppConfig.from_env()


def get_config() -> AppConfig:
    """Get the global configuration instance."""
    return config


def reload_config() -> AppConfig:
    """Reload configuration from environment variables."""
    global config
    load_dotenv(override=True)
    config = AppConfig.from_env()
    return config
