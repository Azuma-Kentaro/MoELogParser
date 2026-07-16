#!/usr/bin/env python3

import csv
from dataclasses import dataclass
import datetime
import logging
import re

logger = logging.getLogger(__name__)

@dataclass(frozen=True, order=True)
class BankDataEntry:
    log_date: datetime.date
    log_time: datetime.time
    quest_name: str
    finished: str
    plus: str

def update_entry(entry_list, new_entry):
    """
    所持枠拡張クエストのクリア状況に関するエントリを更新する
    同じ所持枠拡張クエストに関するエントリが重複した場合には最新のエントリで置き換える
    既存エントリを更新した場合はTrueを返し、そうでない場合はFalseを返す
    """
    updated = False
    for i, existing_entry in enumerate(entry_list):
        # クエスト名が違うので次のエントリに対する試行を開始する
        if existing_entry.quest_name != new_entry.quest_name:
            continue
        # 既存エントリの方が日付が新しい場合は最新のエントリで置き換える
        if existing_entry <= new_entry:
            logger.debug(f"update {existing_entry.quest_name} {existing_entry.finished} {existing_entry.log_date} {existing_entry.log_time} -> {new_entry.finished} {new_entry.log_date} {new_entry.log_time}")
            entry_list[i] = new_entry
            updated = True
        # 同じクエスト名のエントリは重複しないので、置き換えたか否かに関係なくループを終了する
        break
    else:
        # break以外でループが終わった場合は、同じクエスト名のエントリが存在しなかった場合なので
        # 新しいエントリとして、リストに追加する
        logger.debug(f"new {new_entry.quest_name} {new_entry.finished} {new_entry.log_date} {new_entry.log_time}")
        entry_list.append(new_entry)
    return updated

# 複数の行に対して同じ正規表現を適用するので、コンパイル済みのパターンを用いて効率化する。
# 日付部分は所持枠拡張以外にも共通のパターンなので、他の処理にも流用できる。
date_pattern = r"^(?P<yymmdd>[0-9]{2}/[0-9]{2}/[0-9]{2}) (?P<hhmmss>[0-9]{2}:[0-9]{2}:[0-9]{2})"
# 所持枠拡張クエストのパターン
quest_pattern = r": \[ (?P<finish>.) \] (?P<quest_name>.+) : \+ (?P<plus>[0-9])$"
# どちらも同じ行に表示されるので、1つの行に対して処理するために結合する。
bank_pattern = re.compile(''.join((date_pattern, quest_pattern)))

def create_entry(line):
    """
    与えられた行データが所持枠拡張クエストに関するものであれば、データ化したエントリ情報を返す
    """
    m = bank_pattern.match(line)
    if m is None:
        return None

    log_date = datetime.date.fromisoformat("20" + m.group("yymmdd").replace('/', '-'))
    log_time = datetime.time.fromisoformat(m.group("hhmmss"))
    quest_name = m.group("quest_name")
    finished = m.group("finish")
    plus = m.group("plus")

    return BankDataEntry(log_date, log_time, quest_name, finished, plus)

def convert_log_to_entries(log_list):
    """
    ログファイルのテキストに対して所持枠拡張クエストの情報をエントリとして抽出する
    """
    # 作業過程で抽出したデータの管理はエントリマネージャに任せる
    # 最終的な結果だけが必要なので、関数終了時に破棄されるようにローカル変数としている
    entry_list = []
    for log in log_list:
        # 所持枠拡張クエストのエントリとして抽出を試みる
        new_entry = create_entry(log)
        if new_entry:
            # 新規エントリなら追加、重複なら最新のエントリだけ残す
            update_entry(entry_list, new_entry)

    # 最終的なエントリ情報を返して処理を終了する
    return entry_list

def get_bank_data(filename):
    # ゲームの仕様で、生成するファイルのエンコーディングはShift JIS
    with open(filename, "r", encoding="shift-jis") as logfile:
        bank_entries = convert_log_to_entries(logfile)
    return bank_entries

if __name__ == "__main__":
    # テスト用の入力ファイル
    input_filename = "mlog_26_04_01_0.txt"
    bank_entries = get_bank_data(input_filename)

    # テスト用の出力ファイル
    output_filename = "mlog_26_04_01_0.csv"
    with open(output_filename, "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        for entry in bank_entries:
            writer.writerow((entry.quest_name, entry.finished, entry.log_date, entry.log_time))
