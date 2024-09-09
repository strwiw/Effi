import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from sklearn.model_selection import train_test_split
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

COP_MIN = 0
COP_MIN_CLEANSE = 0.5
COP_MAX = 6
FLOW_TEMP_MAX = 55
FLOW_TEMP_MIN = 15
POINT_SIZE = 50
ALPHA = 0.6
COP_LOWER_THRESHOLD = 0
COP_UPPER_THRESHOLD = COP_MAX
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
        (system_data['combined_cop'] > COP_MAX) |
        (system_data['combined_cop'] <= COP_LOWER_THRESHOLD) |
        (system_data['space_cop'] > COP_MAX) |
        (system_data['water_cop'] > COP_MAX)
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
        (all_filtered_data['combined_cop'] > COP_MIN_CLEANSE) &
        (all_filtered_data['space_cop'] > COP_MIN) &
        (all_filtered_data['water_cop'] > COP_MIN) &
        (all_filtered_data['combined_flowT_mean'] <= FLOW_TEMP_MAX) &
        (all_filtered_data['space_flowT_mean'] <= FLOW_TEMP_MAX) &
        (all_filtered_data['water_flowT_mean'] <= FLOW_TEMP_MAX) &
        (all_filtered_data['combined_flowT_mean'] >= FLOW_TEMP_MIN) &
        (all_filtered_data['space_flowT_mean'] >= FLOW_TEMP_MIN) &
        (all_filtered_data['water_flowT_mean'] >= FLOW_TEMP_MIN)
        ]

    return filtered_data


def create_grid_and_contour(x, y, z, x_min, x_max, y_min, y_max):
    grid_x, grid_y = np.mgrid[x_min:x_max:GRID_DENSITY * 1j, y_min:y_max:GRID_DENSITY * 1j]
    points = np.column_stack((x, y))

    try:
        grid_z = griddata(points, z, (grid_x, grid_y), method='cubic')
    except Exception as e:
        logging.warning(f"Cubic interpolation failed: {e}. Back to linear interpolation.")
        try:
            grid_z = griddata(points, z, (grid_x, grid_y), method='linear')
        except Exception as e:
            logging.error(f"Linear interpolation failed: {e}. Unable to create contour plot.")
            return None, None, None

    return grid_x, grid_y, grid_z


def calculate_r_squared_train_test(x, y, test_size=0.2):
    try:
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=test_size, random_state=42)

        coeffs_train = np.polyfit(x_train, y_train, 1)
        p_train = np.poly1d(coeffs_train)

        y_pred_train = p_train(x_train)
        y_pred_test = p_train(x_test)

        ss_res_train = np.sum((y_train - y_pred_train) ** 2)
        ss_tot_train = np.sum((y_train - np.mean(y_train)) ** 2)
        r_squared_train = 1 - (ss_res_train / ss_tot_train)

        ss_res_test = np.sum((y_test - y_pred_test) ** 2)
        ss_tot_test = np.sum((y_test - np.mean(y_test)) ** 2)
        r_squared_test = 1 - (ss_res_test / ss_tot_test)

        return r_squared_train, r_squared_test, p_train
    except Exception as e:
        logging.error(f"Error in calculating R-squared: {e}")
        return None, None, None


def plot_scatter(x, y, group_name, x_label, y_label):
    plt.scatter(
        x, y,
        alpha=ALPHA,
        edgecolors='k',
        facecolor=GROUP_COLORS[group_name],
        label=GROUP_LABELS[group_name],
        s=POINT_SIZE,
        marker="o"
    )
    plt.xlabel(x_label, fontsize=FONT_SIZE_MEDIUM)
    plt.ylabel(y_label, fontsize=FONT_SIZE_MEDIUM)
    plt.grid(True)

    # Calculate R^2 for train and test sets
    r_squared_train, r_squared_test, p_train = calculate_r_squared_train_test(x, y)
    if r_squared_train is not None and r_squared_test is not None:
        plt.plot(x, p_train(x), color='blue', linewidth=2)
        plt.text(0.05, 0.9, f'$R^2$ (Train) = {r_squared_train:.2f}\n$R^2$ (Test) = {r_squared_test:.2f}',
                 fontsize=FONT_SIZE_LARGE, transform=plt.gca().transAxes, verticalalignment='top')

    plt.legend(loc='upper left')


def plot_contour(grid_x, grid_y, grid_z, x_label, y_label):
    if grid_z is not None:
        contour = plt.contourf(grid_x, grid_y, grid_z, levels=CONTOUR_LEVELS, cmap="RdYlBu", alpha=0.75)
        plt.colorbar(contour)
    plt.xlabel(x_label, fontsize=FONT_SIZE_MEDIUM)
    plt.ylabel(y_label, fontsize=FONT_SIZE_MEDIUM)
    plt.grid(True)


def plot_data(group_name, filtered_data, period, x, y, x_label, y_label, title_prefix, side_by_side=True):
    if not filtered_data.empty:
        x_min, x_max = x.min(), x.max()
        y_min, y_max = max(y.min(), COP_MIN), y.max()

        if side_by_side:
            plt.figure(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))
            plt.subplot(1, 2, 1)
            plot_scatter(x, y, group_name, x_label, y_label)

            plt.subplot(1, 2, 2)
            grid_x, grid_y, grid_z = create_grid_and_contour(x, y, y, x_min, x_max, y_min, y_max)
            plot_contour(grid_x, grid_y, grid_z, x_label, y_label)

            plt.suptitle(f'{title_prefix} - {GROUP_LABELS[group_name]} ({period})', fontsize=FONT_SIZE_EXTRA_LARGE,
                         y=0.97, ha='center')
            plt.subplots_adjust(top=0.85, wspace=0.3)
        else:
            plt.figure(figsize=(COMBINED_FIGURE_WIDTH, COMBINED_FIGURE_HEIGHT))
            plot_scatter(x, y, group_name, x_label, y_label)
            grid_x, grid_y, grid_z = create_grid_and_contour(x, y, y, x_min, x_max, y_min, y_max)
            plot_contour(grid_x, grid_y, grid_z, x_label, y_label)
            plt.title(f'{title_prefix} - {GROUP_LABELS[group_name]} ({period})',
                      fontsize=FONT_SIZE_LARGE)

        plt.tight_layout()
        plt.show()


plot_configs = [
    {
        'x_col': 'combined_flowT_mean',
        'y_col': 'combined_cop',
        'x_label': 'Flow Temperature (°C)',
        'y_label': 'COP',
        'title_prefix': 'COP vs Flow Temperature'
    },
    {
        'x_col': 'combined_outsideT_mean',
        'y_col': 'combined_cop',
        'x_label': 'Outside Temperature (°C)',
        'y_label': 'COP',
        'title_prefix': 'COP vs Outside Temperature'
    },
    {
        'x_col': 'space_flowT_mean',
        'y_col': 'space_cop',
        'x_label': 'Flow Temperature (°C)',
        'y_label': 'Space heating COP',
        'title_prefix': 'Space heating COP vs Flow Temperature'
    },
    {
        'x_col': 'water_flowT_mean',
        'y_col': 'water_cop',
        'x_label': 'Flow Temperature (°C)',
        'y_label': 'Water heating COP',
        'title_prefix': 'Water heating COP vs Flow Temperature'
    },
    {
        'x_col': lambda df: df['combined_roomT_mean'] - df['combined_outsideT_mean'],
        'y_col': 'combined_cop',
        'x_label': 'Combined Room-Outside Temperature Difference (°C)',
        'y_label': 'Combined COP',
        'title_prefix': 'Combined COP vs Room-Outside Temp Difference'
    },
    {
        'x_col': lambda df: df['space_roomT_mean'] - df['space_outsideT_mean'],
        'y_col': 'space_cop',
        'x_label': 'Space heating Room-Outside Temperature Difference (°C)',
        'y_label': 'Space heating COP',
        'title_prefix': 'Space heating COP vs Room-Outside Temp Difference'
    },
    {
        'x_col': lambda df: df['water_roomT_mean'] - df['water_outsideT_mean'],
        'y_col': 'water_cop',
        'x_label': 'Water heating Room-Outside Temperature Difference (°C)',
        'y_label': 'Water heating COP',
        'title_prefix': 'Water heating COP vs Room-Outside Temp Difference'
    }
]

data_directory = os.path.join('..', 'system_daily_data')
group_files = {
    'less_than_50_group': 'less_than_50_group.csv',
    'bet_50_100_group': 'bet_50_100_group.csv',
    'bet_100_200_group': 'bet_100_200_group.csv',
    'more_than_200_group': 'more_than_200_group.csv'
}

for group_name, group_file in group_files.items():
    for period, file_type in [(ANNUAL_PERIOD, 'clean'), (WINTER_PERIOD, 'winter')]:
        filtered_data = process_group(group_file, data_directory, file_type)

        for config in plot_configs:
            x_col = config['x_col'](filtered_data) if callable(config['x_col']) else filtered_data[config['x_col']]
            y_col = filtered_data[config['y_col']]

            logging.info(
                f"Plotting {period} Data (scatter and contour side by side) for {GROUP_LABELS[group_name]} "
                f"({config['title_prefix']})...")
            plot_data(group_name, filtered_data, period, x_col, y_col, config['x_label'], config['y_label'],
                      config['title_prefix'], side_by_side=True)

            logging.info(
                f"Plotting {period} Data (scatter and contour combined) for {GROUP_LABELS[group_name]} "
                f"({config['title_prefix']})...")
            plot_data(group_name, filtered_data, period, x_col, y_col, config['x_label'], config['y_label'],
                      config['title_prefix'], side_by_side=False)

        time.sleep(60)
