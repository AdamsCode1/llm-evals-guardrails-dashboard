# 📊 Evaluation Metrics and Safety Framework

This document outlines the evaluation metrics, safety features, and policy framework implemented in the LLM Evals CLI.

## 🎯 Core Metrics

### Performance Metrics
- **Latency**: Response time from request to completion (milliseconds)
- **Token Usage**: Input/output token counts with cost estimation
- **Throughput**: Evaluations per second
- **Availability**: Provider uptime and model accessibility

### Quality Metrics
- **Accuracy**: Regex pattern matching against expected outputs
- **Coherence**: Response relevance to prompt (manual review required)
- **Consistency**: Reproducibility across multiple runs

## 🛡️ Safety Features

### Toxicity Detection
- **Model**: Detoxify (Perspective API alternative)
- **Threshold**: Configurable 0.0-1.0 scale
- **Categories**: Toxic, severe toxic, obscene, threat, insult, identity hate
- **Fallback**: Graceful degradation if model unavailable

### PII Detection
- **Engine**: Microsoft Presidio + spaCy NLP
- **Entities**: Names, emails, phone numbers, addresses, SSNs, credit cards
- **Languages**: English (extensible to other languages)
- **Anonymization**: Optional redaction of detected PII

### Content Filtering
- **Policy-based blocking**: Configurable thresholds per metric
- **Reason tracking**: Detailed failure classification
- **Audit trail**: Complete evaluation history

## 📋 Policy Configuration

### Policy Structure
```json
{
  "max_latency_ms": 5000,
  "require_accuracy": true,
  "enable_toxicity": true,
  "toxicity_threshold": 0.3,
  "enable_pii": true
}
```

### Policy Enforcement
- **Blocking**: Automatic filtering of violations
- **Logging**: Comprehensive violation tracking
- **Reporting**: Policy compliance summaries
- **Alerts**: Threshold breach notifications

## 📈 Reporting Framework

### Output Formats
1. **JSONL**: Machine-readable evaluation results
2. **CSV**: Tabular data for analysis
3. **Markdown**: Human-readable reports
4. **Dashboard**: Real-time web monitoring

### Report Contents
- Executive summary with key metrics
- Detailed evaluation results
- Policy violation analysis
- Performance trend analysis
- Recommendations for improvement

## 🔧 Implementation Details

### Graceful Degradation
- Core functionality works without optional dependencies
- Safety features return `null` if models unavailable
- Clear error messages guide dependency installation

### Error Handling
- Comprehensive exception catching
- Detailed error logging
- Retry mechanisms for transient failures
- Timeout protection for hanging requests

### Performance Optimization
- Async evaluation pipeline
- Batch processing capabilities
- Memory-efficient streaming
- Configurable concurrency limits

---

*This framework ensures comprehensive evaluation while maintaining production reliability and safety standards.*
