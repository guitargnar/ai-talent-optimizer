#!/usr/bin/env python3
"""
Non-interactive wrapper for verify_metrics.py
Runs without user input for automation
"""

import sys
import os

# Suppress input calls
class NoInput:
    def __call__(self, *args, **kwargs):
        return "no"
    def strip(self):
        return "no"

# Monkey-patch input
import builtins
builtins.input = NoInput()

# Import and run the original script
sys.path.insert(0, os.path.dirname(__file__))
script_name = "verify_metrics"
module = __import__(script_name)

# Run main if exists
if hasattr(module, 'main'):
    try:
        module.main()
    except (EOFError, KeyboardInterrupt):
        print("\nScript completed (non-interactive mode)")
