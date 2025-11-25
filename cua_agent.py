#!/usr/bin/env python3
"""
Computer Use Agent (CUA) Template
=================================

A simplified, beginner-friendly template for building Computer Use Agents.
This agent automates tasks by controlling a cloud browser - no API integrations needed.

Default use case: Processing refund requests from email -> payment processor
Easily customizable for any workflow that a human could do in a browser.

How it works:
1. Connects to a cloud computer via Orgo (free tier: 2 concurrent instances)
2. Sends a detailed prompt to Claude describing the workflow
3. Claude controls the browser to complete the task (clicks, types, navigates)
4. You watch it work or check logs after completion

To customize for your use case:
1. Modify WORKFLOW_CONFIG below with your services
2. Update build_workflow_prompt() with your specific steps
3. Update config.py with your credentials
"""

import os
import sys
import logging
import argparse
from datetime import datetime, timedelta
from typing import Optional

from orgo import Computer
from config import (
    validate_config,
    SEARCH_KEYWORDS,
    DISPLAY_WIDTH,
    DISPLAY_HEIGHT,
    EMAIL_SERVICE_EMAIL,
    EMAIL_SERVICE_PASSWORD,
    PAYMENT_SERVICE_EMAIL,
    PAYMENT_SERVICE_PASSWORD,
    ORGO_COMPUTER_ID,
)

# =============================================================================
# WORKFLOW CONFIGURATION - Customize this for your use case!
# =============================================================================

WORKFLOW_CONFIG = {
    # Email service settings (where requests come from)
    "email_service": "Zoho Mail",           # Name of your email service
    "email_url": "mail.zoho.com",           # URL to navigate to
    "email_bookmark": "Zoho Mail",          # Firefox bookmark name (optional)
    
    # Payment service settings (where actions are taken)
    "payment_service": "Stripe",            # Name of your payment service
    "payment_url": "dashboard.stripe.com",  # URL to navigate to
    "payment_bookmark": "Stripe",           # Firefox bookmark name (optional)
    
    # Action settings
    "action_name": "Refund payment",        # Button/menu text to click
    "action_menu": "three dots",            # How to access the action (e.g., "three dots menu")
    
    # What to search for in emails
    "search_keywords": SEARCH_KEYWORDS,     # Loaded from config.py
    
    # Time window for processing
    "hours_lookback": 24,                   # Only process requests from last N hours
}

# =============================================================================
# LOGGING SETUP
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cua_agent.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


# =============================================================================
# MAIN AGENT CLASS
# =============================================================================

class CUAAgent:
    """
    Computer Use Agent that automates browser-based workflows.
    
    This agent connects to a cloud computer and uses Claude to control
    the browser, completing tasks just like a human would.
    """
    
    def __init__(self, computer_id: Optional[str] = None, dry_run: bool = False):
        """
        Initialize the CUA agent.
        
        Args:
            computer_id: Optional existing computer ID to reuse. 
                        If not provided, uses ORGO_COMPUTER_ID from config.
                        If that's also empty, creates a new computer.
            dry_run: If True, don't actually perform actions (for testing)
        """
        self.computer_id = computer_id if computer_id is not None else ORGO_COMPUTER_ID
        self.dry_run = dry_run
        self.computer: Optional[Computer] = None
        
        # Validate that we have the required API keys
        validate_config()
    
    def initialize_computer(self):
        """
        Initialize or connect to an Orgo cloud computer.
        
        Orgo provides cloud desktops with browsers that Claude can control.
        Free tier includes 2 concurrent computer instances.
        """
        try:
            if self.computer_id:
                logger.info(f"Connecting to existing computer: {self.computer_id}")
                self.computer = Computer(computer_id=self.computer_id)
            else:
                logger.info("Creating new computer instance...")
                self.computer = Computer()
                self.computer_id = self.computer.computer_id
            
            logger.info(f"Computer ready! ID: {self.computer_id}")
            logger.info(f"View at: https://orgo-{self.computer_id}.orgo.dev")
            
        except Exception as e:
            logger.error(f"Failed to initialize computer: {e}")
            raise
    
    def get_time_strings(self) -> tuple[str, str]:
        """Get current time and lookback time as formatted strings."""
        now = datetime.now()
        lookback = now - timedelta(hours=WORKFLOW_CONFIG["hours_lookback"])
        return now.strftime("%Y-%m-%d %H:%M:%S"), lookback.strftime("%Y-%m-%d %H:%M:%S")
    
    def build_workflow_prompt(self) -> str:
        """
        Build the detailed prompt that tells Claude exactly what to do.
        
        This is the core of your automation - modify this to change the workflow.
        The prompt should be detailed and specific, like instructions for a new employee.
        
        CUSTOMIZATION TIP: 
        - Be very specific about what to click and where
        - Include fallback instructions for common variations
        - Add "CRITICAL" notes for steps that often go wrong
        """
        current_time, lookback_time = self.get_time_strings()
        
        # Get configuration values
        config = WORKFLOW_CONFIG
        keywords_str = ", ".join(config["search_keywords"])
        
        # Build credentials sections
        email_creds = ""
        if EMAIL_SERVICE_EMAIL and EMAIL_SERVICE_PASSWORD:
            email_creds = f"\n   - Email: {EMAIL_SERVICE_EMAIL}\n   - Password: {EMAIL_SERVICE_PASSWORD}"
        
        payment_creds = ""
        if PAYMENT_SERVICE_EMAIL and PAYMENT_SERVICE_PASSWORD:
            payment_creds = f"\n   - Email: {PAYMENT_SERVICE_EMAIL}\n   - Password: {PAYMENT_SERVICE_PASSWORD}"
        
        # =====================================================================
        # THE WORKFLOW PROMPT - This is what Claude will execute
        # Modify this section to change what the agent does
        # =====================================================================
        
        prompt = f"""You are an automation agent tasked with processing requests.
Current time: {current_time}
Only process requests from the last {config["hours_lookback"]} hours (since {lookback_time}).

{"="*60}
WORKFLOW STEPS
{"="*60}

1. OPEN BROWSER
   - Open Firefox browser (if not already open)
   - Look for bookmarks for "{config["email_bookmark"]}" and "{config["payment_bookmark"]}"
   - If bookmarks exist, you can use them for faster navigation

2. GO TO EMAIL ({config["email_service"]})
   - Navigate to: {config["email_url"]}
   - Check if you're already logged in (look for inbox, profile icon, etc.)
   - If NOT logged in, use these credentials:{email_creds if email_creds else " (check environment variables)"}
   - Verify you're in the correct account

3. SEARCH FOR REQUESTS
   - Search for emails containing: {keywords_str}
   - CRITICAL: Just type the search term and press Enter
   - CRITICAL: Do NOT click dropdown suggestions that appear while typing
   - CRITICAL: Only process emails from the last {config["hours_lookback"]} hours
   - If no matching emails found, the task is complete - log "No requests found" and finish

4. FOR EACH REQUEST FOUND (process one at a time):

   a. EXTRACT INFORMATION
      - Open the email
      - Find the customer's email address (usually in "From" field or email body)
      - Note any specific details mentioned (amounts, order numbers, etc.)
   
   b. GO TO PAYMENT SERVICE ({config["payment_service"]})
      - Navigate to: {config["payment_url"]}
      - Log in if needed using:{payment_creds if payment_creds else " (check environment variables)"}
      - Verify you're logged in
   
   c. FIND THE CUSTOMER
      - Go to the Payments or Customers section
      - Search for the customer by their email address
      - Wait for results to load
      - Verify you found the correct customer (email must match exactly)
   
   d. PERFORM THE ACTION
      - Find the relevant transaction/payment
      - Click the {config["action_menu"]} menu (usually ⋯ or ...)
      - Click "{config["action_name"]}"
      - Confirm the action if prompted
      - Wait for success confirmation
      - Take a screenshot to document the action
   
   e. RETURN TO EMAIL
      - Go back to {config["email_service"]}
      - Process the next request

5. COMPLETION
   - After all requests are processed, take a final screenshot
   - Log a summary of actions taken
   - Your task is complete

{"="*60}
IMPORTANT RULES
{"="*60}

- Process requests ONE AT A TIME (not in parallel)
- Take screenshots after important steps for verification
- If you encounter an error, take a screenshot and try to recover
- If a customer is not found, skip and move to the next request
- If an action was already performed, skip and move to the next
- Be careful and methodical - accuracy over speed

{f"[DRY RUN MODE] Do NOT actually click action buttons. Instead, take screenshots and describe what you would do." if self.dry_run else ""}

Begin by opening the browser and starting the workflow."""

        return prompt
    
    def run(self):
        """
        Execute the CUA workflow.
        
        This method:
        1. Initializes the cloud computer
        2. Sends the workflow prompt to Claude
        3. Claude controls the browser to complete the task
        4. Logs progress and results
        """
        try:
            logger.info("=" * 60)
            logger.info("STARTING CUA WORKFLOW")
            logger.info("=" * 60)
            logger.info(f"Dry run mode: {self.dry_run}")
            logger.info(f"Email service: {WORKFLOW_CONFIG['email_service']}")
            logger.info(f"Payment service: {WORKFLOW_CONFIG['payment_service']}")
            
            # Step 1: Connect to cloud computer
            self.initialize_computer()
            
            # Step 2: Build the workflow prompt
            prompt = self.build_workflow_prompt()
            logger.debug(f"Workflow prompt:\n{prompt}")
            
            # Step 3: Define callback to log Claude's actions
            def progress_callback(event_type, event_data):
                """Log what Claude is doing in real-time."""
                if event_type == "text":
                    logger.info(f"Claude: {event_data}")
                elif event_type == "tool_use":
                    action = event_data.get('action', 'unknown')
                    logger.info(f"Action: {action}")
                    if 'coordinate' in event_data:
                        logger.debug(f"  Click at: {event_data['coordinate']}")
                elif event_type == "thinking":
                    logger.debug(f"Thinking: {event_data[:200]}...")  # Truncate long thoughts
                elif event_type == "error":
                    logger.error(f"Error: {event_data}")
            
            # Step 4: Execute the workflow via Claude
            logger.info("Sending workflow to Claude...")
            
            messages = self.computer.prompt(
                prompt,
                callback=progress_callback,
                model="claude-haiku-4-5-20251001",  # Fast and cost-effective
                display_width=DISPLAY_WIDTH,
                display_height=DISPLAY_HEIGHT,
                thinking_enabled=True,
                thinking_budget=1024,
                max_iterations=50,  # Allow up to 50 actions
                max_tokens=8192,
            )
            
            # Step 5: Log completion
            logger.info("=" * 60)
            logger.info("WORKFLOW COMPLETE")
            logger.info("=" * 60)
            logger.info(f"Computer ID: {self.computer_id}")
            logger.info(f"Computer URL: https://orgo-{self.computer_id}.orgo.dev")
            logger.info(f"Dry run: {self.dry_run}")
            logger.info("Computer remains running for future use.")
            logger.info("=" * 60)
            
        except KeyboardInterrupt:
            logger.warning("Workflow interrupted by user (Ctrl+C)")
            raise
        except Exception as e:
            logger.error(f"Workflow failed: {e}", exc_info=True)
            # Try to capture a screenshot for debugging
            if self.computer:
                try:
                    self.computer.screenshot()
                    logger.info("Debug screenshot captured")
                except:
                    pass
            raise


# =============================================================================
# COMMAND LINE INTERFACE
# =============================================================================

def main():
    """
    Main entry point - handles command line arguments.
    
    Usage:
        python cua_agent.py                    # Run normally
        python cua_agent.py --dry-run          # Test without performing actions
        python cua_agent.py --computer-id X    # Reuse existing computer
        python cua_agent.py --verbose          # Show detailed logs
    """
    parser = argparse.ArgumentParser(
        description="CUA Template - Automate browser workflows with Claude",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cua_agent.py                     Run the workflow
  python cua_agent.py --dry-run           Test without taking actions  
  python cua_agent.py --computer-id abc   Reuse existing computer
  python cua_agent.py --verbose           Show detailed debug logs
        """
    )
    parser.add_argument(
        "--computer-id",
        type=str,
        help="Reuse an existing Orgo computer instance by ID"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in test mode - describe actions without performing them"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable detailed debug logging"
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")
    
    # Create and run the agent
    agent = CUAAgent(computer_id=args.computer_id, dry_run=args.dry_run)
    
    try:
        agent.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

