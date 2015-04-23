#!/usr/bin/env python3
from __future__ import print_function, division, with_statement
import re
import atexit
from datetime import datetime
# Basic Regexes for each type.
# Strings only support double quotes cause yes.
regex = {
    "str": "^\s*([^=]+)\s*=\s*\"([^\"]*)\"\s*$",
    "int": "^\s*([^=]+)\s*=\s*(\d+)\s*$",
    "list": "^\s*([^=]+)\s*=\s*\[(.*?)\]\s*$",
    "bool": "^\s*([^=]+)\s*=\s*([fF][aA][lL][sS][eE]|[tT][rR][uU][eE])\s*",
    "file": "^\s*([^=]+)\s*=[fF][iI][lL][eE]\s*\((.*?)\s*,\s*(.*?)\)\s*$"
}
for i in regex:
    regex[i] = re.compile(regex[i])

section_start = re.compile("^\[(.*?)\]$")


def parse_line(line, section=None):
    data_dict = {}
    if section is not None:
        data_dict[section] = {}
    for type_, reg in regex.items():
        data = reg.match(line)
        if data:
            if type_ == "list":
                if section is None:
                    data_dict[data.group(1)] = []
                else:
                    data_dict[section][data.group(1)] = []
                for elem in data.group(2).split(","):
                    elem = elem.strip()
                    if section is  None:
                        data_dict[data.group(1)].append(parse_line("dummy={}".format(elem))["dummy"])
                    else:
                        data_dict[section][data.group(1)].append(parse_line("dummy={}".format(elem))["dummy"])
            elif type_ == "str":
                if section is None:
                    data_dict[data.group(1)] = str(data.group(2))
                else:
                    data_dict[section][data.group(1)] = str(data.group(2))
            elif type_ == "int":
                if section is None:
                    data_dict[data.group(1)] = int(data.group(2))
                else:
                    data_dict[section][data.group(1)] = int(data.group(2))
            elif type_ == "bool":
                if section is None:
                    data_dict[data.group(1)] = data.group(2).lower() == "true"
                else:
                    data_dict[section][data.group(1)] = data.group(2).lower() == "true"
            elif type_ == "file":
                filename, filemode = data.group(2), data.group(3)
                filename = parse_line("dummy={}".format(filename))["dummy"]
                filemode = parse_line("dummy={}".format(filemode))["dummy"]
                if not all((filename, filemode)):
                    return
                if not isinstance(filename, str) or not isinstance(filemode, str):
                    return
                try:
                    file_obj = open(filename.format(datetime.today().strftime("%Y-%m-%d")), filemode)
                except FileNotFoundError:
                    return
                file_obj.raw_name = filename
                atexit.register(file_obj.close)
                if section is None:
                    data_dict[data.group(1)] = file_obj
                else:
                    data_dict[section][data.group(1)] = file_obj
            return data_dict


def parse_file(file_obj):
    file_obj.seek(0)
    section = None
    chosen = {}
    for line in file_obj:
        if line.startswith("#"):
            continue
        sect = section_start.match(line)
        if sect:
            section = sect.group(1)
            chosen[section] = {}
            continue
        parsed = parse_line(line, section)
        if parsed is not None:
            if section is None:
                chosen.update(parsed)
            else:
                chosen[section].update(parsed[section])
    return chosen
