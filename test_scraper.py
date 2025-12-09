#!/usr/bin/env python3
"""
Test script for ss.com-Scraper
Validates core functionality without doing full scrape
"""

import ssWebScraper as sws
import sys

def test_price_cleaning():
    """Test cleanPrices function with various inputs"""
    print("Testing cleanPrices function...")

    test_cases = [
        ('1,234.56', 1234.56, 'Comma-separated number'),
        ('500 /mon.', 500.00, 'Monthly rate'),
        ('120 /week', 480.00, 'Weekly rate (×4)'),
        ('20 /day', 600.00, 'Daily rate (×30)'),
        ('-', 0.00, 'Dash placeholder'),
        ('buy ', 0.00, 'Buy keyword'),
        ('1234', 1234.00, 'Simple number'),
    ]

    passed = 0
    failed = 0

    for input_val, expected, description in test_cases:
        result = sws.cleanPrices(input_val)
        if abs(result - expected) < 0.01:  # Float comparison
            print(f"  ✓ {description}: {input_val} -> {result}")
            passed += 1
        else:
            print(f"  ✗ {description}: Expected {expected}, got {result}")
            failed += 1

    return passed, failed

def test_district_discovery():
    """Test gatherSubCats function"""
    print("\nTesting district discovery...")

    try:
        districts = sws.gatherSubCats('https://www.ss.com/en/real-estate/flats/riga/')
        if len(districts) > 0:
            print(f"  ✓ Discovered {len(districts)} districts")
            print(f"    Sample: {list(districts.keys())[:5]}")
            return 1, 0
        else:
            print("  ✗ No districts found")
            return 0, 1
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return 0, 1

def test_small_scrape():
    """Test actual scraping with minimal data"""
    print("\nTesting scraper (1 page, 1 district)...")

    try:
        districts = sws.gatherSubCats('https://www.ss.com/en/real-estate/flats/riga/')
        # Pick any district that exists
        test_district = list(districts.keys())[0] if districts else None

        if not test_district:
            print("  ✗ No district available for testing")
            return 0, 1

        data = sws.readPostList(
            districts,
            categories=[test_district],
            page_n=1,
            verbose=False
        )

        print(f"  ✓ Scraped from {test_district}")
        print(f"    Records: {len(data)}")
        if len(data) > 0:
            print(f"    Columns: {', '.join(data.columns[:5])}...")
        return 1, 0

    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 0, 1

def main():
    """Run all tests"""
    print("=" * 60)
    print("ss.com-Scraper Test Suite")
    print("=" * 60)

    total_passed = 0
    total_failed = 0

    # Run tests
    p, f = test_price_cleaning()
    total_passed += p
    total_failed += f

    p, f = test_district_discovery()
    total_passed += p
    total_failed += f

    p, f = test_small_scrape()
    total_passed += p
    total_failed += f

    # Summary
    print("\n" + "=" * 60)
    print(f"Results: {total_passed} passed, {total_failed} failed")
    print("=" * 60)

    if total_failed == 0:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
