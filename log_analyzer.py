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

# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

default_config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}


class LogInfo:
    def __init__(self):
        self._remote_addr = ""
        self._remote_user = ""
        self._http_x_real_ip = ""
        self._time_local = datetime.date
        self._request = ""
        self._status = ""
        self._body_bytes_sent = ""
        self._http_referer = ""
        self._http_user_agent = ""
        self._http_x_forwarded_for = ""
        self._http_X_REQUEST_ID = ""
        self._http_X_RB_USER = ""
        self._request_time = 0.0

    def request(self) -> str:
        return self._request

    def request_clear(self) -> str:
        fields = self._request.split()
        if len(fields) > 2:
            return fields[1]
        else:
            return fields[0]

    def request_time(self) -> float:
        return self._request_time


class StatInfo:
    def __init__(self, request: str):
        assert (len(request) > 0)
        self._request = request
        self._request_times = []

    def append_time(self, request_time: float):
        return self._request_times.append(request_time)

    def count(self):
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
    result._remote_addr = next(data)
    result._remote_user = next(data)
    result._http_x_real_ip = next(data)
    result._time_local = time.strptime(next(data), "[%d/%b/%Y:%H:%M:%S %z]")
    result._request = next(data)
    result._status = next(data)
    result._body_bytes_sent = next(data)
    result._http_referer = next(data)
    result._http_user_agent = next(data)
    result._http_x_forwarded_for = next(data)
    result._http_X_REQUEST_ID = next(data)
    result._http_X_RB_USER = next(data)
    result._request_time = float(next(data))
    return result


def process_log_info(reader: tp.Generator[tp.Iterator[str], None, None]) -> tp.Dict[str, StatInfo]:
    request_2_log_info = {}
    for info in reader:
        try:
            log_info = parse_log_info(info)
            request = log_info.request_clear()
            sat_info = request_2_log_info[request] if request_2_log_info.get(request, False) else StatInfo(request)
            sat_info.append_time(log_info.request_time())
            request_2_log_info[request] = sat_info
        except Exception as exc:
            logging.error(exc.args)
    return request_2_log_info


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
            "count_perc":  round(float(info.count()) / all_count, 3),
            "time_sum": round(info.request_times_sum(), 3),
            "time_perc": round(info.request_times_sum() / all_time, 3),
            "time_avg": round(info.request_times_avg(), 3),
            "time_max": round(info.request_times_max(), 3),
            "time_med": round(info.request_times_median(), 3),
        }
        result.append(row_table)

    return result


def splitter(s: str) -> tp.List[str]:
    parts = re.sub('".+?"|\[.+?\]', lambda x: x.group(0).replace(" ", "\x00"), s).split()
    return [part.replace("\x00", " ").replace('"', '') for part in parts]


def _read_log(log_name: str) -> tp.Generator[tp.Iterator[str], None, None]:
    reader = gzip.open if log_name.lower().endswith(".gz") else open
    with reader(log_name, mode="rt", encoding="utf8") as file:
        for line in file:
            yield iter(splitter(line.rstrip()))


def process_log_file(log_name: str) -> tp.List[dict]:
    stat_info = calculate_stat_info(process_log_info(_read_log(log_name)))
    stat_info.sort(key=lambda x: x["time_perc"], reverse=True)
    return stat_info


def create_html_file(html_save: str, stat_info: tp.List[dict]):
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


def process_folder(log_folder: str, report_folder: str, report_size: int = 0):
    log_name, date_str = provide_last_log_path_and_date(log_folder)
    if log_name is None or date_str is None:
        logging.warning("No log file to work, exit")
        return
    html_save = os.path.join(report_folder, f"report-{date_str}.html")
    if os.path.exists(html_save):
        logging.info("report file to log already exists, working was canceled, exit")
        return
    stat_info = process_log_file(os.path.join(log_folder, log_name))
    if report_size > 0:
        stat_info = stat_info[:min(len(stat_info), report_size)]
    create_html_file(html_save, stat_info)


def main(config=None):
    if config is None:
        config = default_config
    logging.basicConfig(filename=None,
                        level=logging.DEBUG,
                        )
    process_folder(config["LOG_DIR"], config["REPORT_DIR"], config["REPORT_SIZE"])


if __name__ == "__main__":
    main()
