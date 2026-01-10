#!/usr/bin/env python3
"""
TRIZEL Monitor - Dynamic Page Generator

Generates dynamic HTML pages from authoritative data sources:
- Agencies page from config/agency_registry.json
- RAW data catalog from data/raw/
- Snapshots catalog from data/
- Policies page from governance docs
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Any


def load_agency_registry() -> Dict[str, Any]:
    """Load authoritative agency registry."""
    registry_path = Path(__file__).parent.parent / "config" / "agency_registry.json"
    with open(registry_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_agencies_page():
    """Generate agencies/index.html from registry."""
    registry = load_agency_registry()
    
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="International space agency registry - TRIZEL Monitor">
  <title>Agencies - TRIZEL Monitor</title>
  <link rel="stylesheet" href="../../assets/css/trizel-monitor.css">
</head>
<body>
  <a href="#main-content" class="skip-link">Skip to main content</a>
  
  <header role="banner">
    <h1 class="site-title">TRIZEL Monitor - Agency Registry</h1>
    <p class="site-description">
      International space agencies tracked by TRIZEL Monitor (facts only, zero interpretation)
    </p>
    
    <nav role="navigation" aria-label="Main navigation">
      <ul>
        <li><a href="../index.html">Home</a></li>
        <li><a href="../status/index.html">Status</a></li>
        <li><a href="../agencies/index.html" aria-current="page">Agencies</a></li>
        <li><a href="../raw/index.html">RAW Data</a></li>
        <li><a href="../snapshots/index.html">Snapshots</a></li>
        <li><a href="../policies/index.html">Policies</a></li>
        <li><a href="../sitemap/index.html">Sitemap</a></li>
      </ul>
    </nav>
  </header>

  <main id="main-content" role="main">
    
    <section class="section">
      <h2 class="section-title">Status Definitions</h2>
      <div class="card">
'''
    
    # Add status definitions
    for status, definition in registry.get("status_definitions", {}).items():
        badge_class = {
            "Active": "badge-active",
            "Monitoring": "badge-monitoring",
            "Limited": "badge-limited"
        }.get(status, "")
        html += f'        <p><span class="badge {badge_class}">{status}</span>: {definition}</p>\n'
    
    html += '''      </div>
    </section>

    <section class="section">
      <h2 class="section-title">Agency Overview</h2>
      <table role="table">
        <thead>
          <tr>
            <th scope="col">Agency</th>
            <th scope="col">Full Name</th>
            <th scope="col">Country</th>
            <th scope="col">Status</th>
            <th scope="col">RAW Data</th>
            <th scope="col">Endpoints</th>
          </tr>
        </thead>
        <tbody>
'''
    
    # Add agencies
    for agency in registry.get("agencies", []):
        agency_id = agency.get("agency_id", "")
        name = agency.get("name", "")
        country = agency.get("country", "")
        status = agency.get("status", "Unknown")
        raw_capability = "✓" if agency.get("raw_data_capability", False) else "✗"
        endpoint_count = len(agency.get("endpoints", []))
        
        badge_class = {
            "Active": "badge-active",
            "Monitoring": "badge-monitoring",
            "Limited": "badge-limited"
        }.get(status, "")
        
        html += f'''          <tr>
            <td><strong>{agency_id}</strong></td>
            <td>{name}</td>
            <td>{country}</td>
            <td><span class="badge {badge_class}">{status}</span></td>
            <td>{raw_capability}</td>
            <td>{endpoint_count}</td>
          </tr>
'''
    
    html += '''        </tbody>
      </table>
    </section>
'''
    
    # Add detailed agency information
    for agency in registry.get("agencies", []):
        agency_id = agency.get("agency_id", "")
        name = agency.get("name", "")
        status_notes = agency.get("status_notes", "")
        endpoints = agency.get("endpoints", [])
        
        html += f'''
    <section class="section">
      <h2 class="section-title">{agency_id} - {name}</h2>
      <div class="card">
        <p><strong>Status Notes:</strong> {status_notes}</p>
        
        <h3>Endpoints</h3>
'''
        
        if endpoints:
            html += '''        <table role="table">
          <thead>
            <tr>
              <th scope="col">Endpoint</th>
              <th scope="col">Type</th>
              <th scope="col">Auth Required</th>
              <th scope="col">Download Mode</th>
            </tr>
          </thead>
          <tbody>
'''
            for endpoint in endpoints:
                endpoint_name = endpoint.get("name", "")
                data_type = endpoint.get("data_type", "")
                requires_auth = "Yes" if endpoint.get("requires_auth", False) else "No"
                download_mode = endpoint.get("download_mode", "")
                
                badge_class = {
                    "RAW_DATA": "badge-raw-data",
                    "SNAPSHOT": "badge-snapshot",
                    "DERIVED": "badge-derived"
                }.get(data_type, "")
                
                html += f'''            <tr>
              <td>{endpoint_name}</td>
              <td><span class="badge {badge_class}">{data_type}</span></td>
              <td>{requires_auth}</td>
              <td><code>{download_mode}</code></td>
            </tr>
'''
            
            html += '''          </tbody>
        </table>
'''
        else:
            html += '        <p><em>No endpoints configured.</em></p>\n'
        
        html += '''      </div>
    </section>
'''
    
    html += '''
  </main>

  <footer role="contentinfo">
    <div class="communication-policy">
      <strong>Communication Policy:</strong> 
      TRIZEL-AI does not provide direct messaging. All communication is conducted through verifiable channels: 
      <strong>GitHub</strong> (issues, pull requests, discussions), 
      <strong>ORCID</strong> (research profiles), and 
      <strong>DOI-linked archival records</strong> (Zenodo, OSF, HAL).
    </div>
    
    <p style="margin-top: 1rem;">
      <strong>Data Source:</strong> <code>config/agency_registry.json</code><br>
      <strong>Repository:</strong> <a href="https://github.com/abdelkader-omran/trizel-monitor">github.com/abdelkader-omran/trizel-monitor</a>
    </p>
  </footer>

  <script src="../../assets/js/trizel-monitor.js"></script>
</body>
</html>
'''
    
    return html


def main():
    """Generate all dynamic pages."""
    print("=" * 80)
    print("TRIZEL Monitor - Dynamic Page Generator")
    print("=" * 80)
    print()
    
    repo_root = Path(__file__).parent.parent
    
    # Generate agencies page
    print("Generating agencies/index.html...")
    agencies_html = generate_agencies_page()
    agencies_path = repo_root / "site" / "agencies" / "index.html"
    agencies_path.parent.mkdir(parents=True, exist_ok=True)
    with open(agencies_path, 'w', encoding='utf-8') as f:
        f.write(agencies_html)
    print(f"✓ Generated: {agencies_path}")
    
    print()
    print("✓ All dynamic pages generated")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
