# Analysis Integration in Hospital AI Chatbot

## Overview

The Hospital AI chatbot now supports direct integration with analysis result files. When users include `@analysis` in their message, the chatbot will reference the analysis result files instead of querying the database directly.

## How It Works

### 1. Analysis Query Detection
- The chatbot detects `@analysis` in user messages
- When detected, it skips database queries and loads relevant analysis files
- The analysis data is formatted and passed to the AI model for interpretation

### 2. Available Analyses

| Analysis Type | File | Description |
|---------------|------|-------------|
| **Staffing Forecast** | `staffing_result.json` | Projects nursing head-count requirements over 3 days |
| **Average Length-of-Stay** | `average_los_result.json` | Computes mean stay duration by ward |
| **Tool Utilization** | `tool_utilisation_result.json` | Ranks medical devices by usage percentage |
| **Inventory Expiry** | `inventory_expiry_result.json` | Lists items expiring within 90 days |
| **Staff Load** | `staff_load_result.json` | Shows patient assignments per staff member |
| **Bed Census Forecast** | `census_forecast_result.json` | Forecasts occupied beds for 3 days |
| **Elective vs Emergency** | `admission_split_result.json` | Splits admissions by type and time |
| **LOS Prediction** | `los_prediction_result.json` | Predicts patient stay duration |
| **Burn Rate Forecast** | `burn_rate_result.json` | Predicts consumable usage over 7 days |

### 3. Usage Examples

#### General Analysis Question
```
@analysis What is our current hospital status?
```
*Returns overview from all available analyses*

#### Specific Analysis Questions
```
@analysis How is our staffing situation?
```
*Returns staffing forecast and current staff numbers*

```
@analysis What tools need attention?
```
*Returns tool utilization analysis*

```
@analysis Which inventory items are expiring soon?
```
*Returns inventory expiry analysis*

```
@analysis What is the average length of stay by ward?
```
*Returns ALOS analysis*

```
@analysis How loaded are our staff members?
```
*Returns staff workload analysis*

```
@analysis What's our bed forecast for the next few days?
```
*Returns bed census forecast*

#### Keywords That Trigger Specific Analyses

**Staffing Analysis:**
- staffing, staff needs, nurse, doctor, workforce

**Staff Load Analysis:**
- staff load, workload, patient assignments, overworked

**Length of Stay Analysis:**
- length of stay, los, alos, average stay, discharge

**Tool Utilization Analysis:**
- tool utilization, equipment, devices, medical tools

**Inventory Expiry Analysis:**
- expiry, inventory, blood units, expired, medical supplies

**Census Forecast Analysis:**
- bed census, bed forecast, bed occupancy, capacity

**Admission Split Analysis:**
- admission, elective, emergency, planned, urgent

**LOS Prediction Analysis:**
- los prediction, stay prediction, discharge prediction

**Burn Rate Analysis:**
- burn rate, consumption, usage rate, supply consumption

## Response Format

The AI provides structured responses with:

1. **Direct Answer** - Addresses the specific question
2. **Key Insights** - Highlights important findings
3. **Medical Context** - Professional interpretation
4. **Recommendations** - Actionable insights

All numerical data is formatted with LaTeX for proper display.

## Implementation Details

### File Structure
```
backend/result/
├── staffing_result.json
├── staff_load_result.json
├── average_los_result.json
├── tool_utilisation_result.json
├── inventory_expiry_result.json
├── census_forecast_result.json
├── admission_split_result.json
├── los_prediction_result.json
└── burn_rate_result.json
```

### Analysis Service
- **Location**: `src/services/analysis_service.py`
- **Main Class**: `AnalysisService`
- **Key Methods**:
  - `is_analysis_query()` - Detects @analysis in messages
  - `determine_relevant_analyses()` - Maps questions to files
  - `process_analysis_query()` - Formats data for AI

### Integration Points
- **Main Handler**: `src/components/interface.py` in `handle_ai_response()`
- **Priority**: Analysis queries are processed before database queries
- **Token Allocation**: Increased to 2500 tokens for complex analysis data

## Benefits

1. **Faster Responses** - No database queries needed
2. **Rich Context** - Pre-computed analysis data
3. **Structured Insights** - Professional medical interpretation
4. **Current Data** - Based on latest analysis runs
5. **Smart Detection** - Automatic file selection based on keywords

## Notes

- Analysis files are cached for 5 minutes by the JSON data loader
- If `@analysis` is in the message, database queries are completely skipped
- The system gracefully falls back to regular responses if analysis files are unavailable
- All responses include medical disclaimers as appropriate 