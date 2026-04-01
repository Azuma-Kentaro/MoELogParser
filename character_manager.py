from collections import namedtuple
#from dataclasses import dataclass
import logging
from pathlib import Path
import re

logger = logging.getLogger(__name__)

MOE_DIRECTORY_DEFAULT_PATH = r"C:/MOE/Master of Epic"
MOE_USERDATA_DEFAULT_PATH = r"userdata"

#@dataclass(frozen=True)
#class CharacterDirectroy:
#    filepath: Path
#    server: str
#    name: str

CharacterDirectroy = namedtuple("CharacterDirectroy", ["filepath", "server", "name"])

class MoECharacterManager:
    def __init__(self, direcotry_path, userdata_path):
        self._character_list = []
        self._directory_path = direcotry_path
        self._userdata_path = userdata_path

    @staticmethod
    def normalize_name(name):
        """フォルダ名に含まれる.を除去してキャラクター名に変換する"""
        """ゲーム側の仕様で、英大文字が含まれるキャラクター名の場合は"""
        """ディレクトリ名において英大文字の直後にドットがついている"""
        normalized = name.replace('.', '')
        return normalized

    @staticmethod
    def extract_character_server_and_name(directory_name):
        """キャラクタ毎のディレクトリ名からサーバ名とキャラクター名を抽出する"""
        m = re.match(r"^(?P<server>(DIAMOND)|(EMERALD)|(PEARL))_(?P<name>.+)_", directory_name)
        if not m:
            return (None, None)
        server = m.group("server")
        name = MoECharacterManager.normalize_name(m.group("name"))
        return (server, name)

    def get_character_list(self):
        try:
            p = Path(self._directory_path, self._userdata_path)

            for subdir in p.iterdir():
                (server, name) = MoECharacterManager.extract_character_server_and_name(subdir.name)
                if server and name:
                    self._character_list.append(CharacterDirectroy(subdir, server, name))

        except Exception as e:
            logger.error(e)
        finally:
            pass

        return self._character_list

def get_character_list(direcotry_path=MOE_DIRECTORY_DEFAULT_PATH, userdata_path=MOE_USERDATA_DEFAULT_PATH):
    m = MoECharacterManager(direcotry_path, userdata_path)
    character_list = m.get_character_list()
    return character_list

if __name__ == "__main__":
    # 動作確認のため、DEBUGレベルのログ出力を有効にする。
    logging.basicConfig(level=logging.DEBUG)

    character_list = get_character_list()
    print(f"{character_list=}")