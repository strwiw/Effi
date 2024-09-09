import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

file1_path = 'annual_system_scop.csv'
file2_path = 'all_data_sorted_by_id.csv'

scop_df = pd.read_csv(file1_path)
all_data_df = pd.read_csv(file2_path, encoding='latin1')

merged_df = pd.merge(all_data_df, scop_df, on='ID')

custom_cmap = sns.color_palette("Spectral_r", as_cmap=True)

label_mapping = {0: 'Without', 1: 'With'}

plt.figure(figsize=(18, 5))

plt.subplot(1, 3, 1)
heatmap_data1 = merged_df.pivot_table(values='SCOP (Jun 23 to Jun 24)',
                                      index='heatgeek',
                                      columns='ultimaterenewables',
                                      aggfunc='mean')
heatmap_data1.index = heatmap_data1.index.map(label_mapping)
heatmap_data1.columns = heatmap_data1.columns.map(label_mapping)
sns.heatmap(heatmap_data1, annot=True, cmap=custom_cmap, fmt=".2f", linewidths=.5)
plt.title('SCOP Comparison: Heat Geek vs Ultimate Renewables')
plt.xlabel('Ultimate Renewables')
plt.ylabel('Heat Geek')

plt.subplot(1, 3, 2)
heatmap_data2 = merged_df.pivot_table(values='SCOP (Jun 23 to Jun 24)',
                                      index='heatgeek',
                                      columns='heatingacademy',
                                      aggfunc='mean')

heatmap_data2.index = heatmap_data2.index.map(label_mapping)
heatmap_data2.columns = heatmap_data2.columns.map(label_mapping)
sns.heatmap(heatmap_data2, annot=True, cmap=custom_cmap, fmt=".2f", linewidths=.5)
plt.title('SCOP Comparison: Heat Geek vs Heating Academy')
plt.xlabel('Heating Academy')
plt.ylabel('Heat Geek')

plt.subplot(1, 3, 3)
heatmap_data3 = merged_df.pivot_table(values='SCOP (Jun 23 to Jun 24)',
                                      index='ultimaterenewables',
                                      columns='heatingacademy',
                                      aggfunc='mean')

heatmap_data3.index = heatmap_data3.index.map(label_mapping)
heatmap_data3.columns = heatmap_data3.columns.map(label_mapping)
sns.heatmap(heatmap_data3, annot=True, cmap=custom_cmap, fmt=".2f", linewidths=.5)
plt.title('SCOP Comparison: Ultimate Renewables vs Heating Academy')
plt.xlabel('Heating Academy')
plt.ylabel('Ultimate Renewables')

plt.tight_layout()

plt.show()