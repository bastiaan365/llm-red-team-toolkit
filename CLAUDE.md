# llm-red-team-toolkit

Automated security testing CLI for LLM-based applications. Runs prompt injection, jailbreak, data-exfil, and tool-abuse attacks against any LLM endpoint to find vulnerabilities. Maintained by Bastiaan ([@bastiaan365](https://github.com/bastiaan365)).

This file scopes Claude's behaviour for this repo. The global `~/.claude/CLAUDE.md` covers personal conventions; everything below is repo-specific.

## What this repo is

- A **defensive security tool** for testing LLM applications you own or have authorisation to test.
- **Contains actual attack payloads** — prompt injections, jailbreaks, exfiltration prompts. That's the product. They're committed deliberately, not accidentally.
- Multi-backend: OpenAI / Anthropic / Ollama / generic HTTP endpoint.
- Async execution with rate limiting.
- Reports as JSON / HTML with severity ratings.

**Authorization is a hard requirement.** This tool is for testing systems you own or have written permission to test. Helping use it against unauthorised targets is out of scope.

## Repo conventions

### Structure

```
redteam/
├── cli.py
├── core/
│   ├── engine.py       attack runner with async + rate limit
│   ├── target.py       backend abstractions (OpenAI / Anthropic / Ollama / HTTP)
│   └── report.py       JSON + HTML reporting
├── payloads/
│   └── library.py      the actual attack payload definitions
└── utils/
tests/                  pytest, ~73% coverage as of recent merge
QUICKSTART.md
```

### What's safe to commit (and what isn't)

- **Attack payload strings in `redteam/payloads/library.py`** — yes, deliberately committed. They're the product. Reviewers should understand these are red-team test inputs, not malicious code.
- **Attack scenarios in YAML** — yes; they describe what to test against the target.
- **Reports from running the tool** — never. Reports contain the target endpoint URL, the system's responses (potentially including its system prompt or user data), and confirmed vulnerabilities. Add `reports/` and `*.html` (your-output) to `.gitignore` if not already.
- **API keys** — never. OpenAI / Anthropic / target HTTP credentials come from environment variables only. The tool itself reads from env; tests mock the backends.
- **Customer / client target data** — never. Generic `https://api.example.com/v1/chat` style placeholders only.

### Python style

- Python 3.10+ target.
- `redteam/` package; tests in `tests/`.
- async/await throughout the engine — don't break the event loop with synchronous I/O.
- Type hints on `Target`, `AttackResult`, the public engine methods.
- Use `from __future__ import annotations` at top of every module that uses forward refs.

### Testing

- pytest, async tests via `pytest-asyncio`. Currently ~73% coverage (per recent merge).
- Backends MUST be mocked (use `respx` for HTTP, `unittest.mock.AsyncMock` for SDK clients). No test should ever hit a real LLM API — flaky, expensive, leaks intent.
- Payload tests assert structure (presence of injection markers, expected categories) rather than effectiveness — effectiveness depends on the target.

### Validation gates

Before any commit:

- `python -m py_compile redteam/**/*.py`
- `pytest tests/ -v --cov=redteam --cov-report=term-missing` — coverage stays at or above 73%
- **Reports / outputs check:**
  ```bash
  find . -name "*.html" -o -name "report-*.json" -o -name "results-*.json" | grep -v test_fixture
  ```
  Should be empty. If present, those are accidental commits of test outputs.
- **API key leak check:**
  ```bash
  grep -REn 'sk-[A-Za-z0-9]{20,}|AIza[A-Za-z0-9_-]{35}|xoxp-' redteam/ tests/ | head -5
  ```
  Should be empty.

## Workflow expectations for Claude

When I ask you to **add a new attack payload**:

1. Add to `redteam/payloads/library.py` under the appropriate category dict.
2. Add a test in `tests/test_payloads.py` asserting the payload is present and well-formed.
3. Document the new payload in the README's "What's included" or QUICKSTART (rough category, severity).
4. **Cite the source if it's from public research** (a paper, a CVE, a published advisory). Original payloads are fine; lifted-without-credit isn't.

When I ask you to **add a new backend**:

1. Implement the `Target` interface in `redteam/core/target.py`.
2. Add tests in `tests/test_target.py` with a fully mocked backend.
3. Update README's "Multi-backend support" line.
4. Confirm credentials come from env vars; never positional args to the constructor.

When I ask you to **run an attack against a real target**:

1. **Confirm authorization explicitly.** "I own this endpoint" or "I have written permission from the operator" must be stated before running.
2. Default to a small `--max-payloads` count to scope the blast radius.
3. Save the report to a path that's already in `.gitignore`.
4. Don't show me the full report contents in chat — they contain endpoint responses; summarise instead.

## Things to avoid

- `subprocess.run(..., shell=True)` — always list-form, even for "trivial" commands.
- Logging full request/response bodies at INFO level — they may contain secrets, system prompts, or user data. Use DEBUG and require explicit opt-in.
- Hardcoding any LLM provider's URL outside the backend module.
- Adding payloads designed to extract specific known systems' system prompts (e.g., a known commercial product) without explicit defense-research justification.
- Releases without me — `gh release` only by my hand, after a real authorised target test.

## Related repos

- [`ai-agent-sandbox`](https://github.com/bastiaan365/ai-agent-sandbox) — defensive counterpart (runtime sandboxing of agents)
- [`mcp-it-ops`](https://github.com/bastiaan365/mcp-it-ops) — same Python conventions; sibling project

## Drift from target structure

_Claude maintains this section. List anything in the repo that doesn't match the conventions above, with why it's still there and what would need to happen to fix it._

- _(empty until first audit pass — fill on next session that actually edits code)_
