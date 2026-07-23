import json
from typing import Any

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Amazon Sentiment Analyzer",
    page_icon="🛍️",
    layout="wide",
)

session = st.connection("snowflake").session()

FQN = "AMAZON_SENTIMENT_DB.ANALYTICS"


@st.cache_data(ttl=300)
def query_df(query: str) -> pd.DataFrame:
    return session.sql(query).to_pandas()


def escape_sql(value: str) -> str:
    return value.replace("'", "''")


def parse_variant(value: Any) -> dict:
    if value is None:
        return {}

    if isinstance(value, dict):
        return value

    if hasattr(value, "as_dict"):
        return value.as_dict()

    try:
        return json.loads(str(value))
    except (TypeError, json.JSONDecodeError):
        return {}


def sentiment_display(value: str) -> str:
    sentiment = (value or "unknown").lower()

    icons = {
        "positive": "🟢",
        "negative": "🔴",
        "neutral": "⚪",
        "mixed": "🟡",
        "unknown": "❔",
    }

    return f"{icons.get(sentiment, '❔')} {sentiment.title()}"


st.title("Amazon Review Sentiment Analyzer")
st.caption(
    "Real Amazon product reviews from Snowflake Marketplace, "
    "analyzed with Snowflake Cortex AI_SENTIMENT."
)

overview_tab, product_tab, live_tab = st.tabs(
    [
        "Overview",
        "Product Analysis",
        "Live Analyzer",
    ]
)


# ============================================================
# OVERVIEW
# ============================================================
with overview_tab:

    kpi_df = query_df(
        f"""
        SELECT
            COUNT(*) AS TOTAL_REVIEWS,
            COUNT(DISTINCT ASIN) AS TOTAL_PRODUCTS,

            ROUND(
                COUNT_IF(OVERALL_SENTIMENT = 'positive')
                * 100.0 / NULLIF(COUNT(*), 0),
                2
            ) AS POSITIVE_PERCENTAGE,

            ROUND(
                COUNT_IF(OVERALL_SENTIMENT = 'negative')
                * 100.0 / NULLIF(COUNT(*), 0),
                2
            ) AS NEGATIVE_PERCENTAGE,

            COUNT_IF(REQUIRES_ATTENTION)
                AS ATTENTION_REVIEWS,

            COUNT_IF(RATING_SENTIMENT_MATCH = FALSE)
                AS RATING_MISMATCHS

        FROM {FQN}.REVIEW_SENTIMENT_ANALYSIS
        """
    )

    if kpi_df.empty or int(
        kpi_df.iloc[0]["TOTAL_REVIEWS"] or 0
    ) == 0:
        st.warning(
            "No analyzed reviews are available. Run "
            "`CALL AMAZON_SENTIMENT_DB.ANALYTICS."
            "PROCESS_REVIEW_SENTIMENT(10);` first."
        )

    else:
        row = kpi_df.iloc[0]
        metrics = st.columns(6)

        metrics[0].metric(
            "Reviews analyzed",
            f"{int(row['TOTAL_REVIEWS']):,}",
        )

        metrics[1].metric(
            "Products",
            f"{int(row['TOTAL_PRODUCTS']):,}",
        )

        metrics[2].metric(
            "Positive",
            f"{float(row['POSITIVE_PERCENTAGE'] or 0):.1f}%",
        )

        metrics[3].metric(
            "Negative",
            f"{float(row['NEGATIVE_PERCENTAGE'] or 0):.1f}%",
        )

        metrics[4].metric(
            "Need attention",
            f"{int(row['ATTENTION_REVIEWS'] or 0):,}",
        )

        metrics[5].metric(
            "Rating mismatches",
            f"{int(row['RATING_MISMATCHS'] or 0):,}",
        )

        left, right = st.columns(2)

        with left:
            st.subheader("Overall sentiment")

            sentiment_df = query_df(
                f"""
                SELECT
                    OVERALL_SENTIMENT,
                    REVIEW_COUNT
                FROM {FQN}.VW_SENTIMENT_OVERVIEW
                ORDER BY REVIEW_COUNT DESC
                """
            )

            if not sentiment_df.empty:
                st.bar_chart(
                    sentiment_df.set_index(
                        "OVERALL_SENTIMENT"
                    )["REVIEW_COUNT"]
                )

        with right:
            st.subheader("Sentiment by star rating")

            stars_df = query_df(
                f"""
                SELECT
                    STARS,
                    OVERALL_SENTIMENT,
                    COUNT(*) AS REVIEW_COUNT
                FROM {FQN}.REVIEW_SENTIMENT_ANALYSIS
                GROUP BY STARS, OVERALL_SENTIMENT
                ORDER BY STARS, OVERALL_SENTIMENT
                """
            )

            if not stars_df.empty:
                stars_pivot = stars_df.pivot_table(
                    index="STARS",
                    columns="OVERALL_SENTIMENT",
                    values="REVIEW_COUNT",
                    fill_value=0,
                )

                st.bar_chart(stars_pivot)

        left, right = st.columns(2)

        with left:
            st.subheader("Aspect sentiment")

            aspect_df = query_df(
                f"""
                SELECT
                    ASPECT,
                    SENTIMENT,
                    REVIEW_COUNT
                FROM {FQN}.VW_ASPECT_SENTIMENT
                ORDER BY ASPECT, SENTIMENT
                """
            )

            if not aspect_df.empty:
                aspect_pivot = aspect_df.pivot_table(
                    index="ASPECT",
                    columns="SENTIMENT",
                    values="REVIEW_COUNT",
                    fill_value=0,
                )

                st.bar_chart(aspect_pivot)

        with right:
            st.subheader("Products with most negative sentiment")

            product_df = query_df(
                f"""
                SELECT
                    PRODUCT_TITLE,
                    ANALYZED_REVIEWS,
                    NEGATIVE_PERCENTAGE,
                    ATTENTION_REVIEWS
                FROM {FQN}.VW_PRODUCT_SENTIMENT
                WHERE ANALYZED_REVIEWS >= 3
                ORDER BY
                    NEGATIVE_PERCENTAGE DESC,
                    ATTENTION_REVIEWS DESC
                LIMIT 10
                """
            )

            st.dataframe(
                product_df,
                use_container_width=True,
                hide_index=True,
            )

        st.subheader("Rating and text sentiment mismatches")

        mismatch_df = query_df(
            f"""
            SELECT
                PRODUCT_TITLE,
                STARS,
                OVERALL_SENTIMENT,
                MISMATCH_TYPE,
                REVIEW_TITLE,
                REVIEW_TEXT
            FROM {FQN}.VW_RATING_MISMATCH
            ORDER BY FOUND_HELPFUL DESC NULLS LAST
            LIMIT 20
            """
        )

        st.dataframe(
            mismatch_df,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# PRODUCT ANALYSIS
# ============================================================
with product_tab:

    products_df = query_df(
        f"""
        SELECT
            ASIN,
            PRODUCT_TITLE
        FROM {FQN}.VW_PRODUCT_SENTIMENT
        ORDER BY PRODUCT_TITLE
        """
    )

    if products_df.empty:
        st.info("Process reviews to populate product analysis.")

    else:
        product_options = {
            f"{row.PRODUCT_TITLE} [{row.ASIN}]": row.ASIN
            for row in products_df.itertuples()
        }

        selected_label = st.selectbox(
            "Select a product",
            list(product_options.keys()),
        )

        selected_asin = escape_sql(
            product_options[selected_label]
        )

        selected_product_df = query_df(
            f"""
            SELECT *
            FROM {FQN}.VW_PRODUCT_SENTIMENT
            WHERE ASIN = '{selected_asin}'
            """
        )

        if not selected_product_df.empty:
            product = selected_product_df.iloc[0]

            image_column, details_column = st.columns([1, 3])

            with image_column:
                image_url = product.get("MAIN_IMAGE")

                if pd.notna(image_url) and str(image_url).strip():
                    st.image(
                        str(image_url),
                        use_container_width=True,
                    )

            with details_column:
                st.subheader(str(product["PRODUCT_TITLE"]))
                st.caption(f"ASIN: {product['ASIN']}")

                metrics = st.columns(5)

                metrics[0].metric(
                    "Amazon rating",
                    f"{float(product['PRODUCT_RATING'] or 0):.1f}",
                )

                metrics[1].metric(
                    "Total ratings",
                    f"{int(product['NUMBER_OF_RATINGS'] or 0):,}",
                )

                metrics[2].metric(
                    "Analyzed reviews",
                    f"{int(product['ANALYZED_REVIEWS'] or 0):,}",
                )

                metrics[3].metric(
                    "Positive",
                    f"{float(product['POSITIVE_PERCENTAGE'] or 0):.1f}%",
                )

                metrics[4].metric(
                    "Negative",
                    f"{float(product['NEGATIVE_PERCENTAGE'] or 0):.1f}%",
                )

            reviews_df = query_df(
                f"""
                SELECT
                    REVIEW_TITLE,
                    REVIEW_TEXT,
                    STARS,
                    OVERALL_SENTIMENT,
                    PRODUCT_QUALITY_SENTIMENT,
                    VALUE_SENTIMENT,
                    USABILITY_SENTIMENT,
                    DURABILITY_SENTIMENT,
                    PACKAGING_SENTIMENT,
                    RATING_SENTIMENT_MATCH,
                    REQUIRES_ATTENTION,
                    FOUND_HELPFUL
                FROM {FQN}.REVIEW_SENTIMENT_ANALYSIS
                WHERE ASIN = '{selected_asin}'
                ORDER BY
                    REQUIRES_ATTENTION DESC,
                    FOUND_HELPFUL DESC
                """
            )

            st.subheader("Customer reviews")

            for review in reviews_df.itertuples():

                title = review.REVIEW_TITLE or "Customer review"

                with st.expander(
                    f"{int(review.STARS)}★ · "
                    f"{sentiment_display(review.OVERALL_SENTIMENT)} · "
                    f"{title}"
                ):
                    st.write(review.REVIEW_TEXT)

                    aspects = pd.DataFrame(
                        {
                            "Aspect": [
                                "Product quality",
                                "Value for money",
                                "Usability",
                                "Durability",
                                "Packaging",
                            ],
                            "Sentiment": [
                                sentiment_display(
                                    review.PRODUCT_QUALITY_SENTIMENT
                                ),
                                sentiment_display(
                                    review.VALUE_SENTIMENT
                                ),
                                sentiment_display(
                                    review.USABILITY_SENTIMENT
                                ),
                                sentiment_display(
                                    review.DURABILITY_SENTIMENT
                                ),
                                sentiment_display(
                                    review.PACKAGING_SENTIMENT
                                ),
                            ],
                        }
                    )

                    st.dataframe(
                        aspects,
                        use_container_width=True,
                        hide_index=True,
                    )

                    columns = st.columns(3)

                    columns[0].write(
                        f"**Rating-text match:** "
                        f"{'Yes' if review.RATING_SENTIMENT_MATCH else 'No'}"
                    )

                    columns[1].write(
                        f"**Helpful votes:** "
                        f"{int(review.FOUND_HELPFUL or 0)}"
                    )

                    columns[2].write(
                        f"**Needs attention:** "
                        f"{'Yes' if review.REQUIRES_ATTENTION else 'No'}"
                    )


# ============================================================
# LIVE ANALYZER
# ============================================================
with live_tab:

    st.subheader("Analyze a review instantly")

    review_stars = st.slider(
        "Review stars",
        min_value=1,
        max_value=5,
        value=3,
    )

    review_text = st.text_area(
        "Customer review",
        height=160,
        placeholder=(
            "The chair is comfortable and easy to assemble, "
            "but one leg became loose after two weeks."
        ),
    )

    if st.button(
        "Analyze Sentiment",
        type="primary",
    ):
        clean_text = review_text.strip()

        if len(clean_text) < 10:
            st.error(
                "Enter a review containing at least 10 characters."
            )

        else:
            with st.spinner(
                "Analyzing review with Snowflake Cortex AI..."
            ):
                result = session.sql(
                    """
                    SELECT AI_SENTIMENT(
                        ?,
                        [
                            'product quality',
                            'value for money',
                            'usability',
                            'durability',
                            'packaging'
                        ]
                    ) AS RESULT
                    """,
                    params=[clean_text],
                ).collect()[0]["RESULT"]

            result_object = parse_variant(result)
            categories = result_object.get("categories", [])

            sentiments = {
                str(item.get("name", "")).lower():
                str(item.get("sentiment", "unknown")).lower()
                for item in categories
            }

            overall = sentiments.get("overall", "unknown")

            rating_match = (
                (
                    review_stars <= 2
                    and overall == "negative"
                )
                or
                (
                    review_stars == 3
                    and overall in {"neutral", "mixed"}
                )
                or
                (
                    review_stars >= 4
                    and overall == "positive"
                )
            )

            requires_attention = (
                (
                    overall == "negative"
                    and review_stars <= 2
                )
                or
                sentiments.get("product quality") == "negative"
                or
                sentiments.get("durability") == "negative"
            )

            metrics = st.columns(3)

            metrics[0].metric(
                "Overall sentiment",
                sentiment_display(overall),
            )

            metrics[1].metric(
                "Rating-text match",
                "Yes" if rating_match else "No",
            )

            metrics[2].metric(
                "Needs attention",
                "Yes" if requires_attention else "No",
            )

            aspect_rows = []

            for aspect in [
                "product quality",
                "value for money",
                "usability",
                "durability",
                "packaging",
            ]:
                aspect_rows.append(
                    {
                        "Aspect": aspect.title(),
                        "Sentiment": sentiment_display(
                            sentiments.get(aspect, "unknown")
                        ),
                    }
                )

            st.dataframe(
                pd.DataFrame(aspect_rows),
                use_container_width=True,
                hide_index=True,
            )

            if requires_attention:
                st.warning(
                    "This review contains negative product-quality "
                    "or durability feedback and should be reviewed."
                )
            else:
                st.success(
                    "No immediate product concern was detected."
                )
