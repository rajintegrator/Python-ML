import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load the dataset
file_path = "/mnt/data/call_center_data.csv"
df = pd.read_csv(file_path)

# Remove duplicates based on unique combination of ivr_call_id and acss_call_id
df = df.drop_duplicates(subset=['ivr_call_id', 'acss_call_id'])

# Fill empty PSO Vendor values with associated ACSS_CALL_CTR_DESC + " - No PSO Vendor Associated"
df['PSO_Vendor'] = df.apply(lambda row: row['ACSS_CALL_CTR_DESC'] + " - No PSO Vendor Associated" if pd.isnull(row['PSO_Vendor']) else row['PSO_Vendor'], axis=1)

# Convert call_answer_dt to datetime
df['call_answer_dt'] = pd.to_datetime(df['call_answer_dt'])

# Basic EDA
category_intent_counts = df['category_intent'].value_counts(normalize=True) * 100
sub_category_intent_counts = df.groupby(['category_intent', 'sub_category_intent']).size().unstack(fill_value=0)

# Longest and Shortest Call Handling Times
longest_call = df.loc[df['call_handle_tm'].idxmax()]
shortest_call = df.loc[df['call_handle_tm'].idxmin()]
print(f"Longest Call: {longest_call['category_intent']} - {longest_call['sub_category_intent']} ({longest_call['call_handle_tm']} sec)")
print(f"Shortest Call: {shortest_call['category_intent']} - {shortest_call['sub_category_intent']} ({shortest_call['call_handle_tm']} sec)")

# Performance Variance by Call Centers and PSO Vendors
call_center_performance = df.groupby('ACSS_CALL_CTR_DESC')['call_handle_tm'].agg(['mean', 'min', 'max']).reset_index()
pso_vendor_performance = df.groupby('PSO_Vendor')['call_handle_tm'].agg(['mean', 'min', 'max']).reset_index()

# Callout for highest and lowest performing call centers
best_call_center = call_center_performance.loc[call_center_performance['mean'].idxmin()]
worst_call_center = call_center_performance.loc[call_center_performance['mean'].idxmax()]
print(f"Best Performing Call Center: {best_call_center['ACSS_CALL_CTR_DESC']} (Avg Handle Time: {best_call_center['mean']:.2f} sec)")
print(f"Worst Performing Call Center: {worst_call_center['ACSS_CALL_CTR_DESC']} (Avg Handle Time: {worst_call_center['mean']:.2f} sec)")

# Distribution of call handle times
time_bins = [1306, 5000, 10000, 15000, 20000]
labels = ['1306-5000', '5001-10000', '10001-15000', '15001-20000']
df['call_handle_tm_bin'] = pd.cut(df['call_handle_tm'], bins=time_bins, labels=labels)
call_time_distribution = df['call_handle_tm_bin'].value_counts(normalize=True) * 100

# Compare call handle time with average handle times
df['above_avg_ctgry'] = df['call_handle_tm'] > df['avg_handle_tm__ctgry_call_ctr']
df['above_avg_all'] = df['call_handle_tm'] > df['avg_handle_tm_call_ctr']

grouped_df = df.groupby(['ACSS_CALL_CTR_DESC', 'PSO_Vendor']).agg(
    total_calls=('call_handle_tm', 'count'),
    avg_call_handle_tm=('call_handle_tm', 'mean'),
    above_avg_ctgry_percentage=('above_avg_ctgry', lambda x: (x.sum() / len(x)) * 100),
    above_avg_all_percentage=('above_avg_all', lambda x: (x.sum() / len(x)) * 100)
).reset_index()

# Callout for PSO Vendors with highest and lowest above-average call handle times
best_vendor = grouped_df.loc[grouped_df['above_avg_all_percentage'].idxmin()]
worst_vendor = grouped_df.loc[grouped_df['above_avg_all_percentage'].idxmax()]
print(f"Best PSO Vendor: {best_vendor['PSO_Vendor']} ({best_vendor['above_avg_all_percentage']:.2f}% calls above avg)")
print(f"Worst PSO Vendor: {worst_vendor['PSO_Vendor']} ({worst_vendor['above_avg_all_percentage']:.2f}% calls above avg)")

# Visualizations
plt.figure(figsize=(10, 6))
sns.countplot(data=df, y='category_intent', order=category_intent_counts.index)
plt.title('Distribution of Category Intents')
plt.xlabel('Number of Calls')
plt.ylabel('Category Intent')
plt.show()

if 'Billing' in sub_category_intent_counts.index:
    billing_sub_intents = sub_category_intent_counts.loc['Billing']
    sorted_billing_sub_intents = billing_sub_intents.sort_values(ascending=False).index
    plt.figure(figsize=(10, 6))
    sns.countplot(data=df[df['category_intent'] == 'Billing'], y='sub_category_intent', order=sorted_billing_sub_intents)
    plt.title('Distribution of Sub-category Intents for Billing')
    plt.xlabel('Number of Calls')
    plt.ylabel('Sub-category Intent')
    plt.show()

plt.figure(figsize=(8, 8))
call_time_distribution.plot(kind='pie', autopct='%1.1f%%', startangle=90)
plt.title('Distribution of Call Handle Times')
plt.ylabel('')
plt.show()

pivot_table = grouped_df.pivot(index='ACSS_CALL_CTR_DESC', columns='PSO_Vendor', values='above_avg_ctgry_percentage')
plt.figure(figsize=(12, 8))
sns.heatmap(pivot_table, annot=True, cmap='coolwarm', fmt='.1f')
plt.title('Percentage of Calls Above Average Handle Time per Category Call Center')
plt.show()
