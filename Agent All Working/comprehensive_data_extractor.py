#!/usr/bin/env python3
"""
COMPREHENSIVE DATA STORAGE SYSTEM
Captures and stores ALL AppFolio data with proper relationships

This system captures EVERYTHING:
- Tenant names, contact info, demographics
- Property details, addresses, unit specifics
- Financial data with full transaction history
- Lease terms, dates, and legal details
- Payment history and calculation breakdowns
- Fee structures and penalty details
- Maintenance records and service history
- All relationships between entities

Data is stored with:
✅ Proper data types and validation
✅ Referential integrity between records
✅ Privacy controls and security
✅ Complete audit trails
✅ Search and reporting capabilities
"""

import asyncio
import json
import re
from datetime import datetime, date
from decimal import Decimal
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any, Union
from pathlib import Path
import hashlib
import sqlite3
from playwright.async_api import Page

@dataclass
class TenantRecord:
    """Complete tenant information"""
    tenant_id: str
    first_name: str
    last_name: str
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    emergency_contact: Optional[str] = None
    ssn_last_four: Optional[str] = None  # Only last 4 digits for privacy
    date_of_birth: Optional[str] = None
    employment_info: Dict[str, Any] = field(default_factory=dict)
    credit_score: Optional[int] = None
    background_check_status: Optional[str] = None
    move_in_date: Optional[str] = None
    move_out_date: Optional[str] = None
    lease_ids: List[str] = field(default_factory=list)
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class PropertyRecord:
    """Complete property information"""
    property_id: str
    property_name: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    zip_code: str
    property_type: str  # apartment, house, commercial, etc.
    total_units: int = 0
    year_built: Optional[int] = None
    square_footage: Optional[int] = None
    lot_size: Optional[str] = None
    property_manager: Optional[str] = None
    owner_name: Optional[str] = None
    owner_contact: Optional[str] = None
    purchase_date: Optional[str] = None
    purchase_price: Optional[Decimal] = None
    current_value: Optional[Decimal] = None
    units: List[str] = field(default_factory=list)  # Unit IDs
    amenities: List[str] = field(default_factory=list)
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class UnitRecord:
    """Complete unit information"""
    unit_id: str
    property_id: str
    unit_number: str
    unit_type: str  # 1BR, 2BR, studio, etc.
    square_footage: Optional[int] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    floor: Optional[int] = None
    market_rent: Optional[Decimal] = None
    current_rent: Optional[Decimal] = None
    security_deposit: Optional[Decimal] = None
    pet_deposit: Optional[Decimal] = None
    features: List[str] = field(default_factory=list)
    appliances: List[str] = field(default_factory=list)
    condition: Optional[str] = None
    last_renovated: Optional[str] = None
    current_tenant_id: Optional[str] = None
    lease_id: Optional[str] = None
    availability_date: Optional[str] = None
    photos: List[str] = field(default_factory=list)
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class LeaseRecord:
    """Complete lease information"""
    lease_id: str
    property_id: str
    unit_id: str
    tenant_ids: List[str] = field(default_factory=list)  # Primary + co-tenants
    lease_type: str  # fixed, month-to-month, commercial
    lease_start_date: str
    lease_end_date: str
    monthly_rent: Decimal
    security_deposit: Decimal
    pet_deposit: Optional[Decimal] = None
    last_month_rent: Optional[Decimal] = None
    rent_due_day: int = 1  # Day of month rent is due
    late_fee_amount: Optional[Decimal] = None
    late_fee_percentage: Optional[float] = None
    grace_period_days: int = 5
    lease_terms: Dict[str, Any] = field(default_factory=dict)
    special_conditions: List[str] = field(default_factory=list)
    rent_history: List[Dict] = field(default_factory=list)  # Rent changes over time
    lease_documents: List[str] = field(default_factory=list)
    renewal_info: Dict[str, Any] = field(default_factory=dict)
    termination_notice_days: int = 30
    pets_allowed: bool = False
    pet_info: List[Dict] = field(default_factory=list)
    parking_spaces: int = 0
    utilities_included: List[str] = field(default_factory=list)
    status: str = "active"  # active, expired, terminated, pending
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class PaymentRecord:
    """Complete payment transaction"""
    payment_id: str
    tenant_id: str
    lease_id: str
    property_id: str
    unit_id: str
    payment_date: str
    due_date: str
    amount_due: Decimal
    amount_paid: Decimal
    payment_method: str  # check, online, cash, money_order
    check_number: Optional[str] = None
    transaction_id: Optional[str] = None
    payment_type: str  # rent, late_fee, security_deposit, pet_fee, etc.
    late_fee_charged: Decimal = Decimal('0.00')
    penalty_amount: Decimal = Decimal('0.00')
    days_late: int = 0
    payment_breakdown: Dict[str, Decimal] = field(default_factory=dict)
    partial_payment: bool = False
    balance_remaining: Decimal = Decimal('0.00')
    memo: Optional[str] = None
    processed_by: Optional[str] = None
    deposit_date: Optional[str] = None
    cleared_date: Optional[str] = None
    payment_status: str = "completed"  # pending, completed, failed, reversed
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class FinancialRecord:
    """Complete financial data"""
    record_id: str
    property_id: str
    record_type: str  # income, expense, asset, liability
    category: str  # rent, maintenance, utilities, taxes, etc.
    subcategory: Optional[str] = None
    description: str
    amount: Decimal
    transaction_date: str
    due_date: Optional[str] = None
    vendor: Optional[str] = None
    tenant_id: Optional[str] = None
    unit_id: Optional[str] = None
    invoice_number: Optional[str] = None
    receipt_number: Optional[str] = None
    payment_method: Optional[str] = None
    account_code: Optional[str] = None
    tax_deductible: bool = False
    recurring: bool = False
    recurring_frequency: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    attachments: List[str] = field(default_factory=list)
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class MaintenanceRecord:
    """Complete maintenance/work order data"""
    work_order_id: str
    property_id: str
    unit_id: Optional[str] = None
    tenant_id: Optional[str] = None
    request_date: str
    description: str
    category: str  # plumbing, electrical, hvac, appliance, etc.
    priority: str  # low, medium, high, emergency
    status: str  # pending, assigned, in_progress, completed, closed
    assigned_to: Optional[str] = None
    vendor_name: Optional[str] = None
    vendor_contact: Optional[str] = None
    scheduled_date: Optional[str] = None
    completed_date: Optional[str] = None
    estimated_cost: Optional[Decimal] = None
    actual_cost: Optional[Decimal] = None
    labor_hours: Optional[float] = None
    parts_used: List[Dict] = field(default_factory=list)
    tenant_present_required: bool = False
    photos_before: List[str] = field(default_factory=list)
    photos_after: List[str] = field(default_factory=list)
    tenant_satisfaction: Optional[int] = None  # 1-5 rating
    warranty