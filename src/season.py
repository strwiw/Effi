import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

os.makedirs('plot', exist_ok=True)

def process_and_plot_scop(file_path, scop_type):
    scop_data = pd.read_csv(file_path)

    scop_data['SCOP (Jun 23 to Aug 23)'] = pd.to_numeric(scop_data['SCOP (Jun 23 to Aug 23)'], errors='coerce')
    scop_data['SCOP (Sep 23 to Nov 23)'] = pd.to_numeric(scop_data['SCOP (Sep 23 to Nov 23)'], errors='coerce')
    scop_data['SCOP (Dec 23 to Feb 24)'] = pd.to_numeric(scop_data['SCOP (Dec 23 to Feb 24)'], errors='coerce')
    scop_data['SCOP (Mar 24 to May 24)'] = pd.to_numeric(scop_data['SCOP (Mar 24 to May 24)'], errors='coerce')

    melted_scop_data = scop_data.melt(
        value_vars=[
            'SCOP (Jun 23 to Aug 23)',
            'SCOP (Sep 23 to Nov 23)',
            'SCOP (Dec 23 to Feb 24)',
            'SCOP (Mar 24 to May 24)'
        ],
        var_name='Season',
        value_name='SCOP'
    )

    season_labels = {
        'SCOP (Jun 23 to Aug 23)': 'Summer\n(Jun 23 to Aug 23)',
        'SCOP (Sep 23 to Nov 23)': 'Autumn\n(Sep 23 to Nov 23)',
        'SCOP (Dec 23 to Feb 24)': 'Winter\n(Dec 23 to Feb 24)',
        'SCOP (Mar 24 to May 24)': 'Spring\n(Mar 24 to May 24)'
    }
    melted_scop_data['Season'] = melted_scop_data['Season'].map(season_labels)

    median_summer = scop_data['SCOP (Jun 23 to Aug 23)'].median()
    median_autumn = scop_data['SCOP (Sep 23 to Nov 23)'].median()
    median_winter = scop_data['SCOP (Dec 23 to Feb 24)'].median()
    median_spring = scop_data['SCOP (Mar 24 to May 24)'].median()

    season_colors = {
        'Summer': '#5BCBCE',
        'Autumn': '#FFCC31',
        'Winter': '#A25430',
        'Spring': '#CA2D8D'
    }

    plt.figure(figsize=(12, 8))

    for i, season in enumerate(season_labels.values()):
        color = season_colors[list(season_colors.keys())[i]]
        sns.violinplot(
            x='Season',
            y='SCOP',
            data=melted_scop_data[melted_scop_data['Season'] == season],
            inner=None,
            color=color,
            linewidth=2
        )

        sns.boxplot(
            x='Season',
            y='SCOP',
            data=melted_scop_data[melted_scop_data['Season'] == season],
            width=0.2,
            boxprops=dict(facecolor='white', edgecolor=color),
            medianprops=dict(color=color, linewidth=2),
            whiskerprops=dict(color='black'),
            capprops=dict(color='black')
        )

    plt.scatter(0, median_summer, color=season_colors['Summer'], s=100, zorder=3)
    plt.scatter(1, median_autumn, color=season_colors['Autumn'], s=100, zorder=3)
    plt.scatter(2, median_winter, color=season_colors['Winter'], s=100, zorder=3)
    plt.scatter(3, median_spring, color=season_colors['Spring'], s=100, zorder=3)

    plt.text(0, median_summer + 0.1, f'{median_summer:.2f}', horizontalalignment='center', fontsize=14, color='black')
    plt.text(1, median_autumn + 0.1, f'{median_autumn:.2f}', horizontalalignment='center', fontsize=14, color='black')
    plt.text(2, median_winter + 0.1, f'{median_winter:.2f}', horizontalalignment='center', fontsize=14, color='black')
    plt.text(3, median_spring + 0.1, f'{median_spring:.2f}', horizontalalignment='center', fontsize=14, color='black')

    count_valid_summer = scop_data['SCOP (Jun 23 to Aug 23)'].dropna().count()
    count_valid_autumn = scop_data['SCOP (Sep 23 to Nov 23)'].dropna().count()
    count_valid_winter = scop_data['SCOP (Dec 23 to Feb 24)'].dropna().count()
    count_valid_spring = scop_data['SCOP (Mar 24 to May 24)'].dropna().count()

    plt.text(0, 7.2, f'Valid counts = {count_valid_summer}', horizontalalignment='center', fontsize=14, color='black')
    plt.text(1, 7.2, f'Valid counts = {count_valid_autumn}', horizontalalignment='center', fontsize=14, color='black')
    plt.text(2, 7.2, f'Valid counts = {count_valid_winter}', horizontalalignment='center', fontsize=14, color='black')
    plt.text(3, 7.2, f'Valid counts = {count_valid_spring}', horizontalalignment='center', fontsize=14, color='black')

    plt.ylabel('SCOP', fontsize=16)
    plt.xlabel('Season', fontsize=16)
    plt.grid(True)
    plt.ylim(0, 7)
    plt.xticks(fontsize=14)

    plt.legend(
        handles=[
            plt.Line2D([0], [0], color=season_colors['Summer'], lw=4, label='Summer'),
            plt.Line2D([0], [0], color=season_colors['Autumn'], lw=4, label='Autumn'),
            plt.Line2D([0], [0], color=season_colors['Winter'], lw=4, label='Winter'),
            plt.Line2D([0], [0], color=season_colors['Spring'], lw=4, label='Spring')
        ],
        loc='upper left',
        fontsize=14
    )

    plt.tight_layout()
    plt.savefig(os.path.join('plot', f'{scop_type}_scop_vs_season.png'))
    plt.show()

process_and_plot_scop('system_scop_clean.csv', 'Combined')
process_and_plot_scop('system_sh_scop_clean.csv', 'Space')
process_and_plot_scop('system_wh_scop_clean.csv', 'Water')