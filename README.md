# Find My Angel - Business Angel Profile Extractor

A tool for extracting business angel personal and investment profile data from LinkedIn profiles.

## Features

- **Personal Profile Extraction**: Extracts name, headline, location, current role, company, summary, experience, and education
- **Investment Profile Extraction**: Identifies investors, extracts portfolio companies, investment focus areas, sectors of interest, and investment stage preferences
- **Batch Processing**: Extract profiles for multiple business angels at once
- **Data Export**: Export extracted profiles to JSON or CSV formats
- **Rate Limiting**: Built-in delays to respect LinkedIn's rate limits

## Installation

```bash
pip install -r requirements.txt
```

## Dependencies

- `requests` - HTTP library for fetching web pages
- `beautifulsoup4` - HTML parsing library
- `lxml` - XML/HTML parser

## Usage

### Basic Usage: Extract Single Profile

```python
from profile_extractor import extract_angel_profile

profile = extract_angel_profile(
    name="John Doe",
    linkedin_url="https://www.linkedin.com/in/johndoe"
)

print(profile)
```

### Batch Extraction

```python
from profile_extractor import ProfileExtractor

# List of business angels
angels = [
    {'name': 'Angel 1', 'linkedin': 'https://www.linkedin.com/in/angel1'},
    {'name': 'Angel 2', 'linkedin': 'https://www.linkedin.com/in/angel2'},
]

# Create extractor
extractor = ProfileExtractor(delay=2)  # 2 second delay between requests

# Extract all profiles
profiles = extractor.extract_profiles_batch(angels)

# Save results
extractor.save_profiles_json('profiles.json')
extractor.save_profiles_csv('profiles.csv')
```

### Extract from EstBAN Scraper Results

```python
import json
from profile_extractor import ProfileExtractor

# Load members from EstBAN scraper
with open('estban_members.json', 'r') as f:
    members = json.load(f)

# Filter to those with LinkedIn
members_with_linkedin = [m for m in members if m.get('linkedin')]

# Extract profiles
extractor = ProfileExtractor(delay=2)
profiles = extractor.extract_profiles_batch(members_with_linkedin)

# Save results
extractor.save_profiles_json('angel_profiles.json')
extractor.save_profiles_csv('angel_profiles.csv')
```

## Profile Data Structure

Each extracted profile contains:

### Personal Information
- `name`: Full name
- `headline`: LinkedIn headline
- `location`: Geographic location
- `current_role`: Current job title
- `company`: Current company
- `summary`: Profile summary/about section
- `experience`: List of work experience entries
- `education`: List of education entries

### Investment Profile
- `is_investor`: Boolean indicating if person is identified as an investor
- `investment_role`: Investment role (e.g., "Angel Investor", "VC Partner")
- `investment_focus`: Focus areas (e.g., "Early Stage", "B2B")
- `portfolio_companies`: List of portfolio companies
- `sectors_of_interest`: List of sectors (e.g., "tech", "fintech", "AI")
- `investment_stage`: Investment stages (e.g., "seed", "series a")

## Example Output

```json
{
  "name": "John Doe",
  "linkedin_url": "https://www.linkedin.com/in/johndoe",
  "personal_info": {
    "name": "John Doe",
    "headline": "Angel Investor | Startup Advisor",
    "location": "San Francisco, CA",
    "current_role": "Angel Investor",
    "company": "Independent",
    "summary": "Experienced angel investor...",
    "experience": [...],
    "education": [...]
  },
  "investment_profile": {
    "is_investor": true,
    "investment_role": "Angel Investor",
    "investment_focus": ["Early Stage", "B2B"],
    "portfolio_companies": ["Company A", "Company B"],
    "sectors_of_interest": ["tech", "saas", "fintech"],
    "investment_stage": ["seed", "series a"]
  },
  "extraction_status": "success"
}
```

## Important Notes

⚠️ **LinkedIn Rate Limiting**: LinkedIn may require authentication or rate limit requests. The tool includes:
- Built-in delays between requests (default: 2 seconds)
- Detection of authentication requirements
- Error handling for failed requests

⚠️ **LinkedIn Structure Changes**: LinkedIn frequently updates their HTML structure. The extractor uses flexible selectors, but may need updates if LinkedIn changes their layout significantly.

## Files

- `scraper.py` - EstBAN members page scraper
- `profile_extractor.py` - Profile extractor class for business angels
- `profile_extractor_example.py` - Example usage scripts
- `requirements.txt` - Python dependencies

## License

MIT License
