"""Command Line Interface for LLM evaluation."""

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from .policy import load_policy
from .providers import get_provider, parse_model_string
from .report import generate_report, load_and_generate_report
from .run import run_evaluation


app = typer.Typer(help="LLM Evaluation CLI - Free, Local, and Offline-First")
console = Console()


def format_timestamp() -> str:
    """Generate timestamp string for output directory."""
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


@app.command()
def providers() -> None:
    """List available providers and models."""
    console.print("[bold green]Available Providers[/bold green]")
    console.print()
    
    # Ollama provider
    provider = get_provider("ollama")
    
    table = Table(title="Ollama Provider")
    table.add_column("Provider", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Models Available")
    
    if provider.is_available():
        models = provider.list_models()
        models_str = ", ".join(models) if models else "None installed"
        table.add_row("ollama", "✅ Available", models_str)
    else:
        table.add_row("ollama", "❌ Unavailable", "Service not running")
    
    console.print(table)
    
    if not provider.is_available():
        console.print("\n[yellow]To use Ollama:[/yellow]")
        console.print("1. Install: https://ollama.ai/")
        console.print("2. Start service: [cyan]ollama serve[/cyan]")
        console.print("3. Pull model: [cyan]ollama pull llama3[/cyan]")


@app.command()
def check(
    model: Optional[str] = typer.Option(None, "--model", help="Check specific model availability")
) -> None:
    """Check environment and dependencies."""
    console.print("[bold green]Environment Check[/bold green]")
    console.print()
    
    # Python version
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    console.print(f"✅ Python {py_version}")
    
    # Required packages
    required_packages = [
        ("typer", "typer"),
        ("requests", "requests"),
        ("pydantic", "pydantic"),
        ("pandas", "pandas"),
        ("rich", "rich"),
        ("tabulate", "tabulate")
    ]
    
    console.print("\n[bold]Core Dependencies:[/bold]")
    for display_name, import_name in required_packages:
        try:
            __import__(import_name)
            console.print(f"✅ {display_name}")
        except ImportError:
            console.print(f"❌ {display_name} - run: pip install {display_name}")
    
    # Optional packages
    console.print("\n[bold]Safety & PII Dependencies:[/bold]")
    
    # Detoxify
    try:
        import torch
        from detoxify import Detoxify
        console.print("✅ Detoxify (toxicity detection)")
    except ImportError:
        console.print("⚠️  Detoxify - install: pip install detoxify torch --index-url https://download.pytorch.org/whl/cpu")
    
    # Presidio
    try:
        from presidio_analyzer import AnalyzerEngine
        console.print("✅ Presidio (PII detection)")
        
        # Check spaCy model
        try:
            import spacy
            nlp = spacy.load("en_core_web_sm")
            console.print("✅ spaCy en_core_web_sm model")
        except (ImportError, OSError):
            console.print("⚠️  spaCy model - install: python -m spacy download en_core_web_sm")
            
    except ImportError:
        console.print("⚠️  Presidio - install: pip install presidio-analyzer presidio-anonymizer spacy")
    
    # Ollama
    console.print("\n[bold]LLM Providers:[/bold]")
    provider = get_provider("ollama")
    
    if provider.is_available():
        console.print("✅ Ollama service")
        
        models = provider.list_models()
        if models:
            console.print(f"✅ Models available: {', '.join(models)}")
        else:
            console.print("⚠️  No models installed - run: ollama pull <model>")
        
        # Check specific model if requested
        if model:
            _, model_name = parse_model_string(model)
            if provider.model_exists(model_name):
                console.print(f"✅ Model '{model_name}' is available")
            else:
                console.print(f"❌ Model '{model_name}' not found - run: ollama pull {model_name}")
    else:
        console.print("❌ Ollama service not available")
        console.print("   Fix: ollama serve")


@app.command()
def run(
    model: str = typer.Option(..., "--model", help="Model to use (e.g., ollama/llama3)"),
    prompts: str = typer.Option("prompts.csv", "--prompts", help="Path to prompts CSV file"),
    policy: str = typer.Option("policy.json", "--policy", help="Path to policy JSON file"),
    out: Optional[str] = typer.Option(None, "--out", help="Output directory"),
    temp: Optional[float] = typer.Option(None, "--temp", help="Temperature for generation")
) -> None:
    """Run LLM evaluation."""
    
    # Validate model string
    provider_name, model_name = parse_model_string(model)
    if provider_name != "ollama":
        console.print(f"[red]Error:[/red] Only free local provider 'ollama' is supported. Got: {provider_name}")
        console.print("Use format: [cyan]ollama/model_name[/cyan] or just [cyan]model_name[/cyan]")
        raise typer.Exit(1)
    
    # Set default output directory
    if out is None:
        out = f"runs/{format_timestamp()}"
    
    # Validate input files
    if not Path(prompts).exists():
        console.print(f"[red]Error:[/red] Prompts file not found: {prompts}")
        raise typer.Exit(1)
    
    if not Path(policy).exists():
        console.print(f"[red]Error:[/red] Policy file not found: {policy}")
        raise typer.Exit(1)
    
    try:
        # Load policy
        eval_policy = load_policy(policy)
        
        # Run evaluation
        console.print(f"[green]Starting evaluation with {model}[/green]")
        console.print(f"📝 Prompts: {prompts}")
        console.print(f"📋 Policy: {policy}")
        console.print(f"📁 Output: {out}")
        console.print()
        
        metadata = run_evaluation(
            model_string=model,
            prompts_path=prompts,
            policy=eval_policy,
            output_dir=out,
            temperature=temp
        )
        
        # Load results and generate report
        results_path = Path(out) / "results.jsonl"
        if results_path.exists():
            import json
            results = []
            with open(results_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        results.append(json.loads(line))
            
            generate_report(results, metadata, Path(out))
            console.print(f"📊 Report generated: {Path(out) / 'report.md'}")
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def report(
    output_dir: str = typer.Argument(..., help="Directory containing evaluation results")
) -> None:
    """Generate report from existing evaluation results."""
    try:
        load_and_generate_report(output_dir)
        console.print(f"[green]Report generated successfully[/green]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
