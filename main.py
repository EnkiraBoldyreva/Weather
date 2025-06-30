import requests
import tkinter as tk
from tkinter import ttk, Toplevel, Label, filedialog, messagebox
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


# Часть 1: Текущая погода и прогноз (первая вкладка)
def save_graph(fig):
    """
    Сохраняет график в файл.
    :param fig: Объект графика, который необходимо сохранить.
    :type fig: matplotlib.figure.Figure
    :raises Exception: Если сохранение файла не удалось.
    :return: Путь к сохраненному файлу, если сохранение прошло успешно.
    :rtype: str
    """
    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
    )
    if file_path:
        fig.savefig(file_path)


def fon(temp_c):
    """
    Определяет цвет в зависимости от температуры в градусах Цельсия.
    :param temp_c: Температура в градусах Цельсия.
    :type temp_c: float
    :return: Цвет, соответствующий указанной температуре.
    :rtype: str
    :raises ValueError: Если переданное значение не является числом.
    """
    if not isinstance(temp_c, (int, float)):
        raise TypeError("Температура должна быть числом.")
    if temp_c < -20:
        return 'midnightblue'
    elif -20 <= temp_c <= -10:
        return 'steelblue'
    elif -9 <= temp_c <= -5:
        return 'powderblue'
    elif -4 <= temp_c <= 0:
        return 'lightcyan'
    elif 0 < temp_c <= 10:
        return 'moccasin'
    elif 10 < temp_c <= 15:
        return 'burlywood'
    elif 16 <= temp_c < 21:
        return 'goldenrod'
    elif 21 <= temp_c < 26:
        return 'darkorange'
    else:
        return 'firebrick'


def print_fon_color(temp_c):
    print(fon(temp_c))


def get_weather(city_tf, parent):
    """
    Получает данные о погоде для указанного города.
    :param city_tf: Название города.
    :type city_tf: str
    :param parent: Родительский объект, который будет использоваться для обработки данных о погоде.
    :type parent: объект
    :return: Данные о погоде в формате JSON.
    :rtype: dict
    :raises ValueError: Если указанный город не найден или данные о погоде недоступны.
    """
    city_name = city_tf.get()
    if city_name:
        api_key = '8ce6e15d64d5b0620181ac460c756bf7'
        weather_data = requests.get(
            f'https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}'
        )
        if weather_data.status_code == 200:
            temp = weather_data.json()['main']['temp']
            temp_c = int(temp - 273)
            feels_like = weather_data.json()['main']['feels_like']
            feel_c = int(feels_like - 273)
            humidity = weather_data.json()['main']['humidity']
            pressure = weather_data.json()['main']['pressure']
            wind_speed = weather_data.json()['wind']['speed']
            weather_window = Toplevel(parent)
            weather_window.title(f"Погода в {city_name}")

            bg_color = fon(temp_c)
            weather_window.configure(bg=bg_color)
            Label(weather_window, text=f"{temp_c}°C", font=("Arial", 50),
                  background=bg_color, fg='black').grid(row=0, column=0, padx=20, pady=20)
            Label(weather_window,
                  text=f"Ощущается как: {feel_c}°C\nВлажность: {humidity}%\nДавление: {pressure} hPa\n"
                       f"Скорость ветра: {wind_speed} м/с",
                  font=("Arial", 14), background=bg_color, fg='black').grid(row=0, column=1, columnspan=1, padx=20,
                                                                            pady=20)
            forecast_data = requests.get(
                f'https://api.openweathermap.org/data/2.5/forecast?q={city_name}&appid={api_key}'
            )
            if forecast_data.status_code == 200:
                forecast = forecast_data.json()
                times = []
                temperatures = []
                colors = []
                count = 0
                for item in forecast['list']:
                    if count >= 8:
                        break
                    timestamp = item['dt']
                    hour = (timestamp // 3600) % 24
                    times.append(f"{hour:02d}")
                    temp_fr = item['main']['temp']
                    temp_c_fr = int(temp_fr - 273.15)
                    temperatures.append(temp_c_fr)
                    count += 1
                y_upper = max(temperatures) + 5
                y_lower = min(temperatures) - 5
                for t in temperatures:
                    if t < -20:
                        colors.append('midnightblue')
                    elif -20 <= t <= -10:
                        colors.append('steelblue')
                    elif -9 <= t <= -5:
                        colors.append('powderblue')
                    elif -4 <= t <= 0:
                        colors.append('lightcyan')
                    elif 0 < t <= 10:
                        colors.append('moccasin')
                    elif 10 < t <= 15:
                        colors.append('burlywood')
                    elif 16 <= t < 21:
                        colors.append('goldenrod')
                    elif 21 <= t < 26:
                        colors.append('darkorange')
                    else:
                        colors.append('firebrick')
                fig, ax = plt.subplots()
                ax.bar(times, temperatures, color=colors)
                ax.set_title('Изменение температуры в ближайшие 24 часа')
                ax.set_xlabel('Время')
                ax.set_ylabel('Температура (°C)')
                ax.set_ylim([y_lower, y_upper])
                ax.set_yticks(np.arange(y_lower, y_upper + 1, 5))
                ax.set_xticks(times)
                ax.set_xticklabels(times, rotation=90)
                ax.axhline(0, color='k', linestyle='--', linewidth=1.5, label='0°C')
                ax.legend()
                canvas = FigureCanvasTkAgg(fig, master=weather_window)
                canvas.get_tk_widget().grid(row=1, columnspan=2)
                canvas.draw()
                tk.Button(weather_window, text='Сохранить график',
                          command=lambda: save_graph(fig)).grid(row=2, columnspan=2, pady=10)
            else:
                messagebox.showerror("Ошибка", "Не удалось получить данные прогноза.")
        else:
            messagebox.showerror("Ошибка", "Город не найден.")
    else:
        messagebox.showwarning("Предупреждение", "Введите название города.")


# Часть 2: Графики с отклонениями (вторая вкладка)
def fetch_weather_data_std(city, start_date, end_date, frequency):
    """
    Получает данные о погоде из API Visual Crossing для указанного города и временного диапазона.
    :param city: Название города для получения данных о погоде.
    :type city: str
    :param start_date: Дата начала диапазона в формате 'YYYY-MM-DD'.
    :type start_date: str
    :param end_date: Дата окончания диапазона в формате 'YYYY-MM-DD'.
    :type end_date: str
    :param frequency: Частота данных.
    :type frequency: str
    :return: Словарь с данными о погоде, включая температуру, влажность, скорость ветра и другие параметры.
    :rtype: dict
    :raises ValueError: Если указаны неверные параметры, такие как неправильный формат даты или недопустимая частота.
    """
    api_key = '5K77AMRZV84RCLG8R7BLNG498'
    url = (f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/'
           f'{city}/{start_date}/{end_date}?key={api_key}')
    response = requests.get(url)

    try:
        datetime.strptime(start_date, '%Y-%m-%d')
        datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Некорректный формат даты. Ожидается 'YYYY-MM-DD'.")

    if response.status_code == 200:
        data = response.json()
        results = []
        frequency_intervals = {'1h': 1, '3h': 3, '6h': 6, '12h': 12, '1d': 24}
        interval = frequency_intervals[frequency]
        if 'days' in data:
            for day in data['days']:
                date = day['datetime']
                if start_date <= date <= end_date and 'hours' in day:
                    for i, hour in enumerate(day['hours']):
                        if i % interval == 0:
                            hour_data = {
                                'datetime': datetime.strptime(f"{date} {hour['datetime']}", '%Y-%m-%d %H:%M:%S'),
                                'temperature': hour['temp'],
                                'pressure': hour['pressure'],
                                'humidity': hour['humidity'],
                                'windspeed': hour['windspeed']
                            }
                            results.append(hour_data)
        return results
    return None


def plot_weather_data_std(city, start_date, end_date, frequency):
    """
    Строит график погодных данных для указанного города в заданный период времени.
    :param city: Название города, для которого будут получены погодные данные.
    :type city: str
    :param start_date: Дата начала периода в формате 'YYYY-MM-DD'.
    :type start_date: str
    :param end_date: Дата окончания периода в формате 'YYYY-MM-DD'.
    :type end_date: str
    :param frequency: Частота данных для графика (например, 'daily', 'hourly').
    :type frequency: str
    :raises ValueError: Если указанный город не найден или даты указаны неверно.
    """
    data = fetch_weather_data_std(city, start_date, end_date, frequency)
    if not data:
        messagebox.showinfo("Инфо", "Нет данных для отображения")
        return
    times = [entry['datetime'] for entry in data]
    temperatures = [entry['temperature'] for entry in data]
    pressures = [entry['pressure'] for entry in data]
    humidities = [entry['humidity'] for entry in data]
    windspeeds = [entry['windspeed'] for entry in data]
    fig, axs = plt.subplots(4, 1, figsize=(10, 12))
    plot_with_deviation_lines(axs[0], times, temperatures, "Температура", "blue", "Температура (°C)")
    plot_with_deviation_lines(axs[1], times, pressures, "Давление", "green", "Давление (мм рт. ст.)")
    plot_with_deviation_lines(axs[2], times, humidities, "Влажность", "orange", "Влажность (%)")
    plot_with_deviation_lines(axs[3], times, windspeeds, "Скорость ветра", "purple", "Скорость ветра (м/с)")

    plt.tight_layout()
    plt.show()


def plot_with_deviation_lines(ax, times, values, label, color, y_label):
    """
    Строит график значений с линиями отклонения на заданной оси.
    :param ax: Объект оси (Axes), на которой будет построен график.
    :type ax: matplotlib.axes.Axes
    :param times: Список или массив временных меток для оси X.
    :type times: list or numpy.ndarray
    :param values: Список или массив значений для оси Y.
    :type values: list or numpy.ndarray
    :param label: Метка для графика, отображаемая в легенде.
    :type label: str
    :param color: Цвет линии графика.
    :type color: str
    :param y_label: Подпись для оси Y.
    :type y_label: str
    """
    mean_value = np.mean(values)
    std_value = np.std(values)
    ax.plot(times, values, marker='o', label=label, color=color)
    upper_line = [v + std_value for v in values]
    lower_line = [v - std_value for v in values]
    ax.plot(times, upper_line, linestyle='--', color=color, alpha=0.6, label=f'+σ={std_value:.2f}')
    ax.plot(times, lower_line, linestyle='--', color=color, alpha=0.6, label=f'-σ={std_value:.2f}')
    ax.axhline(mean_value, color='red', linestyle='--', label=f'Среднее: {mean_value:.2f}')
    ax.set_ylabel(y_label)
    ax.legend()
    ax.grid()


def on_submit_std(city_entry, start_date_entry, end_date_entry, frequency_combobox):
    """
    Обрабатывает событие отправки формы для получения стандартных данных.
    :param city_entry: Ввод имени города, для которого необходимо получить данные.
    :type city_entry: str
    :param start_date_entry: Ввод даты начала периода в формате 'YYYY-MM-DD'.
    :type start_date_entry: str
    :param end_date_entry: Ввод даты окончания периода в формате 'YYYY-MM-DD'.
    :type end_date_entry: str
    :param frequency_combobox: Выбор частоты данных.
    :type frequency_combobox: str
    """
    city = city_entry.get()
    start_date = start_date_entry.get()
    end_date = end_date_entry.get()
    frequency = frequency_combobox.get()
    plot_weather_data_std(city, start_date, end_date, frequency)


# Часть 3: Графики со средними значениями (третья вкладка)
def fetch_weather_data_avg(city, start_date, end_date, frequency):
    """
    Получает данные о погоде из API Visual Crossing для указанного города и временного диапазона.
    :param city: Название города для получения данных о погоде.
    :type city: str
    :param start_date: Дата начала диапазона в формате 'YYYY-MM-DD'.
    :type start_date: str
    :param end_date: Дата окончания диапазона в формате 'YYYY-MM-DD'.
    :type end_date: str
    :param frequency: Частота данных.
    :type frequency: str
    :return: Словарь с данными о погоде, включая температуру, влажность, скорость ветра и другие параметры.
    :rtype: dict
    :raises ValueError: Если указаны неверные параметры, такие как неправильный формат даты или недопустимая частота.
    """
    import re


    frequency_intervals = {'1h': 1, '3h': 3, '6h': 6, '12h': 12, '1d': 24}
    if frequency not in frequency_intervals:
        raise ValueError(f"Недопустимая частота: {frequency}. Допустимые значения: {list(frequency_intervals.keys())}")


    date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    if not date_pattern.match(start_date):
        raise ValueError(f"Неправильный формат даты начала: {start_date}. Используйте 'YYYY-MM-DD'.")
    if not date_pattern.match(end_date):
        raise ValueError(f"Неправильный формат даты окончания: {end_date}. Используйте 'YYYY-MM-DD'.")


    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError as ve:
        raise ValueError(f"Ошибка при парсинге дат: {ve}")

    if start > end:
        raise ValueError("Дата начала должна быть раньше даты окончания.")

    api_key = '5K77AMRZV84RCLG8R7BLNG498'
    url = (f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/'
           f'{city}/{start_date}/{end_date}?key={api_key}')
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        results = []
        frequency_intervals = {'1h': 1, '3h': 3, '6h': 6, '12h': 12, '1d': 24}
        interval = frequency_intervals[frequency]
        if 'days' in data:
            for day in data['days']:
                date = day['datetime']
                if 'hours' in day:
                    for i, hour in enumerate(day['hours']):
                        if i % interval == 0:
                            hour_data = {
                                'datetime': datetime.strptime(f"{date} {hour['datetime']}", '%Y-%m-%d %H:%M:%S'),
                                'temperature': hour['temp'],
                                'pressure': hour['pressure'],
                                'humidity': hour['humidity'],
                                'windspeed': hour['windspeed']
                            }
                            results.append(hour_data)

        return results
    return None


def plot_weather_data_avg(city, start_date, end_date, frequency):
    """
    Строит график средних данных для заданного города и периода.
    :param city: Название города, для которого необходимо получить средние данные.
    :type city: str
    :param start_date: Дата начала периода в формате 'YYYY-MM-DD'.
    :type start_date: str
    :param end_date: Дата окончания периода в формате 'YYYY-MM-DD'.
    :type end_date: str
    :param frequency: Частота данных ('daily', 'weekly', 'monthly').
    :type frequency: str
    """
    data = fetch_weather_data_avg(city, start_date, end_date, frequency)
    if not data:
        messagebox.showinfo("Инфо", "Нет данных для отображения")
        return
    times = [entry['datetime'] for entry in data]
    temperatures = [entry['temperature'] for entry in data]
    pressures = [entry['pressure'] for entry in data]
    humidities = [entry['humidity'] for entry in data]
    windspeeds = [entry['windspeed'] for entry in data]
    fig, axs = plt.subplots(4, 1, figsize=(10, 12))
    axs[0].plot(times, temperatures, marker='o', label='Температура')
    axs[0].plot(times, [np.mean(temperatures)] * len(times), color='r', linestyle='--', label='Средняя температура')
    axs[0].set_title('Температура')
    axs[0].set_ylabel('°F')
    axs[0].legend()
    axs[0].grid()
    axs[1].plot(times, pressures, marker='o', color='orange', label='Давление')
    axs[1].plot(times, [np.mean(pressures)] * len(times), color='r', linestyle='--', label='Среднее давление')
    axs[1].set_title('Давление')
    axs[1].set_ylabel('hPa')
    axs[1].legend()
    axs[1].grid()
    axs[2].plot(times, humidities, marker='o', color='green', label='Влажность')
    axs[2].plot(times, [np.mean(humidities)] * len(times), color='r', linestyle='--', label='Средняя влажность')
    axs[2].set_title('Влажность')
    axs[2].set_ylabel('%')
    axs[2].legend()
    axs[2].grid()
    axs[3].plot(times, windspeeds, marker='o', color='red', label='Скорость ветра')
    axs[3].plot(times, [np.mean(windspeeds)] * len(times), color='r', linestyle='--', label='Средняя скорость ветра')
    axs[3].set_title('Скорость ветра')
    axs[3].set_ylabel('м/с')
    axs[3].legend()
    axs[3].grid()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def on_submit_avg(city_entry, start_date_entry, end_date_entry, frequency_combobox):
    """
    Обрабатывает событие отправки данных для вычисления среднего значения.
    :param city_entry: Ввод города, для которого необходимо вычислить среднее значение.
    :type city_entry: str
    :param start_date_entry: Дата начала периода для расчета.
    :type start_date_entry: str
    :param end_date_entry: Дата окончания периода для расчета.
    :type end_date_entry: str
    :param frequency_combobox: Частота, с которой будут агрегироваться данные.
    :type frequency_combobox: str
    :raises ValueError: Если введенные даты некорректны или если город не найден.
    :raises TypeError: Если типы входных параметров не соответствуют ожидаемым.
    :return: Среднее значение для заданного города и периода.
    :rtype: float
    """
    city = city_entry.get()
    start_date = start_date_entry.get()
    end_date = end_date_entry.get()
    frequency = frequency_combobox.get()
    plot_weather_data_avg(city, start_date, end_date, frequency)


if __name__ == '__main__':
    root = tk.Tk()
    root.title("Приложение Погода")
    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)

    tab_current = ttk.Frame(notebook)
    notebook.add(tab_current, text="Текущая погода")
    tk.Label(tab_current, text="Введите город:").grid(row=0, column=0, padx=5, pady=5)
    city_tf_current = tk.Entry(tab_current)
    city_tf_current.grid(row=0, column=1, padx=5, pady=5)
    tk.Button(tab_current, text='Найти', command=lambda: get_weather(city_tf_current, root)).grid(row=0, column=2,
                                                                                                  padx=5,
                                                                                                  pady=5)

    tab_std = ttk.Frame(notebook)
    notebook.add(tab_std, text="Статистика (СКО)")
    tk.Label(tab_std, text="Город:").grid(row=0, column=0, padx=5, pady=5)
    city_entry_std = tk.Entry(tab_std)
    city_entry_std.grid(row=0, column=1, padx=5, pady=5)
    tk.Label(tab_std, text="Дата начала (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5)
    start_date_entry_std = tk.Entry(tab_std)
    start_date_entry_std.grid(row=1, column=1, padx=5, pady=5)
    tk.Label(tab_std, text="Дата конца (YYYY-MM-DD):").grid(row=2, column=0, padx=5, pady=5)
    end_date_entry_std = tk.Entry(tab_std)
    end_date_entry_std.grid(row=2, column=1, padx=5, pady=5)
    tk.Label(tab_std, text="Частота:").grid(row=3, column=0, padx=5, pady=5)
    frequency_combobox_std = ttk.Combobox(tab_std, values=['1h', '3h', '6h', '12h', '1d'])
    frequency_combobox_std.grid(row=3, column=1, padx=5, pady=5)
    frequency_combobox_std.set('1h')
    tk.Button(tab_std, text="Построить графики",
              command=lambda: on_submit_std(city_entry_std, start_date_entry_std, end_date_entry_std,
                                            frequency_combobox_std)).grid(row=4, columnspan=2, pady=10)
   
    tab_avg = ttk.Frame(notebook)
    notebook.add(tab_avg, text="Статистика (Средние)")
    tk.Label(tab_avg, text="Город:").grid(row=0, column=0, padx=5, pady=5)
    city_entry_avg = tk.Entry(tab_avg)
    city_entry_avg.grid(row=0, column=1, padx=5, pady=5)
    tk.Label(tab_avg, text="Дата начала (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5)
    start_date_entry_avg = tk.Entry(tab_avg)
    start_date_entry_avg.grid(row=1, column=1, padx=5, pady=5)
    tk.Label(tab_avg, text="Дата конца (YYYY-MM-DD):").grid(row=2, column=0, padx=5, pady=5)
    end_date_entry_avg = tk.Entry(tab_avg)
    end_date_entry_avg.grid(row=2, column=1, padx=5, pady=5)
    tk.Label(tab_avg, text="Частота:").grid(row=3, column=0, padx=5, pady=5)
    frequency_combobox_avg = ttk.Combobox(tab_avg, values=['1h', '3h', '6h', '12h', '1d'])
    frequency_combobox_avg.grid(row=3, column=1, padx=5, pady=5)
    frequency_combobox_avg.set('1h')
    tk.Button(tab_avg, text="Построить графики",
              command=lambda: on_submit_avg(city_entry_avg, start_date_entry_avg, end_date_entry_avg,
                                            frequency_combobox_avg)).grid(row=4, columnspan=2, pady=10)
    root.mainloop()
