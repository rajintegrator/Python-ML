import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats

# Load the dataset
file_path = "R:/Learning/Python/Python-WS/Data_Project/call_center_data.csv"
df = pd.read_csv(file_path)

# Remove duplicates based on unique combination of ivr_call_id and acss_call_id
df = df.drop_duplicates(subset=['ivr_call_id', 'acss_call_id'])

# Fill empty PSO Vendor values with associated ACSS_CALL_CTR_DESC + " - No PSO Vendor Associated"
df['PSO_Vendor'] = df.apply(
    lambda row: row['ACSS_CALL_CTR_DESC'] + " - No PSO Vendor Associated" if pd.isnull(row['PSO_Vendor']) else row[
        'PSO_Vendor'], axis=1)

# Convert call_answer_dt to datetime
df['call_answer_dt'] = pd.to_datetime(df['call_answer_dt'])

# Filter dataset to include only "Billing" or "Disconnect" category_intents
df = df[df['category_intent'].isin(['Billing', 'Disconnect'])]


# Function to filter data based on intent
def filter_data(intent):
    return df[df['category_intent'] == intent].copy()


# Function to identify outliers using Z-score method and additional deviation check
def find_outliers(data, column, z_threshold=2, deviation_threshold=0.3):
    # Z-score method for outliers
    z_scores = np.abs(stats.zscore(data[column]))
    outliers_zscore = data[z_scores > z_threshold]

    # Deviation-based outliers (deviation from mean)
    mean_handle_time = data[column].mean()
    deviation_outliers = data[np.abs(data[column] - mean_handle_time) / mean_handle_time > deviation_threshold]

    # Combine both conditions
    combined_outliers = pd.concat([outliers_zscore, deviation_outliers]).drop_duplicates()

    return combined_outliers


# Function to describe the issues with the outliers
def explain_outliers(outliers):
    outlier_explanations = []
    for index, row in outliers.iterrows():
        issue = "Unknown issue"
        if row['call_handle_tm'] > 1000:
            issue = "Call took unusually long; this could be due to a complex issue or agent inefficiency."
        elif row['call_handle_tm'] < 30:
            issue = "Call was resolved too quickly; possibly due to misclassification or premature call end."

        explanation = f"Call ID: {row['ivr_call_id']} - Call Handle Time: {row['call_handle_tm']} sec | Possible Issue: {issue}"
        outlier_explanations.append(explanation)

    return outlier_explanations


# Basic EDA
category_intent_counts = df['category_intent'].value_counts(normalize=True) * 100
sub_category_intent_counts = df.groupby(['category_intent', 'sub_category_intent']).size().unstack(fill_value=0)

# Longest and Shortest Call Handling Times
longest_call = df.loc[df['call_handle_tm'].idxmax()]
shortest_call = df.loc[df['call_handle_tm'].idxmin()]
print(
    f"Longest Call: {longest_call['category_intent']} - {longest_call['sub_category_intent']} ({longest_call['call_handle_tm']} sec)")
print(
    f"Shortest Call: {shortest_call['category_intent']} - {shortest_call['sub_category_intent']} ({shortest_call['call_handle_tm']} sec)")

# Performance Variance by Call Centers and PSO Vendors
call_center_performance = df.groupby('ACSS_CALL_CTR_DESC')['call_handle_tm'].agg(['mean', 'min', 'max']).reset_index()
pso_vendor_performance = df.groupby('PSO_Vendor')['call_handle_tm'].agg(['mean', 'min', 'max']).reset_index()

# Key Insights and Performance Callouts
# Callout 1: Intent and Sub-Intent Combination Performance
print("\n### Performance Insights for Intent and Sub-Intent Combinations ###")
intent_subintent_performance = \
    df.groupby(['category_intent', 'sub_category_intent', 'ACSS_CALL_CTR_DESC', 'PSO_Vendor'])[
        'call_handle_tm'].mean().reset_index()
for intent, sub_intent in intent_subintent_performance.groupby(['category_intent', 'sub_category_intent']):
    highest_time_row = sub_intent.loc[sub_intent['call_handle_tm'].idxmax()]
    print(
        f"For {intent[0]} -> {intent[1]}, the highest call handle time is at {highest_time_row['ACSS_CALL_CTR_DESC']} with vendor {highest_time_row['PSO_Vendor']} ({highest_time_row['call_handle_tm']} sec)")

# Callout 2: Best and Worst Performing Call Centers and Associated Vendors
best_call_center = call_center_performance.loc[call_center_performance['mean'].idxmin()]
worst_call_center = call_center_performance.loc[call_center_performance['mean'].idxmax()]
print(
    f"\nBest Performing Call Center: {best_call_center['ACSS_CALL_CTR_DESC']} (Avg Handle Time: {best_call_center['mean']:.2f} sec)")
print(
    f"Worst Performing Call Center: {worst_call_center['ACSS_CALL_CTR_DESC']} (Avg Handle Time: {worst_call_center['mean']:.2f} sec)")

# Callout 3: Highest Time Taken by Intent and Sub-Intent per Call Center and Vendor
highest_time_intent = df.groupby(['category_intent', 'sub_category_intent', 'ACSS_CALL_CTR_DESC', 'PSO_Vendor'])[
    'call_handle_tm'].mean().reset_index()
max_time_intent = highest_time_intent.loc[highest_time_intent['call_handle_tm'].idxmax()]
print(
    f"Highest Call Handle Time Intent: {max_time_intent['category_intent']} - {max_time_intent['sub_category_intent']} at {max_time_intent['ACSS_CALL_CTR_DESC']} ({max_time_intent['PSO_Vendor']}) with {max_time_intent['call_handle_tm']:.2f} sec")

# Callout 4: Call Centers with Best and Worst Performance for Vendors
print("\n### Call Centers with Best and Worst Performance for Vendors ###")
grouped_df = df.groupby(['ACSS_CALL_CTR_DESC', 'PSO_Vendor']).agg(
    total_calls=('call_handle_tm', 'count'),
    avg_call_handle_tm=('call_handle_tm', 'mean'),
).reset_index()
best_vendor = grouped_df.loc[grouped_df['avg_call_handle_tm'].idxmin()]
worst_vendor = grouped_df.loc[grouped_df['avg_call_handle_tm'].idxmax()]
print(
    f"Best PSO Vendor: {best_vendor['PSO_Vendor']} with Call Center: {best_vendor['ACSS_CALL_CTR_DESC']} (Avg Handle Time: {best_vendor['avg_call_handle_tm']:.2f} sec)")
print(
    f"Worst PSO Vendor: {worst_vendor['PSO_Vendor']} with Call Center: {worst_vendor['ACSS_CALL_CTR_DESC']} (Avg Handle Time: {worst_vendor['avg_call_handle_tm']:.2f} sec)")


# Visualization: Boxplot for Call Handle Time by Sub-Intent, Call Center, and PSO Vendor
def plot_boxplots(data, top_percentage=0.1):
    # Select top percentage of data
    n = int(len(data) * top_percentage)
    sampled_data = data.sample(n=n, random_state=42)

    # Box plot for call handle time by sub-intent
    plt.figure(figsize=(15, 8))
    sns.boxplot(x='sub_category_intent', y='call_handle_tm', data=sampled_data)
    plt.title('Distribution of Call Handle Time by Sub-Intent')
    plt.xticks(rotation=90)
    plt.show()

    # Box plot for call handle time by call center
    plt.figure(figsize=(15, 8))
    sns.boxplot(x='ACSS_CALL_CTR_DESC', y='call_handle_tm', data=sampled_data)
    plt.xticks(rotation=90)
    plt.title('Distribution of Call Handle Time by Call Center')
    plt.show()

    # Box plot for call handle time by PSO Vendor
    plt.figure(figsize=(15, 8))
    sns.boxplot(x='PSO_Vendor', y='call_handle_tm', data=sampled_data)
    plt.xticks(rotation=90)
    plt.title('Distribution of Call Handle Time by PSO Vendor')
    plt.show()


# Main function to execute the analysis
def main(intent):
    # Filter data based on intent
    data = filter_data(intent)

    # Plot box plots for call handle times
    plot_boxplots(data)

    # Provide performance insights
    print("\n### Detailed Performance Insights ###")
    provide_insights(data)


# Function to provide detailed insights and recommendations
def provide_insights(data):
    print("\n### Detailed Insights and Recommendations ###")

    # Identify outliers in call handle times
    print("\n#### Outliers in Call Handle Times ####")
    outliers = find_outliers(data, 'call_handle_tm')
    outliers_display = outliers[
        ['cust_id', 'ivr_call_id', 'acss_call_id', 'call_handle_tm', 'PSO_Vendor', 'ACSS_CALL_CTR_DESC']].head(5)
    print(outliers_display)

    # Explain the outliers
    explanations = explain_outliers(outliers_display)
    for explanation in explanations:
        print(explanation)

    # Identify underperforming call centers and PSO Vendors
    print("\n#### Underperforming Call Centers and PSO Vendors ####")
    avg_call_handle_time_vendor = data.groupby('PSO_Vendor')['call_handle_tm'].mean().sort_values(ascending=False)
    print("Average Call Handle Time by PSO Vendor:")
    print(avg_call_handle_time_vendor)

    avg_call_handle_time_center = data.groupby('ACSS_CALL_CTR_DESC')['call_handle_tm'].mean().sort_values(
        ascending=False)
    print("\nAverage Call Handle Time by Call Center:")
    print(avg_call_handle_time_center)

    # Recommendations
    print("\n#### Recommendations ####")
    print("1. Focus on reducing outliers in call handle times for high sub-intents.")
    print("2. Improve processes for underperforming PSO Vendors and call centers.")
    print("3. Conduct root cause analysis for outliers and implement corrective actions.")
    print("4. Consider additional training for agents handling complex sub-intents.")


# Run the analysis for either Billing or Disconnect intent
if __name__ == "__main__":
    intent = input("Enter the intent ('Billing' or 'Disconnect'): ").strip().capitalize()
    main(intent)
