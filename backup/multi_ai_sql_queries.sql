-- ===============================================
-- ESSENTIAL SQL QUERIES FOR MULTI-AI AGENT
-- ===============================================

-- 1. INSERT NEW VALIDATION RESULT
-- Use this when your agent completes a multi-AI validation
INSERT INTO multi_ai_validations (
    page_id, 
    formula_id, 
    openai_result,
    gemini_result,
    claude_result,
    wolfram_result,
    consensus_achieved,
    consensus_score,
    successful_validations,
    total_attempts,
    validation_priority,
    processing_time_seconds,
    final_recommendation,
    requires_manual_review
) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14);

-- 2. GET NEXT HIGH PRIORITY FORMULAS TO VALIDATE
SELECT 
    cf.id as formula_id,
    ap.id as page_id,
    ap.url as page_url,
    cf.formula_type,
    cf.formula_expression,
    CASE 
        WHEN ap.page_type IN ('rent_roll_report', 'income_statement', 'delinquency_report') THEN 'HIGH'
        WHEN ap.page_type IN ('account_totals', 'property_dashboard') THEN 'MEDIUM'
        ELSE 'LOW'
    END as priority
FROM calculation_formulas cf
JOIN appfolio_pages ap ON cf.page_id = ap.id
LEFT JOIN multi_ai_validations mav ON cf.id = mav.formula_id
WHERE cf.verification_status = 'pending'
    AND mav.id IS NULL  -- Never validated
ORDER BY 
    CASE 
        WHEN ap.page_type IN ('rent_roll_report', 'income_statement', 'delinquency_report') THEN 1
        WHEN ap.page_type IN ('account_totals', 'property_dashboard') THEN 2
        ELSE 3
    END
LIMIT 10;

-- 3. LOG AI API CALL MONITORING
INSERT INTO ai_api_monitoring (
    validation_id,
    ai_provider,
    request_timestamp,
    response_timestamp,
    response_time_ms,
    success,
    error_message,
    error_type,
    tokens_used,
    cost_estimate
) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10);

-- 4. UPDATE FORMULA VERIFICATION STATUS
UPDATE calculation_formulas 
SET verification_status = $1,
    expected_result = $2
WHERE id = $3;

-- 5. GET VALIDATION DASHBOARD STATUS
SELECT * FROM validation_dashboard;

-- 6. GET AI API PERFORMANCE (Last 24 Hours)
SELECT * FROM ai_api_performance;

-- 7. CHECK FOR FAILED VALIDATIONS NEEDING RETRY
SELECT 
    cf.id as formula_id,
    ap.title as page_title,
    cf.formula_type,
    COUNT(mav.id) as failed_attempts,
    MAX(mav.validation_timestamp) as last_attempt
FROM calculation_formulas cf
JOIN appfolio_pages ap ON cf.page_id = ap.id
JOIN multi_ai_validations mav ON cf.id = mav.formula_id
WHERE mav.consensus_achieved = false
    AND cf.verification_status = 'pending'
GROUP BY cf.id, ap.title, cf.formula_type
HAVING COUNT(mav.id) < 3  -- Haven't exceeded retry limit
ORDER BY COUNT(mav.id) ASC;

-- 8. GET PAGE VALIDATION SUMMARY
SELECT * FROM get_page_validation_summary($1);  -- Pass page URL

-- 9. INSERT NEW APPFOLIO PAGE
INSERT INTO appfolio_pages (url, title, page_type, html_content, screenshot_url)
VALUES ($1, $2, $3, $4, $5)
ON CONFLICT (url) DO UPDATE SET
    title = EXCLUDED.title,
    page_type = EXCLUDED.page_type,
    html_content = EXCLUDED.html_content,
    processed_at = NOW();

-- 10. INSERT DISCOVERED CALCULATION FORMULA
INSERT INTO calculation_formulas (
    page_id,
    formula_type,
    formula_expression,
    variables,
    expected_result,
    javascript_code,
    context_description
) VALUES ($1, $2, $3, $4, $5, $6, $7);

-- 11. GET CONSENSUS RATE FOR VALIDATION SESSION
SELECT 
    validation_session_id,
    COUNT(*) as total_validations,
    COUNT(*) FILTER (WHERE consensus_achieved = true) as consensus_count,
    ROUND(
        (COUNT(*) FILTER (WHERE consensus_achieved = true)::decimal / COUNT(*)) * 100, 2
    ) as consensus_rate_percent,
    AVG(consensus_score) as avg_consensus_score
FROM multi_ai_validations
WHERE validation_session_id = $1
GROUP BY validation_session_id;

-- 12. GET ALL PENDING VALIDATIONS WITH PRIORITY
SELECT * FROM priority_validation_queue;

-- 13. MARK VALIDATION AS MANUAL REVIEW REQUIRED
UPDATE multi_ai_validations 
SET requires_manual_review = true,
    final_recommendation = 'Manual review required due to ' || $2
WHERE id = $1;

-- 14. GET RELATIONSHIP BETWEEN PAGES
SELECT 
    source_page.title as source_page,
    target_page.title as target_page,
    pr.relationship_type,
    pr.relationship_strength,
    pr.shared_calculations
FROM page_relationships pr
JOIN appfolio_pages source_page ON pr.source_page_id = source_page.id
JOIN appfolio_pages target_page ON pr.target_page_id = target_page.id
WHERE source_page.url = $1;

-- 15. GET SYSTEM HEALTH OVERVIEW
SELECT 
    (SELECT COUNT(*) FROM appfolio_pages) as total_pages,
    (SELECT COUNT(*) FROM calculation_formulas) as total_formulas,
    (SELECT COUNT(*) FROM multi_ai_validations) as total_validations,
    (SELECT COUNT(*) FROM multi_ai_validations WHERE consensus_achieved = true) as successful_validations,
    (SELECT COUNT(*) FROM multi_ai_validations WHERE requires_manual_review = true) as manual_reviews_needed,
    (SELECT ROUND(AVG(consensus_score), 2) FROM multi_ai_validations WHERE consensus_achieved = true) as avg_consensus_score;