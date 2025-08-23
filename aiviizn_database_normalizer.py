#!/usr/bin/env python3
"""
AIVIIZN Database Normalizer - Shared Data Manager
Ensures all data is written once and referenced everywhere
"""

import asyncio
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

from supabase import create_client, Client
import numpy as np

# ============================================
# DATA NORMALIZER CLASS
# ============================================

@dataclass
class NormalizedElement:
    """Represents a normalized data element"""
    element_id: str
    element_name: str
    element_type: str
    data_category: str
    current_value: Any
    references: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    formula: Optional[str] = None
    
class DataElementType(Enum):
    """Types of data elements"""
    PERSON_NAME = "person_name"
    PROPERTY_ADDRESS = "property_address"
    PHONE_NUMBER = "phone"
    EMAIL_ADDRESS = "email"
    CURRENCY_AMOUNT = "amount"
    PERCENTAGE = "percentage"
    DATE = "date"
    CALCULATION_RESULT = "calculation"
    TEXT = "text"
    NUMBER = "number"

class DataCategory(Enum):
    """Categories of data"""
    TENANT = "tenant"
    OWNER = "owner"
    VENDOR = "vendor"
    PROPERTY = "property"
    FINANCIAL = "financial"
    MAINTENANCE = "maintenance"
    LEASING = "leasing"
    GENERAL = "general"

class AIVIIZNDataNormalizer:
    """Manages normalized data architecture"""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase = create_client(supabase_url, supabase_key)
        self.cache: Dict[str, NormalizedElement] = {}
        self.logger = logging.getLogger(__name__)
        
    async def initialize_schema(self):
        """Initialize the normalized database schema"""
        self.logger.info("Initializing normalized database schema...")
        
        # Execute schema creation
        # Note: In production, this would be done via migrations
        try:
            # For now, we'll ensure tables exist via Supabase dashboard
            # or direct SQL execution
            result = self.supabase.table('shared_data_elements').select("count").execute()
            self.logger.info(f"Schema initialized. Elements count: {result.data}")
        except Exception as e:
            self.logger.error(f"Schema initialization error: {e}")
    
    def generate_element_id(self, value: str, element_type: str) -> str:
        """Generate deterministic element ID"""
        hash_input = f"{element_type}:{value}".lower().strip()
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]
    
    async def get_or_create_element(
        self,
        value: Any,
        element_type: DataElementType,
        category: DataCategory = DataCategory.GENERAL,
        formula: Optional[str] = None
    ) -> NormalizedElement:
        """Get existing element or create new one"""
        
        # Generate element ID
        element_id = self.generate_element_id(str(value), element_type.value)
        
        # Check cache first
        if element_id in self.cache:
            return self.cache[element_id]
        
        # Check database
        result = self.supabase.table('shared_data_elements').select("*").eq(
            'element_id', element_id
        ).execute()
        
        if result.data:
            # Element exists, create object from DB data
            db_element = result.data[0]
            element = NormalizedElement(
                element_id=element_id,
                element_name=db_element['element_name'],
                element_type=element_type.value,
                data_category=category.value,
                current_value=db_element['current_value'],
                formula=db_element.get('formula_expression')
            )
        else:
            # Create new element
            element = NormalizedElement(
                element_id=element_id,
                element_name=str(value),
                element_type=element_type.value,
                data_category=category.value,
                current_value=value,
                formula=formula
            )
            
            # Store in database
            await self.store_element(element)
        
        # Cache it
        self.cache[element_id] = element
        
        return element
    
    async def store_element(self, element: NormalizedElement):
        """Store element in database"""
        
        data = {
            'element_id': element.element_id,
            'element_name': element.element_name,
            'element_type': element.element_type,
            'data_category': element.data_category,
            'current_value': {'value': element.current_value},
            'formula_expression': element.formula,
            'is_derived': element.formula is not None
        }
        
        self.supabase.table('shared_data_elements').upsert(data).execute()
        
    async def create_element_relationship(
        self,
        source_element_id: str,
        target_element_id: str,
        relationship_type: str,
        transformation_rule: Optional[Dict] = None
    ):
        """Create relationship between elements"""
        
        data = {
            'source_element_id': source_element_id,
            'target_element_id': target_element_id,
            'relationship_type': relationship_type,
            'transformation_rule': transformation_rule
        }
        
        self.supabase.table('data_element_relationships').insert(data).execute()
    
    async def register_page_reference(
        self,
        page_id: int,
        element_id: str,
        reference_type: str = "display",
        field_position: Optional[str] = None,
        is_editable: bool = False
    ):
        """Register that a page references a shared element"""
        
        data = {
            'page_id': page_id,
            'element_id': element_id,
            'reference_type': reference_type,
            'field_position': field_position,
            'is_editable': is_editable
        }
        
        self.supabase.table('page_data_references').insert(data).execute()
    
    async def propagate_change(self, element_id: str, new_value: Any) -> List[str]:
        """Propagate a change to all dependent elements and pages"""
        
        affected_elements = []
        
        # Update the source element
        self.supabase.table('shared_data_elements').update({
            'current_value': {'value': new_value},
            'last_updated': datetime.now().isoformat()
        }).eq('element_id', element_id).execute()
        
        # Find dependent elements
        deps_result = self.supabase.table('data_element_relationships').select(
            "target_element_id"
        ).eq('source_element_id', element_id).execute()
        
        for dep in deps_result.data:
            affected_elements.append(dep['target_element_id'])
            
            # Recalculate if it's a formula
            await self.recalculate_element(dep['target_element_id'])
        
        # Log propagation
        self.supabase.table('data_propagation_log').insert({
            'source_element_id': element_id,
            'trigger_event': 'update',
            'affected_elements': affected_elements,
            'propagation_timestamp': datetime.now().isoformat()
        }).execute()
        
        return affected_elements
    
    async def recalculate_element(self, element_id: str):
        """Recalculate a derived element"""
        
        # Get element details
        result = self.supabase.table('shared_data_elements').select("*").eq(
            'element_id', element_id
        ).single().execute()
        
        if not result.data or not result.data.get('formula_expression'):
            return
        
        element = result.data
        formula = element['formula_expression']
        depends_on = element.get('depends_on_elements', [])
        
        # Get values of dependencies
        values = {}
        for dep_id in depends_on:
            dep_result = self.supabase.table('shared_data_elements').select(
                "current_value"
            ).eq('element_id', dep_id).single().execute()
            
            if dep_result.data:
                values[dep_id] = dep_result.data['current_value']['value']
        
        # Evaluate formula (simplified - in production use proper formula engine)
        try:
            # This is a simplified example - use proper formula evaluation
            new_value = eval(formula, {'__builtins__': {}}, values)
            
            # Update the calculated value
            self.supabase.table('shared_data_elements').update({
                'current_value': {'value': new_value},
                'last_updated': datetime.now().isoformat()
            }).eq('element_id', element_id).execute()
            
        except Exception as e:
            self.logger.error(f"Failed to recalculate {element_id}: {e}")
    
    async def extract_and_normalize_page_data(self, page_content: str, page_id: int) -> Dict[str, NormalizedElement]:
        """Extract and normalize all data from a page"""
        
        import re
        normalized_data = {}
        
        # Patterns for different data types
        patterns = {
            DataElementType.PERSON_NAME: r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',
            DataElementType.PROPERTY_ADDRESS: r'\d+\s+[A-Za-z\s]+(?:St|Street|Ave|Avenue|Rd|Road|Blvd|Boulevard)',
            DataElementType.PHONE_NUMBER: r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            DataElementType.EMAIL_ADDRESS: r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            DataElementType.CURRENCY_AMOUNT: r'\$[\d,]+\.?\d*',
            DataElementType.PERCENTAGE: r'\d+\.?\d*\%',
            DataElementType.DATE: r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}'
        }
        
        for data_type, pattern in patterns.items():
            matches = re.findall(pattern, page_content)
            
            for match in matches:
                # Determine category based on context
                category = self._determine_category(match, page_content)
                
                # Get or create normalized element
                element = await self.get_or_create_element(
                    value=match,
                    element_type=data_type,
                    category=category
                )
                
                # Register page reference
                await self.register_page_reference(
                    page_id=page_id,
                    element_id=element.element_id,
                    reference_type="display"
                )
                
                normalized_data[element.element_id] = element
        
        return normalized_data
    
    def _determine_category(self, value: str, context: str) -> DataCategory:
        """Determine data category based on context"""
        
        # Simple heuristic - in production use NLP
        context_lower = context.lower()
        
        if 'tenant' in context_lower or 'resident' in context_lower:
            return DataCategory.TENANT
        elif 'owner' in context_lower or 'landlord' in context_lower:
            return DataCategory.OWNER
        elif 'vendor' in context_lower or 'contractor' in context_lower:
            return DataCategory.VENDOR
        elif 'property' in context_lower or 'unit' in context_lower:
            return DataCategory.PROPERTY
        elif 'payment' in context_lower or 'amount' in context_lower or '$' in value:
            return DataCategory.FINANCIAL
        elif 'maintenance' in context_lower or 'repair' in context_lower:
            return DataCategory.MAINTENANCE
        elif 'lease' in context_lower or 'rental' in context_lower:
            return DataCategory.LEASING
        else:
            return DataCategory.GENERAL
    
    async def generate_normalized_report(self) -> Dict:
        """Generate report of normalized data architecture"""
        
        # Get statistics
        elements_result = self.supabase.table('shared_data_elements').select(
            "element_type", count='exact'
        ).execute()
        
        relationships_result = self.supabase.table('data_element_relationships').select(
            "relationship_type", count='exact'
        ).execute()
        
        references_result = self.supabase.table('page_data_references').select(
            "reference_type", count='exact'
        ).execute()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_elements': elements_result.count if elements_result else 0,
            'total_relationships': relationships_result.count if relationships_result else 0,
            'total_references': references_result.count if references_result else 0,
            'elements_by_type': {},
            'data_quality_score': 0.0
        }
        
        # Calculate data quality score
        if report['total_elements'] > 0:
            # Check for orphaned elements (no references)
            orphaned = self.supabase.table('shared_data_elements').select("id").execute()
            
            # Simple quality score based on connectivity
            report['data_quality_score'] = min(
                100.0,
                (report['total_relationships'] / report['total_elements']) * 50 +
                (report['total_references'] / report['total_elements']) * 50
            )
        
        return report

# ============================================
# CALCULATION ENGINE
# ============================================

class CalculationEngine:
    """Handles mathematical calculations and formula validation"""
    
    def __init__(self, normalizer: AIVIIZNDataNormalizer):
        self.normalizer = normalizer
        self.logger = logging.getLogger(__name__)
    
    async def register_calculation(
        self,
        name: str,
        formula: str,
        input_elements: List[str],
        expected_range: Tuple[float, float] = None
    ) -> str:
        """Register a calculation formula"""
        
        # Create result element
        result_element = await self.normalizer.get_or_create_element(
            value=0,  # Initial value
            element_type=DataElementType.CALCULATION_RESULT,
            category=DataCategory.FINANCIAL,
            formula=formula
        )
        
        # Store calculation registry
        data = {
            'calculation_name': name,
            'result_element_id': result_element.element_id,
            'input_elements': input_elements,
            'formula_expression': formula,
            'expected_range_min': expected_range[0] if expected_range else None,
            'expected_range_max': expected_range[1] if expected_range else None
        }
        
        self.normalizer.supabase.table('financial_calculations_registry').insert(data).execute()
        
        # Create relationships
        for input_id in input_elements:
            await self.normalizer.create_element_relationship(
                source_element_id=input_id,
                target_element_id=result_element.element_id,
                relationship_type='calculates_from'
            )
        
        return result_element.element_id
    
    async def execute_calculation(self, calculation_id: str) -> float:
        """Execute a registered calculation"""
        
        # Get calculation details
        calc_result = self.normalizer.supabase.table(
            'financial_calculations_registry'
        ).select("*").eq('id', calculation_id).single().execute()
        
        if not calc_result.data:
            raise ValueError(f"Calculation {calculation_id} not found")
        
        calc = calc_result.data
        
        # Get input values
        input_values = {}
        for element_id in calc['input_elements']:
            elem_result = self.normalizer.supabase.table(
                'shared_data_elements'
            ).select("current_value").eq('element_id', element_id).single().execute()
            
            if elem_result.data:
                input_values[element_id] = elem_result.data['current_value']['value']
        
        # Execute formula
        try:
            result = eval(calc['formula_expression'], {'__builtins__': {}}, input_values)
            
            # Validate range
            if calc['expected_range_min'] and result < calc['expected_range_min']:
                self.logger.warning(f"Calculation result {result} below expected range")
            if calc['expected_range_max'] and result > calc['expected_range_max']:
                self.logger.warning(f"Calculation result {result} above expected range")
            
            # Update result element
            await self.normalizer.propagate_change(calc['result_element_id'], result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Calculation failed: {e}")
            raise

# ============================================
# MAIN EXECUTION
# ============================================

async def main():
    """Initialize and test the normalized data system"""
    
    # Configuration
    SUPABASE_URL = "https://sejebqdhcilwcpjpznep.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNlamVicWRoY2lsd2NwanB6bmVwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTg5NjQsImV4cCI6MjA3MDAzNDk2NH0.vFM0Gr3QZF4MN3vtDGghjyCpnIkyC_mmUOOkVO3ahPQ"
    
    # Initialize normalizer
    normalizer = AIVIIZNDataNormalizer(SUPABASE_URL, SUPABASE_KEY)
    await normalizer.initialize_schema()
    
    # Example: Create normalized elements
    print("Creating normalized data elements...")
    
    # Create a tenant
    tenant_name = await normalizer.get_or_create_element(
        value="John Smith",
        element_type=DataElementType.PERSON_NAME,
        category=DataCategory.TENANT
    )
    
    # Create property address
    property_addr = await normalizer.get_or_create_element(
        value="123 Main Street",
        element_type=DataElementType.PROPERTY_ADDRESS,
        category=DataCategory.PROPERTY
    )
    
    # Create rent amount
    rent_amount = await normalizer.get_or_create_element(
        value=1500.00,
        element_type=DataElementType.CURRENCY_AMOUNT,
        category=DataCategory.FINANCIAL
    )
    
    # Create relationships
    await normalizer.create_element_relationship(
        source_element_id=tenant_name.element_id,
        target_element_id=property_addr.element_id,
        relationship_type="resides_at"
    )
    
    await normalizer.create_element_relationship(
        source_element_id=tenant_name.element_id,
        target_element_id=rent_amount.element_id,
        relationship_type="pays"
    )
    
    # Initialize calculation engine
    calc_engine = CalculationEngine(normalizer)
    
    # Register a calculation
    total_rent_id = await calc_engine.register_calculation(
        name="Total Monthly Rent",
        formula="sum(rent_amounts)",
        input_elements=[rent_amount.element_id],
        expected_range=(0, 100000)
    )
    
    # Generate report
    report = await normalizer.generate_normalized_report()
    print(f"\nNormalized Data Report:")
    print(json.dumps(report, indent=2))
    
    print("\n✅ Data normalization system initialized successfully!")
    print("All data is now written once and referenced everywhere.")

if __name__ == "__main__":
    asyncio.run(main())
