#!/usr/bin/env python3
"""
Consensus-based field analyzer using all three AI models
For integration with aiviizn_real_agent_with_ai_intelligence_updated.py
"""

import json
import asyncio
from typing import Dict, List, Optional
import google.generativeai as genai
from openai import AsyncOpenAI
import anthropic
import logging

logger = logging.getLogger(__name__)

class ConsensusFieldAnalyzer:
    """
    Uses Gemini, OpenAI, and Claude in consensus for 100% reliable field analysis
    """
    
    def __init__(self, gemini_model, openai_client, anthropic_client):
        self.gemini_model = gemini_model
        self.openai_client = openai_client
        self.anthropic_client = anthropic_client
        
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
            return result
        except Exception as e:
            logger.error(f"Gemini failed: {e}")
            return None
    
    async def analyze_with_openai(self, field_name: str, field_attrs: Dict, context: str) -> Optional[Dict]:
        """Analyze with OpenAI using function calling"""
        if not self.openai_client:
            return None
            
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-0125-preview",  # Latest GPT-4 Turbo
                messages=[
                    {"role": "system", "content": "You are a form field analysis expert."},
                    {"role": "user", "content": f"Analyze field: {field_name}\nAttributes: {json.dumps(field_attrs)}\nContext: {context[:500]}"}
                ],
                functions=[self.openai_function],
                function_call={"name": "analyze_field"},
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.function_call.arguments)
            result['provider'] = 'openai'
            return result
        except Exception as e:
            logger.error(f"OpenAI failed: {e}")
            return None
    
    async def analyze_with_claude(self, field_name: str, field_attrs: Dict, context: str) -> Optional[Dict]:
        """Analyze with Claude"""
        if not self.anthropic_client:
            return None
            
        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-opus-20240229",
                messages=[{
                    "role": "user",
                    "content": f"""Analyze this field and return ONLY JSON:
Field: {field_name}
Attributes: {json.dumps(field_attrs)}
Context: {context[:500]}

Return JSON with: ai_generated_name, semantic_type, data_type, unit_of_measure, is_calculated, calculation_formula, related_fields, confidence, context_clues"""
                }],
                max_tokens=500,
                temperature=0.1
            )
            
            text = response.content[0].text.strip()
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0]
            elif '```' in text:
                text = text.split('```')[1].split('```')[0]
            
            result = json.loads(text)
            result['provider'] = 'claude'
            return result
        except Exception as e:
            logger.error(f"Claude failed: {e}")
            return None
    
    async def analyze_with_consensus(self, field_name: str, field_attrs: Dict, context: str, surrounding_fields: List[str] = None) -> Dict:
        """
        Run all three models and use consensus for maximum accuracy
        Returns the consensus result with highest confidence
        """
        
        # Run all three providers in parallel
        tasks = [
            self.analyze_with_gemini(field_name, field_attrs, context),
            self.analyze_with_openai(field_name, field_attrs, context),
            self.analyze_with_claude(field_name, field_attrs, context)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out failures and exceptions
        valid_results = [r for r in results if isinstance(r, dict) and r is not None]
        
        if not valid_results:
            # All failed - return fallback
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
            # Only one succeeded
            return valid_results[0]
        
        # Calculate consensus
        consensus_result = self._calculate_consensus(valid_results, field_name)
        return consensus_result
    
    def _calculate_consensus(self, results: List[Dict], field_name: str) -> Dict:
        """
        Calculate consensus from multiple AI results
        Uses voting for categorical fields and averaging for numerical
        """
        
        # Start with the result that has highest confidence
        confidences = [r.get('confidence', 0) for r in results]
        best_idx = confidences.index(max(confidences))
        consensus = results[best_idx].copy()
        
        # Vote on semantic_type (most important field)
        semantic_types = [r.get('semantic_type', 'unknown') for r in results]
        from collections import Counter
        type_votes = Counter(semantic_types)
        consensus['semantic_type'] = type_votes.most_common(1)[0][0]
        
        # Vote on data_type
        data_types = [r.get('data_type', 'text') for r in results]
        dtype_votes = Counter(data_types)
        consensus['data_type'] = dtype_votes.most_common(1)[0][0]
        
        # Vote on is_calculated
        calculated_votes = [r.get('is_calculated', False) for r in results]
        consensus['is_calculated'] = sum(calculated_votes) > len(calculated_votes) / 2
        
        # Average confidence across all results
        consensus['confidence'] = sum(confidences) / len(confidences)
        
        # Take the most common ai_generated_name (or the one from highest confidence)
        ai_names = [r.get('ai_generated_name', field_name) for r in results]
        name_votes = Counter(ai_names)
        consensus['ai_generated_name'] = name_votes.most_common(1)[0][0]
        
        # Note which providers agreed
        providers = [r.get('provider', 'unknown') for r in results]
        consensus['provider'] = f"consensus({','.join(providers)})"
        consensus['consensus_count'] = len(results)
        
        return consensus
