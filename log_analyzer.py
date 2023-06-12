#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import gzip
import typing as tp
import re
import pathlib
import logging
from dataclasses import dataclass
from typing import Type
import time

# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}


@dataclass
class LogInfo:
    _remote_addr = ""
    _remote_user = ""
    _http_x_real_ip = ""
    _time_local = datetime.date
    _request = ""
    _status = ""
    _body_bytes_sent = ""
    _http_referer = ""
    _http_user_agent = ""
    _http_x_forwarded_for = ""
    _http_X_REQUEST_ID = ""
    _http_X_RB_USER = ""
    _request_time = ""

    @classmethod
    def request(cls) -> str:
        return cls._request

    @classmethod
    def request_clear(cls) -> str:
        fields = cls._request.split()
        if len(fields) > 2:
            return fields[1]
        else:
            return fields[0]


def parse_log_info(data: tp.Iterator[str]) -> Type[LogInfo]:
    result = LogInfo
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
    result._request_time = next(data)
    return result


def process_log_info(reader: tp.Generator[tp.Iterator[str], None, None]):
    request_2_log_info = {}
    lines = 0
    for info in reader:
        lines += 1
        try:
            log_info = parse_log_info(info)
            if request_2_log_info.get(log_info.request_clear(), None) is None:
                request_2_log_info[log_info.request_clear()] = [log_info]
            else:
                request_2_log_info[log_info.request_clear()].append(log_info)
        except Exception as exc:
            logging.error(exc.args)

    count = 0
    for val in request_2_log_info.values():
        count += len(val)
    print(
        f"lines = {lines}, keys count = {len(request_2_log_info.keys())}, key[0] = {request_2_log_info.keys()}, log_info count = {count}")


def splitter(s: str) -> tp.List[str]:
    parts = re.sub('".+?"|\[.+?\]', lambda x: x.group(0).replace(" ", "\x00"), s).split()
    return [part.replace("\x00", " ").replace('"', '') for part in parts]


def _read_log(log_name: pathlib.Path) -> tp.Generator[tp.Iterator[str], None, None]:
    reader = gzip.open if log_name.as_posix().lower().endswith(".gz") else open
    with reader(log_name, mode="rt", encoding="utf8") as file:
        for line in file:
            yield iter(splitter(line.rstrip()))


def process_log_file(log_file: pathlib.Path):
    process_log_info(_read_log(log_file))


def main():
    process_log_file(pathlib.Path(config["LOG_DIR"] + "/nginx-access-ui.log-20170630"))


if __name__ == "__main__":
    main()
