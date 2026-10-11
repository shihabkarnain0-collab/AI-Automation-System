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
- Python tests for calculate_discount: 6 tests pass (run inside apps/automation: python -m unittest test_analysis -v)
- Price calculator (savings, discount %, validation, rounding): 6 tests pass with `node --test apps/javascript/priceCalculator.test.js`

## Known issues
- No README yet
- Python tests cover only calculate_discount (apps/automation/test_analysis.py); other analysis functions are untested
- get_old_price has a specs fallback that guesses the old price; checked on 2026-10-11: 0 of 26 products use it (10 have old_price directly), so low risk for now
- Scoring uses substring matching, so short terms like ai, m1, hp can match inside other words; review for scoring transparency
- Old backup files exist (main_backup.py, research_backup.py, analytics_old, content_old, research_old); kept until approved for cleanup
- node_modules/ is not in .gitignore yet (no npm packages installed so far)

## Security
- .env and .venv are in .gitignore and are not tracked by Git

## Next task
Review scoring term matching in analysis.py (short terms like ai, m1, hp can match inside other words) and add tests before changing it.

## Pending decisions (need approval)
- Whether to remove or archive the old backup files
- Confirm: keep the JavaScript calculator separate from the Python pipeline (Python already has calculate_discount)


