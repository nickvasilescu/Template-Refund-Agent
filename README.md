# CUA Template - Computer Use Agent

A beginner-friendly template for building **Computer Use Agents** - AI agents that control a browser to automate tasks, just like a human would.

**Default Use Case:** Automatically process refund requests from email (Zoho Mail) to payment processor (Stripe).

## Why Computer Use Agents?

| Traditional Automation | Computer Use Agents |
|------------------------|---------------------|
| Learn complex APIs | Describe tasks in plain English |
| Handle OAuth flows | Just use login credentials |
| Debug API responses | Watch it work visually |
| Days to build | Hours to build |

**Start with CUA to get value fast, then optimize with APIs later.**

---

## Prerequisites

Before you begin, make sure you have the following installed on your computer:

### 1. Git (for cloning the repository)

**Check if installed:**
```bash
git --version
```

**Install if needed:**
- **Mac:** Open Terminal and run `xcode-select --install`
- **Windows:** Download from [git-scm.com](https://git-scm.com/download/win)
- **Linux:** `sudo apt install git` (Ubuntu/Debian) or `sudo dnf install git` (Fedora)

### 2. Python 3.8 or higher

**Check if installed:**
```bash
python3 --version
```

**Install if needed:**
- **Mac:** `brew install python` (if you have [Homebrew](https://brew.sh)) or download from [python.org](https://www.python.org/downloads/)
- **Windows:** Download from [python.org](https://www.python.org/downloads/) (check "Add Python to PATH" during install!)
- **Linux:** `sudo apt install python3 python3-pip python3-venv`

### 3. A Code Editor (Recommended: Cursor)

We recommend **Cursor** - an AI-powered code editor that makes working with this template even easier:
- Download from [cursor.com](https://cursor.com)
- It's free and works on Mac, Windows, and Linux
- You can also use VS Code, PyCharm, or any text editor you prefer

### 4. API Keys (Free to start)

You'll need accounts with these services:

| Service | Sign Up | Cost |
|---------|---------|------|
| **Orgo** | [orgo.ai](https://orgo.ai) | Free tier: 2 concurrent computers |
| **Anthropic** | [console.anthropic.com](https://console.anthropic.com) | Pay as you go (~$0.10-0.50 per run) |

---

## Getting Started

### Step 1: Clone this Repository

Open your terminal (Mac/Linux) or Command Prompt (Windows) and run:

```bash
git clone https://github.com/nickvasilescu/Template-Refund-Agent.git
cd Template-Refund-Agent
```

> 💡 **Tip:** If you're using Cursor, you can open the terminal with `Ctrl+`` (backtick) or `Cmd+`` on Mac.

### Step 2: Create a Virtual Environment

This keeps your project's packages separate from other Python projects:

```bash
# Create the virtual environment
python3 -m venv venv

# Activate it
# On Mac/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

> ✅ You'll know it's working when you see `(venv)` at the start of your terminal prompt.

### Step 3: Install Required Packages

```bash
pip install -r requirements.txt
```

This installs:
- `orgo` - Cloud desktop infrastructure
- `anthropic` - Claude AI SDK
- `python-dotenv` - Environment variable loader

### Step 4: Set Up Your Credentials

Create your environment file from the template:

```bash
cp .env.example .env
```

Now open `.env` in your editor and fill in your values:

```env
# Required API Keys
ORGO_API_KEY=your_orgo_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Email Service (default: Zoho Mail)
EMAIL_SERVICE_EMAIL=your_email@zoho.com
EMAIL_SERVICE_PASSWORD=your_password

# Payment Service (default: Stripe)
PAYMENT_SERVICE_EMAIL=your_stripe_email
PAYMENT_SERVICE_PASSWORD=your_stripe_password
```

> ⚠️ **Security:** Never share your `.env` file or commit it to GitHub!

### Step 5: Test with a Dry Run

Before running for real, test that everything is connected:

```bash
python cua_agent.py --dry-run --verbose
```

This runs through the workflow without actually clicking any action buttons.

### Step 6: Run for Real

Once your dry run succeeds:

```bash
python cua_agent.py
```

🎉 Watch the agent work at: `https://orgo-{computer_id}.orgo.dev`

---

## Command Line Options

```bash
python cua_agent.py                     # Run normally
python cua_agent.py --dry-run           # Test without taking actions
python cua_agent.py --computer-id ID    # Reuse existing computer
python cua_agent.py --verbose           # Show detailed logs
```

## How It Works

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Your Script   │────▶│  Orgo Cloud      │────▶│    Claude AI    │
│  (cua_agent.py) │     │  Desktop         │     │  (Controls      │
│                 │     │  (Firefox)       │     │   Browser)      │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                              │
                              ▼
                        ┌──────────────────┐
                        │  Zoho Mail →     │
                        │  Find refunds →  │
                        │  Stripe →        │
                        │  Process refund  │
                        └──────────────────┘
```

1. **Your script** connects to Orgo (cloud desktop with Firefox)
2. **Claude receives** a detailed prompt describing the workflow
3. **Claude controls** the browser: clicks, types, navigates
4. **Claude completes** the task and logs results

## Customization Guide

### Change Services (Email/Payment)

Edit `WORKFLOW_CONFIG` in `cua_agent.py`:

```python
WORKFLOW_CONFIG = {
    # Change email service
    "email_service": "Gmail",               # Was: "Zoho Mail"
    "email_url": "mail.google.com",         # Was: "mail.zoho.com"
    
    # Change payment service
    "payment_service": "PayPal",            # Was: "Stripe"  
    "payment_url": "paypal.com/business",   # Was: "dashboard.stripe.com"
    
    # Change action
    "action_name": "Issue refund",          # Button text to click
    ...
}
```

### Change Keywords

Edit `.env`:

```env
# For cancellations instead of refunds
SEARCH_KEYWORDS=cancel,cancellation,cancel order,cancel subscription
```

### Change the Workflow

Edit `build_workflow_prompt()` in `cua_agent.py`. The prompt is like instructions for a new employee - be specific about:
- What to click
- What to look for
- How to handle edge cases

### Different Use Cases

This template can be adapted for:

- **Order fulfillment**: Email → Inventory system
- **Lead processing**: Email → CRM
- **Support tickets**: Email → Help desk
- **Invoice processing**: Email → Accounting software
- **Social media**: Notifications → Response actions

## Cost Expectations

| Resource | Cost | Notes |
|----------|------|-------|
| **Orgo** | Free | 2 concurrent computers on free tier |
| **Claude** | ~$0.10-0.50/run | Depends on workflow complexity |

A typical refund workflow uses ~10-50 Claude actions, costing roughly $0.10-0.50.

## File Structure

```
├── cua_agent.py       # Main agent (run this)
├── config.py          # Configuration loader
├── requirements.txt   # Python dependencies
├── .env.example       # Template for credentials
├── .env               # Your credentials (don't commit!)
└── README.md          # This file
```

## Troubleshooting

### "Missing API keys"
- Check `.env` file exists and has valid keys
- Run `cat .env` to verify (don't share the output!)

### "Computer connection failed"
- Verify Orgo API key at [orgo.ai](https://orgo.ai)
- Check if you've hit free tier limits

### "Login failed"
- Verify credentials in `.env`
- For Gmail: Use App Password, not regular password
- Try logging in manually first to check for 2FA prompts

### "Can't find emails/buttons"
- Run with `--verbose` to see Claude's actions
- Check screenshots in logs
- The UI might have changed - update the prompt

### Reusing Computers

Save the computer ID from logs to reuse it:

```bash
# First run - note the computer ID
python cua_agent.py
# Logs: "Computer ready! ID: abc-123-def"

# Future runs - reuse that computer
python cua_agent.py --computer-id abc-123-def
```

Benefits: Maintains login sessions, faster startup.

## Security Notes

- **Never commit `.env`** to version control
- The agent has access to your credentials - only run on trusted computers
- Review the workflow before running in production
- Use `--dry-run` to test first

## Learn More

- [Orgo Documentation](https://orgo.ai/docs)
- [Claude Computer Use](https://docs.anthropic.com/en/docs/computer-use)
- [Video Tutorial](#) <!-- Add your YouTube link here -->

## License

MIT - Use freely for personal or commercial projects.
