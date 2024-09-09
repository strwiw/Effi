import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Patch

file_all_data = 'all_data_sorted_by_id.csv'
file_annual_scop = 'annual_system_scop.csv'

df_all_data = pd.read_csv(file_all_data, encoding='latin1')
df_annual_scop = pd.read_csv(file_annual_scop, encoding='latin1')

df_merged = pd.merge(df_all_data[['ID', 'UFH']], df_annual_scop, on='ID', how='inner')

plt.figure(figsize=(8, 6))

colors = sns.color_palette("Set2")

sns.violinplot(x='UFH', y='SCOP (Jun 23 to Jun 24)', data=df_merged, inner=None,
               hue='UFH', palette={0: colors[0], 1: colors[1]}, legend=False)

sns.boxplot(x='UFH', y='SCOP (Jun 23 to Jun 24)', data=df_merged, whis=1.5, width=0.3,
            hue='UFH', palette={0: colors[0], 1: colors[1]}, linewidth=1.5, dodge=False, legend=False)

plt.xticks([0, 1], ['Without', 'With'], fontsize=14)

# plt.title('SCOP vs Underfloor Heating')
plt.xlabel('Underfloor Heating', fontsize=14)
plt.ylabel('SCOP (Jun 23 to Jun 24)', fontsize=14)

plt.grid(True, linestyle='--')

medians = df_merged.groupby('UFH')['SCOP (Jun 23 to Jun 24)'].median()

for i in range(len(medians)):
    plt.text(i, medians[i] + 0.02, f'{medians[i]:.2f}', horizontalalignment='center',
             color='black')

legend_labels = [Patch(facecolor=colors[0], edgecolor=colors[0], label='Without UFH'),
                 Patch(facecolor=colors[1], edgecolor=colors[1], label='With UFH')]

plt.legend(handles=legend_labels)

plt.show()
