#!/usr/bin/env python3
"""
Script di convenienza per eseguire la suite di test migliorata di Saltino
"""

import subprocess
import sys
import argparse
from pathlib import Path

def run_command(cmd_list, description):
    """Esegue un comando e mostra il risultato"""
    print(f"\n🚀 {description}")
    print("=" * 60)
    
    try:
        result = subprocess.run(cmd_list, capture_output=True, text=True)
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
            
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Errore nell'esecuzione: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Test Runner per Saltino")
    parser.add_argument("--category", "-c", choices=["arithmetic", "basic", "conditions", "functions", "lists", "error_cases"], 
                       help="Esegui solo test di una categoria specifica")
    parser.add_argument("--html", action="store_true", help="Genera report HTML")
    parser.add_argument("--verbose", "-v", action="store_true", help="Output verboso")
    parser.add_argument("--quiet", "-q", action="store_true", help="Output minimo")
    parser.add_argument("--fast", action="store_true", help="Esegui solo test veloci (escludi test con input)")
    
    args = parser.parse_args()
    
    # Costruisci il comando pytest
    cmd_parts = ["python", "-m", "pytest"]
    
    if args.verbose:
        cmd_parts.append("-v")
    elif args.quiet:
        cmd_parts.append("-q")
    
    if args.html:
        cmd_parts.extend(["--html=reports/report.html", "--self-contained-html"])
    
    if args.category:
        cmd_parts.extend(["-m", args.category])
    
    if args.fast:
        # Escludi test che richiedono input
        cmd_parts.extend(["-k", "not (main_with_params or map_operation or dot_product)"])
    
    # Aggiungi path dei test
    cmd_parts.append("tests/")
    
    # Esegui i test
    success = run_command(cmd_parts, f"Esecuzione Test Suite Saltino")
    
    if args.html and success:
        report_path = Path("reports/report.html")
        if report_path.exists():
            print(f"\n📊 Report HTML generato: {report_path.absolute()}")
    
    # Statistiche finali
    if success:
        print("\n🎉 Test completati con successo!")
        return 0
    else:
        print("\n⚠️ Alcuni test sono falliti")
        return 1

if __name__ == "__main__":
    sys.exit(main())
