-- ============================================================
-- 07_run_analysis.sql
-- Runs the procedure in small controlled batches.
-- ============================================================

USE WAREHOUSE AMAZON_SENTIMENT_WH;
USE DATABASE AMAZON_SENTIMENT_DB;
USE SCHEMA ANALYTICS;

-- Start with 10 reviews.
CALL PROCESS_REVIEW_SENTIMENT(10);

-- Validate the result.
SELECT
    REVIEW_ID,
    STARS,
    OVERALL_SENTIMENT,
    PRODUCT_QUALITY_SENTIMENT,
    VALUE_SENTIMENT,
    USABILITY_SENTIMENT,
    DURABILITY_SENTIMENT,
    PACKAGING_SENTIMENT,
    RATING_SENTIMENT_MATCH,
    MISMATCH_TYPE,
    REQUIRES_ATTENTION
FROM REVIEW_SENTIMENT_ANALYSIS
ORDER BY ANALYZED_AT DESC
LIMIT 20;

-- After checking the first results, run more batches.
-- CALL PROCESS_REVIEW_SENTIMENT(50);
-- CALL PROCESS_REVIEW_SENTIMENT(100);

-- Progress.
SELECT
    (SELECT COUNT(*) FROM REVIEW_SAMPLE)
        AS SAMPLE_REVIEWS,

    (SELECT COUNT(*) FROM REVIEW_SENTIMENT_ANALYSIS)
        AS ANALYZED_REVIEWS,

    (
        SELECT COUNT(*)
        FROM REVIEW_SAMPLE S
        WHERE NOT EXISTS (
            SELECT 1
            FROM REVIEW_SENTIMENT_ANALYSIS A
            WHERE A.REVIEW_ID = S.REVIEW_ID
        )
    ) AS REMAINING_REVIEWS;
