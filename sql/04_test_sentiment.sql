-- ============================================================
-- 04_test_sentiment.sql
-- Tests Cortex access and confirms the result structure.
-- ============================================================

USE WAREHOUSE AMAZON_SENTIMENT_WH;
USE DATABASE AMAZON_SENTIMENT_DB;
USE SCHEMA ANALYTICS;

-- Overall sentiment.
SELECT
    REVIEW_ID,
    STARS,
    REVIEW_TEXT,
    AI_SENTIMENT(REVIEW_TEXT) AS SENTIMENT_RESULT
FROM REVIEW_SAMPLE
LIMIT 5;

-- Overall and aspect-level sentiment.
SELECT
    REVIEW_ID,
    STARS,
    REVIEW_TEXT,
    AI_SENTIMENT(
        REVIEW_TEXT,
        [
            'product quality',
            'value for money',
            'usability',
            'durability',
            'packaging'
        ]
    ) AS SENTIMENT_RESULT
FROM REVIEW_SAMPLE
LIMIT 5;

-- Flatten the result.
WITH TEST_RESULTS AS (
    SELECT
        REVIEW_ID,
        AI_SENTIMENT(
            REVIEW_TEXT,
            [
                'product quality',
                'value for money',
                'usability',
                'durability',
                'packaging'
            ]
        ) AS RESULT
    FROM REVIEW_SAMPLE
    LIMIT 5
)
SELECT
    T.REVIEW_ID,
    F.VALUE:name::VARCHAR AS SENTIMENT_CATEGORY,
    F.VALUE:sentiment::VARCHAR AS SENTIMENT
FROM TEST_RESULTS T,
LATERAL FLATTEN(INPUT => T.RESULT:categories) F
ORDER BY T.REVIEW_ID, SENTIMENT_CATEGORY;
