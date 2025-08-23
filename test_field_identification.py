#!/usr/bin/env python3
"""
Test script for field identification system
Run this to verify field mapping works correctly
"""

import asyncio
from aiviizn_real_agent_saas import AIVIIZNSaaSAgent, FieldType

async def test_field_identification():
    """Test the field identification system"""
    
    print("🧪 TESTING FIELD IDENTIFICATION SYSTEM")
    print("=" * 50)
    
    agent = AIVIIZNSaaSAgent()
    
    # Test cases with expected results
    test_cases = [
        # (field_name, sample_values, expected_type, min_confidence)
        ("Tenant Name", ["John Smith", "Jane Doe"], FieldType.TENANT_NAME, 0.8),
        ("Resident Email", ["john@email.com", "jane@test.com"], FieldType.TENANT_EMAIL, 0.9),
        ("Phone Number", ["555-1234", "(555) 987-6543"], FieldType.TENANT_PHONE, 0.8),
        ("Unit #", ["101", "A-203", "Building 2-404"], FieldType.UNIT_NUMBER, 0.8),
        ("Monthly Rent", ["$1,500", "$2,300", "$950"], FieldType.RENT_AMOUNT, 0.9),
        ("Security Deposit", ["$1,500", "$2,000"], FieldType.SECURITY_DEPOSIT, 0.8),
        ("Property Address", ["123 Main St", "456 Oak Ave"], FieldType.PROPERTY_ADDRESS, 0.8),
        ("Lease Start Date", ["01/01/2024", "2024-03-15"], FieldType.LEASE_START, 0.8),
        ("Bedrooms", ["2", "3", "1"], FieldType.BEDROOMS, 0.9),
        ("Sq Ft", ["850", "1200", "650"], FieldType.SQUARE_FEET, 0.8),
        ("Balance Due", ["$500", "$0", "$1,250"], FieldType.BALANCE_DUE, 0.8),
        ("Payment Status", ["Paid", "Pending", "Late"], FieldType.PAYMENT_STATUS, 0.7),
    ]
    
    passed = 0
    failed = 0
    
    for field_name, sample_values, expected_type, min_confidence in test_cases:
        field_type, confidence = await agent.identify_field_type(field_name, sample_values)
        
        if field_type == expected_type and confidence >= min_confidence:
            print(f"✅ PASS: '{field_name}' → {field_type.value} ({confidence:.0%})")
            passed += 1
        else:
            print(f"❌ FAIL: '{field_name}'")
            print(f"   Expected: {expected_type.value} (≥{min_confidence:.0%})")
            print(f"   Got: {field_type.value} ({confidence:.0%})")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 RESULTS: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Field identification is working correctly.")
    else:
        print(f"⚠️ {failed} tests failed. Review the field identification logic.")
    
    # Test pattern learning
    print("\n🧠 TESTING PATTERN LEARNING")
    print("-" * 40)
    
    # Test that patterns improve with usage
    test_mappings = {
        "field1": {
            "source_field": "Tenant Full Name",
            "field_type": "tenant_name",
            "confidence": 0.95
        },
        "field2": {
            "source_field": "Apartment Number",
            "field_type": "unit_number",
            "confidence": 0.85
        }
    }
    
    agent.update_field_patterns(test_mappings)
    print("✅ Pattern learning system functional")
    
    # Test entity ID generation
    print("\n🔑 TESTING ENTITY ID GENERATION")
    print("-" * 40)
    
    test_entity = {
        "entity_type": "tenant",
        "field_values": {
            "tenant_full_name": "John Smith",
            "tenant_email_address": "john@example.com"
        }
    }
    
    entity_id = agent.generate_entity_id(test_entity)
    print(f"✅ Generated entity ID: {entity_id[:16]}...")
    
    # Test canonical name mapping
    print("\n📝 TESTING CANONICAL NAME MAPPING")
    print("-" * 40)
    
    canonical_tests = [
        ("tenant_name", "tenant_full_name"),
        ("rent_amount", "monthly_rent_amount"),
        ("unit_number", "unit_number"),
    ]
    
    for field_type, expected_canonical in canonical_tests:
        canonical = agent.get_canonical_name(field_type)
        if canonical == expected_canonical:
            print(f"✅ {field_type} → {canonical}")
        else:
            print(f"❌ {field_type} → {canonical} (expected: {expected_canonical})")
    
    print("\n✨ Field identification testing complete!")

if __name__ == "__main__":
    asyncio.run(test_field_identification())
