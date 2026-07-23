-- ============================================================
-- 06_create_processing_procedure.sql
-- Simple procedure:
--   1. Selects reviews that have not been analyzed
--   2. Calls AI_SENTIMENT
--   3. Flattens sentiment categories
--   4. Inserts the final result
-- ============================================================

USE WAREHOUSE AMAZON_SENTIMENT_WH;
USE DATABASE AMAZON_SENTIMENT_DB;
USE SCHEMA ANALYTICS;

CREATE OR REPLACE PROCEDURE PROCESS_REVIEW_SENTIMENT(P_LIMIT NUMBER)
RETURNS VARCHAR
LANGUAGE SQL
EXECUTE AS OWNER
AS
$$
DECLARE
    V_SELECTED NUMBER DEFAULT 0;
BEGIN

    IF (P_LIMIT IS NULL OR P_LIMIT <= 0) THEN
        RETURN 'P_LIMIT must be greater than zero';
    END IF;

    CREATE OR REPLACE TEMPORARY TABLE TMP_REVIEW_BATCH AS
    SELECT S.*
    FROM REVIEW_SAMPLE S
    WHERE NOT EXISTS (
        SELECT 1
        FROM REVIEW_SENTIMENT_ANALYSIS A
        WHERE A.REVIEW_ID = S.REVIEW_ID
    )
    ORDER BY HASH(S.REVIEW_ID)
    LIMIT :P_LIMIT;

    SELECT COUNT(*)
    INTO :V_SELECTED
    FROM TMP_REVIEW_BATCH;

    IF (V_SELECTED = 0) THEN
        RETURN 'No unprocessed reviews remain';
    END IF;

    CREATE OR REPLACE TEMPORARY TABLE TMP_SENTIMENT_RESULT AS
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
        ) AS SENTIMENT_RESULT
    FROM TMP_REVIEW_BATCH;

    CREATE OR REPLACE TEMPORARY TABLE TMP_PARSED_SENTIMENT AS
    SELECT
        S.REVIEW_ID,

        MAX(IFF(
            LOWER(F.VALUE:name::VARCHAR) = 'overall',
            LOWER(F.VALUE:sentiment::VARCHAR),
            NULL
        )) AS OVERALL_SENTIMENT,

        MAX(IFF(
            LOWER(F.VALUE:name::VARCHAR) = 'product quality',
            LOWER(F.VALUE:sentiment::VARCHAR),
            NULL
        )) AS PRODUCT_QUALITY_SENTIMENT,

        MAX(IFF(
            LOWER(F.VALUE:name::VARCHAR) = 'value for money',
            LOWER(F.VALUE:sentiment::VARCHAR),
            NULL
        )) AS VALUE_SENTIMENT,

        MAX(IFF(
            LOWER(F.VALUE:name::VARCHAR) = 'usability',
            LOWER(F.VALUE:sentiment::VARCHAR),
            NULL
        )) AS USABILITY_SENTIMENT,

        MAX(IFF(
            LOWER(F.VALUE:name::VARCHAR) = 'durability',
            LOWER(F.VALUE:sentiment::VARCHAR),
            NULL
        )) AS DURABILITY_SENTIMENT,

        MAX(IFF(
            LOWER(F.VALUE:name::VARCHAR) = 'packaging',
            LOWER(F.VALUE:sentiment::VARCHAR),
            NULL
        )) AS PACKAGING_SENTIMENT

    FROM TMP_SENTIMENT_RESULT S,
    LATERAL FLATTEN(
        INPUT => S.SENTIMENT_RESULT:categories
    ) F

    GROUP BY S.REVIEW_ID;

    INSERT INTO REVIEW_SENTIMENT_ANALYSIS (
        REVIEW_ID,
        ASIN,
        PRODUCT_TITLE,
        PRODUCT_URL,
        MAIN_IMAGE,
        BREADCRUMBS,

        REVIEW_TITLE,
        REVIEW_TEXT,
        REVIEW_DATE,
        STARS,
        USER_ID,
        VARIATION,
        FOUND_HELPFUL,
        VERIFIED_PURCHASE,

        PRODUCT_RATING,
        NUMBER_OF_RATINGS,

        OVERALL_SENTIMENT,
        PRODUCT_QUALITY_SENTIMENT,
        VALUE_SENTIMENT,
        USABILITY_SENTIMENT,
        DURABILITY_SENTIMENT,
        PACKAGING_SENTIMENT,

        RATING_SENTIMENT_MATCH,
        MISMATCH_TYPE,
        REQUIRES_ATTENTION,

        SENTIMENT_RESPONSE,
        ANALYZED_AT
    )
    SELECT
        B.REVIEW_ID,
        B.ASIN,
        B.PRODUCT_TITLE,
        B.PRODUCT_URL,
        B.MAIN_IMAGE,
        B.BREADCRUMBS,

        B.REVIEW_TITLE,
        B.REVIEW_TEXT,
        B.REVIEW_DATE,
        B.STARS,
        B.USER_ID,
        B.VARIATION,
        B.FOUND_HELPFUL,
        B.VERIFIED_PURCHASE,

        B.PRODUCT_RATING,
        B.NUMBER_OF_RATINGS,

        P.OVERALL_SENTIMENT,
        P.PRODUCT_QUALITY_SENTIMENT,
        P.VALUE_SENTIMENT,
        P.USABILITY_SENTIMENT,
        P.DURABILITY_SENTIMENT,
        P.PACKAGING_SENTIMENT,

        CASE
            WHEN B.STARS IN (1, 2)
                 AND P.OVERALL_SENTIMENT = 'negative'
                THEN TRUE

            WHEN B.STARS = 3
                 AND P.OVERALL_SENTIMENT IN ('neutral', 'mixed')
                THEN TRUE

            WHEN B.STARS IN (4, 5)
                 AND P.OVERALL_SENTIMENT = 'positive'
                THEN TRUE

            ELSE FALSE
        END AS RATING_SENTIMENT_MATCH,

        CASE
            WHEN B.STARS >= 4
                 AND P.OVERALL_SENTIMENT = 'negative'
                THEN 'HIGH_RATING_NEGATIVE_TEXT'

            WHEN B.STARS <= 2
                 AND P.OVERALL_SENTIMENT = 'positive'
                THEN 'LOW_RATING_POSITIVE_TEXT'

            WHEN B.STARS = 3
                 AND P.OVERALL_SENTIMENT IN ('positive', 'negative')
                THEN 'THREE_STAR_STRONG_SENTIMENT'

            WHEN NOT (
                (B.STARS IN (1, 2)
                 AND P.OVERALL_SENTIMENT = 'negative')
                OR
                (B.STARS = 3
                 AND P.OVERALL_SENTIMENT IN ('neutral', 'mixed'))
                OR
                (B.STARS IN (4, 5)
                 AND P.OVERALL_SENTIMENT = 'positive')
            )
                THEN 'OTHER_MISMATCH'

            ELSE NULL
        END AS MISMATCH_TYPE,

        CASE
            WHEN P.OVERALL_SENTIMENT = 'negative'
                 AND B.STARS <= 2
                THEN TRUE

            WHEN P.PRODUCT_QUALITY_SENTIMENT = 'negative'
                 OR P.DURABILITY_SENTIMENT = 'negative'
                THEN TRUE

            ELSE FALSE
        END AS REQUIRES_ATTENTION,

        S.SENTIMENT_RESULT,
        CURRENT_TIMESTAMP()

    FROM TMP_REVIEW_BATCH B

    INNER JOIN TMP_SENTIMENT_RESULT S
        ON B.REVIEW_ID = S.REVIEW_ID

    INNER JOIN TMP_PARSED_SENTIMENT P
        ON B.REVIEW_ID = P.REVIEW_ID;

    RETURN 'Successfully processed '
        || V_SELECTED
        || ' reviews';

END;
$$;

SHOW PROCEDURES LIKE 'PROCESS_REVIEW_SENTIMENT'
IN SCHEMA AMAZON_SENTIMENT_DB.ANALYTICS;
