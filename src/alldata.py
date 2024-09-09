import requests
import csv


def fetch_json_data(url):
    response = requests.get(url)
    return response.json()


def combine_meta_and_stats(meta, stats):
    combined_data = []
    for system in meta:
        if str(system['id']) in stats:
            system['stats'] = stats[str(system['id'])]
            combined_data.append(system)
    return combined_data


def sort_systems_by_cop(systems):
    return sorted(systems, key=lambda x: x['stats']['combined_cop'] if x['stats']['combined_cop']
                                                                       is not None else float('-inf'), reverse=True)


def sort_systems_by_id(systems):
    return sorted(systems, key=lambda x: x['id'])


def prepare_table_data(systems, headers, limited=True):
    table = []
    for system in systems:
        if system['stats']['combined_cop'] is not None:
            row = [
                system['id'], system['location'], f"{system['hp_output']} kW", system['hp_model'],
                "%.2f" % system['stats']['combined_cop'] if system['stats']['combined_cop']
                                                            is not None else "N/A",
                "%.1f" % system['stats']['running_flowT_mean'] if system['stats'][
                                                                      'running_flowT_mean']
                                                                  is not None else "N/A",
                "%.1f" % system['stats']['running_outsideT_mean'] if system['stats'][
                                                                         'running_outsideT_mean']
                                                                     is not None else "N/A",
                "%.0f" % (system['stats']['combined_data_length'] / 86400) if system['stats'][
                                                                                  'combined_data_length']
                                                                              is not None else "N/A"
            ]

            if not limited:
                for field in headers[8:]:
                    value = system['stats'].get(field, system.get(field, "N/A"))
                    row.append(value if value is not None else "N/A")

            table.append(row)
    return table


def save_to_csv(filename, headers, table):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(table)
    return f"Data has been written to {filename}"


def fetch_heatpump_data():
    # Define URLs
    url_meta = "https://heatpumpmonitor.org/system/list/public.json"
    url_stats = "https://heatpumpmonitor.org/system/stats/last365"

    meta = fetch_json_data(url_meta)
    stats = fetch_json_data(url_stats)

    systems = combine_meta_and_stats(meta, stats)

    sorted_by_cop = sort_systems_by_cop(systems)

    sorted_by_id = sort_systems_by_id(systems)

    headers_limited = ["ID", "Location", "Output", "Model", "COP", "FlowT", "OutsideT", "Days"]
    headers_detailed = headers_limited + [
        "installer_name", "installer_url", "installer_logo", "heatgeek", "ultimaterenewables", "heatingacademy",
        "betateach", "youtube", "url", "share", "hp_type", "refrigerant", "dhw_method", "cylinder_volume",
        "dhw_coil_hex_area",
        "new_radiators", "old_radiators", "fan_coil_radiators", "UFH", "hydraulic_separation",
        "flow_temp", "design_temp", "flow_temp_typical", "wc_curve", "freeze", "zone_number", "space_heat_control_type",
        "dhw_control_type", "dhw_target_temperature", "legionella_frequency", "legionella_target_temperature",
        "property", "floor_area", "heat_demand", "water_heat_demand", "EPC_spaceheat_demand", "EPC_waterheat_demand",
        "heat_loss", "age", "insulation", "kwh_m2",
        "electricity_tariff", "electricity_tariff_type", "electricity_tariff_unit_rate_all",
        "solar_pv_generation", "solar_pv_self_consumption", "solar_pv_divert", "battery_storage_capacity",
        "mid_metering", "electric_meter", "heat_meter", "metering_inc_boost",
        "metering_inc_central_heating_pumps", "metering_inc_brine_pumps", "metering_inc_controls", "indoor_temperature",
        "notes",
        "timestamp", "combined_elec_kwh", "combined_heat_kwh", "combined_cop", "combined_data_length",
        "combined_elec_mean", "combined_heat_mean", "combined_flowT_mean", "combined_returnT_mean",
        "combined_outsideT_mean", "combined_roomT_mean", "combined_prc_carnot", "combined_cooling_kwh",
        "running_elec_kwh", "running_heat_kwh", "running_cop", "running_data_length", "running_elec_mean",
        "running_heat_mean", "running_flowT_mean", "running_returnT_mean", "running_outsideT_mean",
        "running_roomT_mean", "running_prc_carnot",
        "space_elec_kwh", "space_heat_kwh", "space_cop", "space_data_length", "space_elec_mean",
        "space_heat_mean", "space_flowT_mean", "space_returnT_mean", "space_outsideT_mean", "space_roomT_mean",
        "space_prc_carnot", "water_elec_kwh", "water_heat_kwh", "water_cop", "water_data_length", "water_elec_mean",
        "water_heat_mean", "water_flowT_mean", "water_returnT_mean", "water_outsideT_mean", "water_roomT_mean",
        "water_prc_carnot", "from_energy_feeds_elec_kwh", "from_energy_feeds_heat_kwh", "from_energy_feeds_cop",
        "quality_elec", "quality_heat", "quality_flowT", "quality_returnT", "quality_outsideT", "quality_roomT"
    ]

    table_sorted_by_cop_limited = prepare_table_data(sorted_by_cop, headers_limited, limited=True)
    table_sorted_by_id_limited = prepare_table_data(sorted_by_id, headers_limited, limited=True)
    table_sorted_by_cop_detailed = prepare_table_data(sorted_by_cop, headers_detailed, limited=False)
    table_sorted_by_id_detailed = prepare_table_data(sorted_by_id, headers_detailed, limited=False)

    cop_limited_result = save_to_csv("limited_data_sorted_by_cop.csv", headers_limited, table_sorted_by_cop_limited)
    id_limited_result = save_to_csv("limited_data_sorted_by_id.csv", headers_limited, table_sorted_by_id_limited)
    cop_detailed_result = save_to_csv("all_data_sorted_by_cop.csv", headers_detailed, table_sorted_by_cop_detailed)
    id_detailed_result = save_to_csv("all_data_sorted_by_id.csv", headers_detailed, table_sorted_by_id_detailed)

    return {
        "cop_limited_result": cop_limited_result,
        "id_limited_result": id_limited_result,
        "cop_detailed_result": cop_detailed_result,
        "id_detailed_result": id_detailed_result
    }


result = fetch_heatpump_data()

cop_limited_msg = result['cop_limited_result']
id_limited_msg = result['id_limited_result']
cop_detailed_msg = result['cop_detailed_result']
id_detailed_msg = result['id_detailed_result']
