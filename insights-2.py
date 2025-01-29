import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load the dataset
file_path = "R:/Learning/Python/Python-WS/Data_Project/call_center_data.csv"
df = pd.read_csv(file_path)

# Remove duplicates based on unique combination of ivr_call_id and acss_call_id
df = df.drop_duplicates(subset=['ivr_call_id', 'acss_call_id'])

# Fill empty PSO Vendor values with associated ACSS_CALL_CTR_DESC + " - No PSO Vendor Associated"
df['PSO_Vendor'] = df.apply(lambda row: row['ACSS_CALL_CTR_DESC'] + " - No PSO Vendor Associated" if pd.isnull(row['PSO_Vendor']) else row['PSO_Vendor'], axis=1)

# Convert call_answer_dt to datetime
df['call_answer_dt'] = pd.to_datetime(df['call_answer_dt'])

# Filter dataset to include only "Billing" or "Disconnect" category_intents
df = df[df['category_intent'].isin(['Billing', 'Disconnect'])]

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

# Best and Worst Performing Call Centers
best_call_center = call_center_performance.loc[call_center_performance['mean'].idxmin()]
worst_call_center = call_center_performance.loc[call_center_performance['mean'].idxmax()]
print(f"Best Performing Call Center: {best_call_center['ACSS_CALL_CTR_DESC']} (Avg Handle Time: {best_call_center['mean']:.2f} sec)")
print(f"Worst Performing Call Center: {worst_call_center['ACSS_CALL_CTR_DESC']} (Avg Handle Time: {worst_call_center['mean']:.2f} sec)")

# Highest Time Taken by Intent and Sub-intent per Call Center and Vendor
highest_time_intent = df.groupby(['category_intent', 'sub_category_intent', 'ACSS_CALL_CTR_DESC', 'PSO_Vendor'])['call_handle_tm'].mean().reset_index()
max_time_intent = highest_time_intent.loc[highest_time_intent['call_handle_tm'].idxmax()]
print(f"Highest Call Handle Time Intent: {max_time_intent['category_intent']} - {max_time_intent['sub_category_intent']} at {max_time_intent['ACSS_CALL_CTR_DESC']} ({max_time_intent['PSO_Vendor']}) with {max_time_intent['call_handle_tm']:.2f} sec")

# Create 'call_handle_tm_bin' correctly before using it in countplot
time_bins = [1306, 5000, 10000, 15000, 20000]
labels = ['1306-5000', '5001-10000', '10001-15000', '15001-20000']
df['call_handle_tm_bin'] = pd.cut(df['call_handle_tm'], bins=time_bins, labels=labels)

# Compare call handle time with average handle times
df['above_avg_ctgry'] = df['call_handle_tm'] > df['avg_handle_tm__ctgry_call_ctr']
df['above_avg_all'] = df['call_handle_tm'] > df['avg_handle_tm_call_ctr']

grouped_df = df.groupby(['ACSS_CALL_CTR_DESC', 'PSO_Vendor']).agg(
    total_calls=('call_handle_tm', 'count'),
    avg_call_handle_tm=('call_handle_tm', 'mean'),
    above_avg_ctgry_percentage=('above_avg_ctgry', lambda x: (x.sum() / len(x)) * 100),
    above_avg_all_percentage=('above_avg_all', lambda x: (x.sum() / len(x)) * 100)
).reset_index()

# Best and Worst PSO Vendors
best_vendor = grouped_df.loc[grouped_df['above_avg_all_percentage'].idxmin()]
worst_vendor = grouped_df.loc[grouped_df['above_avg_all_percentage'].idxmax()]
print(f"Best PSO Vendor: {best_vendor['PSO_Vendor']} ({best_vendor['above_avg_all_percentage']:.2f}% calls above avg)")
print(f"Worst PSO Vendor: {worst_vendor['PSO_Vendor']} ({worst_vendor['above_avg_all_percentage']:.2f}% calls above avg)")

# Important Visualizations
plt.figure(figsize=(10, 6))
sns.boxplot(x='category_intent', y='call_handle_tm', data=df)
plt.title('Call Handle Time Distribution by Intent')
plt.xlabel('Intent')
plt.ylabel('Call Handle Time (seconds)')
plt.show()

# Barplot for average call handle time by Call Center and PSO Vendor
plt.figure(figsize=(14, 7))
sns.barplot(x='ACSS_CALL_CTR_DESC', y='avg_call_handle_tm', data=grouped_df, hue='PSO_Vendor', estimator=np.mean, errorbar=None)
plt.xticks(rotation=90)
plt.title('Average Call Handle Time by Call Center and PSO Vendor')
plt.xlabel('Call Center')
plt.ylabel('Average Call Handle Time (seconds)')
plt.show()

# Countplot for call_handle_tm_bin with hue as ACSS_CALL_CTR_DESC
plt.figure(figsize=(14, 7))
sns.countplot(x='call_handle_tm_bin', data=df, hue='ACSS_CALL_CTR_DESC')
plt.title('Distribution of Call Handle Times across Call Centers')
plt.xlabel('Call Handle Time Bins')
plt.ylabel('Frequency')
plt.show()

# Additional countplot showing distribution per PSO Vendor
plt.figure(figsize=(14, 7))
sns.countplot(x='call_handle_tm_bin', data=df, hue='PSO_Vendor')
plt.title('Distribution of Call Handle Times across PSO Vendors')
plt.xlabel('Call Handle Time Bins')
plt.ylabel('Frequency')
plt.show()

# Split of call handle times by call center and intent
plt.figure(figsize=(14, 7))
sns.countplot(x='call_handle_tm_bin', data=df, hue='category_intent')
plt.title('Distribution of Call Handle Times by Intent')
plt.xlabel('Call Handle Time Bins')
plt.ylabel('Frequency')
plt.show()
