# Quick Start Guide

## Installation

```bash
# Clone or navigate to the project
cd llm-red-team-toolkit

# Install in development mode
pip install -e .

# Install test dependencies (optional)
pip install pytest pytest-asyncio
```

## Basic Usage

### 1. List Available Attacks

See all 13 attack types with descriptions:

```bash
redteam list-attacks
```

Output shows:
- Attack name and type
- Description and severity
- Number of payloads
- 78 total payloads across 13 categories

### 2. Validate a Scenario

Check if your YAML scenario is properly formatted:

```bash
redteam validate-scenario scenarios/example_scan.yaml
```

This validates:
- Scenario structure
- Target configuration
- Attack definitions
- Option parameters

### 3. Run a Security Scan

Execute attacks against an LLM endpoint:

```bash
# Against the example scenario
redteam scan scenarios/example_scan.yaml --output report.json

# With custom settings
redteam scan scenarios/example_scan.yaml \
  --output report.json \
  --concurrency 10 \
  --timeout 60 \
  --backend openai \
  --model gpt-4

# Dry run (validation only, no execution)
redteam scan scenarios/example_scan.yaml --dry-run
```

Options:
- `--output`: Where to save JSON results (default: redteam_report.json)
- `--concurrency`: Parallel attacks (1-50, default: 5)
- `--timeout`: Request timeout in seconds (default: 30)
- `--backend`: Override target backend (openai, anthropic, ollama, http)
- `--model`: Override model name
- `--endpoint`: Override API endpoint
- `--dry-run`: Validate without executing

### 4. Generate Reports

Convert JSON results to readable formats:

```bash
# Generate HTML report
redteam report report.json --format html --output report.html

# Convert to JSON (different name)
redteam report report.json --format json --output analyzed.json
```

The HTML report includes:
- Executive summary with statistics
- Vulnerability breakdown by severity
- Detailed results by attack type
- Color-coded severity indicators
- Response previews
- Professional styling

## Example Workflow

```bash
# 1. List what attacks are available
redteam list-attacks

# 2. Validate your scenario file
redteam validate-scenario scenarios/example_scan.yaml

# 3. Run a quick dry-run to check everything
redteam scan scenarios/example_scan.yaml --dry-run

# 4. Execute the actual scan
redteam scan scenarios/example_scan.yaml \
  --output results.json \
  --concurrency 5 \
  --timeout 30

# 5. Generate an HTML report
redteam report results.json --format html --output results.html

# 6. View the report in your browser
open results.html  # macOS
# or
xdg-open results.html  # Linux
# or
start results.html  # Windows
```

## Creating Custom Scenarios

Create a YAML file with your own attack configuration:

```yaml
name: "My Custom Scan"
description: "Testing specific vulnerabilities"

target:
  backend: openai
  model: gpt-4
  api_key: ${OPENAI_API_KEY}  # Uses environment variable
  endpoint: https://api.openai.com/v1/chat/completions
  timeout: 30
  max_tokens: 1000

attacks:
  # Direct prompt injection - 5 payloads
  - name: direct_prompt_injection
    payloads: 5
    severity: critical

  # Jailbreak attempts - 3 payloads
  - name: roleplay_jailbreak
    payloads: 3
    severity: high

  # Data exfiltration - all payloads
  - name: data_extraction
    enabled: true

options:
  concurrency: 5
  timeout: 30
  rate_limit: 10
  retry_count: 2
```

Then run:
```bash
redteam scan my_scenario.yaml --output results.json
```

## Supported Backends

### OpenAI
```yaml
target:
  backend: openai
  model: gpt-4
  api_key: ${OPENAI_API_KEY}
```

### Anthropic
```yaml
target:
  backend: anthropic
  model: claude-3-opus-20240229
  api_key: ${ANTHROPIC_API_KEY}
```

### Ollama (Local)
```yaml
target:
  backend: ollama
  model: llama2:7b
  endpoint: http://localhost:11434/api/generate
```

### Generic HTTP
```yaml
target:
  backend: http
  model: custom-model
  endpoint: http://your-api.com/chat
```

## Attack Categories

### Prompt Injection (4 attacks)
- `direct_prompt_injection` - Append-based injection
- `indirect_prompt_injection` - Context-based injection
- `token_smuggling` - Encoded injection (unicode, base64, rot13)
- `context_leakage` - System prompt extraction

### Jailbreaks (4 attacks)
- `roleplay_jailbreak` - Roleplay personas
- `dan_jailbreak` - Do Anything Now style
- `hypothetical_jailbreak` - Hypothetical scenarios
- `instruction_confusion` - Conflicting instructions

### Data Exfiltration (3 attacks)
- `data_extraction` - Extract sensitive data
- `privilege_escalation` - Gain elevated permissions
- `multi_turn_setup` - Social engineering setup

### Tool Abuse (2 attacks)
- `tool_abuse` - Exploit connected tools
- `boundary_testing` - Test safety boundaries

### Total: 13 attacks, 78 payloads

## Understanding Results

JSON report structure:
```json
{
  "summary": {
    "scenario_name": "Basic Security Scan",
    "total_attacks": 42,
    "successful_attacks": 5,
    "success_rate": 11.9,
    "vulnerabilities_by_severity": {
      "critical": 2,
      "high": 3
    },
    "duration_seconds": 24.5
  },
  "results": [
    {
      "attack_name": "direct_prompt_injection",
      "payload": "Ignore previous instructions...",
      "success": true,
      "response": "System prompt: ...",
      "confidence": 0.95,
      "severity": "critical",
      "timestamp": "2026-04-03T22:25:34.123456"
    }
  ]
}
```

Key fields:
- `success`: Whether attack bypassed safety measures
- `confidence`: Score 0-1 indicating certainty (0.0-1.0)
- `severity`: Level of vulnerability (critical, high, medium, low)
- `response`: Model's actual response
- `timestamp`: When attack was executed

## Tips and Best Practices

1. **Start with dry-run**: Always validate scenarios before running
   ```bash
   redteam scan scenario.yaml --dry-run
   ```

2. **Use concurrency wisely**: Higher concurrency = faster but more API calls
   ```bash
   --concurrency 5  # Conservative
   --concurrency 20  # Aggressive
   ```

3. **Monitor API costs**: Each attack makes a request to your LLM
   ```
   42 attacks × $0.01/request = $0.42 per scan
   ```

4. **Check API keys**: Use environment variables, never hardcode
   ```yaml
   api_key: ${OPENAI_API_KEY}  # Good
   api_key: sk-...            # Bad!
   ```

5. **Review HTML reports**: Better for stakeholders and presentations

6. **Test before going live**: Run on development models first

7. **Customize payloads**: Edit `redteam/payloads/library.py` to add your own

## Troubleshooting

### CLI not found
```bash
# Ensure package is installed
pip install -e .

# Or run directly
python -m redteam.cli scan scenario.yaml
```

### Import errors
```bash
# Reinstall dependencies
pip install -e ".[dev]"
```

### API key issues
```bash
# Set environment variable
export OPENAI_API_KEY="sk-..."

# Or in scenario file
api_key: ${OPENAI_API_KEY}
```

### Timeout errors
```bash
# Increase timeout
redteam scan scenario.yaml --timeout 60
```

### Permission denied errors
```bash
# Check directory permissions
chmod +x redteam/cli.py
```

## Next Steps

1. Try the example scan:
   ```bash
   redteam scan scenarios/example_scan.yaml
   ```

2. Create your own scenario for your LLM endpoint

3. Review the HTML report to understand vulnerabilities

4. Fix identified issues and re-test

5. Integrate into your CI/CD pipeline

6. Set up regular scheduled scans

## Getting Help

- View all available commands: `redteam --help`
- Get help for specific command: `redteam scan --help`
- Check README.md for detailed documentation
- Review test files in `tests/` for code examples

## Responsible Security Testing

This toolkit is designed for:
- Authorized security testing of your own systems
- Red team exercises for defense improvements
- Vulnerability identification before deployment

Always:
- Test only systems you own or have explicit permission to test
- Document all findings and fixes
- Follow responsible disclosure practices
- Use results to improve security, not for malicious purposes

Happy testing!
