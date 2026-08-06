# Data Quality Impact & Recovery Report

## 1. Metrics Comparison Overview

| Metric | Baseline | Corrupted | Repaired | Impact Delta (Baseline -> Corrupted) | Recovery Delta (Corrupted -> Repaired) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Retrieval Hit Rate** | 100.00% | 91.67% | 100.00% | -8.33% | +8.33% |
| **Mean Token F1** | 0.3176 | 0.2626 | 0.3176 | -0.0550 | +0.0550 |
| **Mean Judge Score** | 2.02 | 1.85 | 2.02 | -0.17 | +0.17 |

## 2. Observability & Data Quality Signals

### Corrupted State Signals
- **Quality Checks Passed**: False
- **Total Rows**: 23
- **Null Titles / Short Summaries**: 0 null titles, 2 short summaries
- **Freshness Stale Rows**: 2

### Repaired State Signals
- **Quality Checks Passed**: True
- **Total Rows**: 24
- **Null Titles / Short Summaries**: 0 null titles, 0 short summaries
- **Freshness Stale Rows**: 0

## 3. Findings & Evidence Summary
- Synthetic data corruption significantly degraded model quality and retrieval accuracy.
- Automated Data Quality and Freshness checks successfully flagged anomalies prior to downstream consumption.
- Re-executing ETL cleaning pipeline from immutable raw JSON sources fully restored pipeline accuracy to baseline levels.
