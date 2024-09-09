import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

all_data_file_path = 'all_data_sorted_by_id.csv'
sh_scop_file_path = 'annual_system_sh_scop.csv'

all_data_df = pd.read_csv(all_data_file_path, encoding='latin1')
sh_scop_df = pd.read_csv(sh_scop_file_path)

merged_df = pd.merge(sh_scop_df, all_data_df[['ID', 'space_heat_control_type']], on='ID', how='left')

plt.figure(figsize=(12, 8))
sns.boxplot(data=merged_df, x='space_heat_control_type', y='SCOP (Jun 23 to Jun 24)',
            hue='space_heat_control_type', palette='Set2', dodge=False)

plt.xticks(rotation=45, ha='right')
plt.grid(True, linestyle='--', alpha=0.7)
plt.title('Space Heat Control Type vs SCOP', fontsize=14)
plt.xlabel('Space Heat Control Type', fontsize=12)
plt.ylabel('SCOP (Jun 23 to Jun 24)', fontsize=12)
plt.legend([],[], frameon=False)

plt.tight_layout()
plt.show()
