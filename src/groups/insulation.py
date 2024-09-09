import os
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def load_csv(filename: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(filename, encoding='ISO-8859-1')
        if df.empty:
            raise pd.errors.EmptyDataError(f"The file {filename} is empty.")
        return df
    except FileNotFoundError:
        raise FileNotFoundError(f"The file {filename} does not exist.")


def process_group(group_df: pd.DataFrame, all_data_df: pd.DataFrame, scop_df: pd.DataFrame,
                  group_name: str) -> pd.DataFrame:
    group_ids = set(group_df['ID'])
    insulation_data = all_data_df[all_data_df['ID'].isin(group_ids)][['ID', 'insulation']]
    scop_data = scop_df[scop_df['ID'].isin(group_ids)][['ID', 'SCOP (Jun 23 to Jun 24)']].rename(
        columns={'SCOP (Jun 23 to Jun 24)': 'SCOP'})

    merged_data = pd.merge(insulation_data, scop_data, on='ID', how='inner')
    merged_data['Group'] = group_name

    return merged_data


def create_color_palette(unique_insulation_types: List[str]) -> Dict[str, Tuple[float, float, float]]:
    color_palette = sns.color_palette("husl", len(unique_insulation_types))
    return dict(zip(unique_insulation_types, color_palette))


def plot_scatterplot(data: pd.DataFrame, ax: plt.Axes, title: str, palette: Dict[str, Tuple[float, float, float]],
                     insulation_order: List[str]) -> None:
    data['insulation'] = pd.Categorical(data['insulation'], categories=insulation_order, ordered=True)

    sns.scatterplot(x='insulation', y='SCOP', hue='insulation', data=data, ax=ax, palette=palette, legend=False)
    ax.set_title(title)
    ax.set_xlabel('Insulation')
    ax.set_ylabel('SCOP')
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, linestyle='--', alpha=0.7)


def plot_boxplot(group_data: Dict[str, pd.DataFrame], palette: Dict[str, Tuple[float, float, float]],
                 insulation_order: List[str]) -> None:
    fig, axs = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle("SCOP by Insulation Type for Each Load Group", fontsize=16)

    titles = ['Minimal load (Jun 23 to Jun 24)', 'Moderate load (Jun 23 to Jun 24)',
              'High load (Jun 23 to Jun 24)', 'Excessive load (Jun 23 to Jun 24)']

    for (group_name, data), ax, title in zip(group_data.items(), axs.flatten(), titles):
        data['insulation'] = pd.Categorical(data['insulation'], categories=insulation_order, ordered=True)

        sns.boxplot(x='insulation', y='SCOP', data=data, hue='insulation', palette=palette, ax=ax, order=insulation_order, dodge=False)
        ax.set_title(title)
        ax.set_xlabel('Insulation')
        ax.set_ylabel('SCOP')
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.show()


def load_and_process_data(base_dir: str) -> Tuple[Dict[str, pd.DataFrame], pd.DataFrame]:
    all_data_df = load_csv(os.path.join(base_dir, '..', 'all_data_sorted_by_id.csv'))
    scop_df = load_csv(os.path.join(base_dir, '..', 'annual_system_scop.csv'))
    group_files = {
        'Less than 50': 'less_than_50_group.csv',
        'Between 50 and 100': 'bet_50_100_group.csv',
        'Between 100 and 200': 'bet_100_200_group.csv',
        'More than 200': 'more_than_200_group.csv'
    }

    group_data = {}
    for group_name, filename in group_files.items():
        group_df = load_csv(os.path.join(base_dir, filename))
        group_data[group_name] = process_group(group_df, all_data_df, scop_df, group_name)

    combined_data = pd.concat(group_data.values())
    return group_data, combined_data


def create_scatter_plots(group_data: Dict[str, pd.DataFrame], palette_dict: Dict[str, Tuple[float, float, float]],
                         insulation_order: List[str]) -> None:
    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    titles = ['Minimal load (Jun 23 to Jun 24)', 'Moderate load (Jun 23 to Jun 24)',
              'High load (Jun 23 to Jun 24)', 'Excessive load (Jun 23 to Jun 24)']

    for (group_name, data), ax, title in zip(group_data.items(), axs.flatten(), titles):
        plot_scatterplot(data, ax, title, palette_dict, insulation_order)

    handles = [plt.Line2D([0], [0], marker='o', color=color, linestyle='', label=insulation)
               for insulation, color in palette_dict.items()]
    plt.legend(handles=handles, title='Insulation Types', bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout(rect=[0, 0, 1, 1])
    plt.show()


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    group_data, combined_data = load_and_process_data(base_dir)

    unique_insulation_types = combined_data['insulation'].unique()
    insulation_order = sorted(unique_insulation_types)
    palette_dict = create_color_palette(insulation_order)

    create_scatter_plots(group_data, palette_dict, insulation_order)
    plot_boxplot(group_data, palette_dict, insulation_order)


if __name__ == "__main__":
    main()