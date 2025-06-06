#!/usr/bin/env python3

# Test import of interpreter module
try:
    print("Importing interpreter module...")
    import interpreter
    print("✓ interpreter module imported successfully")
    
    print("Looking for IterativeSaltinoInterpreter class...")
    if hasattr(interpreter, 'IterativeSaltinoInterpreter'):
        print("✓ IterativeSaltinoInterpreter class found")
        cls = getattr(interpreter, 'IterativeSaltinoInterpreter')
        print(f"Class: {cls}")
        
        # Try to instantiate
        print("Trying to instantiate...")
        instance = cls()
        print("✓ Instance created successfully")
    else:
        print("✗ IterativeSaltinoInterpreter class not found")
        print("Available attributes:")
        for attr in dir(interpreter):
            if not attr.startswith('_'):
                print(f"  - {attr}")
                
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
