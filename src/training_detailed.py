import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

file1_path = 'annual_system_scop.csv'
file2_path = 'all_data_sorted_by_id.csv'

scop_df = pd.read_csv(file1_path)
all_data_df = pd.read_csv(file2_path, encoding='latin1')

merged_df = pd.merge(all_data_df, scop_df, on='ID')

plt.figure(figsize=(18, 8))

custom_palette = ['#FC9676', '#53ABDA', '#A2BD2C', '#FFCC31', '#8080D7', '#CA2D8D']

plt.subplot(1, 3, 1)
sns.violinplot(x='heatgeek', y='SCOP (Jun 23 to Jun 24)', data=merged_df, hue='heatgeek',
               palette=[custom_palette[0], custom_palette[1]], inner=None)
sns.boxplot(x='heatgeek', y='SCOP (Jun 23 to Jun 24)', data=merged_df, hue='heatgeek',
            palette=[custom_palette[0], custom_palette[1]], width=0.2, showfliers=False)

medians_heatgeek = merged_df.groupby('heatgeek')['SCOP (Jun 23 to Jun 24)'].median().values
for i, median in enumerate(medians_heatgeek):
    plt.text(i, median + 0.05, f'{median:.2f}', ha='center', color='black')

plt.title('SCOP Comparison by Heat Geek')
plt.xlabel('Heat Geek')
plt.ylabel('SCOP (Jun 23 to Jun 24)')
plt.xticks([0, 1], ['Without', 'With'])
plt.grid(True, linestyle='--')
plt.legend(title="Heat Geek", labels=['Without', 'With'], loc='upper right')

plt.subplot(1, 3, 2)
sns.violinplot(x='ultimaterenewables', y='SCOP (Jun 23 to Jun 24)', data=merged_df, hue='ultimaterenewables',
               palette=[custom_palette[2], custom_palette[3]], inner=None)
sns.boxplot(x='ultimaterenewables', y='SCOP (Jun 23 to Jun 24)', data=merged_df, hue='ultimaterenewables',
            palette=[custom_palette[2], custom_palette[3]], width=0.2, showfliers=False)

medians_ultimate = merged_df.groupby('ultimaterenewables')['SCOP (Jun 23 to Jun 24)'].median().values
for i, median in enumerate(medians_ultimate):
    plt.text(i, median + 0.05, f'{median:.2f}', ha='center', color='black')

plt.title('SCOP Comparison by Ultimate Renewables')
plt.xlabel('Ultimate Renewables')
plt.ylabel('SCOP (Jun 23 to Jun 24)')
plt.xticks([0, 1], ['Without', 'With'])
plt.grid(True, linestyle='--')
plt.legend(title="Ultimate Renewables", labels=['Without', 'With'], loc='upper right')

plt.subplot(1, 3, 3)
sns.violinplot(x='heatingacademy', y='SCOP (Jun 23 to Jun 24)', data=merged_df, hue='heatingacademy',
               palette=[custom_palette[4], custom_palette[5]], inner=None)
sns.boxplot(x='heatingacademy', y='SCOP (Jun 23 to Jun 24)', data=merged_df, hue='heatingacademy',
            palette=[custom_palette[4], custom_palette[5]], width=0.2, showfliers=False)

medians_heating = merged_df.groupby('heatingacademy')['SCOP (Jun 23 to Jun 24)'].median().values
for i, median in enumerate(medians_heating):
    plt.text(i, median + 0.05, f'{median:.2f}', ha='center', color='black')

plt.title('SCOP Comparison by Heating Academy')
plt.xlabel('Heating Academy')
plt.ylabel('SCOP (Jun 23 to Jun 24)')
plt.xticks([0, 1], ['Without', 'With'])
plt.grid(True, linestyle='--')
plt.legend(title="Heating Academy", labels=['Without', 'With'], loc='upper right')

plt.tight_layout()

plt.show()
