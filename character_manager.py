from collections import namedtuple
#from dataclasses import dataclass
import logging
from pathlib import Path
import re

logger = logging.getLogger(__name__)

MOE_DIRECTORY_DEFAULT_PATH = r"C:/MOE/Master of Epic"
MOE_USERDATA_DEFAULT_PATH = r"userdata"

#@dataclass(frozen=True)
#class CharacterDirectory :
#    filepath: Path
#    server: str
#    name: str

CharacterDirectory  = namedtuple("CharacterDirectory", ["filepath", "server", "name"])

def normalize_name(name):
    """
    フォルダ名に含まれる.を除去してキャラクター名に変換する
    ゲーム側の仕様で、英大文字が含まれるキャラクター名の場合は
    ディレクトリ名において英大文字の直後にドットがついている

    >>> normalize_name("T.est")
    'Test'
    """
    normalized = name.replace('.', '')
    return normalized

def extract_character_server_and_name(directory_name):
    """
    キャラクタ毎のディレクトリ名からサーバ名とキャラクター名を抽出する

    >>> extract_character_server_and_name("DIAMOND_P.layerN.ame_")
    ('DIAMOND', 'PlayerName')
    """
    m = re.match(r"^(?P<server>(DIAMOND)|(EMERALD)|(PEARL))_(?P<name>.+)_", directory_name)
    if not m:
        return (None, None)
    server = m.group("server")
    name = normalize_name(m.group("name"))
    return (server, name)

def get_character_list(directory_path=MOE_DIRECTORY_DEFAULT_PATH, userdata_path=MOE_USERDATA_DEFAULT_PATH):
    cl = []
    try:
        p = Path(directory_path, userdata_path)

        for subdir in p.iterdir():
            if not subdir.is_dir():
                continue
            (server, name) = extract_character_server_and_name(subdir.name)
            if server and name:
                cl.append(CharacterDirectory(subdir, server, name))

    except Exception as e:
        # エラーは記録するが、処理を継続するために意図的に握りつぶす
        logger.error(e)
    finally:
        pass

    return cl

if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
