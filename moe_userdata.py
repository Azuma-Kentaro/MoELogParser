
from pathlib import Path
import datetime
import re
import sys

import numpy as np
import pandas as pd

from bank_data import * 

class MessageLogInfo:
    def __init__(self, mlog_date: str, mlog_num: int):
        self._mlog_date = mlog_date
        self._mlog_num = mlog_num
        self._bank_data = None

    @property
    def mlog_date(self) -> str:
        return self._mlog_date

    @property
    def mlog_num(self) -> int:
        return self._mlog_min

    @property
    def filename(self) -> str:
        return "mlog_{}_{}.txt".format(self._mlog_date, self._mlog_num)

    @property
    def bank_data(self) -> list[BankDataEntry]:
        return self._bank_data

    @bank_data.setter
    def bank_data(self, data: list[BankDataEntry]) -> None:
        self._bank_data = data

class PlayerData:
    def __init__(self, server: str, name: str):
        self._server = server
        self._name = name.replace('.', '')
        self._mlog_info = None

    @property
    def server(self) -> str:
        return self._server

    @property
    def name(self) -> str:
        return self._name

    @property
    def mlog_info(self) -> MessageLogInfo:
        return self._mlog_info

    @mlog_info.setter
    def mlog_info(self, mlog_info: MessageLogInfo) -> None:
        self._mlog_info = mlog_info


def createPlayerData(path: Path) -> PlayerData:
    if not path.is_dir():
        return None

    match_player_dir = re.match(r"^(?P<server>(DIAMOND)|(EMERALD)|(PEARL))_(?P<name>.+)_", path.name)
    if not match_player_dir:
        return None

    player = PlayerData(match_player_dir.group("server"), match_player_dir.group("name"))
    for child in path.iterdir():
        mlog_info = extract_message_log(child)
        if mlog_info is not None:
            player.mlog_info = mlog_info
    return player

def extract_message_log(path: Path) -> MessageLogInfo:
    if not path.is_file():
        return None

    match_mlog_file = re.match(r"^mlog_(?P<yy_mm_dd>[0-9]{2}_[0-9]{2}_[0-9]{2})_(?P<num>[0-9]+)\.txt", path.name)
    if not match_mlog_file:
        return None

    mlog_info = MessageLogInfo(match_mlog_file.group("yy_mm_dd"), match_mlog_file.group("num"))

    converter = LogConverter(BankParser())
    with path.open("r", encoding="shift-jis") as logfile:
        bank_data = converter.convert(logfile)

        # bank data not found
        if len(bank_data):
            mlog_info.bank_data = bank_data

    return mlog_info


if __name__ == "__main__":
    userdata_path = Path("C:/MOE/Master of Epic/userdata")
    if userdata_path.exists() and userdata_path.is_dir():
        print("directory {} exists".format(userdata_path))
    else:
        print("directory {} not found".format(userdata_path))
        sys.exit(1)

    all_data = {}
    for child in userdata_path.iterdir():
        player = createPlayerData(child)
        if player is not None:
            #print("Player {} found on {}".format(player.name, player.server))
            if player.mlog_info is not None:
                #print("{} found".format(player.mlog_info.filename))
                if player.mlog_info.bank_data is not None:
                    #print("{} {} {} bank data found".format(player.server, player.name, player.mlog_info.filename))
                    quest_dict = {}
                    for entry in player.mlog_info.bank_data:
                        #print("{} {}".format(entry.quest_name, entry.finished))
                        quest_dict[entry.quest_name]= entry.finished
                    all_data[player.name] = (quest_dict)
    output_filename = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".csv"
    df = pd.DataFrame(all_data)
    df.to_csv(output_filename, encoding="shift-jis")
