import requests
import csv
from collections import defaultdict
from tabulate import tabulate


INDEX_COP = 4
INDEX_HEAT_DEMAND_PER_FLOOR_AREA = 10


def fetch_url_data(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def calculate_heat_demand_per_floor_area(heat_demand, floor_area):
    try:
        if float(floor_area) > 0:
            return "{:.2f}".format(float(heat_demand) / float(floor_area))
    except (ValueError, TypeError):
        pass
    return "N/A"


def prepare_system_data(systems, stats):
    table = []
    for system in systems:
        system_stats = stats.get(str(system['id']), {})
        cop = "{:.2f}".format(float(system_stats.get('combined_cop', "N/A"))) \
            if system_stats.get('combined_cop') is not None else "N/A"
        flowT = "{:.1f}".format(float(system_stats.get('running_flowT_mean', "N/A"))) \
            if system_stats.get('running_flowT_mean') is not None else "N/A"
        outsideT = "{:.1f}".format(float(system_stats.get('running_outsideT_mean', "N/A"))) \
            if system_stats.get('running_outsideT_mean') is not None else "N/A"
        days = "{:.0f}".format(float(system_stats.get('combined_data_length', 0)) / 86400) \
            if system_stats.get('combined_data_length') is not None else "N/A"
        heat_demand = system.get('heat_demand', "N/A")
        floor_area = system.get('floor_area', "N/A")
        heat_demand_per_floor_area = calculate_heat_demand_per_floor_area(heat_demand, floor_area)
        table.append([system['id'], system['location'], f"{system['hp_output']} kW", system['hp_model'], cop,
                      flowT, outsideT, days, heat_demand, floor_area, heat_demand_per_floor_area])
    return table


def save_data_to_csv(file_name, headers, data, sort_by_index):
    data.sort(key=lambda x: (float(x[sort_by_index]) if x[sort_by_index] != "N/A" else float('-inf')), reverse=True)
    with open(file_name, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(data)
    return f"Data has been saved to {file_name}"


def filter_and_save_data(input_csv, output_csv, ids_to_remove):
    filtered_data = []
    with open(input_csv, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            heat_demand_per_floor_area = row['Heat Demand/Floor Area']
            cop = row['COP']
            flowT = row['FlowT']
            if (
                row['ID'] not in ids_to_remove and
                heat_demand_per_floor_area not in ("N/A") and
                cop not in ("N/A") and
                flowT not in ("N/A") and
                float(heat_demand_per_floor_area) != 0 and
                float(cop) > 0 and
                float(flowT) > 0
            ):
                filtered_data.append(row)

    with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(filtered_data)

    return f"Filtered data has been saved to {output_csv}"

def group_systems_by_heat_demand(systems):
    grouped_systems = defaultdict(list)

    for system in systems:
        try:
            hd_per_fa = float(system["Heat Demand/Floor Area"])
            if hd_per_fa < 50:
                group = "<50 kWh/m²"
                grouped_systems[group].append(system)
            elif 50 <= hd_per_fa < 100:
                group = "50-100 kWh/m²"
                grouped_systems[group].append(system)
            elif 100 <= hd_per_fa < 200:
                group = "100-200 kWh/m²"
                grouped_systems[group].append(system)
            else:
                group = ">200 kWh/m²"
                grouped_systems[group].append(system)
        except ValueError:
            continue

    return grouped_systems

def format_grouped_systems(grouped_systems, headers):
    tables = []
    sorted_groups = ["<50 kWh/m²", "50-100 kWh/m²", "100-200 kWh/m²", ">200 kWh/m²"]

    for group in sorted_groups:
        items = grouped_systems[group]
        items.sort(key=lambda x: float(x["Heat Demand/Floor Area"]))
        table = [[item[h] for h in headers] for item in items]
        tables.append((group, table, len(table)))

    results = []
    for group, table, count in tables:
        results.append((f"Group: {group} (Count: {count})", tabulate(table, headers=headers, tablefmt="psql")))

    return results

def save_grouped_data_to_csv(grouped_systems, headers):
    filenames = {
        ">200 kWh/m²": "more_than_200_group.csv",
        "100-200 kWh/m²": "bet_100_200_group.csv",
        "50-100 kWh/m²": "bet_50_100_group.csv",
        "<50 kWh/m²": "less_than_50_group.csv"
    }

    for group, filename in filenames.items():
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            for row in grouped_systems.get(group, []):
                writer.writerow([row[h] for h in headers])

    return f"Grouped data has been saved to separate CSV files."

def main():
    url_meta = "https://heatpumpmonitor.org/system/list/public.json"
    url_stats = "https://heatpumpmonitor.org/system/stats/last365"
    meta = fetch_url_data(url_meta)
    stats = fetch_url_data(url_stats)

    headers = ["ID", "Location", "Output", "Model", "COP", "FlowT", "OutsideT", "Days", "Heat Demand", "Floor Area",
               "Heat Demand/Floor Area"]
    data = prepare_system_data(meta, stats)

    csv_cop = "data_sorted_by_cop.csv"
    cop_save_result = save_data_to_csv(csv_cop, headers, list(data), INDEX_COP)

    csv_heat_demand = "data_sorted_by_heat_demand_per_floor_area.csv"
    heat_demand_save_result = save_data_to_csv(csv_heat_demand, headers, list(data),
                                               INDEX_HEAT_DEMAND_PER_FLOOR_AREA)

    ids_to_remove = {'12', '17', '21', '36', '49', '52', '67', '105', '117', '148', '163', '169', '224', '276', '301',
                     '305', '311', '325', '333'}
    output_csv = 'classify_clean.csv'
    filter_save_result = filter_and_save_data(csv_heat_demand, output_csv, ids_to_remove)

    systems = []
    with open(output_csv, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            systems.append(row)

    grouped_systems = group_systems_by_heat_demand(systems)

    grouped_results = format_grouped_systems(grouped_systems, headers)

    grouped_save_result = save_grouped_data_to_csv(grouped_systems, headers)

    return {
        "cop_save_result": cop_save_result,
        "heat_demand_save_result": heat_demand_save_result,
        "filter_save_result": filter_save_result,
        "grouped_results": grouped_results,
        "grouped_save_result": grouped_save_result,
    }


if __name__ == "__main__":
    results = main()
