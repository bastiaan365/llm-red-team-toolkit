"""Click-based CLI for red team toolkit."""

import asyncio
import logging
import json
from pathlib import Path
from typing import Optional

import click

from redteam.core.engine import (
    Engine,
    ScenarioConfig,
    load_scenario_from_file,
    get_available_attacks,
)
from redteam.core.report import ReportGenerator
from redteam.utils.helpers import setup_logging

logger = logging.getLogger(__name__)


@click.group()
@click.option("--log-level", default="INFO", help="Logging level")
def main(log_level: str) -> None:
    """LLM Red Team Toolkit - Automated security testing for LLM applications."""
    setup_logging(log_level)


@main.command()
def list_attacks() -> None:
    """List all available attacks."""
    click.echo("\nAvailable Attacks:")
    click.echo("=" * 60)

    attacks = get_available_attacks()

    for name, description in sorted(attacks.items()):
        click.echo(f"\n{click.style(name, fg='cyan')}")
        click.echo(f"  {description}")

    click.echo(f"\n{click.style(f'Total: {len(attacks)} attacks', fg='green')}\n")


@main.command()
@click.argument("scenario_path", type=click.Path(exists=True))
def validate_scenario(scenario_path: str) -> None:
    """Validate a scenario YAML file."""
    try:
        scenario = load_scenario_from_file(scenario_path)

        click.echo(f"\n{click.style('Scenario Validation', fg='cyan', bold=True)}")
        click.echo("=" * 60)

        click.echo(f"Name:        {scenario.name}")
        click.echo(f"Description: {scenario.description}")
        click.echo(f"Backend:     {scenario.target.backend}")
        click.echo(f"Model:       {scenario.target.model}")
        click.echo(f"Attacks:     {len(scenario.attacks)}")

        for i, attack_cfg in enumerate(scenario.attacks, 1):
            attack_name = attack_cfg.get("name")
            payloads = attack_cfg.get("payloads", "all")
            click.echo(f"  {i}. {attack_name} ({payloads} payloads)")

        click.echo(f"\n{click.style('✓ Scenario is valid', fg='green')}\n")

    except Exception as e:
        click.echo(click.style(f"✗ Validation failed: {e}", fg='red'), err=True)
        raise click.Abort()


@main.command()
@click.argument("scenario_path", type=click.Path(exists=True))
@click.option(
    "--output",
    "-o",
    default="redteam_report.json",
    help="Output file path",
)
@click.option(
    "--concurrency",
    "-c",
    default=5,
    type=int,
    help="Number of concurrent attacks",
)
@click.option(
    "--timeout",
    "-t",
    default=30,
    type=int,
    help="Request timeout in seconds",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Validate scenario without executing",
)
@click.option(
    "--backend",
    default=None,
    help="Override target backend",
)
@click.option(
    "--model",
    default=None,
    help="Override target model",
)
@click.option(
    "--endpoint",
    default=None,
    help="Override target endpoint",
)
def scan(
    scenario_path: str,
    output: str,
    concurrency: int,
    timeout: int,
    dry_run: bool,
    backend: Optional[str],
    model: Optional[str],
    endpoint: Optional[str],
) -> None:
    """Run a red team scan against an LLM endpoint."""
    try:
        # Load scenario
        scenario = load_scenario_from_file(scenario_path)

        # Override target config if specified
        if backend:
            scenario.target.backend = backend
        if model:
            scenario.target.model = model
        if endpoint:
            scenario.target.endpoint = endpoint

        scenario.target.timeout = timeout
        scenario.options["concurrency"] = concurrency

        click.echo(f"\n{click.style('LLM Red Team Scan', fg='cyan', bold=True)}")
        click.echo("=" * 60)
        click.echo(f"Scenario:     {scenario.name}")
        click.echo(f"Target:       {scenario.target.backend}://{scenario.target.model}")
        click.echo(f"Concurrency:  {concurrency}")
        click.echo(f"Dry Run:      {dry_run}")
        click.echo()

        # Initialize and run engine
        engine = Engine(scenario)

        asyncio.run(engine.initialize())

        with click.progressbar(
            length=100,
            label="Executing attacks",
            show_pos=True,
        ) as pbar:
            results = asyncio.run(engine.execute_scenario(dry_run=dry_run))
            pbar.update(100)

        if dry_run:
            click.echo(click.style("✓ Scenario validated successfully", fg='green'))
            return

        # Generate report
        summary = engine.get_summary()

        click.echo("\n" + click.style("Results:", fg='cyan', bold=True))
        click.echo(f"  Total Attacks:     {summary['total_attacks']}")
        click.echo(f"  Successful:        {summary['successful_attacks']}")
        click.echo(f"  Success Rate:      {summary['success_rate']:.1f}%")
        click.echo(f"  Duration:          {summary['duration_seconds']:.1f}s")

        vulns = summary.get("vulnerabilities_by_severity", {})
        if vulns:
            click.echo("\n" + click.style("Vulnerabilities by Severity:", fg='yellow', bold=True))
            for severity in ["critical", "high", "medium", "low"]:
                count = vulns.get(severity, 0)
                if count > 0:
                    color = (
                        "red" if severity == "critical"
                        else "yellow" if severity == "high"
                        else "blue"
                    )
                    click.echo(f"  {severity.capitalize():10s} {count}")

        # Save report
        generator = ReportGenerator(results, summary)
        generator.save_json(output)

        click.echo(f"\n{click.style(f'✓ Report saved to: {output}', fg='green')}\n")

    except Exception as e:
        click.echo(click.style(f"✗ Scan failed: {e}", fg='red'), err=True)
        raise click.Abort()


@main.command()
@click.argument("report_path", type=click.Path(exists=True))
@click.option(
    "--output",
    "-o",
    default=None,
    help="Output file path",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "html"], case_sensitive=False),
    default="html",
    help="Output format",
)
def report(report_path: str, output: Optional[str], format: str) -> None:
    """Generate a report from scan results."""
    try:
        # Load existing report
        with open(report_path, "r") as f:
            data = json.load(f)

        results_data = data.get("results", [])
        summary = data.get("summary", {})

        # Reconstruct AttackResult objects
        from redteam.attacks.base import AttackResult
        from datetime import datetime

        results = []
        for r in results_data:
            result = AttackResult(
                attack_name=r.get("attack_name"),
                payload=r.get("payload"),
                success=r.get("success", False),
                response=r.get("response", ""),
                confidence=r.get("confidence", 0.0),
                severity=r.get("severity", "medium"),
                timestamp=datetime.fromisoformat(r.get("timestamp", datetime.utcnow().isoformat())),
                error=r.get("error"),
                metadata=r.get("metadata", {}),
            )
            results.append(result)

        # Determine output path
        if not output:
            base = Path(report_path).stem
            output = f"{base}_report.{format}"

        # Generate and save report
        generator = ReportGenerator(results, summary)
        generator.save(output, format=format)

        click.echo(
            click.style(f"✓ {format.upper()} report saved to: {output}", fg='green')
        )

    except Exception as e:
        click.echo(click.style(f"✗ Report generation failed: {e}", fg='red'), err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()
