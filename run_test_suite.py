#!/usr/bin/env python3
"""
Script per eseguire automaticamente la suite di test completa per Saltino.
Distingue tra test che dovrebbero funzionare e test che dovrebbero generare errori.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_test(test_file, should_fail=False):
    """Esegue un singolo test e ritorna (success, output, error)"""
    try:
        result = subprocess.run(
            [sys.executable, "interpreter.py", str(test_file)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if should_fail:
            # Per i test di errore, il successo è quando il programma fallisce
            success = result.returncode != 0
        else:
            # Per i test normali, il successo è quando il programma funziona
            success = result.returncode == 0
            
        return success, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"
    except Exception as e:
        return False, "", str(e)

def main():
    test_suite_dir = Path("test_suite")
    
    if not test_suite_dir.exists():
        print("❌ Directory test_suite non trovata!")
        return 1
    
    # Test che dovrebbero funzionare
    success_tests = [
        "basic_functionality",
        "arithmetic", 
        "lists",
        "conditions",
        "functions",
        "variables_scope",
        "edge_cases"
    ]
    
    # Test che dovrebbero fallire
    error_tests = ["error_cases"]
    
    total_passed = 0
    total_failed = 0
    
    print("🧪 Esecuzione Suite di Test per Saltino")
    print("=" * 50)
    
    # Esegui test che dovrebbero funzionare
    for category in success_tests:
        category_dir = test_suite_dir / category
        if not category_dir.exists():
            continue
            
        print(f"\n📁 Categoria: {category}")
        print("-" * 30)
        
        test_files = sorted(category_dir.glob("**/*.salt"))
        for test_file in test_files:
            success, stdout, stderr = run_test(test_file, should_fail=False)
            
            if success:
                print(f"✅ {test_file.name}")
                total_passed += 1
            else:
                print(f"❌ {test_file.name}")
                if stderr:
                    print(f"   Errore: {stderr.strip()}")
                total_failed += 1
    
    # Esegui test che dovrebbero fallire  
    for category in error_tests:
        category_dir = test_suite_dir / category
        if not category_dir.exists():
            continue
            
        print(f"\n📁 Categoria: {category} (test di errori)")
        print("-" * 30)
        
        test_files = sorted(category_dir.glob("**/*.salt"))
        for test_file in test_files:
            success, stdout, stderr = run_test(test_file, should_fail=True)
            
            if success:
                print(f"✅ {test_file.name} (errore rilevato correttamente)")
                total_passed += 1
            else:
                print(f"❌ {test_file.name} (dovrebbe generare errore ma non lo fa)")
                total_failed += 1
    
    # Riassunto finale
    print("\n" + "=" * 50)
    print(f"📊 Riassunto: {total_passed} test passati, {total_failed} test falliti")
    
    if total_failed == 0:
        print("🎉 Tutti i test sono passati!")
        return 0
    else:
        print(f"⚠️  {total_failed} test hanno fallito")
        return 1

if __name__ == "__main__":
    sys.exit(main())
