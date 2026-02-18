import argparse
import csv
import sys
from tabulate import tabulate

def parse_args(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--files", nargs="+", dest="files", required=True)
    parser.add_argument("--report", dest="report", required=True)
    return parser.parse_args(args)

def read_files(filenames):
    all_gdp = {}
    for filename in filenames:
        with open(filename, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            header = next(reader, None)
            if header is None:
                continue
            try:
                country_pos = header.index("country")
                gdp_pos = header.index("gdp")
                year_pos = header.index("year")
            except ValueError:
                continue
            for row in reader:
                if len(row) <= max(country_pos, gdp_pos, year_pos):
                    continue
                country = row[country_pos]
                year = int(row[year_pos])
                gdp = int(row[gdp_pos])
                if country not in all_gdp:
                    all_gdp[country] = {}
                all_gdp[country][year] = gdp
    return all_gdp

def compute_averages(all_gdp):
    averages = {}
    for country, years in all_gdp.items():
        averages[country] = sum(years.values()) / len(years)
    sorted_items = sorted(averages.items(), key=lambda item: -item[1])
    return sorted_items

def print_table(averages_list):
    headers = ["country", "gdp"]
    custom_index = range(1, len(averages_list) + 1)
    print(tabulate(averages_list, headers=headers, tablefmt="grid",
                   floatfmt=".2f", showindex=custom_index))

def write_report(averages_list, report_filename):
    with open(report_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(["country", "average_gdp"])
        for country, avg in averages_list:
            writer.writerow([country, f"{avg:.2f}"])

def main():
    args = parse_args()
    all_gdp = read_files(args.files)
    averages = compute_averages(all_gdp)
    print_table(averages)
    write_report(averages, args.report)

if __name__ == "__main__":
    main()