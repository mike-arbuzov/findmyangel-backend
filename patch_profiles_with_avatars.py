#!/usr/bin/env python3
"""
Script to patch existing profile outputs with avatar URLs from estban_members.csv

This script:
1. Loads member data from estban_members.csv (with avatar_url)
2. Loads existing profile JSON files
3. Matches profiles by name or LinkedIn URL
4. Updates profiles with avatar URLs
5. Saves updated profiles back to JSON files
"""

import json
import csv
import sys
from pathlib import Path
from typing import Dict, List, Optional


def load_members_csv(csv_file: str) -> Dict[str, Dict]:
    """
    Load members from CSV and create lookup dictionaries
    
    Returns:
        Dictionary with keys: by_name, by_linkedin
    """
    members_by_name = {}
    members_by_linkedin = {}
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get('name', '').strip()
                linkedin = row.get('linkedin', '').strip()
                avatar_url = row.get('avatar_url', '').strip() or None
                
                if name:
                    # Normalize name for matching (lowercase, strip)
                    normalized_name = name.lower().strip()
                    members_by_name[normalized_name] = {
                        'name': name,
                        'linkedin': linkedin,
                        'avatar_url': avatar_url
                    }
                
                if linkedin:
                    # Normalize LinkedIn URL (remove trailing slash, lowercase)
                    normalized_linkedin = linkedin.rstrip('/').lower()
                    members_by_linkedin[normalized_linkedin] = {
                        'name': name,
                        'linkedin': linkedin,
                        'avatar_url': avatar_url
                    }
    except FileNotFoundError:
        print(f"Error: CSV file '{csv_file}' not found.")
        return None
    except Exception as e:
        print(f"Error loading CSV file '{csv_file}': {e}")
        return None
    
    return {
        'by_name': members_by_name,
        'by_linkedin': members_by_linkedin
    }


def find_member_for_profile(profile: Dict, members_lookup: Dict) -> Optional[Dict]:
    """
    Find matching member data for a profile
    
    Args:
        profile: Profile dictionary
        members_lookup: Dictionary with 'by_name' and 'by_linkedin' keys
        
    Returns:
        Member data dictionary or None
    """
    # Try matching by name
    name = profile.get('name', '').strip()
    if name:
        normalized_name = name.lower().strip()
        if normalized_name in members_lookup['by_name']:
            return members_lookup['by_name'][normalized_name]
    
    return None


def patch_profiles_json(json_file: str, members_lookup: Dict, dry_run: bool = False) -> tuple[int, int]:
    """
    Patch profiles in a JSON file with avatar URLs
    
    Args:
        json_file: Path to JSON file with profiles
        members_lookup: Dictionary with member lookup data
        dry_run: If True, don't save changes
        
    Returns:
        Tuple of (updated_count, total_count)
    """
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            profiles = json.load(f)
    except FileNotFoundError:
        print(f"Error: JSON file '{json_file}' not found.")
        return 0, 0
    except Exception as e:
        print(f"Error loading JSON file '{json_file}': {e}")
        return 0, 0
    
    if not isinstance(profiles, list):
        print(f"Error: JSON file '{json_file}' does not contain a list of profiles.")
        return 0, 0
    
    updated_count = 0
    total_count = len(profiles)
    
    for profile in profiles:
        member_data = find_member_for_profile(profile, members_lookup)
        
        if member_data and member_data.get('avatar_url'):
            current_avatar = profile.get('avatar_url')
            if current_avatar != member_data['avatar_url']:
                profile['avatar_url'] = member_data['avatar_url']
                updated_count += 1
                print(f"  Updated {profile.get('name', 'Unknown')}: {member_data['avatar_url']}")
        elif member_data:
            # Member found but no avatar URL
            print(f"  No avatar URL for {profile.get('name', 'Unknown')}")
        else:
            # No matching member found
            print(f"  No match found for {profile.get('name', 'Unknown')}")
    
    if not dry_run and updated_count > 0:
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(profiles, f, indent=2, ensure_ascii=False)
            print(f"Saved {updated_count} updates to {json_file}")
        except Exception as e:
            print(f"Error saving JSON file '{json_file}': {e}")
            return updated_count, total_count
    
    return updated_count, total_count


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Patch existing profile outputs with avatar URLs from estban_members.csv'
    )
    parser.add_argument(
        '--csv',
        default='estban_members.csv',
        help='Path to estban_members.csv file (default: estban_members.csv)'
    )
    parser.add_argument(
        '--json',
        nargs='+',
        default=['angel_profiles.json', 'angel_profiles_linkup.json', 'angel_profiles_llm.json'],
        help='JSON profile files to patch (default: angel_profiles.json angel_profiles_linkup.json angel_profiles_llm.json)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be updated without saving changes'
    )
    parser.add_argument(
        '--scrape',
        action='store_true',
        help='Run scraper first to update estban_members.csv'
    )
    
    args = parser.parse_args()
    
    # Optionally run scraper first
    if args.scrape:
        print("="*60)
        print("Running scraper to update estban_members.csv...")
        print("="*60)
        from scraper import EstBANScraper
        scraper = EstBANScraper()
        members = scraper.scrape_all()
        if members:
            scraper.save_to_csv(args.csv)
            print(f"\nScraper completed. Found {len(members)} members.")
        else:
            print("\nScraper failed or found no members. Exiting.")
            sys.exit(1)
    
    # Load member data
    print("\n" + "="*60)
    print("Loading member data from CSV...")
    print("="*60)
    members_lookup = load_members_csv(args.csv)
    
    if not members_lookup:
        print("Failed to load member data. Exiting.")
        sys.exit(1)
    
    print(f"Loaded {len(members_lookup['by_name'])} members by name")
    print(f"Loaded {len(members_lookup['by_linkedin'])} members by LinkedIn URL")
    
    # Count members with avatars
    members_with_avatars = sum(
        1 for m in members_lookup['by_name'].values() if m.get('avatar_url')
    )
    print(f"Members with avatar URLs: {members_with_avatars}")
    
    # Patch each JSON file
    print("\n" + "="*60)
    print("Patching profile files...")
    print("="*60)
    
    total_updated = 0
    total_profiles = 0
    
    for json_file in args.json:
        if not Path(json_file).exists():
            print(f"\nSkipping {json_file}: File not found")
            continue
        
        print(f"\nProcessing {json_file}...")
        updated, total = patch_profiles_json(json_file, members_lookup, dry_run=args.dry_run)
        total_updated += updated
        total_profiles += total
        print(f"  Updated {updated}/{total} profiles")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total profiles processed: {total_profiles}")
    print(f"Total profiles updated: {total_updated}")
    if args.dry_run:
        print("\n(DRY RUN - No files were modified)")


if __name__ == '__main__':
    main()

