"""Report generation in JSON and HTML formats."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from jinja2 import Template

from redteam.attacks.base import AttackResult
from redteam.utils.helpers import sanitize_for_html, get_severity_color, truncate_string

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate reports in various formats."""

    def __init__(self, results: List[AttackResult], summary: Dict[str, Any]) -> None:
        """Initialize report generator.

        Args:
            results: List of attack results
            summary: Summary statistics
        """
        self.results = results
        self.summary = summary

    def generate_json(self) -> str:
        """Generate JSON report.

        Returns:
            JSON string
        """
        report = {
            "summary": self.summary,
            "results": [result.to_dict() for result in self.results],
        }

        return json.dumps(report, indent=2)

    def save_json(self, path: str) -> None:
        """Save JSON report to file.

        Args:
            path: Output file path
        """
        with open(path, "w") as f:
            f.write(self.generate_json())

        logger.info(f"JSON report saved to: {path}")

    def generate_html(self) -> str:
        """Generate HTML report.

        Returns:
            HTML string
        """
        # Group results by attack name
        by_attack = {}
        for result in self.results:
            if result.attack_name not in by_attack:
                by_attack[result.attack_name] = []
            by_attack[result.attack_name].append(result)

        # Count by severity
        critical = sum(1 for r in self.results if r.success and r.severity == "critical")
        high = sum(1 for r in self.results if r.success and r.severity == "high")
        medium = sum(1 for r in self.results if r.success and r.severity == "medium")
        low = sum(1 for r in self.results if r.success and r.severity == "low")

        html_template = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>LLM Red Team Report</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        h1 {
            border-bottom: 3px solid #007bff;
            padding-bottom: 10px;
            color: #007bff;
        }
        h2 {
            margin-top: 30px;
            color: #333;
            border-left: 4px solid #007bff;
            padding-left: 10px;
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .summary-card {
            background: #f9f9f9;
            padding: 20px;
            border-radius: 6px;
            border-left: 4px solid #ccc;
            text-align: center;
        }
        .summary-card.critical { border-left-color: #dc3545; }
        .summary-card.high { border-left-color: #fd7e14; }
        .summary-card.medium { border-left-color: #ffc107; }
        .summary-card.low { border-left-color: #28a745; }
        .summary-card-value {
            font-size: 32px;
            font-weight: bold;
            color: #007bff;
        }
        .summary-card-label {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
            text-transform: uppercase;
        }
        .attack-group {
            margin: 20px 0;
            padding: 15px;
            background: #fafafa;
            border-radius: 6px;
        }
        .attack-name {
            font-weight: bold;
            font-size: 16px;
            margin-bottom: 10px;
        }
        .result {
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            margin: 10px 0;
            padding: 12px;
            border-left: 4px solid #ccc;
        }
        .result.success {
            border-left-color: #dc3545;
            background: #fff5f5;
        }
        .result.failed {
            border-left-color: #28a745;
        }
        .result-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }
        .badge.critical { background: #dc3545; color: white; }
        .badge.high { background: #fd7e14; color: white; }
        .badge.medium { background: #ffc107; color: #333; }
        .badge.low { background: #28a745; color: white; }
        .badge.success { background: #dc3545; color: white; }
        .badge.failed { background: #28a745; color: white; }
        .confidence {
            font-size: 12px;
            color: #666;
        }
        .response-preview {
            background: #f5f5f5;
            padding: 10px;
            border-radius: 4px;
            font-family: monospace;
            font-size: 12px;
            margin-top: 10px;
            max-height: 200px;
            overflow: auto;
            border: 1px solid #ddd;
            word-break: break-word;
        }
        .timestamp {
            font-size: 12px;
            color: #999;
        }
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #666;
            font-size: 12px;
        }
        .severity-meter {
            width: 100%;
            height: 30px;
            background: #e0e0e0;
            border-radius: 4px;
            overflow: hidden;
            display: flex;
            margin-top: 10px;
        }
        .severity-bar {
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 12px;
        }
        .critical-bar { background: #dc3545; width: {{ critical_pct }}%; }
        .high-bar { background: #fd7e14; width: {{ high_pct }}%; }
        .medium-bar { background: #ffc107; width: {{ medium_pct }}%; }
        .low-bar { background: #28a745; width: {{ low_pct }}%; }
    </style>
</head>
<body>
    <div class="container">
        <h1>LLM Red Team Assessment Report</h1>

        <p><strong>Scenario:</strong> {{ scenario_name }}</p>
        <p><strong>Executed:</strong> {{ start_time }}</p>
        <p><strong>Duration:</strong> {{ duration_seconds }}s</p>

        <h2>Executive Summary</h2>

        <div class="summary-grid">
            <div class="summary-card">
                <div class="summary-card-value">{{ total_attacks }}</div>
                <div class="summary-card-label">Total Tests</div>
            </div>
            <div class="summary-card">
                <div class="summary-card-value">{{ successful_attacks }}</div>
                <div class="summary-card-label">Successful</div>
            </div>
            <div class="summary-card">
                <div class="summary-card-value">{{ success_rate|round(1) }}%</div>
                <div class="summary-card-label">Success Rate</div>
            </div>
        </div>

        <h2>Vulnerabilities by Severity</h2>

        <div class="summary-grid">
            <div class="summary-card critical">
                <div class="summary-card-value">{{ critical }}</div>
                <div class="summary-card-label">Critical</div>
            </div>
            <div class="summary-card high">
                <div class="summary-card-value">{{ high }}</div>
                <div class="summary-card-label">High</div>
            </div>
            <div class="summary-card medium">
                <div class="summary-card-value">{{ medium }}</div>
                <div class="summary-card-label">Medium</div>
            </div>
            <div class="summary-card low">
                <div class="summary-card-value">{{ low }}</div>
                <div class="summary-card-label">Low</div>
            </div>
        </div>

        <div class="severity-meter">
            {% if critical > 0 %}<div class="severity-bar critical-bar">{{ critical }} Critical</div>{% endif %}
            {% if high > 0 %}<div class="severity-bar high-bar">{{ high }} High</div>{% endif %}
            {% if medium > 0 %}<div class="severity-bar medium-bar">{{ medium }} Medium</div>{% endif %}
            {% if low > 0 %}<div class="severity-bar low-bar">{{ low }} Low</div>{% endif %}
        </div>

        <h2>Detailed Results by Attack</h2>

        {% for attack_name, attack_results in by_attack.items() %}
        <div class="attack-group">
            <div class="attack-name">{{ attack_name }}</div>
            {% for result in attack_results[:5] %}
            <div class="result {% if result.success %}success{% else %}failed{% endif %}">
                <div class="result-header">
                    <span>
                        <span class="badge {% if result.success %}success{% else %}failed{% endif %}">
                            {% if result.success %}VULNERABLE{% else %}BLOCKED{% endif %}
                        </span>
                        <span class="badge {{ result.severity }}">{{ result.severity|upper }}</span>
                    </span>
                    <span class="confidence">Confidence: {{ (result.confidence * 100)|round(0)|int }}%</span>
                </div>
                <div class="timestamp">{{ result.timestamp }}</div>
                {% if result.response %}
                <div class="response-preview">{{ result.response|truncate(150) }}</div>
                {% endif %}
            </div>
            {% endfor %}
            {% if attack_results|length > 5 %}
            <p style="color: #999; font-size: 12px;">... and {{ attack_results|length - 5 }} more results</p>
            {% endif %}
        </div>
        {% endfor %}

        <div class="footer">
            <p>Report generated by LLM Red Team Toolkit v0.1.0</p>
            <p>For responsible disclosure and security research only</p>
        </div>
    </div>
</body>
</html>"""

        template = Template(html_template)

        # Calculate percentages
        total = critical + high + medium + low or 1
        critical_pct = (critical / total * 100) if total > 0 else 0
        high_pct = (high / total * 100) if total > 0 else 0
        medium_pct = (medium / total * 100) if total > 0 else 0
        low_pct = (low / total * 100) if total > 0 else 0

        return template.render(
            scenario_name=self.summary.get("scenario_name", "Unknown"),
            total_attacks=self.summary.get("total_attacks", 0),
            successful_attacks=self.summary.get("successful_attacks", 0),
            success_rate=self.summary.get("success_rate", 0),
            duration_seconds=int(self.summary.get("duration_seconds", 0)),
            start_time=self.summary.get("start_time", "Unknown"),
            critical=critical,
            high=high,
            medium=medium,
            low=low,
            critical_pct=critical_pct,
            high_pct=high_pct,
            medium_pct=medium_pct,
            low_pct=low_pct,
            by_attack=by_attack,
        )

    def save_html(self, path: str) -> None:
        """Save HTML report to file.

        Args:
            path: Output file path
        """
        with open(path, "w") as f:
            f.write(self.generate_html())

        logger.info(f"HTML report saved to: {path}")

    def save(self, path: str, format: str = "json") -> None:
        """Save report in specified format.

        Args:
            path: Output file path
            format: Report format (json or html)

        Raises:
            ValueError: If format is not supported
        """
        if format.lower() == "json":
            self.save_json(path)
        elif format.lower() == "html":
            self.save_html(path)
        else:
            raise ValueError(f"Unsupported format: {format}")
