# Sample Data Files

This folder contains sample CSV files you can use to test the Risk Assessment Tool's data import feature.

## Files

### `sample_engagements.csv`
A ready-to-use engagement file with 6 sample customers across different industries.

## How to Use

1. Open the web app at http://localhost:3000
2. Navigate to **Import Data** in the header navigation
3. Either:
   - Click "Upload & Process" and select `sample_engagements.csv` from this folder, or
   - Drag and drop the file onto the upload area
4. The system will automatically:
   - Create engagement records
   - Generate platform activity signals
   - Calculate risk scores
   - Create AI-powered explanations

## CSV Format

| Column | Required | Description |
|--------|----------|-------------|
| `customer_name` | Yes | Company name |
| `industry` | Yes | Technology, Healthcare, Financial Services, Retail, Manufacturing, or Energy |
| `start_date` | Yes | YYYY-MM-DD format |
| `target_completion_date` | Yes | YYYY-MM-DD format |
| `scope_size` | Yes | small, medium, or large |
| `sa_assigned` | Yes | Solution Architect name |
| `sa_confidence_score` | Yes | 1-5 (1=low, 5=high confidence) |

## Creating Your Own Data

Copy `sample_engagements.csv` and modify it with your own engagement data, or use it as a reference for the expected format.
