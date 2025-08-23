#!/usr/bin/env python3
"""
Dual-model field analyzer using Gemini and OpenAI
For integration with aiviizn_real_agent_with_ai_intelligence_updated.py
"""

import json
import asyncio
from typing import Dict, List, Optional
import google.generativeai as genai
from openai import AsyncOpenAI
import logging

logger = logging.getLogger(__name__)

class DualModelFieldAnalyzer:
    """
    Uses Gemini and OpenAI together for reliable field analysis
    Claude is excluded from this specific functionality
    """
    
    def __init__(self, gemini_model, openai_client):
        self.gemini_model = gemini_model
        self.openai_client = openai_client
        
        # Configure Gemini for JSON output
        if self.gemini_model:
            self.gemini_model = genai.GenerativeModel(
                'gemini-1.5-pro-002',
                generation_config={
                    'temperature': 0.1,
                    'top_p': 0.95,
                    'top_k': 40,
                    'max_output_tokens': 2048,
                    'response_mime_type': 'application/json'  # CRITICAL: Forces JSON
                }
            )
            self.gemini_chat = self.gemini_model.start_chat(history=[])
        
        # OpenAI function for structured output
        self.openai_function = {
            "name": "analyze_field",
            "description": "Analyze a form field",
            "parameters": {
                "type": "object",
                "properties": {
                    "ai_generated_name": {"type": "string"},
                    "semantic_type": {"type": "string"},
                    "data_type": {"type": "string"},
                    "unit_of_measure": {"type": "string"},
                    "is_calculated": {"type": "boolean"},
                    "calculation_formula": {"type": "string"},
                    "related_fields": {"type": "array", "items": {"type": "string"}},
                    "confidence": {"type": "number"},
                    "context_clues": {"type": "object"}
                },
                "required": ["ai_generated_name", "semantic_type", "data_type", "confidence"]
            }
        }
    
    async def analyze_with_gemini(self, field_name: str, field_attrs: Dict, context: str) -> Optional[Dict]:
        """Analyze with Gemini"""
        if not self.gemini_model:
            return None
            
        prompt = f"""Analyze this form field and return JSON:
Field Name: {field_name}
Attributes: {json.dumps(field_attrs)}
Context: {context[:500]}

Return JSON with: ai_generated_name, semantic_type, data_type, unit_of_measure, is_calculated, calculation_formula, related_fields, confidence, context_clues"""
        
        try:
            response = self.gemini_chat.send_message(prompt)
            result = json.loads(response.text)
            result['provider'] = 'gemini'
            logger.info(f"✓ Gemini analyzed: {field_name}")
            return result
        except Exception as e:
            logger.error(f"Gemini failed for {field_name}: {e}")
            return None
    
    async def analyze_with_openai(self, field_name: str, field_attrs: Dict, context: str) -> Optional[Dict]:
        """Analyze with OpenAI using function calling"""
        if not self.openai_client:
            return None
            
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-0125-preview",  # Latest GPT-4 Turbo
                messages=[
                    {"role": "system", "content": "You are a form field analysis expert for property management systems."},
                    {"role": "user", "content": f"Analyze field: {field_name}\nAttributes: {json.dumps(field_attrs)}\nContext: {context[:500]}"}
                ],
                functions=[self.openai_function],
                function_call={"name": "analyze_field"},
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.function_call.arguments)
            result['provider'] = 'openai'
            logger.info(f"✓ OpenAI analyzed: {field_name}")
            return result
        except Exception as e:
            logger.error(f"OpenAI failed for {field_name}: {e}")
            return None
    
    async def analyze_with_dual_consensus(self, field_name: str, field_attrs: Dict, context: str, surrounding_fields: List[str] = None) -> Dict:
        """
        Run both Gemini and OpenAI, use consensus or best result
        This is more reliable than single model but faster than triple consensus
        """
        
        # Run both providers in parallel
        tasks = [
            self.analyze_with_gemini(field_name, field_attrs, context),
            self.analyze_with_openai(field_name, field_attrs, context)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out failures and exceptions
        valid_results = [r for r in results if isinstance(r, dict) and r is not None]
        
        if not valid_results:
            # Both failed - return fallback
            logger.warning(f"Both models failed for {field_name}, using fallback")
            return {
                'ai_generated_name': field_name.replace('_', ' ').title(),
                'semantic_type': 'unknown',
                'data_type': 'text',
                'unit_of_measure': None,
                'is_calculated': False,
                'calculation_formula': None,
                'related_fields': [],
                'confidence': 0.1,
                'context_clues': {},
                'provider': 'fallback'
            }
        
        if len(valid_results) == 1:
            # Only one succeeded - use it
            logger.info(f"Only {valid_results[0]['provider']} succeeded for {field_name}")
            return valid_results[0]
        
        # Both succeeded - calculate consensus
        consensus = self._calculate_dual_consensus(valid_results, field_name)
        logger.info(f"Both models agreed on {field_name}: {consensus['semantic_type']}")
        return consensus
    
    def _calculate_dual_consensus(self, results: List[Dict], field_name: str) -> Dict:
        """
        Calculate consensus from Gemini and OpenAI results
        """
        
        gemini_result = next((r for r in results if r.get('provider') == 'gemini'), results[0])
        openai_result = next((r for r in results if r.get('provider') == 'openai'), results[1])
        
        # Start with the result that has higher confidence
        if gemini_result.get('confidence', 0) >= openai_result.get('confidence', 0):
            consensus = gemini_result.copy()
        else:
            consensus = openai_result.copy()
        
        # If both agree on semantic_type, boost confidence
        if gemini_result.get('semantic_type') == openai_result.get('semantic_type'):
            consensus['semantic_type'] = gemini_result['semantic_type']
            # Boost confidence when both agree
            consensus['confidence'] = min(1.0, (gemini_result.get('confidence', 0) + openai_result.get('confidence', 0)) / 2 * 1.1)
            consensus['agreement'] = 'full'
        else:
            # Use the one with higher confidence
            consensus['agreement'] = 'partial'
        
        # If both agree on data_type, use it
        if gemini_result.get('data_type') == openai_result.get('data_type'):
            consensus['data_type'] = gemini_result['data_type']
        
        # If both agree on is_calculated, use it
        if gemini_result.get('is_calculated') == openai_result.get('is_calculated'):
            consensus['is_calculated'] = gemini_result['is_calculated']
        
        # Average confidence if they disagree
        if consensus.get('agreement') == 'partial':
            consensus['confidence'] = (gemini_result.get('confidence', 0) + openai_result.get('confidence', 0)) / 2
        
        # Note both providers were used
        consensus['provider'] = 'gemini+openai'
        consensus['providers_used'] = 2
        
        return consensus
    
    async def analyze_with_fallback(self, field_name: str, field_attrs: Dict, context: str) -> Dict:
        """
        Try Gemini first (faster/cheaper), fallback to OpenAI if needed
        Use this for non-critical fields to save cost
        """
        
        # Try Gemini first
        result = await self.analyze_with_gemini(field_name, field_attrs, context)
        
        if result and result.get('confidence', 0) >= 0.7:
            # Good enough confidence from Gemini
            return result
        
        # Low confidence or failure - try OpenAI
        logger.info(f"Gemini confidence low for {field_name}, trying OpenAI")
        openai_result = await self.analyze_with_openai(field_name, field_attrs, context)
        
        if openai_result:
            return openai_result
        elif result:
            # OpenAI failed but we have Gemini result
            return result
        else:
            # Both failed
            return {
                'ai_generated_name': field_name.replace('_', ' ').title(),
                'semantic_type': 'unknown',
                'data_type': 'text',
                'confidence': 0.1,
                'provider': 'fallback'
            }
