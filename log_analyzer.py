#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import gzip
import typing as tp
import re
import pathlib
import logging
import time
import os
import os.path
from dataclasses import dataclass

# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

default_config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "ERROR_MAX_RATIO": 0.4,  # отношение ошибочных строк к общим, больше которого - ошибка обработки лога
    "LOG_FILE": None  # файл для лога, если нет - в консоль
}


@dataclass
class LogInfo:
    remote_addr = ""
    remote_user = ""
    http_x_real_ip = ""
    time_local = datetime.date
    request = ""
    status = ""
    body_bytes_sent = ""
    http_referer = ""
    http_user_agent = ""
    http_x_forwarded_for = ""
    http_X_REQUEST_ID = ""
    http_X_RB_USER = ""
    request_time = 0.0

    def request_clear(self) -> str:
        fields = self.request.split()
        if len(fields) > 2:
            return fields[1]
        else:
            return fields[0]


class StatInfo:
    def __init__(self, request: str):
        assert (len(request) > 0)
        self._request = request
        self._request_times = []

    def append_time(self, request_time: float) -> None:
        self._request_times.append(request_time)

    def count(self) -> int:
        return len(self._request_times)

    def request_times_sum(self) -> float:
        return sum(self._request_times)

    def request_times_avg(self) -> float:
        assert (len(self._request_times) > 0)
        return sum(self._request_times) / len(self._request_times)

    def request_times_max(self) -> float:
        assert (len(self._request_times) > 0)
        return max(self._request_times)

    def request_times_median(self) -> float:
        assert (len(self._request_times) > 0)
        sorted_times = sorted(self._request_times)
        length = len(sorted_times)
        if length == 1:
            return 0.5 * sorted_times[0]
        elif length % 2 == 0:  # в четных рядах - полусумма элементов
            return 0.5 * (sorted_times[length // 2] + sorted_times[length // 2 - 1])
        else:  # иначе - элемент посредине
            return sorted_times[length // 2 + 1]


def parse_log_info(data: tp.Iterator[str]) -> LogInfo:
    result = LogInfo()
    result.remote_addr = next(data)
    result.remote_user = next(data)
    result.http_x_real_ip = next(data)
    result.time_local = time.strptime(next(data), "[%d/%b/%Y:%H:%M:%S %z]")
    result.request = next(data)
    result.status = next(data)
    result.body_bytes_sent = next(data)
    result.http_referer = next(data)
    result.http_user_agent = next(data)
    result.http_x_forwarded_for = next(data)
    result.http_X_REQUEST_ID = next(data)
    result.http_X_RB_USER = next(data)
    result.request_time = float(next(data))
    return result


def process_log_info(reader: tp.Generator[tp.Iterator[str], None, None]) -> tp.Tuple[tp.Dict[str, StatInfo], int]:
    request_2_log_info = {}
    error_count = 0
    for info in reader:
        try:
            log_info = parse_log_info(info)
            request = log_info.request_clear()
            sat_info = request_2_log_info[request] if request_2_log_info.get(request, False) else StatInfo(request)
            sat_info.append_time(log_info.request_time)
            request_2_log_info[request] = sat_info
        except Exception as exc:
            logging.exception(exc.args)
            error_count += 1
    return request_2_log_info, error_count


def log_line_split(s: str) -> tp.List[str]:
    parts = re.sub('".+?"|\[.+?\]', lambda x: x.group(0).replace(" ", "\x00"), s).split()
    return [part.replace("\x00", " ").replace('"', '') for part in parts]


def _read_log(log_name: str) -> tp.Generator[tp.Iterator[str], None, None]:
    reader = gzip.open if log_name.lower().endswith(".gz") else open
    with reader(log_name, mode="rt", encoding="utf8") as file:
        for line in file:
            row = log_line_split(line.rstrip())
            # print(row)
            yield iter(row)


def calculate_stat_info(stat_info: tp.Dict[str, StatInfo]) -> tp.List[dict]:
    all_count = 0
    all_time = 0
    for request, info in stat_info.items():
        all_count += info.count()
        all_time += info.request_times_sum()

    result = []

    for request, info in stat_info.items():
        row_table = {
            "url": request,
            "count": info.count(),
            "count_perc": round(float(info.count()) / all_count, 3),
            "time_sum": round(info.request_times_sum(), 3),
            "time_perc": round(info.request_times_sum() / all_time, 3),
            "time_avg": round(info.request_times_avg(), 3),
            "time_max": round(info.request_times_max(), 3),
            "time_med": round(info.request_times_median(), 3),
        }
        result.append(row_table)

    return result


def process_log_file(log_name: str) -> tp.Tuple[tp.List[dict], int]:
    log_info, error_count = process_log_info(_read_log(log_name))
    stat_info = calculate_stat_info(log_info)
    stat_info.sort(key=lambda x: x["time_perc"], reverse=True)
    return stat_info, error_count


def create_html_file(html_save: str, stat_info: tp.List[dict]) -> None:
    html_txt = pathlib.Path('report.html').read_text().replace("$table_json", str(stat_info))
    pathlib.Path(html_save).write_text(html_txt)


def provide_last_log_path_and_date(log_folder: str) -> tp.Tuple[tp.Optional[str], tp.Optional[str]]:
    reg_mask = r'nginx-access-ui.log-(\d{2})(\d{2})(\d{4})($|.gz)'
    files = sorted(
        [
            file for file in os.listdir(log_folder)
            if os.path.isfile(os.path.join(log_folder, file)) and re.match(reg_mask, file)
        ],
        reverse=True
    )
    if len(files) == 0:
        return None, None
    log_name = files[0]
    date_str = re.search(reg_mask, log_name).group(0)
    return log_name, date_str


def process_folder(log_folder: str, report_folder: str, max_error_ratio: float, report_size: int = 0) -> None:
    log_name, date_str = provide_last_log_path_and_date(log_folder)
    if log_name is None or date_str is None:
        logging.info("No log file to work, exit")
        return
    html_save = os.path.join(report_folder, f"report-{date_str}.html")
    if os.path.exists(html_save):
        logging.info("report file to log already exists, working was canceled, exit")
        return
    stat_info, error_count = process_log_file(os.path.join(log_folder, log_name))
    error_ratio = float(error_count) / len(stat_info)
    if error_ratio > max_error_ratio:
        logging.error(f"report file has too many error(error_ratio is {error_ratio}, limit is {max_error_ratio}, exit")
        return
    if report_size > 0:
        stat_info = stat_info[:min(len(stat_info), report_size)]
    create_html_file(html_save, stat_info)


def prepare_logging(filename: tp.Optional[str]) -> None:
    logging.basicConfig(filename=filename, level=logging.DEBUG,
                        format="[%(asctime)s] %(levelname).1s %(message)s", datefmt="%Y.%m.%d %H:%M:%S")


def main(config=None) -> None:
    if config is None:
        config = default_config
    prepare_logging(config.get("LOG_FILE", None))
    process_folder(config["LOG_DIR"], config["REPORT_DIR"], config["ERROR_MAX_RATIO"], config["REPORT_SIZE"])


if __name__ == "__main__":
    main()
