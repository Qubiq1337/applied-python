# -*- encoding: utf-8 -*-
from re import match
from datetime import datetime


def build_request(www, request, ignore_www):
    request = request.split('?').pop(0)
    if ignore_www is False:
        request = www + request
        return request
    else:
        return request


def counter(all_requests, request, ping, ignore_urls, ignore_files):
    if request not in ignore_urls:
        if ignore_files:
            if '.' in request[request.index("/"):]:
                return
        if all_requests.get(request):
            all_requests[request]['ping'] += int(ping)
            all_requests[request]['count'] += 1
        else:
            all_requests[request] = {'ping': int(ping), 'count': 1}


def sort_requests(all_requests, slow_queries):
    if slow_queries:
        sorted_results = sorted(all_requests.items(), key=lambda t: t[1]['ping'], reverse=True)[:5]
        ping = map(lambda result: int(result[1]['ping'] / result[1]['count']), sorted_results)
        sorted_ping = list(sorted(ping, key=lambda t: -t))
        return sorted_ping
    else:
        sorted_results = sorted(all_requests.items(), key=lambda t: t[1]['count'])[:-6:-1]
        count = list(map(lambda result: int(result[1]['count']), sorted_results))
        return count


def parse(
    ignore_files=False,
    ignore_urls=[],
    start_at=None,
    stop_at=None,
    request_type=None,
    ignore_www=False,
    slow_queries=False
):
    if start_at:
        start_at = datetime.strptime(start_at, '%d/%b/%Y %H:%M:%S')
    if stop_at:
        stop_at = datetime.strptime(stop_at, '%d/%b/%Y %H:%M:%S')
    all_requests = {}
    with open('log.log', 'r') as log:
        reg_exp = (r'\[(?P<date_time>\d{1,2}\/\w{3,4}\/\d{0,4}\s\d\d:\d\d:\d\d)\]\s\"'
                   r'(?P<method>OPTIONS|GET|HEAD|POST|PUT|PATCH|DELETE|RACE|CONNECT)\s'
                   r'(?P<protocol>http:\/\/|https:\/\/|http:\/\/|https:\/\/)'
                   r'(?P<www>www\.|)'
                   r'(?P<request>[a-z0-9]+[\-\.]{1}[a-z0-9]+\.[a-z]{2,5}\/.*)\s'
                   r'(?P<version>\w{3,5}\/\d\.\d)\"\s'
                   r'(?P<status>\d{3})\s'
                   r'(?P<ping>\d+)')
        for line in log.readlines():
            matches = match(reg_exp, line)

            if matches:
                date_time, method, _, www, request, _, _, ping = matches.groups()

                if start_at or stop_at:
                    log_datetime = datetime.strptime(date_time, '%d/%b/%Y %H:%M:%S')
                if start_at:
                    if log_datetime < start_at:
                        continue
                if stop_at:
                    if log_datetime > stop_at:
                        break
                if request_type is None:
                    pass
                elif request_type != method:
                    continue
                request = build_request(www, request, ignore_www)
                counter(all_requests, request, ping, ignore_urls, ignore_files)
    return(sort_requests(all_requests, slow_queries))
