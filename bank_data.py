#!/usr/bin/env python3
import csv
import re
import sys
import datetime

class DataEntry:
    def __init__(self):
        pass

class EntryManager:
    def __init__(self):
        self._manager = []

    @property
    def manager(self) -> list:
        return self._manager

class BankDataEntry(DataEntry):
    def __init__(self, log_date: str, log_time: str, quest_name: str, finished: str, plus: int):
        super().__init__()
        self._log_date = datetime.date.fromisoformat("20" + log_date.replace('/', '-'))
        self._log_time = datetime.time.fromisoformat(log_time)
        self._quest_name = quest_name
        self._finished = finished
        self._plus = plus

    @property
    def log_date(self) -> datetime.date:
        return self._log_date

    @property
    def log_time(self) -> datetime.time:
        return self._log_time

    @property
    def quest_name(self) -> str:
        return self._quest_name

    @property
    def finished(self) -> str:
        return self._finished

    @property
    def plus(self) -> int:
        return self._plus

class BankEntryManager(EntryManager):
    def __init__(self):
        super().__init__()

    def update_entry(self, entry: BankDataEntry) -> bool:
        for i in range(0, len(self._manager)):
            e = self._manager[i]
            if e.quest_name == entry.quest_name:
                if e.log_time < entry.log_time:
                    print("update {} {} -> {} : {} -> {}".format(e.quest_name, e.finished, entry.finished, e.log_time, entry.log_time))
                    self._manager[i] = entry
                    return True
                else:
                    return False
            else:
                continue

        self._manager.append(entry)
        return False

class LogConverter:
    def __init__(self, parser):
        self._parser = parser

    def convert(self, logfile) -> list[DataEntry]:
        entry_manager = BankEntryManager()
        for log in logfile:
            entry = self._parser.create_entry(log)
            if entry is not None:
                entry_manager.update_entry(entry)
        return entry_manager.manager

class Parser:
    def __init__(self, pattern: str):
        self._pattern = re.compile(pattern)

    def create_entry(self) -> DataEntry:
        pass

class BankParser(Parser):
    def __init__(self):
        date_pattern = r"^(?P<yymmdd>[0-9]{2}/[0-9]{2}/[0-9]{2}) (?P<hhmmss>[0-9]{2}:[0-9]{2}:[0-9]{2})"
        quest_pattern = r": \[ (?P<finish>.) \] (?P<quest_name>.+) : \+ (?P<plus>[0-9])$"
        super().__init__(''.join((date_pattern, quest_pattern)))

    def create_entry(self, line: str) -> BankDataEntry:
        m = self._pattern.match(line)
        if m is None:
            return None
        return BankDataEntry(m.group("yymmdd"), m.group("hhmmss"), m.group("quest_name"), m.group("finish"), m.group("plus"))


if __name__ == "__main__":
    input_filename = "mlog_25_03_15_0.txt"
    converter = LogConverter(BankParser())
    with open(input_filename, "r", encoding="utf-8") as logfile:
        data = converter.convert(logfile)

    output_filename = "mlog_25_03_15_0.csv"
    with open(output_filename, "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        for entry in data:
            writer.writerow((entry.quest_name, entry.finished))
