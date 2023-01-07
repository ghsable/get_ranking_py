# -*- coding: utf-8 -*-

import sys
import os
import itertools
import csv
from csv import DictReader
from typing import Dict, Iterator, List

class PlayLog:
    """各プレイヤーの「合計プレイ回数」「合計スコア」を保持

    """
    def __init__(self) -> None:
        self.sum_play: int = 0
        self.sum_score: int = 0

    def add(self, score: int) -> None:
        """各プレイヤーの「プレイ回数」「スコア」を加算

        :param score: 加算するスコア
        :type score: int
        """
        self.sum_play += 1
        self.sum_score += score

    def get_mean(self) -> int:
        """各プレイヤーの「平均スコア」（四捨五入）を算出

        """
        return round(self.sum_score / self.sum_play)

class Rank:
    """「平均スコア」毎に「プレイヤーID」をグルーピング

    :param mean_score: 平均スコア
    :type mean_score: int
    :param player_ids: プレイヤーID群
    :type player_ids: List[str]
    """
    def __init__(self, mean_score: int, player_ids: List[str]):
        self.score: int = mean_score
        self.player_ids: List[str] = player_ids


def main() -> None:
    try:
        # コマンドライン引数のバリデーションチェック
        validate_argv(get_args(), 2)

        # ファイルパスのバリデーションチェック
        validate_filepath(get_filepath(get_args()))

        # ファイルパスから「プレイヤーID」毎にスコアを集計・取得
        groupby_playlog: Dict[str, PlayLog] = groupby_csv(get_filepath(get_args()))

        # 集計後のプレイログから「平均スコア」を算出
        mean_playlog: Dict[str, int] = mean_dict(groupby_playlog)

        # 「平均スコア」算出後のプレイログから「平均スコア」によるランキング（10位以内）を算出
        rank_playlog: Dict[int, Rank] = rank_dict(mean_playlog, 10)

        # 「平均スコア」によるランキングを標準出力
        print_playlog(rank_playlog)
    except Exception as e:
        print(e)


def get_args() -> list[str]:
    """コマンドライン引数を取得

    """
    return sys.argv

def validate_argv(args: list[str], max_length: int) -> None:
    """コマンドライン引数のバリデーションチェック

    :param args: コマンドライン引数
    :type args: list[str]
    :param max_length: コマンドライン引数の最大件数
    :type max_length: int
    """
    if len(args) < max_length:
        raise Exception('more arguments needed')
    if len(args) > max_length:
        raise Exception('too many arguments')

def get_filepath(args: list[str]) -> str:
    """コマンドライン引数からファイルパスを取得

    :param args: コマンドライン引数
    :type args: list[str]
    """
    return args[1]

def validate_filepath(filepath: str) -> None:
    """ファイルパスのバリデーションチェック

    :param filepath: ファイルパス
    :type filepath: str
    """
    if not os.path.isfile(filepath):
        raise Exception('no such file')
    if not os.path.splitext(filepath)[1] == ".csv":
        raise Exception('not a csv file')

def groupby_csv(filepath: str) -> Dict[str, PlayLog]:
    """ファイルパスから「プレイヤーID」毎にスコアを集計・取得

    :param filepath: ファイルパス
    :type filepath: str
    """
    result: Dict[str, PlayLog] = {}

    with open(filepath, 'r') as csv_file:
        reader: DictReader = csv.DictReader(csv_file, lineterminator="\n")
        for row in reader:
            row: Dict[str, str]

            # 「プレイヤーID」「スコア」を取得
            player_id = row['player_id']
            score = int(row['score'])
            # 初めてヒットしたプレイヤーのプレイログを初期化
            if player_id not in result:
                result[player_id] = PlayLog()
            # プレイヤーのプレイログを加算
            result[player_id].add(score)

    return result

def mean_dict(groupby_playlog: Dict[str, PlayLog]) -> Dict[str, int]:
    """集計後のプレイログから「平均スコア」を算出

    :param groupby_playlog: プレイヤー毎に「スコア」が集計されたプレイログ
    :type groupby_playlog: Dict[str, PlayLog]
    """
    result: Dict[str, int] = {}

    for player_id, playlog_obj in groupby_playlog.items():
        player_id: str
        playlog_obj: PlayLog

        result[player_id] = playlog_obj.get_mean()

    return result

def rank_dict(mean_playlog: Dict[str, int], max_rank: int) -> Dict[int, Rank]:
    """「平均スコア」算出後のプレイログから「平均スコア」によるランキングを算出

    :param mean_playlog: プレイヤー毎に「平均スコア」が算出されたプレイログ
    :type mean_playlog: Dict[str, int]
    :param max_rank: 算出するランクの上限値
    :type max_rank: int
    """
    # ランクをキー・ランクオブジェクト（平均スコア・プレイヤーID郡）をバリューとした辞書型
    rank: int = 1
    result: Dict[int, Rank] = {}

    # 「平均スコア」を降順で取得
    desc_mean_playlog = sorted(mean_playlog.items(), reverse=True, key=lambda x: x[1])
    # 「平均スコア」毎にグルーピング
    groupby_mean_playlog = itertools.groupby(desc_mean_playlog, lambda x: x[1])

    for mean_score, player_id_score in groupby_mean_playlog:
        mean_score: int
        player_id_score: Iterator[tuple[str, int]]

        # ランクの上限値を超えた場合に抜ける
        if max_rank < rank:
            break

        # 「平均スコア」でグルーピングされた「プレイヤーID」郡をリストで取得
        player_ids = list(map(lambda x: x[0], list(player_id_score)))
        # ランクをキーにランクオブジェクト（平均スコア・プレイヤーID郡）をセット
        result[rank] = Rank(mean_score, player_ids)
        # プレイヤー数分、ランクをインクリメント（同スコアが複数人の場合を考慮）
        rank += len(player_ids)

    return result

def print_playlog(rank_playlog: Dict[int, Rank]) -> None:
    """「平均スコア」によるランキングを標準出力

    :param rank_playlog: 「平均スコア」によるランキング
    :type rank_playlog: Dict[int, Rank]
    """
    # ヘッダ項目を標準出力
    print("rank,player_id,mean_score")

    for (rank, rank_obj) in rank_playlog.items():
        rank: int
        rank_obj: Rank

        # 「プレイヤーID」を昇順で取得
        asc_player_ids = sorted(rank_obj.player_ids)
        # 同順位のプレイヤーの「ランク」「プレイヤーID」「平均スコア」を出力
        for player_id in asc_player_ids:
            player_id: str

            print(f"{rank},{player_id},{rank_obj.score}")


if __name__ == "__main__":
    main()

