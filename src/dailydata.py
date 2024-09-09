import requests
import csv
import datetime
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SUMMER_START_DATE = datetime.datetime(2023, 6, 1)
SUMMER_END_DATE = datetime.datetime(2023, 9, 1)

AUTUMN_START_DATE = datetime.datetime(2023, 9, 1)
AUTUMN_END_DATE = datetime.datetime(2023, 12, 1)

WINTER_START_DATE = datetime.datetime(2023, 12, 1)
WINTER_END_DATE = datetime.datetime(2024, 3, 1)

SPRING_START_DATE = datetime.datetime(2024, 3, 1)
SPRING_END_DATE = datetime.datetime(2024, 6, 1)

FULL_YEAR_START_DATE = datetime.datetime(2023, 6, 1)
FULL_YEAR_END_DATE = datetime.datetime(2024, 6, 1)

ORIGINAL_FILE_SUFFIX = "_daily_data_original.csv"
CONVERTED_FILE_SUFFIX = "_daily_data_converted.csv"
CLEAN_FILE_SUFFIX = "_daily_data_clean.csv"
WINTER_FILE_SUFFIX = "_daily_data_winter.csv"
METERING_ERROR_FOLDER = "metering_error"

SYSTEM_IDS_TO_REMOVE = [12, 17, 21, 36, 49, 52, 67, 105, 117, 148, 163, 169, 224, 276, 301, 305, 311, 325, 333]


def convert_timestamp(timestamp):
    try:
        timestamp = float(timestamp)
        dt_object = datetime.datetime.fromtimestamp(timestamp)
        return dt_object.strftime('%Y-%m-%d %H:00:00')
    except ValueError:
        return timestamp


def is_within_date_range(date_str, start_date, end_date):
    date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:00:00')
    return start_date <= date_obj < end_date


def fetch_and_save_daily_data(system_id, output_folder):
    url = f"https://heatpumpmonitor.org/system/stats/daily?id={system_id}"
    response = requests.get(url)
    data = response.text

    lines = data.splitlines()
    reader = csv.reader(lines)

    headers = next(reader)

    original_rows = [headers]
    converted_rows = [headers]
    clean_rows = [headers]
    winter_rows = [headers]

    for row in reader:
        if len(row) > 1:
            converted_row = row.copy()
            converted_row[1] = convert_timestamp(row[1])

            original_rows.append(row)
            converted_rows.append(converted_row)

            if is_within_date_range(converted_row[1], SUMMER_START_DATE, SPRING_END_DATE):
                clean_rows.append(converted_row)

            if is_within_date_range(converted_row[1], WINTER_START_DATE, WINTER_END_DATE):
                winter_rows.append(converted_row)
        else:
            converted_rows.append(row)

    original_output_file = os.path.join(output_folder, f"system_{system_id}{ORIGINAL_FILE_SUFFIX}")
    converted_output_file = os.path.join(output_folder, f"system_{system_id}{CONVERTED_FILE_SUFFIX}")
    clean_output_file = os.path.join(output_folder, f"system_{system_id}{CLEAN_FILE_SUFFIX}")
    winter_output_file = os.path.join(output_folder, f"system_{system_id}{WINTER_FILE_SUFFIX}")

    with open(original_output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(original_rows)

    with open(converted_output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(converted_rows)

    with open(clean_output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(clean_rows)

    with open(winter_output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(winter_rows)

    return original_output_file, converted_output_file, clean_output_file, winter_output_file


def calculate_scop_from_file(file_path, start_date, end_date):
    total_heat_kwh = 0.0
    total_elec_kwh = 0.0
    data_available = False

    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            date = row[' timestamp']
            if is_within_date_range(date, start_date, end_date):
                data_available = True
                total_heat_kwh += float(row[' combined_heat_kwh'])
                total_elec_kwh += float(row[' combined_elec_kwh'])

    if not data_available:
        return "Data not available"

    if total_elec_kwh > 0:
        scop = total_heat_kwh / total_elec_kwh
    else:
        scop = "Data not available"

    return scop


def calculate_sh_scop_from_file(file_path, start_date, end_date):
    total_space_heat_kwh = 0.0
    total_space_elec_kwh = 0.0
    data_available = False

    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            date = row[' timestamp']
            if is_within_date_range(date, start_date, end_date):
                data_available = True
                total_space_heat_kwh += float(row[' space_heat_kwh'])
                total_space_elec_kwh += float(row[' space_elec_kwh'])

    if not data_available:
        return "Data not available"

    if total_space_elec_kwh > 0:
        scop = total_space_heat_kwh / total_space_elec_kwh
    else:
        scop = "Data not available"

    return scop


def calculate_wh_scop_from_file(file_path, start_date, end_date):
    total_water_heat_kwh = 0.0
    total_water_elec_kwh = 0.0
    data_available = False

    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            date = row[' timestamp']
            if is_within_date_range(date, start_date, end_date):
                data_available = True
                total_water_heat_kwh += float(row[' water_heat_kwh'])
                total_water_elec_kwh += float(row[' water_elec_kwh'])

    if not data_available:
        return "Data not available"

    if total_water_elec_kwh > 0:
        scop = total_water_heat_kwh / total_water_elec_kwh
    else:
        scop = "Data not available"

    return scop


def move_files_to_metering_error(output_folder, system_ids_to_remove):
    metering_error_folder = os.path.join(output_folder, METERING_ERROR_FOLDER)
    os.makedirs(metering_error_folder, exist_ok=True)

    moved_files = []
    errors = []

    for system_id in system_ids_to_remove:
        original_file = os.path.join(output_folder, f"system_{system_id}{ORIGINAL_FILE_SUFFIX}")
        converted_file = os.path.join(output_folder, f"system_{system_id}{CONVERTED_FILE_SUFFIX}")
        clean_file = os.path.join(output_folder, f"system_{system_id}{CLEAN_FILE_SUFFIX}")
        winter_file = os.path.join(output_folder, f"system_{system_id}{WINTER_FILE_SUFFIX}")

        try:
            if os.path.exists(original_file):
                os.rename(original_file, os.path.join(metering_error_folder, os.path.basename(original_file)))
                moved_files.append(original_file)
            if os.path.exists(converted_file):
                os.rename(converted_file, os.path.join(metering_error_folder, os.path.basename(converted_file)))
                moved_files.append(converted_file)
            if os.path.exists(clean_file):
                os.rename(clean_file, os.path.join(metering_error_folder, os.path.basename(clean_file)))
                moved_files.append(clean_file)
            if os.path.exists(winter_file):
                os.rename(winter_file, os.path.join(metering_error_folder, os.path.basename(winter_file)))
                moved_files.append(winter_file)
        except Exception as e:
            errors.append(f"Error moving files for system ID {system_id}: {e}")

    return moved_files, errors


def main():
    output_folder = "system_daily_data"
    os.makedirs(output_folder, exist_ok=True)

    url = "https://heatpumpmonitor.org/system/list/public.json"
    response = requests.get(url)
    meta = response.json()

    saved_files = []
    scop_results = []
    annual_scop_results = []
    sh_scop_results = []
    annual_sh_scop_results = []
    wh_scop_results = []
    annual_wh_scop_results = []

    for system in meta:
        system_id = system['id']
        original_file, converted_file, clean_file, winter_file = fetch_and_save_daily_data(system_id, output_folder)
        saved_files.append((system_id, original_file, converted_file, clean_file, winter_file))

        # combined SCOP
        summer_scop = calculate_scop_from_file(clean_file, SUMMER_START_DATE, SUMMER_END_DATE)
        autumn_scop = calculate_scop_from_file(clean_file, AUTUMN_START_DATE, AUTUMN_END_DATE)
        winter_scop = calculate_scop_from_file(clean_file, WINTER_START_DATE, WINTER_END_DATE)
        spring_scop = calculate_scop_from_file(clean_file, SPRING_START_DATE, SPRING_END_DATE)
        full_year_scop = calculate_scop_from_file(clean_file, FULL_YEAR_START_DATE, FULL_YEAR_END_DATE)

        scop_results.append({
            'ID': system_id,
            'SCOP (Jun 23 to Aug 23)': summer_scop,
            'SCOP (Sep 23 to Nov 23)': autumn_scop,
            'SCOP (Dec 23 to Feb 24)': winter_scop,
            'SCOP (Mar 24 to May 24)': spring_scop,
            'SCOP (Jun 23 to Jun 24)': full_year_scop
        })

        if full_year_scop != "Data not available" and float(full_year_scop) > 0:
            annual_scop_results.append({
                'ID': system_id,
                'SCOP (Jun 23 to Jun 24)': full_year_scop
            })

        # Space heating SCOP
        summer_sh_scop = calculate_sh_scop_from_file(clean_file, SUMMER_START_DATE, SUMMER_END_DATE)
        autumn_sh_scop = calculate_sh_scop_from_file(clean_file, AUTUMN_START_DATE, AUTUMN_END_DATE)
        winter_sh_scop = calculate_sh_scop_from_file(clean_file, WINTER_START_DATE, WINTER_END_DATE)
        spring_sh_scop = calculate_sh_scop_from_file(clean_file, SPRING_START_DATE, SPRING_END_DATE)
        full_year_sh_scop = calculate_sh_scop_from_file(clean_file, FULL_YEAR_START_DATE, FULL_YEAR_END_DATE)

        sh_scop_results.append({
            'ID': system_id,
            'SCOP (Jun 23 to Aug 23)': summer_sh_scop,
            'SCOP (Sep 23 to Nov 23)': autumn_sh_scop,
            'SCOP (Dec 23 to Feb 24)': winter_sh_scop,
            'SCOP (Mar 24 to May 24)': spring_sh_scop,
            'SCOP (Jun 23 to Jun 24)': full_year_sh_scop
        })

        if full_year_sh_scop != "Data not available" and float(full_year_sh_scop) > 0:
            annual_sh_scop_results.append({
                'ID': system_id,
                'SCOP (Jun 23 to Jun 24)': full_year_sh_scop
            })

        # Water heating SCOP
        summer_wh_scop = calculate_wh_scop_from_file(clean_file, SUMMER_START_DATE, SUMMER_END_DATE)
        autumn_wh_scop = calculate_wh_scop_from_file(clean_file, AUTUMN_START_DATE, AUTUMN_END_DATE)
        winter_wh_scop = calculate_wh_scop_from_file(clean_file, WINTER_START_DATE, WINTER_END_DATE)
        spring_wh_scop = calculate_wh_scop_from_file(clean_file, SPRING_START_DATE, SPRING_END_DATE)
        full_year_wh_scop = calculate_wh_scop_from_file(clean_file, FULL_YEAR_START_DATE, FULL_YEAR_END_DATE)

        wh_scop_results.append({
            'ID': system_id,
            'SCOP (Jun 23 to Aug 23)': summer_wh_scop,
            'SCOP (Sep 23 to Nov 23)': autumn_wh_scop,
            'SCOP (Dec 23 to Feb 24)': winter_wh_scop,
            'SCOP (Mar 24 to May 24)': spring_wh_scop,
            'SCOP (Jun 23 to Jun 24)': full_year_wh_scop
        })

        if full_year_wh_scop != "Data not available" and float(full_year_wh_scop) > 0:
            annual_wh_scop_results.append({
                'ID': system_id,
                'SCOP (Jun 23 to Jun 24)': full_year_wh_scop
            })

    scop_results = sorted(scop_results, key=lambda x: x['ID'])
    annual_scop_results = sorted(annual_scop_results, key=lambda x: x['ID'])

    scop_output_file = "system_scop_original.csv"
    with open(scop_output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=[
            'ID',
            'SCOP (Jun 23 to Aug 23)',
            'SCOP (Sep 23 to Nov 23)',
            'SCOP (Dec 23 to Feb 24)',
            'SCOP (Mar 24 to May 24)',
            'SCOP (Jun 23 to Jun 24)'
        ])
        writer.writeheader()
        for result in scop_results:
            writer.writerow(result)

    annual_scop_output_file = "annual_system_scop.csv"
    with open(annual_scop_output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['ID', 'SCOP (Jun 23 to Jun 24)'])
        writer.writeheader()
        for result in annual_scop_results:
            writer.writerow(result)

    scop_clean_results = [result for result in scop_results if all(
        (scop == "Data not available" or float(scop) > 0) for scop in [
            result['SCOP (Jun 23 to Aug 23)'],
            result['SCOP (Sep 23 to Nov 23)'],
            result['SCOP (Dec 23 to Feb 24)'],
            result['SCOP (Mar 24 to May 24)'],
            result['SCOP (Jun 23 to Jun 24)']
        ]
    ) and not all(
        scop == "Data not available" for scop in [
            result['SCOP (Jun 23 to Aug 23)'],
            result['SCOP (Sep 23 to Nov 23)'],
            result['SCOP (Dec 23 to Feb 24)'],
            result['SCOP (Mar 24 to May 24)'],
            result['SCOP (Jun 23 to Jun 24)']
        ]
    )]

    clean_scop_output_file = "system_scop_clean.csv"
    with open(clean_scop_output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=[
            'ID',
            'SCOP (Jun 23 to Aug 23)',
            'SCOP (Sep 23 to Nov 23)',
            'SCOP (Dec 23 to Feb 24)',
            'SCOP (Mar 24 to May 24)',
            'SCOP (Jun 23 to Jun 24)'
        ])
        writer.writeheader()
        for result in scop_clean_results:
            writer.writerow(result)

    sh_scop_results = sorted(sh_scop_results, key=lambda x: x['ID'])
    annual_sh_scop_results = sorted(annual_sh_scop_results, key=lambda x: x['ID'])

    sh_scop_output_file = "system_sh_scop_original.csv"
    with open(sh_scop_output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=[
            'ID',
            'SCOP (Jun 23 to Aug 23)',
            'SCOP (Sep 23 to Nov 23)',
            'SCOP (Dec 23 to Feb 24)',
            'SCOP (Mar 24 to May 24)',
            'SCOP (Jun 23 to Jun 24)'
        ])
        writer.writeheader()
        for result in sh_scop_results:
            writer.writerow(result)

    annual_sh_scop_output_file = "annual_system_sh_scop.csv"
    with open(annual_sh_scop_output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['ID', 'SCOP (Jun 23 to Jun 24)'])
        writer.writeheader()
        for result in annual_sh_scop_results:
            writer.writerow(result)

    sh_scop_clean_results = [result for result in sh_scop_results if all(
        (scop == "Data not available" or float(scop) > 0) for scop in [
            result['SCOP (Jun 23 to Aug 23)'],
            result['SCOP (Sep 23 to Nov 23)'],
            result['SCOP (Dec 23 to Feb 24)'],
            result['SCOP (Mar 24 to May 24)'],
            result['SCOP (Jun 23 to Jun 24)']
        ]
    ) and not all(
        scop == "Data not available" for scop in [
            result['SCOP (Jun 23 to Aug 23)'],
            result['SCOP (Sep 23 to Nov 23)'],
            result['SCOP (Dec 23 to Feb 24)'],
            result['SCOP (Mar 24 to May 24)'],
            result['SCOP (Jun 23 to Jun 24)']
        ]
    )]

    clean_sh_scop_output_file = "system_sh_scop_clean.csv"
    with open(clean_sh_scop_output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=[
            'ID',
            'SCOP (Jun 23 to Aug 23)',
            'SCOP (Sep 23 to Nov 23)',
            'SCOP (Dec 23 to Feb 24)',
            'SCOP (Mar 24 to May 24)',
            'SCOP (Jun 23 to Jun 24)'
        ])
        writer.writeheader()
        for result in sh_scop_clean_results:
            writer.writerow(result)

    wh_scop_results = sorted(wh_scop_results, key=lambda x: x['ID'])
    annual_wh_scop_results = sorted(annual_wh_scop_results, key=lambda x: x['ID'])

    wh_scop_output_file = "system_wh_scop_original.csv"
    with open(wh_scop_output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=[
            'ID',
            'SCOP (Jun 23 to Aug 23)',
            'SCOP (Sep 23 to Nov 23)',
            'SCOP (Dec 23 to Feb 24)',
            'SCOP (Mar 24 to May 24)',
            'SCOP (Jun 23 to Jun 24)'
        ])
        writer.writeheader()
        for result in wh_scop_results:
            writer.writerow(result)

    annual_wh_scop_output_file = "annual_system_wh_scop.csv"
    with open(annual_wh_scop_output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['ID', 'SCOP (Jun 23 to Jun 24)'])
        writer.writeheader()
        for result in annual_wh_scop_results:
            writer.writerow(result)

    wh_scop_clean_results = [result for result in wh_scop_results if all(
        (scop == "Data not available" or float(scop) > 0) for scop in [
            result['SCOP (Jun 23 to Aug 23)'],
            result['SCOP (Sep 23 to Nov 23)'],
            result['SCOP (Dec 23 to Feb 24)'],
            result['SCOP (Mar 24 to May 24)'],
            result['SCOP (Jun 23 to Jun 24)']
        ]
    ) and not all(
        scop == "Data not available" for scop in [
            result['SCOP (Jun 23 to Aug 23)'],
            result['SCOP (Sep 23 to Nov 23)'],
            result['SCOP (Dec 23 to Feb 24)'],
            result['SCOP (Mar 24 to May 24)'],
            result['SCOP (Jun 23 to Jun 24)']
        ]
    )]

    clean_wh_scop_output_file = "system_wh_scop_clean.csv"
    with open(clean_wh_scop_output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=[
            'ID',
            'SCOP (Jun 23 to Aug 23)',
            'SCOP (Sep 23 to Nov 23)',
            'SCOP (Dec 23 to Feb 24)',
            'SCOP (Mar 24 to May 24)',
            'SCOP (Jun 23 to Jun 24)'
        ])
        writer.writeheader()
        for result in wh_scop_clean_results:
            writer.writerow(result)

    moved_files, errors = move_files_to_metering_error(output_folder, SYSTEM_IDS_TO_REMOVE)

    logging.info(f"SCOP and space heating COP calculations completed and saved to {scop_output_file}, "
                 f"{sh_scop_output_file}, {clean_scop_output_file}, {clean_sh_scop_output_file}, "
                 f"{annual_scop_output_file}, {annual_sh_scop_output_file}, {wh_scop_output_file}, "
                 f"{annual_wh_scop_output_file}, and {clean_wh_scop_output_file}.")

    return {
        'saved_files': saved_files,
        'scop_results': scop_results,
        'annual_scop_results': annual_scop_results,
        'sh_scop_results': sh_scop_results,
        'annual_sh_scop_results': annual_sh_scop_results,
        'wh_scop_results': wh_scop_results,
        'annual_wh_scop_results': annual_wh_scop_results,
        'moved_files': moved_files,
        'errors': errors
    }


if __name__ == "__main__":
    result = main()
