import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

# Constants
REQUIRED_COLUMNS = [
    'category_intent', 'sub_category_intent', 'ACSS_CALL_CTR_DESC',
    'PSO_Vendor', 'call_handle_tm', 'avg_handle_tm__ctgry_call_ctr', 'avg_handle_tm_call_ctr'
]

# Helper function to save multiple styled DataFrames into one HTML file
def save_combined_html(stylers, titles, filename):
    """Save multiple styled DataFrames into one HTML file."""
    with open(filename, 'w') as f:
        f.write("<html><body>\n")
        for styler, title in zip(stylers, titles):
            f.write(f"<h2>{title}</h2>\n")
            f.write(styler.to_html())
        f.write("</body></html>")

# Format insights into a clean table
def format_insights(df, title, columns=None):
    """Format insights into a clean table."""
    renamed_columns = {
        'ACSS_CALL_CTR_DESC': 'Call Center',
        'PSO_Vendor': 'Vendor',
        'avg_handle_time': 'Actual Time (s)',
        'benchmark_handle_time': 'Benchmark (s)',
        'performance_gap_pct': 'Gap %',
        'call_volume': 'Call Volume',
        'call_handle_tm': 'Extreme Call Time (s)',
        'avg_handle_tm__ctgry_call_ctr': 'Avg Handle Time (s)',
        'avg_handle_tm_call_ctr': 'Benchmark Handle Time (s)'
    }

    # Ensure only existing columns are selected
    if columns:
        available_columns = [col for col in columns if col in df.columns]
        formatted_df = df[available_columns].rename(columns=renamed_columns).style.format({
            'Actual Time (s)': '{:.1f}',
            'Benchmark (s)': '{:.1f}',
            'Gap %': '{:.1f}%',
            'Call Volume': '{:,}',
            'Extreme Call Time (s)': '{:.1f}',
            'Avg Handle Time (s)': '{:.1f}',
            'Benchmark Handle Time (s)': '{:.1f}'
        }).set_caption(title)
    else:
        formatted_df = df.rename(columns=renamed_columns).style.format({
            'Actual Time (s)': '{:.1f}',
            'Benchmark (s)': '{:.1f}',
            'Gap %': '{:.1f}%',
            'Call Volume': '{:,}',
            'Extreme Call Time (s)': '{:.1f}',
            'Avg Handle Time (s)': '{:.1f}',
            'Benchmark Handle Time (s)': '{:.1f}'
        }).set_caption(title)

    # Use Styler.map for conditional formatting
    if 'Gap %' in formatted_df.data.columns:
        formatted_df = formatted_df.map(
            lambda x: 'color: red' if isinstance(x, float) and abs(x) > 20 else 'color: green',
            subset=['Gap %']
        )
    return formatted_df

# Generic performance analysis function
def analyze_performance(df, group_by_cols):
    """Generic function to analyze performance metrics."""
    return df.groupby(group_by_cols).agg(
        avg_handle_time=('avg_handle_tm__ctgry_call_ctr', 'mean'),
        benchmark_handle_time=('avg_handle_tm_call_ctr', 'first'),
        call_volume=('PSO_Vendor', 'count')
    ).reset_index() \
        .assign(
        performance_gap=lambda x: x.avg_handle_time - x.benchmark_handle_time,
        performance_gap_pct=lambda x: (
            (x.performance_gap / x.benchmark_handle_time.replace(0, pd.NA) * 100)
            .round(1).fillna(0)
        )
    ) \
        .sort_values('performance_gap_pct', ascending=False)

# Analyze top 10 outlier-like combinations
def analyze_top_10_outliers(df):
    grouped = df.groupby(['ACSS_CALL_CTR_DESC', 'category_intent', 'sub_category_intent']).agg(
        avg_handle_time=('avg_handle_tm__ctgry_call_ctr', 'mean'),
        benchmark_handle_time=('avg_handle_tm_call_ctr', 'first'),
        call_volume=('PSO_Vendor', 'count')
    ).reset_index()

    grouped = grouped.assign(
        performance_gap=lambda x: x.avg_handle_time - x.benchmark_handle_time,
        performance_gap_pct=lambda x: (
            (x.performance_gap / x.benchmark_handle_time * 100)
            .round(1).fillna(0)
        )
    )

    grouped = grouped.sort_values('performance_gap_pct', key=abs, ascending=False).head(10)
    return grouped

# Analyze top 10 extreme calls
def analyze_extreme_calls(df):
    # Identify top 5 highest and top 5 lowest call_handle_tm values
    extreme_high = df.nlargest(5, 'call_handle_tm')
    extreme_low = df.nsmallest(5, 'call_handle_tm')
    extreme_calls = pd.concat([extreme_high, extreme_low])

    # Add avg_handle_tm and benchmark_handle_tm for comparison
    grouped_avg = df.groupby(['category_intent', 'sub_category_intent'])['call_handle_tm'].mean().reset_index()
    grouped_benchmark = df.groupby('ACSS_CALL_CTR_DESC')['avg_handle_tm_call_ctr'].first().reset_index()

    extreme_calls = extreme_calls.merge(
        grouped_avg,
        on=['category_intent', 'sub_category_intent'],
        suffixes=('', '_avg')
    ).merge(
        grouped_benchmark,
        on='ACSS_CALL_CTR_DESC',
        suffixes=('', '_benchmark')
    )

    # Rename columns for clarity
    extreme_calls = extreme_calls.rename(columns={
        'call_handle_tm_avg': 'avg_handle_tm',
        'avg_handle_tm_call_ctr': 'benchmark_handle_tm'
    })

    # Sort by extreme call times for better readability
    extreme_calls = extreme_calls.sort_values('call_handle_tm', ascending=False)

    return extreme_calls

# Load and clean data
try:
    df = pd.read_csv('call_center_data.csv', usecols=REQUIRED_COLUMNS)

    # Validate column existence
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # Optional deduplication based on column availability
    dedup_columns = ['ivr_call_id', 'acss_call_id']
    available_dedup_cols = [col for col in dedup_columns if col in df.columns]

    if available_dedup_cols:
        df = df.drop_duplicates(subset=available_dedup_cols)
    else:
        logging.warning("No deduplication columns found. Skipping drop_duplicates.")

    # Fill missing values and drop rows with NaNs
    df['PSO_Vendor'] = df['PSO_Vendor'].fillna('Unknown')
    df = df.dropna()

    # Generate insights
    performance_summary = analyze_performance(df, ['category_intent', 'sub_category_intent'])
    call_center_perf = analyze_performance(df, ['ACSS_CALL_CTR_DESC', 'category_intent', 'sub_category_intent'])
    vendor_perf = analyze_performance(df, ['PSO_Vendor', 'category_intent', 'sub_category_intent'])

    # Top 10 outlier-like insights
    top_10_outliers = analyze_top_10_outliers(df)

    # Top 10 extreme calls
    extreme_calls = analyze_extreme_calls(df)

    # Log raw DataFrames to the console
    logging.info("=== Overall Performance Summary ===")
    logging.info("\n" + performance_summary.to_string())

    logging.info("\n=== Call Center Performance ===")
    logging.info("\n" + call_center_perf.head(5).to_string())

    logging.info("\n=== Vendor Performance ===")
    logging.info("\n" + vendor_perf.head(5).to_string())

    logging.info("\n=== Top 10 Outlier-Like Insights ===")
    logging.info("\n" + top_10_outliers.to_string())

    logging.info("\n=== Top 10 Extreme Calls ===")
    logging.info("\n" + extreme_calls.to_string())

    # Format insights for HTML
    performance_summary_styled = format_insights(
        performance_summary,
        "Performance Gaps by Category & Sub-Category",
        ['category_intent', 'sub_category_intent',
         'avg_handle_time', 'benchmark_handle_time',
         'performance_gap_pct', 'call_volume']
    )

    call_center_perf_styled = format_insights(
        call_center_perf.head(5),
        "Top 5 Challenging Call Center Combinations",
        ['ACSS_CALL_CTR_DESC', 'category_intent', 'sub_category_intent',
         'avg_handle_time', 'benchmark_handle_time',
         'performance_gap_pct', 'call_volume']
    )

    vendor_perf_styled = format_insights(
        vendor_perf.head(5),
        "Top 5 Challenging Vendor Combinations",
        ['PSO_Vendor', 'category_intent', 'sub_category_intent',
         'avg_handle_time', 'benchmark_handle_time',
         'performance_gap_pct', 'call_volume']
    )

    top_10_outliers_styled = format_insights(
        top_10_outliers,
        "Top 10 Outlier-Like Insights",
        ['ACSS_CALL_CTR_DESC', 'category_intent', 'sub_category_intent',
         'avg_handle_time', 'benchmark_handle_time',
         'performance_gap_pct', 'call_volume']
    )

    extreme_calls_styled = format_insights(
        extreme_calls,
        "Top 10 Extreme Calls"
    )

    # Save all tables into one HTML file
    save_combined_html(
        stylers=[
            performance_summary_styled,
            call_center_perf_styled,
            vendor_perf_styled,
            top_10_outliers_styled,
            extreme_calls_styled
        ],
        titles=[
            "Overall Performance Summary",
            "Top 5 Challenging Call Center Combinations",
            "Top 5 Challenging Vendor Combinations",
            "Top 10 Outlier-Like Insights",
            "Top 10 Extreme Calls"
        ],
        filename="combined_insights.html"
    )

except Exception as e:
    logging.error(f"An error occurred: {e}")