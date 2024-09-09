import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

file_all_data = 'all_data_sorted_by_id.csv'
file_annual_scop = 'annual_system_scop.csv'

WITHOUT_SOLAR_PV_COLOR='#2DAFA7'
WITH_SOLAR_PV_COLOR='#CAA4E8'

df_all_data = pd.read_csv(file_all_data, encoding='latin1')
df_annual_scop = pd.read_csv(file_annual_scop, encoding='latin1')

df_all_data['Solar PV'] = df_all_data['solar_pv_generation'].apply(lambda x: 1 if x > 0 else 0)

df_merged_solar = pd.merge(df_all_data[['ID', 'Solar PV']], df_annual_scop, on='ID', how='inner')

plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
sns.violinplot(x='Solar PV', y='SCOP (Jun 23 to Jun 24)', data=df_merged_solar, hue='Solar PV',
               palette={0: WITHOUT_SOLAR_PV_COLOR, 1: WITH_SOLAR_PV_COLOR}, dodge=False)
plt.xticks([0, 1], ['Without Solar PV', 'With Solar PV'])
plt.title('Violin Plot: SCOP vs Solar PV')
plt.grid(True, linestyle='--')

plt.subplot(1, 2, 2)
sns.boxenplot(x='Solar PV', y='SCOP (Jun 23 to Jun 24)', data=df_merged_solar, hue='Solar PV',
              palette={0: WITHOUT_SOLAR_PV_COLOR, 1: WITH_SOLAR_PV_COLOR}, dodge=False)
plt.xticks([0, 1], ['Without Solar PV', 'With Solar PV'])
plt.title('Boxen Plot: SCOP vs Solar PV')
plt.grid(True, linestyle='--')

plt.tight_layout()
plt.show()
