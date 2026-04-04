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

```bash
# see what's available
redteam list-attacks

# validate a scenario file before running
redteam validate-scenario scenarios/example_scan.yaml

# run a scan
redteam scan scenarios/example_scan.yaml --output report.json

# generate HTML report
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

## Important

This is for **authorized testing only**. Test your own systems or systems you have explicit permission to test. Don't be the reason someone writes another "responsible AI use" policy.

## Related

- [AI Agent Sandbox](https://github.com/bastiaan365/ai-agent-sandbox) — runtime policy enforcement for AI agents
- [MCP IT Ops](https://github.com/bastiaan365/mcp-it-ops) — MCP server for IT administration

## License

MIT
