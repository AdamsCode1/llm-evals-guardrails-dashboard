#!/usr/bin/env python3
"""
Ultra-Simple Guardrails Dashboard

A lightweight web dashboard for monitoring LLM evaluation results
from the llm-evals-cli tool. Provides real-time visibility into
AI safety metrics, policy violations, and performance trends.

Features:
- Real-time monitoring of evaluation runs
- Policy violation alerts
- Performance metrics visualization
- Simple, clean interface
- No external dependencies (uses built-in Python libs)
"""

import json
import os
import sys
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Dict, List, Any
from urllib.parse import parse_qs, urlparse
import webbrowser


class GuardrailsHandler(SimpleHTTPRequestHandler):
    """HTTP handler for the Guardrails Dashboard."""
    
    def __init__(self, *args, runs_dir="../llm-evals-cli/runs", **kwargs):
        self.runs_dir = Path(runs_dir)
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == "/" or parsed_path.path == "/index.html":
            self.serve_dashboard()
        elif parsed_path.path == "/api/runs":
            self.serve_runs_api()
        elif parsed_path.path.startswith("/api/run/"):
            run_id = parsed_path.path.split("/")[-1]
            self.serve_run_details(run_id)
        elif parsed_path.path == "/api/stats":
            self.serve_stats_api()
        else:
            super().do_GET()
    
    def serve_dashboard(self):
        """Serve the main dashboard HTML."""
        html = self.generate_dashboard_html()
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_runs_api(self):
        """API endpoint for listing evaluation runs."""
        runs = self.get_recent_runs()
        self.send_json_response(runs)
    
    def serve_run_details(self, run_id: str):
        """API endpoint for specific run details."""
        run_details = self.get_run_details(run_id)
        self.send_json_response(run_details)
    
    def serve_stats_api(self):
        """API endpoint for dashboard statistics."""
        stats = self.get_dashboard_stats()
        self.send_json_response(stats)
    
    def send_json_response(self, data: Dict[str, Any]):
        """Send JSON response."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def get_recent_runs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent evaluation runs."""
        if not self.runs_dir.exists():
            return []
        
        runs = []
        for run_dir in sorted(self.runs_dir.iterdir(), reverse=True):
            if not run_dir.is_dir():
                continue
                
            meta_file = run_dir / "meta.json"
            if not meta_file.exists():
                continue
            
            try:
                with open(meta_file) as f:
                    meta = json.load(f)
                
                # Add summary stats
                results_file = run_dir / "results.jsonl"
                if results_file.exists():
                    results = self.load_results(results_file)
                    meta["summary"] = self.calculate_run_summary(results)
                
                meta["run_id"] = run_dir.name
                runs.append(meta)
                
                if len(runs) >= limit:
                    break
                    
            except Exception as e:
                print(f"Error loading run {run_dir.name}: {e}")
                continue
        
        return runs
    
    def get_run_details(self, run_id: str) -> Dict[str, Any]:
        """Get detailed data for a specific run."""
        run_dir = self.runs_dir / run_id
        if not run_dir.exists():
            return {"error": "Run not found"}
        
        try:
            # Load metadata
            meta_file = run_dir / "meta.json"
            with open(meta_file) as f:
                meta = json.load(f)
            
            # Load results
            results_file = run_dir / "results.jsonl"
            results = self.load_results(results_file) if results_file.exists() else []
            
            return {
                "metadata": meta,
                "results": results,
                "summary": self.calculate_run_summary(results)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get overall dashboard statistics."""
        runs = self.get_recent_runs(limit=50)  # Last 50 runs
        
        if not runs:
            return {
                "total_runs": 0,
                "total_evaluations": 0,
                "avg_accuracy": 0,
                "avg_latency": 0,
                "violation_rate": 0,
                "recent_violations": []
            }
        
        total_evaluations = sum(r.get("total_prompts", 0) for r in runs)
        
        # Aggregate metrics from summaries
        accuracies = [r["summary"]["accuracy_rate"] for r in runs if "summary" in r and r["summary"]["accuracy_rate"] is not None]
        latencies = [r["summary"]["avg_latency_ms"] for r in runs if "summary" in r and r["summary"]["avg_latency_ms"] is not None]
        blocked_counts = [r["summary"]["blocked_count"] for r in runs if "summary" in r]
        
        # Recent violations
        recent_violations = []
        for run in runs[:5]:  # Last 5 runs
            if "summary" in run and run["summary"]["blocked_count"] > 0:
                recent_violations.append({
                    "run_id": run["run_id"],
                    "timestamp": run.get("start_time"),
                    "blocked_count": run["summary"]["blocked_count"],
                    "total_prompts": run.get("total_prompts", 0)
                })
        
        return {
            "total_runs": len(runs),
            "total_evaluations": total_evaluations,
            "avg_accuracy": sum(accuracies) / len(accuracies) if accuracies else 0,
            "avg_latency": sum(latencies) / len(latencies) if latencies else 0,
            "violation_rate": sum(blocked_counts) / total_evaluations if total_evaluations > 0 else 0,
            "recent_violations": recent_violations
        }
    
    def load_results(self, results_file: Path) -> List[Dict[str, Any]]:
        """Load results from JSONL file."""
        results = []
        try:
            with open(results_file) as f:
                for line in f:
                    if line.strip():
                        results.append(json.loads(line))
        except Exception as e:
            print(f"Error loading results: {e}")
        return results
    
    def calculate_run_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics for a run."""
        if not results:
            return {
                "total_prompts": 0,
                "accuracy_rate": None,
                "avg_latency_ms": None,
                "blocked_count": 0,
                "avg_toxicity": None
            }
        
        total = len(results)
        
        # Accuracy rate
        accuracy_results = [r.get("accuracy") for r in results if r.get("accuracy") is not None]
        accuracy_rate = sum(accuracy_results) / len(accuracy_results) if accuracy_results else None
        
        # Average latency
        latencies = [r.get("latency_ms", 0) for r in results if r.get("latency_ms") is not None]
        avg_latency = sum(latencies) / len(latencies) if latencies else None
        
        # Blocked count
        blocked_count = sum(1 for r in results if r.get("blocked", False))
        
        # Average toxicity
        toxicities = [r.get("toxicity") for r in results if r.get("toxicity") is not None]
        avg_toxicity = sum(toxicities) / len(toxicities) if toxicities else None
        
        return {
            "total_prompts": total,
            "accuracy_rate": accuracy_rate,
            "avg_latency_ms": avg_latency,
            "blocked_count": blocked_count,
            "avg_toxicity": avg_toxicity
        }
    
    def generate_dashboard_html(self) -> str:
        """Generate the dashboard HTML."""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Guardrails Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5; 
            color: #333;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem 0;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header h1 { font-size: 2.5rem; margin-bottom: 0.5rem; }
        .header p { opacity: 0.9; font-size: 1.1rem; }
        
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 3rem;
        }
        
        .stat-card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }
        
        .stat-card h3 {
            color: #666;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.5rem;
        }
        
        .stat-card .value {
            font-size: 2rem;
            font-weight: bold;
            color: #333;
        }
        
        .stat-card.warning { border-left-color: #f39c12; }
        .stat-card.danger { border-left-color: #e74c3c; }
        .stat-card.success { border-left-color: #27ae60; }
        
        .section {
            background: white;
            margin-bottom: 2rem;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .section-header {
            background: #f8f9fa;
            padding: 1rem 1.5rem;
            border-bottom: 1px solid #e9ecef;
        }
        
        .section-header h2 {
            color: #495057;
            font-size: 1.3rem;
        }
        
        .section-content {
            padding: 1.5rem;
        }
        
        .runs-list {
            list-style: none;
        }
        
        .run-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem;
            border-bottom: 1px solid #e9ecef;
            transition: background-color 0.2s;
        }
        
        .run-item:hover {
            background-color: #f8f9fa;
            cursor: pointer;
        }
        
        .run-item:last-child {
            border-bottom: none;
        }
        
        .run-info h4 {
            color: #333;
            margin-bottom: 0.25rem;
        }
        
        .run-info p {
            color: #666;
            font-size: 0.9rem;
        }
        
        .run-stats {
            text-align: right;
        }
        
        .run-stats .metric {
            display: inline-block;
            margin-left: 1rem;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: bold;
        }
        
        .metric.success { background: #d4edda; color: #155724; }
        .metric.warning { background: #fff3cd; color: #856404; }
        .metric.danger { background: #f8d7da; color: #721c24; }
        
        .loading {
            text-align: center;
            padding: 2rem;
            color: #666;
        }
        
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9rem;
            margin-bottom: 1rem;
        }
        
        .refresh-btn:hover {
            background: #5a6fd8;
        }
        
        @media (max-width: 768px) {
            .container { padding: 1rem; }
            .header h1 { font-size: 2rem; }
            .stats-grid { grid-template-columns: 1fr; }
            .run-item { flex-direction: column; align-items: flex-start; }
            .run-stats { margin-top: 0.5rem; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ Guardrails Dashboard</h1>
        <p>Real-time monitoring of LLM safety and performance metrics</p>
    </div>
    
    <div class="container">
        <button class="refresh-btn" onclick="loadDashboard()">🔄 Refresh Data</button>
        
        <div class="stats-grid" id="stats-grid">
            <div class="loading">Loading statistics...</div>
        </div>
        
        <div class="section">
            <div class="section-header">
                <h2>📊 Recent Evaluation Runs</h2>
            </div>
            <div class="section-content">
                <ul class="runs-list" id="runs-list">
                    <li class="loading">Loading recent runs...</li>
                </ul>
            </div>
        </div>
    </div>
    
    <script>
        async function loadDashboard() {
            try {
                await Promise.all([
                    loadStats(),
                    loadRecentRuns()
                ]);
            } catch (error) {
                console.error('Error loading dashboard:', error);
            }
        }
        
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                renderStats(stats);
            } catch (error) {
                document.getElementById('stats-grid').innerHTML = '<div class="loading">Error loading statistics</div>';
            }
        }
        
        async function loadRecentRuns() {
            try {
                const response = await fetch('/api/runs');
                const runs = await response.json();
                renderRuns(runs);
            } catch (error) {
                document.getElementById('runs-list').innerHTML = '<li class="loading">Error loading runs</li>';
            }
        }
        
        function renderStats(stats) {
            const statsGrid = document.getElementById('stats-grid');
            
            const violationRate = (stats.violation_rate * 100).toFixed(1);
            const accuracy = (stats.avg_accuracy * 100).toFixed(1);
            const latency = Math.round(stats.avg_latency);
            
            statsGrid.innerHTML = `
                <div class="stat-card success">
                    <h3>Total Runs</h3>
                    <div class="value">${stats.total_runs}</div>
                </div>
                <div class="stat-card">
                    <h3>Total Evaluations</h3>
                    <div class="value">${stats.total_evaluations}</div>
                </div>
                <div class="stat-card ${accuracy >= 80 ? 'success' : 'warning'}">
                    <h3>Average Accuracy</h3>
                    <div class="value">${accuracy}%</div>
                </div>
                <div class="stat-card ${latency <= 5000 ? 'success' : 'warning'}">
                    <h3>Average Latency</h3>
                    <div class="value">${latency}ms</div>
                </div>
                <div class="stat-card ${violationRate <= 10 ? 'success' : violationRate <= 25 ? 'warning' : 'danger'}">
                    <h3>Violation Rate</h3>
                    <div class="value">${violationRate}%</div>
                </div>
            `;
        }
        
        function renderRuns(runs) {
            const runsList = document.getElementById('runs-list');
            
            if (runs.length === 0) {
                runsList.innerHTML = '<li class="loading">No evaluation runs found. Run the CLI tool first!</li>';
                return;
            }
            
            runsList.innerHTML = runs.map(run => {
                const timestamp = new Date(run.start_time).toLocaleString();
                const summary = run.summary || {};
                const accuracy = summary.accuracy_rate !== null ? (summary.accuracy_rate * 100).toFixed(1) + '%' : 'N/A';
                const latency = summary.avg_latency_ms ? Math.round(summary.avg_latency_ms) + 'ms' : 'N/A';
                const blocked = summary.blocked_count || 0;
                const total = run.total_prompts || 0;
                
                const blockedClass = blocked === 0 ? 'success' : blocked <= total * 0.1 ? 'warning' : 'danger';
                const accuracyClass = summary.accuracy_rate >= 0.8 ? 'success' : 'warning';
                
                return `
                    <li class="run-item" onclick="showRunDetails('${run.run_id}')">
                        <div class="run-info">
                            <h4>${run.model || 'Unknown Model'}</h4>
                            <p>${timestamp} • ${total} prompts • ${run.duration_seconds?.toFixed(1) || 'N/A'}s</p>
                        </div>
                        <div class="run-stats">
                            <span class="metric ${accuracyClass}">Accuracy: ${accuracy}</span>
                            <span class="metric">Latency: ${latency}</span>
                            <span class="metric ${blockedClass}">Blocked: ${blocked}/${total}</span>
                        </div>
                    </li>
                `;
            }).join('');
        }
        
        function showRunDetails(runId) {
            // For now, just log - could open a modal or navigate to details page
            console.log('Show details for run:', runId);
            alert(`Run details for ${runId} - Feature coming soon!`);
        }
        
        // Auto-refresh every 30 seconds
        setInterval(loadDashboard, 30000);
        
        // Initial load
        loadDashboard();
    </script>
</body>
</html>"""


def start_dashboard(port: int = 8080, runs_dir: str = "../llm-evals-cli/runs"):
    """Start the Guardrails Dashboard server."""
    
    # Create handler with custom runs directory
    def handler(*args, **kwargs):
        return GuardrailsHandler(*args, runs_dir=runs_dir, **kwargs)
    
    server = HTTPServer(('localhost', port), handler)
    
    print(f"""
🛡️  Guardrails Dashboard Starting...

📊 Dashboard URL: http://localhost:{port}
📁 Monitoring: {Path(runs_dir).resolve()}
🔄 Auto-refresh: Every 30 seconds

Press Ctrl+C to stop the server
""")
    
    # Try to open browser
    try:
        webbrowser.open(f'http://localhost:{port}')
    except Exception:
        pass
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped")
        server.shutdown()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Ultra-Simple Guardrails Dashboard")
    parser.add_argument("--port", type=int, default=8080, help="Port to run dashboard on")
    parser.add_argument("--runs-dir", default="../llm-evals-cli/runs", help="Directory containing evaluation runs")
    
    args = parser.parse_args()
    
    start_dashboard(port=args.port, runs_dir=args.runs_dir)
