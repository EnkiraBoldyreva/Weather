from main import fon, fetch_weather_data_std, print_fon_color, fetch_weather_data_avg, on_submit_avg, \
    plot_with_deviation_lines
import pytest
import datetime
import builtins
from unittest.mock import Mock
from unittest.mock import MagicMock, patch
from requests.models import Response
import numpy as np
import matplotlib.pyplot as plt


# 1 function
def test_fon():
    assert (fon(-21) == 'midnightblue')
    assert (fon(-15) == 'steelblue')
    assert (fon(-7) == 'powderblue')
    assert (fon(-2) == 'lightcyan')
    assert (fon(5) == 'moccasin')
    assert (fon(12) == 'burlywood')
    assert (fon(18) == 'goldenrod')
    assert (fon(22) == 'darkorange')
    assert (fon(30) == 'firebrick')


def test_fon_invalid_input():
    with pytest.raises(TypeError):
        fon("a")
    with pytest.raises(TypeError):
        fon(None)


# 2 function
def test_fetch_weather_data_std_1():
    result = fetch_weather_data_std("Москва", "2024-12-17", "2024-12-17", '1h')
    assert (result[0]['datetime'] == datetime.datetime(2024, 12, 17, 0, 0))


def test_fetch_weather_data_std_():
    result = fetch_weather_data_std("Москва", "2024-12-16", "2024-12-17", '1h')
    assert (result[1]['datetime'] != datetime.datetime(2024, 12, 17, 0, 0))


# 3 function
def test_print_fon_color_1():
    builtins.print = Mock()
    print_fon_color(20)
    builtins.print.assert_called_with('goldenrod')


def test_print_fon_color_2():
    builtins.print = Mock()
    print_fon_color(-20)
    builtins.print.assert_called_with('steelblue')


def test_print_fon_color_3():
    builtins.print = Mock()
    print_fon_color(-2)
    builtins.print.assert_called_with('lightcyan')


# 4 function
def test_fetch_weather_data_avg_invalid_date(monkeypatch):
    response_mock = MagicMock(spec=Response)
    response_mock.status_code = 200
    response_mock.json.return_value = {"days": []}
    monkeypatch.setattr("requests.get", lambda url: response_mock)

    with pytest.raises(ValueError):
        fetch_weather_data_avg("Moscow", "2023-99-99", "2023-10-10", "1h")


def test_fetch_weather_data_avg_invalid_frequency(monkeypatch):
    response_mock = MagicMock(spec=Response)
    response_mock.status_code = 200
    response_mock.json.return_value = {"days": []}
    monkeypatch.setattr("requests.get", lambda url: response_mock)

    with pytest.raises(ValueError):
        fetch_weather_data_avg("Moscow", "2023-10-01", "2023-10-10", "2h")


# 5 function
@pytest.fixture
def mock_plot():
    return MagicMock()


@pytest.fixture
def city_val():
    return "Moscow"


@pytest.fixture
def start_date_val():
    return "2024-01-01"


@pytest.fixture
def end_date_val():
    return "2024-01-31"


@pytest.fixture
def frequency_val():
    return "1d"


def test_on_submit_avg_success(mock_plot, city_val, start_date_val, end_date_val, frequency_val):
    with patch('main.plot_weather_data_avg', mock_plot):
        city_entry = MagicMock()
        start_date_entry = MagicMock()
        end_date_entry = MagicMock()
        frequency_combobox = MagicMock()

        city_entry.get.return_value = city_val
        start_date_entry.get.return_value = start_date_val
        end_date_entry.get.return_value = end_date_val
        frequency_combobox.get.return_value = frequency_val

        on_submit_avg(city_entry, start_date_entry, end_date_entry, frequency_combobox)
        mock_plot.assert_called_once_with(city_val, start_date_val, end_date_val, frequency_val)


def test_on_submit_avg_value_error():
    city_entry = MagicMock()
    start_date_entry = MagicMock()
    end_date_entry = MagicMock()
    frequency_combobox = MagicMock()

    city_entry.get.return_value = "Moscow"
    start_date_entry.get.return_value = "2024-01-01"
    end_date_entry.get.return_value = "2024-01-31"
    frequency_combobox.get.return_value = "invalid_frequency"
    with pytest.raises(ValueError):
        on_submit_avg(city_entry, start_date_entry, end_date_entry, frequency_combobox)


# 6 function
def test_plot_with_deviation_lines():
    times = [1, 2, 3, 4, 5]
    values = [10, 15, 20, 15, 10]
    label = "Test Data"
    color = "blue"
    y_label = "Value"
    fig, ax = plt.subplots()
    ax_mock = MagicMock(wraps=ax)
    plot_with_deviation_lines(ax_mock, times, values, label, color, y_label)
    ax_mock.plot.assert_any_call(times, values, marker='o', label=label, color=color)
    std_value = np.std(values)
    upper_line = [v + std_value for v in values]
    lower_line = [v - std_value for v in values]
    ax_mock.plot.assert_any_call(times, upper_line, linestyle='--', color=color, alpha=0.6, label=f'+σ={std_value:.2f}')
    ax_mock.plot.assert_any_call(times, lower_line, linestyle='--', color=color, alpha=0.6, label=f'-σ={std_value:.2f}')
    mean_value = np.mean(values)
    ax_mock.axhline.assert_called_with(mean_value, color='red', linestyle='--', label=f'Среднее: {mean_value:.2f}')
    ax_mock.set_ylabel.assert_called_with(y_label)
    ax_mock.legend.assert_called_once()
    ax_mock.grid.assert_called_once()
    plt.close(fig)
