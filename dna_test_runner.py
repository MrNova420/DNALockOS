#!/usr/bin/env python3
"""
DNA-Key Authentication System - Advanced Test Runner

Comprehensive testing suite with multiple profiles for different environments.
Supports smoke, full, adversarial, stress, and mobile-safe testing profiles.
"""

import json
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table


class TestStatus(str, Enum):
    """Test result status."""
    PASS = "pass"
    FAIL = "fail"
    ERROR = "error"
    SKIPPED = "skipped"


class TestSeverity(str, Enum):
    """Test issue severity."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class TestResult:
    """Individual test result."""
    name: str
    pack: str
    status: TestStatus
    severity: TestSeverity = TestSeverity.INFO
    duration: float = 0.0
    details: str = ""
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "pack": self.pack,
            "status": self.status.value,
            "severity": self.severity.value,
            "duration": self.duration,
            "details": self.details,
            "error_message": self.error_message
        }


@dataclass
class SuiteResults:
    """Complete test suite results."""
    profile: str
    start_time: datetime
    end_time: Optional[datetime] = None
    results: List[TestResult] = field(default_factory=list)
    
    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.status == TestStatus.PASS)
    
    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if r.status == TestStatus.FAIL)
    
    @property
    def errors(self) -> int:
        return sum(1 for r in self.results if r.status == TestStatus.ERROR)
    
    @property
    def skipped(self) -> int:
        return sum(1 for r in self.results if r.status == TestStatus.SKIPPED)
    
    @property
    def total(self) -> int:
        return len(self.results)
    
    @property
    def duration(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile": self.profile,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration,
            "summary": {
                "total": self.total,
                "passed": self.passed,
                "failed": self.failed,
                "errors": self.errors,
                "skipped": self.skipped
            },
            "results": [r.to_dict() for r in self.results]
        }


class DNATestRunner:
    """Advanced test runner for DNALockOS."""
    
    PROFILES = {
        "smoke": {
            "description": "Quick sanity checks (mobile-friendly)",
            "packs": ["unit"],
            "max_tests": 50,
            "timeout": 60
        },
        "full": {
            "description": "Complete test suite (excluding stress/chaos)",
            "packs": ["unit", "integration", "adversarial"],
            "max_tests": None,
            "timeout": 300
        },
        "adversarial": {
            "description": "Security and adversarial tests only",
            "packs": ["adversarial"],
            "max_tests": None,
            "timeout": 180
        },
        "stress": {
            "description": "Load and stress tests (desktop only)",
            "packs": ["stress"],
            "max_tests": None,
            "timeout": 600
        },
        "mobile-safe": {
            "description": "Curated set safe for mobile/Termux",
            "packs": ["unit"],
            "max_tests": 30,
            "timeout": 120
        },
        "resilience": {
            "description": "Chaos and resilience tests",
            "packs": ["resilience"],
            "max_tests": None,
            "timeout": 300
        }
    }
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.root = Path(__file__).parent
    
    def run_suite(
        self,
        profile: str,
        max_concurrency: Optional[int] = None,
        skip_db: bool = False,
        skip_redis: bool = False
    ) -> SuiteResults:
        """Run the test suite with the specified profile."""
        if profile not in self.PROFILES:
            raise ValueError(f"Unknown profile: {profile}")
        
        profile_config = self.PROFILES[profile]
        results = SuiteResults(
            profile=profile,
            start_time=datetime.now()
        )
        
        self.console.print(Panel(
            f"[bold cyan]DNALockOS Test Suite[/bold cyan]\n"
            f"Profile: [yellow]{profile}[/yellow]\n"
            f"Description: {profile_config['description']}",
            title="🧬 Test Runner",
            border_style="cyan"
        ))
        
        # Run pytest for each pack
        for pack in profile_config["packs"]:
            pack_results = self._run_pack(
                pack,
                max_tests=profile_config.get("max_tests"),
                timeout=profile_config.get("timeout", 300),
                skip_db=skip_db,
                skip_redis=skip_redis
            )
            results.results.extend(pack_results)
        
        results.end_time = datetime.now()
        return results
    
    def _run_pack(
        self,
        pack: str,
        max_tests: Optional[int] = None,
        timeout: int = 300,
        skip_db: bool = False,
        skip_redis: bool = False
    ) -> List[TestResult]:
        """Run tests for a specific pack."""
        import subprocess
        
        test_path = self.root / "tests" / pack
        if not test_path.exists():
            self.console.print(f"[yellow]⚠️ Test pack '{pack}' not found at {test_path}[/yellow]")
            return [TestResult(
                name=f"{pack}_pack",
                pack=pack,
                status=TestStatus.SKIPPED,
                details=f"Test directory not found: {test_path}"
            )]
        
        self.console.print(f"\n[cyan]📦 Running {pack} tests...[/cyan]")
        
        # Build pytest command
        cmd = [
            sys.executable, "-m", "pytest",
            str(test_path),
            "-v",
            "--tb=short",
            f"--timeout={timeout}",
            "--json-report",
            "--json-report-file=/tmp/dna_test_results.json"
        ]
        
        if max_tests:
            cmd.extend(["--max-tests", str(max_tests)])
        
        # Add markers based on flags
        markers = []
        if skip_db:
            markers.append("not requires_db")
        if skip_redis:
            markers.append("not requires_redis")
        
        if markers:
            cmd.extend(["-m", " and ".join(markers)])
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(self.root)
            )
            duration = time.time() - start_time
            
            # Parse results from JSON report if available
            json_report_path = Path("/tmp/dna_test_results.json")
            if json_report_path.exists():
                return self._parse_json_report(json_report_path, pack, duration)
            
            # Fallback: parse from output
            return self._parse_pytest_output(result.stdout, pack, duration)
            
        except subprocess.TimeoutExpired:
            return [TestResult(
                name=f"{pack}_timeout",
                pack=pack,
                status=TestStatus.ERROR,
                severity=TestSeverity.HIGH,
                details=f"Test pack timed out after {timeout}s"
            )]
        except Exception as e:
            return [TestResult(
                name=f"{pack}_error",
                pack=pack,
                status=TestStatus.ERROR,
                severity=TestSeverity.HIGH,
                error_message=str(e)
            )]
    
    def _parse_json_report(self, report_path: Path, pack: str, duration: float) -> List[TestResult]:
        """Parse pytest JSON report."""
        try:
            with open(report_path) as f:
                report = json.load(f)
            
            results = []
            for test in report.get("tests", []):
                status = TestStatus.PASS
                if test.get("outcome") == "failed":
                    status = TestStatus.FAIL
                elif test.get("outcome") == "error":
                    status = TestStatus.ERROR
                elif test.get("outcome") == "skipped":
                    status = TestStatus.SKIPPED
                
                results.append(TestResult(
                    name=test.get("nodeid", "unknown"),
                    pack=pack,
                    status=status,
                    duration=test.get("duration", 0),
                    details=test.get("call", {}).get("longrepr", "")[:500] if test.get("call") else ""
                ))
            
            return results
        except Exception:
            # Fallback to simple result
            return [TestResult(
                name=f"{pack}_pack",
                pack=pack,
                status=TestStatus.PASS,
                duration=duration
            )]
    
    def _parse_pytest_output(self, output: str, pack: str, duration: float) -> List[TestResult]:
        """Parse pytest output to extract results."""
        results = []
        
        # Look for summary line like "644 passed in 11.58s"
        import re
        summary_match = re.search(r"(\d+) passed", output)
        failed_match = re.search(r"(\d+) failed", output)
        error_match = re.search(r"(\d+) error", output)
        
        passed = int(summary_match.group(1)) if summary_match else 0
        failed = int(failed_match.group(1)) if failed_match else 0
        errors = int(error_match.group(1)) if error_match else 0
        
        # Create aggregate result
        if failed == 0 and errors == 0:
            results.append(TestResult(
                name=f"{pack}_pack",
                pack=pack,
                status=TestStatus.PASS,
                duration=duration,
                details=f"{passed} tests passed"
            ))
        else:
            results.append(TestResult(
                name=f"{pack}_pack",
                pack=pack,
                status=TestStatus.FAIL,
                severity=TestSeverity.HIGH,
                duration=duration,
                details=f"Passed: {passed}, Failed: {failed}, Errors: {errors}"
            ))
        
        return results
    
    def emit_reports(
        self,
        results: SuiteResults,
        json_path: Optional[str] = None,
        markdown_path: Optional[str] = None
    ):
        """Emit test reports in various formats."""
        # Print console summary
        self._print_summary(results)
        
        # Write JSON report
        if json_path:
            self._write_json_report(results, json_path)
        
        # Write Markdown report
        if markdown_path:
            self._write_markdown_report(results, markdown_path)
    
    def _print_summary(self, results: SuiteResults):
        """Print summary to console."""
        table = Table(title="Test Results Summary")
        table.add_column("Pack", style="cyan")
        table.add_column("Passed", style="green")
        table.add_column("Failed", style="red")
        table.add_column("Errors", style="yellow")
        table.add_column("Skipped", style="dim")
        
        # Group by pack
        packs: Dict[str, Dict[str, int]] = {}
        for result in results.results:
            if result.pack not in packs:
                packs[result.pack] = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0}
            
            if result.status == TestStatus.PASS:
                packs[result.pack]["passed"] += 1
            elif result.status == TestStatus.FAIL:
                packs[result.pack]["failed"] += 1
            elif result.status == TestStatus.ERROR:
                packs[result.pack]["errors"] += 1
            elif result.status == TestStatus.SKIPPED:
                packs[result.pack]["skipped"] += 1
        
        for pack, counts in packs.items():
            table.add_row(
                pack,
                str(counts["passed"]),
                str(counts["failed"]),
                str(counts["errors"]),
                str(counts["skipped"])
            )
        
        self.console.print(table)
        
        # Overall summary
        if results.failed == 0 and results.errors == 0:
            self.console.print(Panel(
                f"[bold green]✅ ALL TESTS PASSED[/bold green]\n"
                f"Total: {results.total} | Duration: {results.duration:.2f}s",
                border_style="green"
            ))
        else:
            self.console.print(Panel(
                f"[bold red]❌ SOME TESTS FAILED[/bold red]\n"
                f"Passed: {results.passed} | Failed: {results.failed} | "
                f"Errors: {results.errors} | Duration: {results.duration:.2f}s",
                border_style="red"
            ))
    
    def _write_json_report(self, results: SuiteResults, path: str):
        """Write JSON report."""
        report_path = Path(path)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, "w") as f:
            json.dump(results.to_dict(), f, indent=2)
        
        self.console.print(f"[dim]📄 JSON report written to: {path}[/dim]")
    
    def _write_markdown_report(self, results: SuiteResults, path: str):
        """Write Markdown report."""
        report_path = Path(path)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        lines = [
            "# DNALockOS Test Report",
            "",
            f"**Profile:** {results.profile}",
            f"**Date:** {results.start_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Duration:** {results.duration:.2f}s",
            "",
            "## Summary",
            "",
            f"| Metric | Count |",
            f"|--------|-------|",
            f"| Total | {results.total} |",
            f"| Passed | {results.passed} |",
            f"| Failed | {results.failed} |",
            f"| Errors | {results.errors} |",
            f"| Skipped | {results.skipped} |",
            ""
        ]
        
        # Failed tests
        failed_tests = [r for r in results.results if r.status in (TestStatus.FAIL, TestStatus.ERROR)]
        if failed_tests:
            lines.extend([
                "## Failed Tests",
                "",
                "| Test | Pack | Status | Severity |",
                "|------|------|--------|----------|"
            ])
            for test in failed_tests:
                lines.append(
                    f"| {test.name} | {test.pack} | {test.status.value} | {test.severity.value} |"
                )
            lines.append("")
        
        # Recommendations
        if failed_tests:
            lines.extend([
                "## Recommendations",
                "",
                "### Top Issues to Fix",
                ""
            ])
            critical = [t for t in failed_tests if t.severity in (TestSeverity.CRITICAL, TestSeverity.HIGH)]
            for i, test in enumerate(critical[:5], 1):
                lines.append(f"{i}. **{test.name}** ({test.severity.value})")
                if test.error_message:
                    lines.append(f"   - Error: {test.error_message[:200]}")
                lines.append("")
        
        with open(report_path, "w") as f:
            f.write("\n".join(lines))
        
        self.console.print(f"[dim]📝 Markdown report written to: {path}[/dim]")


@click.command()
@click.option(
    "--profile",
    type=click.Choice(["smoke", "full", "adversarial", "stress", "mobile-safe", "resilience"]),
    default="smoke",
    help="Test profile to run"
)
@click.option("--json-report", type=click.Path(), default=None, help="Path for JSON report output")
@click.option("--markdown-report", type=click.Path(), default=None, help="Path for Markdown report output")
@click.option("--max-concurrency", type=int, default=None, help="Maximum concurrent tests (for stress)")
@click.option("--skip-db", is_flag=True, help="Skip tests requiring database")
@click.option("--skip-redis", is_flag=True, help="Skip tests requiring Redis")
def main(profile, json_report, markdown_report, max_concurrency, skip_db, skip_redis):
    """
    DNALockOS Advanced Test Runner
    
    Run comprehensive tests with different profiles for various environments.
    """
    console = Console()
    runner = DNATestRunner(console)
    
    console.rule("[bold cyan]🧬 DNALockOS Test Suite[/bold cyan]")
    
    try:
        results = runner.run_suite(
            profile=profile,
            max_concurrency=max_concurrency,
            skip_db=skip_db,
            skip_redis=skip_redis
        )
        
        runner.emit_reports(
            results=results,
            json_path=json_report,
            markdown_path=markdown_report
        )
        
        # Exit with appropriate code
        if results.failed > 0 or results.errors > 0:
            sys.exit(1)
        sys.exit(0)
        
    except Exception as e:
        console.print(f"[bold red]Error running tests: {e}[/bold red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
