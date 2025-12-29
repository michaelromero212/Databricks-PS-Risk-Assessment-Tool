# Databricks PS Risk Assessment Tool

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Databricks](https://img.shields.io/badge/Databricks-Free%20Edition-orange)
![License](https://img.shields.io/badge/license-Internal-green)

**Surface early delivery risk across customer engagements using Databricks-native telemetry and AI-powered insights**

</div>

---

## Overview

The PS Risk Assessment Tool is an internal POC designed for Databricks Professional Services teams to:

- **Identify delivery risk early** through platform signal analysis
- **Get AI-powered explanations** of risk factors and mitigation suggestions
- **Track engagement health** across your entire portfolio
- **Enable data-driven decisions** with transparent, auditable scoring

This tool augments human judgment—it does not replace it.

## Key Features

| Feature | Description |
|---------|-------------|
| 📊 **Risk Scoring Engine** | Rule-based heuristics with weighted signal aggregation |
| 🤖 **AI Explanations** | Hugging Face model for plain-English risk explanations |
| 🚀 **Program Impact** | Track ROI, time saved, and adoption for PS Leadership |
| ☁️ **Databricks Native** | Live Unity Catalog browsing and SDK integration |
| 💡 **Smart Recs** | Actionable delivery advice for PS practitioners |
| 📈 **Interactive Dashboards** | React UI + Dash/Plotly visualizations |
| 🔒 **Transparency** | Full AI model metadata visibility |
| ♿ **Accessibility** | WCAG AA compliant, color-blind safe |

## Architecture

For a detailed technical breakdown, see the [System Architecture](file:///Users/michaelromero/Documents/Databricks-PS-Risk-Assessment-Tool/docs/ARCHITECTURE.md).

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Frontend Layer                               │
│  ┌─────────────────────┐    ┌──────────────────────────────────┐   │
│  │   React SPA (3000)  │    │   Dash Dashboard (8050)          │   │
│  │   - Overview        │    │   - Risk Distribution            │   │
│  │   - Detail View     │    │   - Trend Analysis               │   │
│  │   - AI Panel        │    │   - Metrics                      │   │
│  └──────────┬──────────┘    └───────────────┬──────────────────┘   │
└─────────────┼───────────────────────────────┼──────────────────────┘
              │                               │
              ▼                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Backend API (5000)                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐ │
│  │  Engagements    │  │  Risk Engine    │  │   AI Explainer      │ │
│  │  API           │  │  Service        │  │   (Hugging Face)    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────────┘ │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Databricks (Delta Lake)                         │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────────┐   │
│  │ Engagements│ │  Signals   │ │Risk Scores │ │AI Explanations │   │
│  └────────────┘ └────────────┘ └────────────┘ └────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Databricks workspace (Free Edition compatible)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd Databricks-PS-Risk-Assessment-Tool

# Run setup script
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### Configuration

1. Copy the environment template:
   ```bash
   cp .env.template .env
   ```

2. Edit `.env` with your credentials:
   ```bash
   DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
   DATABRICKS_TOKEN=your-personal-access-token
   ```

### Running the Application

**Terminal 1 - Backend API:**
```bash
source venv/bin/activate
python -m backend.app
```

**Terminal 2 - React Frontend:**
```bash
cd frontend
npm start
```

**Terminal 3 - Dash Dashboard:**
```bash
source venv/bin/activate
python dashboards/app.py
```

### Access Points

| Service | URL |
|---------|-----|
| React UI | http://localhost:3000 |
| Dash Dashboard | http://localhost:8050 |
| Backend API | http://localhost:5000 |

## Risk Scoring

### Scoring Weights

| Signal | Weight | Description |
|--------|--------|-------------|
| Job Failure Rate | 25% | Percentage of failed jobs |
| Job Duration Trend | 15% | Increasing execution times |
| Activity Recency | 20% | Days since last activity |
| SA Confidence | 20% | Self-reported confidence (1-5) |
| Schedule Variance | 20% | Timeline progress |

### Risk Levels

| Level | Score Range | Action |
|-------|-------------|--------|
| 🟢 Low | 0-35 | Continue monitoring |
| 🟡 Medium | 36-65 | Review and address concerns |
| 🔴 High | 66-100 | Immediate intervention needed |

## AI Transparency

The tool uses **Hugging Face models** for generating risk explanations:

| Property | Value |
|----------|-------|
| Model Name | google/flan-t5-base |
| Provider | Hugging Face |
| Purpose | Risk explanation and recommendation |

All AI outputs display:
- Model name and provider
- Generation status (Generated / Cached / Unavailable)
- Timestamp of generation

## Project Structure

```
Databricks-PS-Risk-Assessment-Tool/
├── backend/                    # Flask API
│   ├── app.py                  # Application entry point
│   ├── config.py               # Configuration loader
│   ├── routes/                 # API endpoints
│   ├── services/               # Business logic
│   │   ├── risk_engine.py      # Risk scoring
│   │   ├── ai_explainer.py     # AI integration
│   │   └── data_store.py       # Demo data
│   └── models/                 # Pydantic schemas
├── frontend/                   # React SPA
│   ├── src/
│   │   ├── components/         # Reusable components
│   │   ├── pages/              # Page components
│   │   └── index.css           # Design system
├── dashboards/                 # Dash + Plotly
│   ├── app.py                  # Dashboard application
│   ├── layouts/                # Layout components
│   └── components/             # Chart components
├── databricks/                 # Databricks artifacts
│   ├── notebooks/              # PySpark notebooks
│   ├── sql/                    # SQL scripts
│   └── jobs/                   # Job configurations
└── scripts/                    # Utility scripts
```

## Databricks Notebooks

| Notebook | Purpose |
|----------|---------|
| `01_create_delta_tables.py` | Create Delta Lake tables |
| `02_generate_sample_data.py` | Populate with demo data |
| `03_risk_scoring_engine.py` | Compute risk scores |
| `04_ai_explanation_generator.py` | Generate AI explanations |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/engagements` | GET | List all engagements |
| `/api/engagements/{id}` | GET | Get engagement details |
| `/api/engagements/{id}/risk` | GET | Get risk score |
| `/api/engagements/{id}/explanation` | GET | Get AI explanation |
| `/api/metrics` | GET | Get PS metrics |
| `/api/metrics/ai-status` | GET | Get AI model status |

## Demo Scenario

1. **View Overview** - See all engagements with risk levels
2. **Filter High Risk** - Focus on critical engagements
3. **Drill Into Details** - Click an engagement for full analysis
4. **Review AI Explanation** - Understand risk factors
5. **Check Mitigations** - Get actionable recommendations
6. **Verify AI Metadata** - Confirm model transparency

## Security

- ✅ No secrets committed to git
- ✅ Environment variables for all sensitive data
- ✅ `.env` excluded via `.gitignore`
- ✅ Template provided for configuration

## Accessibility

- ✅ Color-blind safe palette
- ✅ High contrast ratios (WCAG AA)
- ✅ Keyboard navigation
- ✅ Screen reader compatible
- ✅ Reduced motion support

## License

Internal use only - Databricks Professional Services

---

<div align="center">

**Built for Databricks Professional Services**

</div>
