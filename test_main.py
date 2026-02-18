import pytest
import csv
import sys
import main

def create_csv(tmp_path, filename, rows, header=True):
    path = tmp_path / filename
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        if header:
            writer.writerow(["country", "gdp", "year"])
        writer.writerows(rows)
    return path

def test_parse_args_valid(monkeypatch):
    test_args = ["script", "--files", "a.csv", "b.csv", "--report", "out.csv"]
    monkeypatch.setattr(sys, "argv", test_args)
    args = main.parse_args()
    assert args.files == ["a.csv", "b.csv"]
    assert args.report == "out.csv"

def test_parse_args_missing_files(monkeypatch):
    test_args = ["script", "--report", "out.csv"]
    monkeypatch.setattr(sys, "argv", test_args)
    with pytest.raises(SystemExit):
        main.parse_args()

def test_parse_args_missing_report(monkeypatch):
    test_args = ["script", "--files", "a.csv"]
    monkeypatch.setattr(sys, "argv", test_args)
    with pytest.raises(SystemExit):
        main.parse_args()

def test_read_files_single(tmp_path):
    file1 = create_csv(tmp_path, "data1.csv", [
        ["Russia", 1000, 2020],
        ["USA", 2000, 2020],
    ])
    result = main.read_files([str(file1)])
    assert result == {
        "Russia": {2020: 1000},
        "USA": {2020: 2000},
    }

def test_read_files_multiple(tmp_path):
    file1 = create_csv(tmp_path, "data1.csv", [
        ["Russia", 1000, 2020],
        ["USA", 2000, 2020],
    ])
    file2 = create_csv(tmp_path, "data2.csv", [
        ["Russia", 1100, 2021],
        ["China", 3000, 2021],
    ])
    result = main.read_files([str(file1), str(file2)])
    assert result == {
        "Russia": {2020: 1000, 2021: 1100},
        "USA": {2020: 2000},
        "China": {2021: 3000},
    }

def test_read_files_empty_file(tmp_path):
    empty = tmp_path / "empty.csv"
    empty.touch()
    file2 = create_csv(tmp_path, "data.csv", [["Russia", 1000, 2020]])
    result = main.read_files([str(empty), str(file2)])
    assert result == {"Russia": {2020: 1000}}

def test_read_files_missing_columns(tmp_path, caplog):
    bad = tmp_path / "bad.csv"
    with open(bad, 'w') as f:
        f.write("a,b,c\n1,2,3\n")
    good = create_csv(tmp_path, "good.csv", [["Russia", 1000, 2020]])
    result = main.read_files([str(bad), str(good)])
    assert result == {"Russia": {2020: 1000}}

def test_compute_averages_basic():
    data = {
        "Russia": {2020: 1000, 2021: 1100},
        "USA": {2020: 2000, 2021: 2100},
    }
    expected = [("USA", 2050.0), ("Russia", 1050.0)]
    assert main.compute_averages(data) == expected

def test_compute_averages_single_country():
    data = {"Russia": {2020: 1000}}
    assert main.compute_averages(data) == [("Russia", 1000.0)]

def test_compute_averages_empty():
    assert main.compute_averages({}) == []

def test_print_table_empty(capsys):
    main.print_table([])
    captured = capsys.readouterr()
    assert "country" in captured.out

def test_write_report_basic(tmp_path):
    data = [("USA", 2050.0), ("Russia", 1050.0)]
    report = tmp_path / "report.csv"
    main.write_report(data, str(report))
    with open(report) as f:
        reader = csv.reader(f)
        rows = list(reader)
    assert rows[0] == ["country", "average_gdp"]
    assert rows[1] == ["USA", "2050.00"]
    assert rows[2] == ["Russia", "1050.00"]

def test_write_report_empty(tmp_path):
    report = tmp_path / "empty.csv"
    main.write_report([], str(report))
    with open(report) as f:
        rows = list(csv.reader(f))
    assert rows == [["country", "average_gdp"]]

def test_main_integration(tmp_path, monkeypatch, capsys):
    file1 = create_csv(tmp_path, "eco1.csv", [
        ["Russia", 1000, 2020],
        ["USA", 2000, 2020],
    ])
    file2 = create_csv(tmp_path, "eco2.csv", [
        ["Russia", 1100, 2021],
        ["China", 3000, 2021],
    ])
    report = tmp_path / "out.csv"
    test_args = ["script", "--files", str(file1), str(file2), "--report", str(report)]
    monkeypatch.setattr(sys, "argv", test_args)
    main.main()
    captured = capsys.readouterr()
    assert "USA" in captured.out
    assert "China" in captured.out
    assert "Russia" in captured.out
    assert "2000.00" in captured.out
    with open(report) as f:
        rows = list(csv.reader(f))
    assert rows[0] == ["country", "average_gdp"]
    assert rows[1][0] == "China"
    assert rows[1][1] == "3000.00"
    assert rows[2][0] == "USA"
    assert rows[2][1] == "2000.00"
    assert rows[3][0] == "Russia"
    assert rows[3][1] == "1050.00"

def test_main_no_files(monkeypatch):
    test_args = ["script", "--report", "out.csv"]
    monkeypatch.setattr(sys, "argv", test_args)
    with pytest.raises(SystemExit):
        main.main()