import os
from supabase import create_client, Client
from datetime import datetime, timedelta
import random
import string

# Initialize Supabase client with service key for admin access
url = "https://sejebqdhcilwcpjpznep.supabase.co"
# You should use the service_role_key here, not the anon key
# The service role key bypasses RLS policies
service_key = "YOUR_SERVICE_ROLE_KEY"  # Replace with actual service role key
supabase: Client = create_client(url, service_key)

def generate_random_string(length=8):
    """Generate a random string for IDs"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def seed_properties():
    """Seed property data"""
    properties = [
        {
            "name": "Sunset Gardens",
            "address": "123 Sunset Blvd",
            "city": "Los Angeles",
            "state": "CA",
            "zip": "90028",
            "property_type": "Apartment Complex",
            "units": 24,
            "year_built": 2010,
            "total_sqft": 18000
        },
        {
            "name": "Downtown Lofts",
            "address": "456 Main Street",
            "city": "Los Angeles",
            "state": "CA",
            "zip": "90012",
            "property_type": "Mixed Use",
            "units": 12,
            "year_built": 2018,
            "total_sqft": 15000
        },
        {
            "name": "Green Valley Townhomes",
            "address": "789 Oak Avenue",
            "city": "Pasadena",
            "state": "CA",
            "zip": "91101",
            "property_type": "Townhouse",
            "units": 8,
            "year_built": 2015,
            "total_sqft": 12000
        }
    ]
    
    print("Seeding properties...")
    for prop in properties:
        result = supabase.table('properties').insert(prop).execute()
        print(f"Added property: {prop['name']}")
    
    return supabase.table('properties').select("*").execute().data

def seed_units(properties):
    """Seed unit data for each property"""
    units = []
    unit_types = ["Studio", "1BR", "2BR", "3BR"]
    
    for prop in properties:
        num_units = prop['units']
        for i in range(1, num_units + 1):
            unit_type = random.choice(unit_types)
            base_rent = {
                "Studio": 1500,
                "1BR": 2000,
                "2BR": 2800,
                "3BR": 3500
            }
            
            unit = {
                "property_id": prop['id'],
                "unit_number": f"{100 + i}",
                "unit_type": unit_type,
                "bedrooms": 0 if unit_type == "Studio" else int(unit_type[0]),
                "bathrooms": 1 if unit_type in ["Studio", "1BR"] else 2,
                "sqft": random.randint(500, 1500),
                "rent_amount": base_rent[unit_type] + random.randint(-200, 500),
                "status": random.choice(["Occupied", "Vacant", "Maintenance"]),
                "available_date": (datetime.now() + timedelta(days=random.randint(0, 60))).isoformat()
            }
            units.append(unit)
    
    print("Seeding units...")
    for unit in units:
        result = supabase.table('units').insert(unit).execute()
    print(f"Added {len(units)} units")
    
    return supabase.table('units').select("*").execute().data

def seed_tenants():
    """Seed tenant data"""
    first_names = ["John", "Jane", "Michael", "Sarah", "David", "Emily", "Robert", "Lisa", "James", "Maria"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
    
    tenants = []
    for i in range(20):
        tenant = {
            "first_name": random.choice(first_names),
            "last_name": random.choice(last_names),
            "email": f"tenant{i+1}@example.com",
            "phone": f"555-{random.randint(1000, 9999)}",
            "emergency_contact": f"Emergency {random.choice(first_names)} - 555-{random.randint(1000, 9999)}",
            "move_in_date": (datetime.now() - timedelta(days=random.randint(30, 365))).isoformat(),
            "lease_end_date": (datetime.now() + timedelta(days=random.randint(30, 365))).isoformat(),
            "monthly_rent": random.randint(1500, 4000),
            "security_deposit": random.randint(1500, 4000),
            "status": random.choice(["Active", "Past", "Prospective"])
        }
        tenants.append(tenant)
    
    print("Seeding tenants...")
    for tenant in tenants:
        result = supabase.table('tenants').insert(tenant).execute()
    print(f"Added {len(tenants)} tenants")
    
    return supabase.table('tenants').select("*").execute().data

def seed_owners():
    """Seed property owner data"""
    owners = [
        {
            "name": "Property Holdings LLC",
            "contact_name": "Robert Chen",
            "email": "rchen@propertyholdings.com",
            "phone": "555-0100",
            "address": "100 Business Park Dr, Los Angeles, CA 90045",
            "ownership_percentage": 100
        },
        {
            "name": "Sunset Investments",
            "contact_name": "Maria Rodriguez",
            "email": "maria@sunsetinvest.com",
            "phone": "555-0200",
            "address": "200 Investment Ave, Beverly Hills, CA 90210",
            "ownership_percentage": 100
        },
        {
            "name": "Green Valley Partners",
            "contact_name": "James Wilson",
            "email": "jwilson@gvpartners.com",
            "phone": "555-0300",
            "address": "300 Partner Plaza, Pasadena, CA 91101",
            "ownership_percentage": 100
        }
    ]
    
    print("Seeding owners...")
    for owner in owners:
        result = supabase.table('owners').insert(owner).execute()
        print(f"Added owner: {owner['name']}")
    
    return supabase.table('owners').select("*").execute().data

def seed_vendors():
    """Seed vendor data"""
    vendors = [
        {
            "company_name": "Quick Fix Plumbing",
            "contact_name": "Mike Johnson",
            "email": "mike@quickfixplumbing.com",
            "phone": "555-PLUMB",
            "service_type": "Plumbing",
            "rating": 4.5,
            "hourly_rate": 85,
            "emergency_available": True
        },
        {
            "company_name": "Bright Electric",
            "contact_name": "Sarah Chen",
            "email": "sarah@brightelectric.com",
            "phone": "555-ELEC",
            "service_type": "Electrical",
            "rating": 4.8,
            "hourly_rate": 95,
            "emergency_available": True
        },
        {
            "company_name": "Crystal Clean Services",
            "contact_name": "Ana Martinez",
            "email": "ana@crystalclean.com",
            "phone": "555-CLEAN",
            "service_type": "Cleaning",
            "rating": 4.2,
            "hourly_rate": 45,
            "emergency_available": False
        },
        {
            "company_name": "Pro Paint Co",
            "contact_name": "Tom Wilson",
            "email": "tom@propaint.com",
            "phone": "555-PAINT",
            "service_type": "Painting",
            "rating": 4.6,
            "hourly_rate": 65,
            "emergency_available": False
        },
        {
            "company_name": "HVAC Masters",
            "contact_name": "David Lee",
            "email": "david@hvacmasters.com",
            "phone": "555-HVAC",
            "service_type": "HVAC",
            "rating": 4.7,
            "hourly_rate": 110,
            "emergency_available": True
        }
    ]
    
    print("Seeding vendors...")
    for vendor in vendors:
        result = supabase.table('vendors').insert(vendor).execute()
        print(f"Added vendor: {vendor['company_name']}")
    
    return supabase.table('vendors').select("*").execute().data

def seed_work_orders(properties, units, vendors):
    """Seed work order data"""
    issues = [
        "Leaking faucet in kitchen",
        "AC not cooling properly",
        "Toilet running constantly",
        "Light fixture not working",
        "Garbage disposal jammed",
        "Door lock broken",
        "Window won't close",
        "Heating issue",
        "Electrical outlet not working",
        "Ceiling fan making noise"
    ]
    
    work_orders = []
    for i in range(30):
        unit = random.choice(units)
        prop = next(p for p in properties if p['id'] == unit['property_id'])
        vendor = random.choice(vendors) if random.random() > 0.3 else None
        
        created_date = datetime.now() - timedelta(days=random.randint(0, 60))
        status = random.choice(["Open", "In Progress", "Completed", "On Hold"])
        
        work_order = {
            "property_id": prop['id'],
            "unit_id": unit['id'],
            "title": random.choice(issues),
            "description": f"Tenant reported: {random.choice(issues)}. Needs immediate attention.",
            "priority": random.choice(["Low", "Medium", "High", "Emergency"]),
            "status": status,
            "created_date": created_date.isoformat(),
            "scheduled_date": (created_date + timedelta(days=random.randint(1, 7))).isoformat() if status != "Open" else None,
            "completed_date": (created_date + timedelta(days=random.randint(2, 10))).isoformat() if status == "Completed" else None,
            "vendor_id": vendor['id'] if vendor else None,
            "estimated_cost": random.randint(50, 1000) if vendor else None,
            "actual_cost": random.randint(50, 1000) if status == "Completed" and vendor else None
        }
        work_orders.append(work_order)
    
    print("Seeding work orders...")
    for wo in work_orders:
        result = supabase.table('work_orders').insert(wo).execute()
    print(f"Added {len(work_orders)} work orders")
    
    return work_orders

def seed_leases(tenants, units):
    """Seed lease data"""
    leases = []
    occupied_units = [u for u in units if u['status'] == 'Occupied']
    active_tenants = [t for t in tenants if t['status'] == 'Active']
    
    for i, tenant in enumerate(active_tenants[:len(occupied_units)]):
        unit = occupied_units[i]
        lease_start = datetime.now() - timedelta(days=random.randint(30, 365))
        
        lease = {
            "tenant_id": tenant['id'],
            "unit_id": unit['id'],
            "lease_start": lease_start.isoformat(),
            "lease_end": (lease_start + timedelta(days=365)).isoformat(),
            "monthly_rent": unit['rent_amount'],
            "security_deposit": unit['rent_amount'],
            "pet_deposit": random.choice([0, 500]) if random.random() > 0.7 else 0,
            "status": "Active",
            "auto_renew": random.choice([True, False])
        }
        leases.append(lease)
    
    print("Seeding leases...")
    for lease in leases:
        result = supabase.table('leases').insert(lease).execute()
    print(f"Added {len(leases)} leases")
    
    return leases

def seed_transactions():
    """Seed financial transaction data"""
    transactions = []
    
    # Generate rent payments
    for i in range(50):
        trans_date = datetime.now() - timedelta(days=random.randint(0, 90))
        transaction = {
            "type": "Income",
            "category": "Rent",
            "amount": random.randint(1500, 4000),
            "date": trans_date.isoformat(),
            "description": f"Rent payment for Unit {random.randint(101, 124)}",
            "payment_method": random.choice(["ACH", "Check", "Online", "Cash"]),
            "status": "Completed"
        }
        transactions.append(transaction)
    
    # Generate expense transactions
    expense_categories = ["Maintenance", "Utilities", "Insurance", "Property Tax", "Management Fee", "Supplies"]
    for i in range(30):
        trans_date = datetime.now() - timedelta(days=random.randint(0, 90))
        transaction = {
            "type": "Expense",
            "category": random.choice(expense_categories),
            "amount": random.randint(100, 2000),
            "date": trans_date.isoformat(),
            "description": f"{random.choice(expense_categories)} expense",
            "payment_method": random.choice(["ACH", "Check", "Credit Card"]),
            "status": "Completed"
        }
        transactions.append(transaction)
    
    print("Seeding transactions...")
    for transaction in transactions:
        result = supabase.table('transactions').insert(transaction).execute()
    print(f"Added {len(transactions)} transactions")
    
    return transactions

def main():
    """Main function to seed all data"""
    print("Starting database seeding...")
    print("=" * 50)
    
    try:
        # Seed data in order of dependencies
        properties = seed_properties()
        units = seed_units(properties)
        tenants = seed_tenants()
        owners = seed_owners()
        vendors = seed_vendors()
        work_orders = seed_work_orders(properties, units, vendors)
        leases = seed_leases(tenants, units)
        transactions = seed_transactions()
        
        print("=" * 50)
        print("Database seeding completed successfully!")
        print(f"Summary:")
        print(f"- Properties: {len(properties)}")
        print(f"- Units: {len(units)}")
        print(f"- Tenants: {len(tenants)}")
        print(f"- Owners: {len(owners)}")
        print(f"- Vendors: {len(vendors)}")
        print(f"- Work Orders: {len(work_orders)}")
        print(f"- Leases: {len(leases)}")
        print(f"- Transactions: {len(transactions)}")
        
    except Exception as e:
        print(f"Error during seeding: {str(e)}")
        print("Please check your Supabase configuration and database schema.")

if __name__ == "__main__":
    main()