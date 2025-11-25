"""
Configuration for CUA Template
==============================

This file loads settings from environment variables (.env file).
Customize the variable names and defaults for your use case.

Required:
- ORGO_API_KEY: Get from https://orgo.ai (free tier available)
- ANTHROPIC_API_KEY: Get from https://console.anthropic.com

Optional:
- Service credentials (for browser login)
- ORGO_COMPUTER_ID (to reuse existing computer)
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# =============================================================================
# REQUIRED API KEYS
# =============================================================================

# Orgo API key - provides cloud desktop infrastructure
# Get yours at https://orgo.ai (free tier: 2 concurrent computers)
ORGO_API_KEY = os.getenv("ORGO_API_KEY")

# Anthropic API key - powers Claude's computer use capabilities
# Get yours at https://console.anthropic.com
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# =============================================================================
# ORGO COMPUTER SETTINGS (Optional)
# =============================================================================

# Reuse an existing computer instance instead of creating a new one
# This helps maintain login sessions between runs
# Leave empty to create a new computer each time
ORGO_COMPUTER_ID = os.getenv("ORGO_COMPUTER_ID", "")

# =============================================================================
# EMAIL SERVICE CREDENTIALS
# =============================================================================
# These are used by Claude to log into your email service via browser
# Default: Zoho Mail (change for Gmail, Outlook, etc.)

EMAIL_SERVICE_EMAIL = os.getenv("EMAIL_SERVICE_EMAIL")
EMAIL_SERVICE_PASSWORD = os.getenv("EMAIL_SERVICE_PASSWORD")

# =============================================================================
# PAYMENT SERVICE CREDENTIALS  
# =============================================================================
# These are used by Claude to log into your payment service via browser
# Default: Stripe (change for PayPal, Square, etc.)

PAYMENT_SERVICE_EMAIL = os.getenv("PAYMENT_SERVICE_EMAIL")
PAYMENT_SERVICE_PASSWORD = os.getenv("PAYMENT_SERVICE_PASSWORD")

# =============================================================================
# SEARCH KEYWORDS
# =============================================================================
# Keywords to search for in emails (comma-separated in .env)
# Claude will look for emails containing any of these keywords

SEARCH_KEYWORDS_STR = os.getenv("SEARCH_KEYWORDS", "refund,refund request,refund please")
SEARCH_KEYWORDS = [keyword.strip().lower() for keyword in SEARCH_KEYWORDS_STR.split(",")]

# =============================================================================
# DISPLAY SETTINGS
# =============================================================================
# Screen resolution for the cloud computer
# 1280x800 is optimized for Claude's computer use capabilities

DISPLAY_WIDTH = 1280
DISPLAY_HEIGHT = 800

# =============================================================================
# VALIDATION
# =============================================================================

def validate_config():
    """
    Validate that required configuration is present.
    
    Raises:
        ValueError: If required API keys are missing
    """
    missing = []
    
    if not ORGO_API_KEY:
        missing.append("ORGO_API_KEY")
    if not ANTHROPIC_API_KEY:
        missing.append("ANTHROPIC_API_KEY")
    
    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            f"Please create a .env file with these values. See .env.example for reference."
        )
    
    # Set environment variables for libraries that need them
    os.environ["ORGO_API_KEY"] = ORGO_API_KEY
    os.environ["ANTHROPIC_API_KEY"] = ANTHROPIC_API_KEY
    
    return True
