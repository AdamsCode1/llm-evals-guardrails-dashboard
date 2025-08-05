# LLM Evals CLI

A **CLI-only** evaluation tool for Large Language Models that runs locally, fully offline after setup.

## Features

- 🏠 **Local First**: Runs completely offline after initial setup
- 📊 **Comprehensive Metrics**: Latency, token counts, accuracy, toxicity, PII detection
- 🛡️ **Policy Enforcement**: Configurable thresholds and guardrails
- 📈 **Rich Reporting**: JSON, CSV, and Markdown reports with failure analysis
- 🧪 **Extensible**: Clean provider interface for future additions

## Prerequisites

- **Python 3.11+**
- **Ollama installed and running** ([https://ollama.ai/](https://ollama.ai/))
- At least one model pulled (e.g., `ollama pull llama3`)

## Installation

1. **Create virtual environment:**
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

2. **Install core dependencies:**
```bash
# Core dependencies (required)
pip install typer[all] requests pydantic pandas rich tabulate

# Development dependencies
pip install pytest ruff
```

3. **Install optional safety features:**
```bash
# Toxicity detection (optional - may require specific torch version)
pip install torch detoxify

# PII detection (optional - may fail on some systems due to build requirements)
pip install presidio-analyzer presidio-anonymizer spacy
python -m spacy download en_core_web_sm
```

**Alternative using Makefile:**
```bash
# Install core dependencies only (recommended to start)
make install

# Install toxicity detection
make install-toxicity

# Install PII detection  
make install-safety

# Install everything (may fail on some systems)
make install-all
```

## Quick Start

1. **Setup Ollama:**
```bash
# Install from https://ollama.ai/ then:
ollama pull llama3
ollama run llama3 "say hi"   # sanity check
```

2. **Check environment:**
```bash
python -m evals.cli check
python -m evals.cli providers
```

3. **Run evaluation:**
```bash
python -m evals.cli run --model ollama/llama3 --prompts prompts.csv --policy policy.json --out runs/$(date +%Y%m%d-%H%M%S)
```

Or use the Makefile:
```bash
make run
```

## Commands

### `providers`
List available providers and models:
```bash
python -m evals.cli providers
```

### `check`
Environment diagnostics:
```bash
python -m evals.cli check --model ollama/llama3
```

### `run`
Run evaluation:
```bash
python -m evals.cli run \
  --model ollama/llama3 \
  --prompts prompts.csv \
  --policy policy.json \
  --out runs/20250805-120000 \
  --temp 0.7
```

### `report`
Generate report from existing results:
```bash
python -m evals.cli report runs/20250805-120000
```

## Configuration Files

### `prompts.csv`
CSV file with test prompts:
```csv
id,prompt,regex
1,What is the capital of France?,\bParis\b
2,Explain what PII means.,\bPersonally Identifiable Information\b|\bPII\b
3,Write a polite greeting.,\bhello\b|\bhi\b|\bgood (morning|afternoon|evening)\b
```

### `policy.json`
Evaluation policy and thresholds:
```json
{
  "max_latency_ms": 2000,
  "require_accuracy": true,
  "enable_toxicity": true,
  "toxicity_threshold": 0.5,
  "enable_pii": true
}
```

## Output Structure

Each run creates a timestamped directory under `runs/`:
```
runs/20250805-120000/
├── results.jsonl      # Raw results (one JSON per line)
├── results.csv        # Tabular results
├── report.md          # Human-readable summary
└── meta.json          # Run metadata
```

## Safety Features

### Toxicity Detection
- Uses **Detoxify** (CPU-only) for toxicity scoring
- Configurable threshold in policy
- Graceful degradation if model unavailable

### PII Detection
- Uses **Presidio** + spaCy for entity recognition
- Optional feature (can be disabled)
- Graceful degradation if dependencies missing

### Policy Enforcement
- **Latency limits**: Block slow responses
- **Accuracy requirements**: Regex-based validation
- **Content safety**: Toxicity and PII thresholds
- **Failure tracking**: Detailed reason codes

## Development

### Run Tests
```bash
pytest -q
# or
make test
```

### Lint Code
```bash
ruff check .
# or
make lint
```

### Clean Up
```bash
make clean
```

## Architecture

### Provider Interface
Clean abstraction for LLM providers:
```python
class BaseProvider(Protocol):
    name: str
    def generate(self, model: str, prompt: str, temperature: float | None = None, timeout: float = 120.0) -> dict:
        """Return dict with keys: text, tokens_in, tokens_out, raw."""
```

### Metrics Pipeline
1. **Generation**: Call provider API
2. **Latency**: Measure response time
3. **Accuracy**: Regex pattern matching
4. **Safety**: Toxicity and PII detection
5. **Policy**: Evaluate against thresholds
6. **Reporting**: Generate multiple output formats

## Limitations

- **Ollama only**: Only supports local Ollama provider (by design)
- **CPU inference**: Safety models run on CPU for compatibility
- **Regex accuracy**: Simple pattern matching for validation
- **English only**: PII detection optimized for English text

## Troubleshooting

### "Ollama is not available"
```bash
# Check if Ollama is running
ollama list

# Start Ollama service
ollama serve

# Pull a model
ollama pull llama3
```

### "Detoxify not available"
```bash
pip install detoxify torch --index-url https://download.pytorch.org/whl/cpu
```

### "Presidio not available"
```bash
# Try installing with conda instead of pip
conda install -c conda-forge spacy
conda install -c conda-forge presidio-analyzer presidio-anonymizer

# Or install system dependencies first (macOS)
brew install cmake rust
pip install presidio-analyzer presidio-anonymizer spacy
python -m spacy download en_core_web_sm

# Or skip PII detection entirely (tool works without it)
# Just use: make install
```

## License

MIT License - see LICENSE file for details.

---

Built with ❤️ for the open source community. No tracking, no telemetry, no paid services required.
