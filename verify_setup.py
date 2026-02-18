
"""
Verify setup is complete
Run: python verify_setup.py
"""

import sys
import os
from pathlib import Path

def verify_folders():
    """Check folder structure"""
    required = [
        'backend/ml',
        'backend/api',
        'backend/data',
        'models/checkpoints',
        'data/eurosat'
    ]
    
    print("Checking folders...")
    all_good = True
    for folder in required:
        if Path(folder).exists():
            print(f"   {folder}")
        else:
            print(f"   {folder} - MISSING")
            all_good = False
    return all_good

def verify_packages():
    """Check required packages"""
    required = ['tensorflow', 'numpy', 'PIL', 'matplotlib']
    
    print("\nChecking packages...")
    all_good = True
    for package in required:
        try:
            __import__(package)
            print(f"   {package}")
        except ImportError:
            print(f"   {package} - NOT INSTALLED")
            all_good = False
    return all_good

def verify_git():
    """Check git status"""
    print("\nChecking Git...")
    
    # Check if git repo
    if Path('.git').exists():
        print("   Git repository initialized")
    else:
        print("   Not a git repository")
        return False
    
    # Check branch
    branch = os.popen('git branch --show-current').read().strip()
    print(f"   Current branch: {branch}")
    
    return True

def verify_venv():
    """Check virtual environment"""
    print("\nChecking virtual environment...")
    
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("   Virtual environment active")
        return True
    else:
        print("   Virtual environment NOT active")
        print("     Run: source venv/bin/activate")
        return False

if __name__ == "__main__":
    print("="*60)
    print("SETUP VERIFICATION")
    print("="*60 + "\n")
    
    results = [
        verify_venv(),
        verify_folders(),
        verify_packages(),
        verify_git()
    ]
    
    print("\n" + "="*60)
    if all(results):
        print(" ALL CHECKS PASSED!")
        print("You're ready for the model code!")
    else:
        print(" SOME CHECKS FAILED")
        print("Fix the issues above before continuing.")
    print("="*60)
