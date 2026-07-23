-- ============================================================
-- 05_create_analysis_table.sql
-- Stores sentiment once so Streamlit does not call Cortex
-- whenever the dashboard refreshes.
-- ============================================================

USE WAREHOUSE AMAZON_SENTIMENT_WH;
USE DATABASE AMAZON_SENTIMENT_DB;
USE SCHEMA ANALYTICS;

CREATE OR REPLACE TABLE REVIEW_SENTIMENT_ANALYSIS (
    REVIEW_ID                   VARCHAR,
    ASIN                        VARCHAR,
    PRODUCT_TITLE               VARCHAR,
    PRODUCT_URL                 VARCHAR,
    MAIN_IMAGE                  VARCHAR,
    BREADCRUMBS                 VARCHAR,

    REVIEW_TITLE                VARCHAR,
    REVIEW_TEXT                 VARCHAR,
    REVIEW_DATE                 DATE,
    STARS                       NUMBER,
    USER_ID                     VARCHAR,
    VARIATION                   VARCHAR,
    FOUND_HELPFUL               NUMBER,
    VERIFIED_PURCHASE           VARCHAR,

    PRODUCT_RATING              FLOAT,
    NUMBER_OF_RATINGS           NUMBER,

    OVERALL_SENTIMENT           VARCHAR,
    PRODUCT_QUALITY_SENTIMENT   VARCHAR,
    VALUE_SENTIMENT             VARCHAR,
    USABILITY_SENTIMENT         VARCHAR,
    DURABILITY_SENTIMENT        VARCHAR,
    PACKAGING_SENTIMENT         VARCHAR,

    RATING_SENTIMENT_MATCH      BOOLEAN,
    MISMATCH_TYPE               VARCHAR,
    REQUIRES_ATTENTION          BOOLEAN,

    SENTIMENT_RESPONSE          VARIANT,
    ANALYZED_AT                 TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
