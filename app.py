
import datetime
import logging
import re

import pandas as pd

from bank_data import get_bank_data
from character_manager import get_character_list

logger = logging.getLogger(__name__)

def is_mlog(filename):
    """filenameがmlogの命名規則を満たしているか確認する"""
    m = re.match(r"^mlog_(?P<yy_mm_dd>[0-9]{2}_[0-9]{2}_[0-9]{2})_(?P<num>[0-9]+)\.txt", filename)
    return True if m else False

def find_mlog(path):
    """指定されたディレクトリ内にあるmlogファイルをリスト化する"""
    mlog_list = []
    for child in path.iterdir():
        # ファイルではない
        if not child.is_file():
            continue

        # ファイル名がmlogの命名規則に従っていない
        if not is_mlog(child.name):
            continue

        mlog_list.append(child)
    return mlog_list

def merge_bank_entries(target_dict, bank_data):
    for bd in bank_data:
        current_data = target_dict.get(bd.quest_name, None)
        if current_data:
            if (current_data.log_date <= bd.log_date) and (current_data.log_time < bd.log_time):
                logger.debug(f"update {current_data.quest_name} {current_data.finished} {current_data.log_date} {current_data.log_time} -> {bd.finished} {bd.log_date} {bd.log_time}")
                current_data = bd
        else:
            # 同じクエスト名のエントリが存在しなかった場合は新しいエントリとして追加する
            logger.debug(f"new {bd.quest_name} {bd.finished} {bd.log_date} {bd.log_time}")
            target_dict[bd.quest_name] = bd

def app_main():
    all_data = {}
    # インストールパスに変更を加えている場合は引数で指定することで対応可能
    cl = get_character_list()
    for chara in cl:
        chara_data = {}
        mlog_list = find_mlog(chara.filepath)
        if not mlog_list:
            logger.info(f"No mlog found for {chara.server} {chara.name}")
            continue
        
        for mlog in mlog_list:
            bank_entries = get_bank_data(chara.filepath / mlog)
            if bank_entries:
                merge_bank_entries(chara_data, bank_entries)

        all_data[chara.name] = {cd.quest_name: cd.finished for cd in chara_data.values()}

    output_filename = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".csv"
    df = pd.DataFrame.from_dict(all_data)
    df.to_csv(output_filename, encoding="shift-jis")

if __name__ == "__main__":
    # 動作確認のため、DEBUGレベルのログ出力を有効にする。
    logging.basicConfig(level=logging.DEBUG)

    app_main()
