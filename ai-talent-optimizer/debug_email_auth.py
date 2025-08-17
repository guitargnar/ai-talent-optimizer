#!/usr/bin/env python3
"""
Debug Email Authentication
Tests different password formats and provides detailed debugging
"""

import smtplib
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)


def test_password_variations():
    """Test different password formats"""
    
    email = "matthewdscott7@gmail.com"
    
    # The password you provided: "qvjr afdk gvra gbf"
    # Different possible interpretations
    passwords