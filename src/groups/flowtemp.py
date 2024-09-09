import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

COP_MIN = 0
COP_MAX = 8
COP_MIN_CLEANSE = 0.5
FLOW_TEMP_MIN = 0
FLOW_TEMP_MAX = 50
POINT_SIZE = 50
ALPHA = 0.6
COP_LOWER_THRESHOLD = 0
COP_UPPER_THRESHOLD = 8

FIGURE_WIDTH = 16
FIGURE_HEIGHT = 6
COMBINED_FIGURE_WIDTH = 12
COMBINED_FIGURE_HEIGHT = 6
FONT_SIZE_SMALL = 12
FONT_SIZE_MEDIUM = 14
FONT_SIZE_LARGE = 16
FONT_SIZE_EXTRA_LARGE = 18
CONTOUR_LEVELS = 15
GRID_DENSITY = 100
LEGEND_FONT_SIZE = 12
LEGEND_TITLE_FONT_SIZE = 14

ANNUAL_PERIOD = 'Jun 23 to Jun 24'
WINTER_PERIOD = 'Dec 23 to Feb 24'

GROUP_COLORS = {
    'less_than_50_group': '#a25430',
    'bet_50_100_group': '#f599b1',
    'bet_100_200_group': '#ffcc31',
    'more_than_200_group': '#7cbbbf'
}

GROUP_LABELS = {
    'less_than_50_group': 'Minimal Load',
    'bet_50_100_group': 'Moderate Load',
    'bet_100_200_group': 'High Load',
    'more_than_200_group': 'Excessive Load'
}

def is_non_empty(df):
    return not df.empty and df.dropna(how='all').shape[0] > 0

def has_invalid_cop(system_data):
    invalid_cop_data = system_data[
        (system_data['combined_cop'] > COP_UPPER_THRESHOLD) |
        (system_data['combined_cop'] <= COP_LOWER_THRESHOLD)
    ]
    return not invalid_cop_data.empty

def process_group(group_file, data_directory, file_type='clean'):
    group_df = pd.read_csv(group_file)
    ids = group_df['ID'].unique()

    all_filtered_data = pd.DataFrame()

    for system_id in ids:
        filename = f"system_{system_id}_daily_data_{file_type}.csv"
        file_path = os.path.join(data_directory, filename)

        if os.path.exists(file_path):
            system_data = pd.read_csv(file_path)
            system_data.columns = system_data.columns.str.strip()

            if has_invalid_cop(system_data):
                continue

            if is_non_empty(system_data):
                all_filtered_data = pd.concat([all_filtered_data, system_data], ignore_index=True)

    filtered_data = all_filtered_data[
        (all_filtered_data['combined_cop'] > COP_MIN_CLEANSE) & (all_filtered_data['combined_cop'] <= COP_MAX)
    ]

    return filtered_data

def plot_scatter_and_contour_side_by_side(group_name, filtered_data, plot_title_suffix):
    if not filtered_data.empty:
        plt.figure(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))

        plt.subplot(1, 2, 1)
        plt.scatter(
            filtered_data['combined_flowT_mean'],
            filtered_data['combined_cop'],
            alpha=ALPHA,
            edgecolors='k',
            facecolor=GROUP_COLORS[group_name],
            label=GROUP_LABELS[group_name],
            s=POINT_SIZE,
            marker="o"
        )
        plt.xlabel('Flow Temperature (°C)', fontsize=FONT_SIZE_MEDIUM)
        plt.ylabel('COP', fontsize=FONT_SIZE_MEDIUM)
        plt.xlim(FLOW_TEMP_MIN, FLOW_TEMP_MAX)
        plt.ylim(COP_MIN, COP_MAX)
        plt.grid(True)
        plt.legend(loc='upper left')

        plt.subplot(1, 2, 2)
        grid_x, grid_y = np.mgrid[FLOW_TEMP_MIN:FLOW_TEMP_MAX:GRID_DENSITY*1j, COP_MIN:COP_MAX:GRID_DENSITY*1j]
        points = filtered_data[['combined_flowT_mean', 'combined_cop']].values
        values = filtered_data['combined_cop'].values
        grid_z = griddata(points, values, (grid_x, grid_y), method='cubic')

        contour = plt.contourf(grid_x, grid_y, grid_z, levels=CONTOUR_LEVELS, cmap="RdYlBu", alpha=0.75)
        plt.colorbar(contour)
        plt.xlabel('Flow Temperature (°C)', fontsize=FONT_SIZE_MEDIUM)
        plt.ylabel('COP', fontsize=FONT_SIZE_MEDIUM)
        plt.xlim(FLOW_TEMP_MIN, FLOW_TEMP_MAX)
        plt.ylim(COP_MIN, COP_MAX)
        plt.grid(True)

        plt.suptitle(f'{GROUP_LABELS[group_name]} ({plot_title_suffix})', fontsize=FONT_SIZE_EXTRA_LARGE, y=0.95, ha='center')
        plt.subplots_adjust(top=0.85, wspace=0.3)
        plt.show()

def plot_scatter_and_contour_combined(group_name, filtered_data, plot_title_suffix):
    if not filtered_data.empty:
        plt.figure(figsize=(COMBINED_FIGURE_WIDTH, COMBINED_FIGURE_HEIGHT))


        grid_x, grid_y = np.mgrid[FLOW_TEMP_MIN:FLOW_TEMP_MAX:GRID_DENSITY*1j, COP_MIN:COP_MAX:GRID_DENSITY*1j]
        points = filtered_data[['combined_flowT_mean', 'combined_cop']].values
        values = filtered_data['combined_cop'].values
        grid_z = griddata(points, values, (grid_x, grid_y), method='cubic')

        scatter = plt.scatter(
            filtered_data['combined_flowT_mean'],
            filtered_data['combined_cop'],
            alpha=ALPHA,
            edgecolors='k',
            facecolor=GROUP_COLORS[group_name],
            label=GROUP_LABELS[group_name],
            s=POINT_SIZE,
            marker="o"
        )

        contour = plt.contourf(grid_x, grid_y, grid_z, levels=CONTOUR_LEVELS, cmap="RdYlBu", alpha=0.6)
        plt.colorbar(contour)

        plt.title(f'Combined Plot - {GROUP_LABELS[group_name]} ({plot_title_suffix})', fontsize=FONT_SIZE_LARGE)
        plt.xlabel('Flow Temperature (°C)', fontsize=FONT_SIZE_MEDIUM)
        plt.ylabel('COP', fontsize=FONT_SIZE_MEDIUM)
        plt.xlim(FLOW_TEMP_MIN, FLOW_TEMP_MAX)
        plt.ylim(COP_MIN, COP_MAX)
        plt.grid(True)
        plt.legend(loc='upper left')
        plt.tight_layout()
        plt.show()

data_directory = os.path.join('..', 'system_daily_data')
group_files = {
    'less_than_50_group': 'less_than_50_group.csv',
    'bet_50_100_group': 'bet_50_100_group.csv',
    'bet_100_200_group': 'bet_100_200_group.csv',
    'more_than_200_group': 'more_than_200_group.csv'
}

for group_name, group_file in group_files.items():
    filtered_data_clean = process_group(group_file, data_directory, file_type='clean')

    logging.info(f'Plotting Annual Data (scatter and contour side by side) for {GROUP_LABELS[group_name]}...')
    plot_scatter_and_contour_side_by_side(group_name, filtered_data_clean, ANNUAL_PERIOD)

    logging.info(f'Plotting Annual Data (scatter and contour combined) for {GROUP_LABELS[group_name]}...')
    plot_scatter_and_contour_combined(group_name, filtered_data_clean, ANNUAL_PERIOD)

    filtered_data_winter = process_group(group_file, data_directory, file_type='winter')

    logging.info(f'Plotting Winter Data (scatter and contour side by side) for {GROUP_LABELS[group_name]}...')
    plot_scatter_and_contour_side_by_side(group_name, filtered_data_winter, WINTER_PERIOD)

    logging.info(f'Plotting Winter Data (scatter and contour combined) for {GROUP_LABELS[group_name]}...')
    plot_scatter_and_contour_combined(group_name, filtered_data_winter, WINTER_PERIOD)