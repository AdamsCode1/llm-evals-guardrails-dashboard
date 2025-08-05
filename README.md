# 🛡️ LLM Evaluation & Guardrails Dashboard

<p align="center">
  <img width="800" alt="Guardrails Dashboard" src="https://github.com/user-attachments/assets/9b1b9a51-47d4-4393-91e3-421b53ff2096" />

</p>

<p align="center">
  <strong>Production-ready LLM evaluation toolkit with CLI tool and real-time monitoring dashboard</strong>
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-demo">Demo</a> •
  <a href="#-technical-highlights">Technical Details</a>
</p>

---

## 🎯 **Project Overview**

This project delivers a comprehensive solution for **LLM safety evaluation and monitoring** in production environments. Built with enterprise-grade reliability and developer experience in mind, it combines a powerful CLI tool with real-time web monitoring.

### **Problem Solved**
- **Safety Monitoring**: Track LLM outputs for toxicity, PII leaks, and policy violations
- **Performance Evaluation**: Measure latency, accuracy, and token usage across models
- **Production Readiness**: Policy-driven guardrails with automated blocking and reporting
- **Local-First**: No external dependencies or API costs - runs entirely on your infrastructure

### **Key Achievements**
- ✅ **Zero-dependency evaluation** - Works completely offline after setup
- ✅ **Enterprise-grade monitoring** - Real-time dashboard with policy enforcement
- ✅ **Production reliability** - Graceful degradation and comprehensive error handling
- ✅ **Developer experience** - Rich CLI with progress bars, colored output, and detailed reports

---

## 🚀 **Features**

### **CLI Evaluation Tool**
- 🏠 **Local-First**: Integrates with Ollama for offline LLM inference
- 📊 **Comprehensive Metrics**: Latency, accuracy, toxicity, PII detection, token counting
- 🛡️ **Policy Enforcement**: Configurable thresholds with automated violation blocking
- 📈 **Rich Reporting**: JSON, CSV, and Markdown outputs with detailed failure analysis
- 🧪 **Extensible Architecture**: Clean provider interface for future LLM integrations

### **Real-Time Dashboard**
- 📱 **Web Interface**: Modern, responsive dashboard for monitoring evaluation results
- 🔄 **Live Updates**: Auto-refreshing metrics and violation tracking
- 📡 **REST APIs**: Programmatic access to evaluation data and statistics
- 🎯 **Production Ready**: Single-file deployment with zero external dependencies

---

## 🏃‍♂️ **Quick Start**

### **Prerequisites**
```bash
# Install Ollama (https://ollama.ai/)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama3

# Verify setup
ollama run llama3 \"Hello world\"
```

### **Installation & Usage**
```bash
# Clone repository
git clone https://github.com/AdamsCode1/llm-evals-guardrails-dashboard.git
cd llm-evals-guardrails-dashboard

# Setup CLI tool
cd llm-evals-cli
python -m venv .venv && source .venv/bin/activate
pip install typer[all] requests pydantic pandas rich tabulate

# Run evaluation
python -m evals.cli run --model llama3 --prompts prompts.csv --policy policy.json

# Start monitoring dashboard
cd ../guardrails-dashboard
python3 dashboard.py
# → Open http://localhost:8080
```

### **Live Dashboard**
The screenshot above shows the dashboard displaying real evaluation data:
- **2 evaluation runs** completed successfully
- **10 total evaluations** across different prompts
- **100% accuracy rate** (all prompts matched expected patterns)
- **4.6s average latency** (typical for local Ollama inference)
- **30% violation rate** (demonstrates safety monitoring in action)

---

## 🏗️ **Architecture**

### **System Design**
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   CLI Tool      │    │   Evaluation     │    │   Dashboard     │
│                 │    │   Pipeline       │    │                 │
│ • Typer CLI     │───▶│ • Provider APIs  │───▶│ • HTTP Server   │
│ • Rich Output   │    │ • Safety Metrics │    │ • REST APIs     │
│ • Progress Bars │    │ • Policy Engine  │    │ • Real-time UI  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   Data Storage   │
                       │                  │
                       │ • JSONL Results  │
                       │ • CSV Reports    │
                       │ • Markdown Docs  │
                       └──────────────────┘
```

### **Core Components**

| Component | Purpose | Technology Stack |
|-----------|---------|------------------|
| **CLI Interface** | User interaction & orchestration | Python, Typer, Rich |
| **Provider Layer** | LLM API integration | HTTP clients, async patterns |
| **Metrics Engine** | Safety & performance analysis | Detoxify, Presidio, regex |
| **Policy Engine** | Threshold enforcement | Pydantic validation |
| **Reporting** | Multi-format output generation | Pandas, tabulate |
| **Dashboard** | Real-time monitoring | HTTP server, responsive HTML |

---

## 🎬 **Demo**

### **CLI Workflow**
```bash
# Environment check
python -m evals.cli check --model llama3
✅ Ollama provider available
✅ Model llama3 accessible
✅ Core dependencies installed

# Run evaluation
python -m evals.cli run --model llama3 --prompts prompts.csv
Evaluating ━━━━━━━━━━━━━━━━━━━━ 100% 5/5 prompts
✅ Evaluation complete: runs/20250805-215941
📊 Results: 5 prompts, 100% accuracy, 1 blocked

# Generate report
python -m evals.cli report runs/20250805-215941
📄 Report generated: runs/20250805-215941/report.md
```

### **Dashboard Features**
- **Real-time metrics**: Live updates from evaluation runs
- **Policy violations**: Track and analyze safety failures
- **Performance monitoring**: Latency and token usage trends
- **Historical data**: Browse past evaluation results

---

## 🔧 **Technical Highlights**

### **Engineering Excellence**
- **Type Safety**: Full Pydantic models with runtime validation
- **Error Handling**: Graceful degradation for optional dependencies
- **Testing**: 34+ unit tests with pytest covering core functionality
- **Code Quality**: Ruff linting and formatting, clean architecture patterns
- **Documentation**: Comprehensive README with examples and troubleshooting

### **Production Features**
- **Dependency Isolation**: Core vs optional feature separation
- **Graceful Degradation**: Works even without advanced safety features
- **Performance Optimization**: Streaming responses and timeout handling
- **Monitoring**: Rich CLI feedback and detailed logging
- **Scalability**: Clean provider interface for multi-LLM support

### **Key Technical Decisions**
1. **Local-First Architecture**: No external API dependencies or costs
2. **Modular Design**: Separation of concerns with clean interfaces
3. **Progressive Enhancement**: Core functionality works, safety features are optional
4. **Developer Experience**: Rich CLI with progress indicators and colored output
5. **Data Portability**: Multiple output formats (JSON, CSV, Markdown)

### **Deployment Options**
- **Development**: Local Python environment with pip
- **Production**: Docker containerization ready
- **CI/CD**: GitHub Actions compatible testing and deployment
- **Enterprise**: Air-gapped environments supported

---

## 📁 **Project Structure**

```
llm-evals-guardrails-dashboard/
├── llm-evals-cli/              # CLI evaluation tool
│   ├── evals/                  # Core Python package
│   │   ├── cli.py             # Typer CLI interface
│   │   ├── providers.py       # LLM provider integrations
│   │   ├── metrics.py         # Safety metrics (toxicity, PII)
│   │   ├── policy.py          # Policy validation engine
│   │   ├── run.py             # Evaluation orchestrator
│   │   └── report.py          # Multi-format reporting
│   ├── tests/                 # Unit test suite (34+ tests)
│   ├── runs/                  # Generated evaluation results
│   ├── prompts.csv            # Sample evaluation prompts
│   ├── policy.json            # Default safety policy
│   └── README.md              # Detailed CLI documentation
└── guardrails-dashboard/       # Web monitoring interface
    ├── dashboard.py           # Single-file HTTP server
    ├── demo.py               # Usage examples
    └── Makefile              # Build automation
```

---

## 🚦 **Usage Examples**

### **Basic Evaluation**
```bash
python -m evals.cli run --model llama3 --prompts prompts.csv
```

### **Custom Policy**
```json
{
  \"max_latency_ms\": 5000,
  \"require_accuracy\": true,
  \"enable_toxicity\": true,
  \"toxicity_threshold\": 0.3,
  \"enable_pii\": true
}
```

### **API Integration**
```bash
# Get evaluation statistics
curl http://localhost:8080/api/stats

# List recent runs
curl http://localhost:8080/api/runs

# Check violations
curl http://localhost:8080/api/violations
```

---

## 🎓 **Learning Outcomes**

This project demonstrates proficiency in:

### **Backend Development**
- **Python Architecture**: Clean package design with proper separation of concerns
- **API Design**: REST endpoints with proper error handling and status codes
- **CLI Development**: Professional command-line tools with rich user experience
- **Data Processing**: Pandas integration for CSV/JSONL data handling

### **DevOps & Reliability**
- **Dependency Management**: Graceful degradation and optional feature handling
- **Testing Strategy**: Comprehensive unit test coverage with pytest
- **Error Handling**: Production-grade exception management
- **Documentation**: Professional README with setup and troubleshooting guides

### **Product Engineering**
- **User Experience**: Progress bars, colored output, and intuitive commands
- **Monitoring**: Real-time dashboards with auto-refresh capabilities
- **Configuration**: JSON-based policy management with validation
- **Scalability**: Extensible provider interface for future enhancements

---

## 📊 **Performance Metrics**

| Metric | Value | Description |
|--------|-------|-------------|
| **Test Coverage** | 34+ tests | Comprehensive unit test suite |
| **Response Time** | ~4.6s avg | Local inference with Ollama |
| **Accuracy Rate** | 100% | Regex pattern matching validation |
| **Safety Detection** | 30% violation rate | Policy-based blocking |
| **Dependencies** | Minimal core | 6 core packages, optional safety features |

---

## 🤝 **Contributing**

This project welcomes contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Run** tests: `pytest -q`
4. **Commit** changes: `git commit -m 'Add amazing feature'`
5. **Push** to branch: `git push origin feature/amazing-feature`
6. **Submit** a Pull Request

---

## 📄 **License**

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🔗 **Links**

- **Live Demo**: [Dashboard Screenshot](#-project-overview)
- **Documentation**: [CLI README](llm-evals-cli/README.md)
- **Technical Details**: [Engineering Guide](docs/ENGINEERING.md)
- **Metrics Framework**: [Evaluation Metrics](docs/METRICS.md)
- **Issues**: [GitHub Issues](https://github.com/AdamsCode1/llm-evals-guardrails-dashboard/issues)
- **Ollama**: [https://ollama.ai/](https://ollama.ai/)

---

<p align=\"center\">
  <strong>Built with ❤️ for production LLM safety and monitoring</strong>
</p>

<p align=\"center\">
  No external APIs • No subscription costs • Local-first architecture
</p>
