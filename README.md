# LLM Red Team Toolkit

A comprehensive Python CLI tool for automated security testing of LLM-based applications. Conducts systematic prompt injection, jailbreak, data exfiltration, and tool-abuse attacks to identify vulnerabilities before deployment.

## Features

- **Automated Attack Orchestration**: Run sophisticated security tests against any LLM endpoint
- **30+ Real Payloads**: Prompt injection, jailbreak attempts, data exfiltration, and tool-abuse variants
- **Multi-Backend Support**: OpenAI, Anthropic, Ollama, and generic HTTP endpoints
- **Configurable Scenarios**: Define custom attack sequences in YAML
- **Concurrent Execution**: Async-based attack parallelization with rate limiting
- **Rich Reporting**: JSON and HTML reports with severity ratings and confidence scores
- **Type-Safe & Tested**: Full type hints, comprehensive test coverage, production-quality code

## Quick Start

### Installation

```bash
git clone https://github.com/bastiaan365/llm-red-team-toolkit.git
cd llm-red-team-toolkit
pip install -e .
```

### Basic Usage

```bash
# List available attacks
redteam list-attacks

# Validate a scenario file
redteam validate-scenario scenarios/example_scan.yaml

# Run a scan against an LLM
redteam scan scenarios/example_scan.yaml --output report.json

# Generate HTML report from JSON results
redteam report report.json --format html --output report.html
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    CLI Interface                        │
│                   (Click-based)                         │
└────────────┬────────────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────────────┐
│                  Engine (Orchestrator)                  │
│  ├─ Scenario parsing & validation                      │
│  ├─ Attack scheduling & concurrency control            │
│  ├─ Rate limiting & retry logic                        │
│  └─ Results aggregation                                │
└────────────┬────────────────────────────────────────────┘
             │
      ┌──────┴──────┬──────────┬────────────┐
      │             │          │            │
┌─────▼──┐  ┌──────▼─┐  ┌────▼───┐  ┌────▼────┐
│ Target │  │ Attacks│  │Payloads│  │ Reports │
│ Manager│  │ Module │  │Library │  │Generator│
└────────┘  └────────┘  └────────┘  └─────────┘
```

### Core Components

- **`target.py`**: Abstraction layer for different LLM endpoints (OpenAI, Anthropic, Ollama, HTTP)
- **`engine.py`**: Main orchestration engine handling scenario execution, concurrency, and result aggregation
- **`base.py`**: Base attack class with severity/confidence scoring
- **`attacks/`**: Individual attack implementations (prompt injection, jailbreaks, data exfiltration, tool abuse)
- **`payloads/library.py`**: 30+ real attack payloads
- **`report.py`**: JSON and HTML report generation with statistics

## Configuration (YAML Scenarios)

Define custom attack sequences:

```yaml
name: "Basic Security Scan"
description: "Test common vulnerabilities"
target:
  backend: openai
  model: gpt-4
  api_key: ${OPENAI_API_KEY}
  endpoint: https://api.openai.com/v1/chat/completions

attacks:
  - name: direct_prompt_injection
    payloads: 5
    severity: critical
  - name: roleplay_jailbreak
    payloads: 3
    severity: high
  - name: data_exfiltration
    enabled: true

options:
  concurrency: 5
  timeout: 30
  rate_limit: 10  # requests per second
  retry_count: 2
```

## Attack Types

### Prompt Injection
- Direct injection: Appending malicious instructions
- Indirect injection: Hidden in system context
- Role confusion: Conflicting role definitions
- Token smuggling: Unicode and encoding tricks

### Jailbreaks
- DAN (Do Anything Now) variants
- Roleplay-based circumvention
- Hypothetical scenario jailbreaks
- Token smuggling and encoding obfuscation

### Data Exfiltration
- Prompt manipulation to leak training data
- Context window extraction
- System prompt recovery attempts

### Tool Abuse
- Boundary testing for connected tools
- Privilege escalation attempts
- Resource exhaustion patterns

## Usage Examples

### Run with custom scenario
```bash
redteam scan my_scenario.yaml --output results.json --concurrency 10
```

### Generate different report formats
```bash
redteam report results.json --format html --output report.html
redteam report results.json --format json --output report.json
```

### Dry-run mode (validate without executing)
```bash
redteam scan scenarios/example.yaml --dry-run
```

### Target different backends
```bash
# OpenAI
redteam scan scenario.yaml --backend openai --model gpt-4

# Anthropic
redteam scan scenario.yaml --backend anthropic --model claude-3-opus

# Local Ollama
redteam scan scenario.yaml --backend ollama --model llama2:7b

# Generic HTTP endpoint
redteam scan scenario.yaml --backend http --endpoint http://localhost:8000/api/chat
```

## Testing

Run the test suite:

```bash
pytest tests/ -v
pytest tests/ --cov=redteam --cov-report=html
```

Tests include:
- Engine orchestration and concurrency control
- Attack payload execution and validation
- Target endpoint abstraction
- Report generation
- Scenario parsing

## Project Structure

```
llm-red-team-toolkit/
├── README.md
├── setup.py
├── pyproject.toml
├── requirements.txt
├── .gitignore
├── LICENSE
├── redteam/
│   ├── __init__.py
│   ├── cli.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── engine.py
│   │   ├── target.py
│   │   └── report.py
│   ├── attacks/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── prompt_injection.py
│   │   ├── jailbreak.py
│   │   ├── data_exfil.py
│   │   └── tool_abuse.py
│   ├── payloads/
│   │   ├── __init__.py
│   │   └── library.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── scenarios/
│   └── example_scan.yaml
└── tests/
    ├── __init__.py
    ├── test_engine.py
    ├── test_attacks.py
    └── test_payloads.py
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Add tests for new functionality
4. Ensure all tests pass (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Setup

```bash
git clone https://github.com/bastiaan365/llm-red-team-toolkit.git
cd llm-red-team-toolkit
pip install -e ".[dev]"
pre-commit install
```

## Security & Responsibility

This toolkit is designed for:
- **Authorized Security Testing**: Only test systems you own or have explicit permission to test
- **Red Team Exercises**: Internal security research and defense improvements
- **Vulnerability Assessment**: Identify and fix weaknesses before deployment

**Do not** use this toolkit for unauthorized access, testing systems without permission, or malicious purposes.

## License

MIT License - See LICENSE file for details

## Citation

If you use this toolkit in your research, please cite:

```bibtex
@software{llm_red_team_toolkit,
  title={LLM Red Team Toolkit: Automated Security Testing for LLM Applications},
  author={Bastiaan Rusch},
  year={2026},
  url={https://github.com/bastiaan365/llm-red-team-toolkit}
}
```

## Support

For issues, feature requests, or questions:
- Open an issue on GitHub
- Check existing documentation
- Review test cases for usage examples

---

**Built with security in mind. Test responsibly.**
