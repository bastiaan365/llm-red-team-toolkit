# LLM Red Team Toolkit

Automated security testing CLI for LLM-based applications. Runs prompt injection, jailbreak, data exfiltration, and tool-abuse attacks against any LLM endpoint to find vulnerabilities before someone else does.

I built this because I was doing a lot of manual prompt testing at work and wanted something repeatable. Define your attack scenarios in YAML, point it at an endpoint, and get a structured report back.

## What's included

- **30+ attack payloads** covering prompt injection, jailbreaks, data exfil, and tool abuse
- **Multi-backend support** — OpenAI, Anthropic, Ollama, or any HTTP endpoint
- **YAML scenarios** — define exactly which attacks to run and how
- **Async execution** with rate limiting so you don't get throttled
- **JSON and HTML reports** with severity ratings and confidence scores

## Quick start

```bash
git clone https://github.com/bastiaan365/llm-red-team-toolkit.git
cd llm-red-team-toolkit
pip install -e .
```

### 1. List available attacks

```bash
redteam list-attacks
```

```
Available Attacks:
============================================================

boundary_testing
  Test boundaries and identify safety measure vulnerabilities

context_leakage
  Trick the model into revealing system prompt via context extraction

dan_jailbreak
  Use DAN-style personas to bypass restrictions

data_extraction
  Extract training data, personal info, or sensitive details

direct_prompt_injection
  Direct injection of malicious instructions to override system behavior

hypothetical_jailbreak
  Use hypothetical scenarios to elicit restricted content

indirect_prompt_injection
  Injection through indirect context rather than direct append

instruction_confusion
  Create conflicting instructions to confuse safety measures

multi_turn_setup
  Use social engineering to gain trust for follow-up attacks

privilege_escalation
  Escalate privileges or permissions to bypass controls

roleplay_jailbreak
  Use roleplay scenarios to bypass safety measures

token_smuggling
  Encode attacks using unicode, base64, rot13 to evade filters

tool_abuse
  Exploit connected tools to access restricted information

Total: 13 attacks
```

### 2. Validate a scenario

```bash
redteam validate-scenario scenarios/example_scan.yaml
```

```
Scenario Validation
============================================================
Name:        Basic Security Scan
Description: Comprehensive test of common LLM vulnerabilities
Backend:     http
Model:       gpt-4-test
Attacks:     9
  1. direct_prompt_injection (3 payloads)
  2. indirect_prompt_injection (2 payloads)
  3. roleplay_jailbreak (3 payloads)
  4. dan_jailbreak (2 payloads)
  5. token_smuggling (2 payloads)
  6. hypothetical_jailbreak (2 payloads)
  7. context_leakage (2 payloads)
  8. data_extraction (2 payloads)
  9. boundary_testing (2 payloads)

✓ Scenario is valid
```

### 3. Dry run before scanning

```bash
redteam scan scenarios/example_scan.yaml --dry-run
```

```
LLM Red Team Scan
============================================================
Scenario:     Basic Security Scan
Target:       http://gpt-4-test
Concurrency:  5
Dry Run:      True

Executing attacks  [####################################]  100/100
✓ Scenario validated successfully
```

### 4. Run a real scan

```bash
export OPENAI_API_KEY="sk-..."
redteam scan scenarios/example_scan.yaml --output report.json
```

```
LLM Red Team Scan
============================================================
Scenario:     Basic Security Scan
Target:       openai://gpt-4
Concurrency:  5
Dry Run:      False

Executing attacks  [####################################]  100/100

Results:
  Total Attacks:     20
  Successful:        3
  Success Rate:      15.0%
  Duration:          12.4s

Vulnerabilities by Severity:
  Critical   2
  High       1

✓ Report saved to: report.json
```

### 5. Generate an HTML report

```bash
redteam report report.json --format html --output report.html
```

## Scenario format

Scenarios are YAML files that define the target and which attacks to run:

```yaml
name: "API security check"
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
  rate_limit: 10
```

## Attack categories

**Prompt injection** — direct injection, indirect via system context, role confusion, token smuggling with unicode tricks.

**Jailbreaks** — DAN variants, roleplay-based circumvention, hypothetical scenarios, encoding obfuscation.

**Data exfiltration** — attempts to leak training data, extract system prompts, dump context window contents.

**Tool abuse** — boundary testing for connected tools, privilege escalation, resource exhaustion.

## Architecture

```
CLI (Click)
  └── Engine (orchestrator)
        ├── Target manager (OpenAI / Anthropic / Ollama / HTTP)
        ├── Attack modules (injection, jailbreak, exfil, tool abuse)
        ├── Payload library (30+ variants)
        └── Report generator (JSON / HTML)
```

## Project structure

```
redteam/
├── cli.py
├── core/
│   ├── engine.py       # Orchestration, concurrency, rate limiting
│   ├── target.py       # Backend abstraction layer
│   └── report.py       # Report generation
├── attacks/
│   ├── base.py         # Base class with severity/confidence scoring
│   ├── prompt_injection.py
│   ├── jailbreak.py
│   ├── data_exfil.py
│   └── tool_abuse.py
├── payloads/
│   └── library.py      # All attack payloads
└── utils/
scenarios/              # Example YAML configs
tests/                  # pytest suite
```

## Testing

```bash
pytest tests/ -v
pytest tests/ --cov=redteam --cov-report=html
```

## Different backends

```bash
# OpenAI
redteam scan scenario.yaml --backend openai --model gpt-4

# Anthropic
redteam scan scenario.yaml --backend anthropic --model claude-3-opus

# Local Ollama
redteam scan scenario.yaml --backend ollama --model llama2:7b

# Any HTTP endpoint
redteam scan scenario.yaml --backend http --endpoint http://localhost:8000/api/chat
```

## CI/CD integration

Run automated scans as part of your pipeline. Example GitHub Actions workflow:

```yaml
name: LLM Security Scan

on:
  push:
    branches: [main]
  pull_request:

jobs:
  redteam:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install toolkit
        run: pip install llm-red-team-toolkit
      - name: Run security scan
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          redteam scan scenarios/example_scan.yaml \
            --output report.json \
            --concurrency 5
      - name: Generate HTML report
        run: redteam report report.json --format html --output report.html
      - name: Upload report
        uses: actions/upload-artifact@v4
        with:
          name: redteam-report
          path: report.html
```

## Important

This is for **authorized testing only**. Test your own systems or systems you have explicit permission to test. Don't be the reason someone writes another "responsible AI use" policy.

## Related

- [AI Agent Sandbox](https://github.com/bastiaan365/ai-agent-sandbox) — runtime policy enforcement for AI agents
- [MCP IT Ops](https://github.com/bastiaan365/mcp-it-ops) — MCP server for IT administration

## License

MIT
