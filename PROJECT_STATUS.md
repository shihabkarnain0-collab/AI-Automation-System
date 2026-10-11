# Project Status

Last updated: 2026-10-11

## Objective
AI Automation System: Python pipeline for Star Tech Bangladesh laptop research, affiliate processing, content generation and analytics, plus a JavaScript learning track and a portfolio website.

## Environment (verified)
- Windows, PowerShell
- Python 3.14.6 (.venv in project root)
- Node.js v24.21.0
- Git, branch main, remote: GitHub AI-Automation-System

## Structure
- apps/automation/: discovery, eligibility, research, analysis, affiliate, content, analytics (Python), data/*/latest.json outputs
- apps/javascript/: priceCalculator.js (+ tests), main.js
- portfolio/: personal website files

## Completed milestones
- Initial project setup, portfolio website, JavaScript foundation, product price analysis
- Price calculator (savings, discount %, validation, rounding): 6 tests pass with `node --test apps/javascript/priceCalculator.test.js`

## Known issues
- No README or automated Python tests yet
- Old backup files exist (main_backup.py, research_backup.py, analytics_old, content_old, research_old); kept until approved for cleanup
- node_modules/ is not in .gitignore yet (no npm packages installed so far)

## Security
- .env and .venv are in .gitignore and are not tracked by Git

## Next task
Decide how the JavaScript price calculator connects to the Python analysis step, after reading apps/automation/analysis.py.

## Pending decisions (need approval)
- Whether to remove or archive the old backup files
- Integration method between JavaScript calculator and Python pipeline
