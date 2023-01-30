# -*- coding: utf-8 -*-

import sys
import os
from argparse import ArgumentParser, Namespace
from collections import defaultdict
import itertools
from itertools import groupby
import csv
from typing import List, Dict, Iterator

class MeanGroup:
    """「平均スコア」毎に「プレイヤーID」をグルーピング

    :param mean_score: 平均スコア
    :type mean_score: int
    :param player_ids: プレイヤーID群
    :type player_ids: list[str]
    """
    def __init__(self, mean_score: int, player_ids: list[str]):
        self.score: int = mean_score
        self.player_ids: list[str] = player_ids


def main() -> None:
    try:
        # コマンドライン引数からcsvファイルパスを取得
        csv_file_path: str = get_file_path()

        # csvファイルパスから「プレイヤーID」毎に「スコア」「プレイ回数」を集計
        scores: Dict[str, List[int]] = summarize_csv_scores(csv_file_path)

        # 集計後のスコアから「プレイヤーID」毎の「平均スコア」を算出
        avarage_scores: Dict[str, int] = get_average(scores)

        # 「平均スコア」算出後のプレイログから「平均スコア」によるランキング（10位以内）を算出
        rank_playlog: Dict[int, MeanGroup] = rank_dict(avarage_scores, 10)

        # 「平均スコア」によるランキングを標準出力
        print_playlog(rank_playlog)
    except Exception as e:
        print(e)
        exit(1)


def get_file_path() -> str:
    """コマンドライン引数からcsvファイルパスを取得

    :returns file_path: csvファイルパス
    :rtype: str
    """
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument("file", help="csvファイルのパス")
    args: Namespace = parser.parse_args()
    file_path: str = args.file

    if not file_path.endswith('.csv'):
        raise Exception("Error: 入力されたファイルはcsvファイルではありません。")

    return file_path

def summarize_csv_scores(file_path: str) -> Dict[str, List[int]]:
    """csvファイルパスから「プレイヤーID」毎に「スコア」「プレイ回数」を集計

    :param file_path: csvファイルパス
    :type file_path: str
    :returns result: 「プレイヤーID」毎に「スコア」「プレイ回数」を集計した辞書
    :rtype: Dict[str, List[int]]
    """
    result: Dict[str, List[int]] = defaultdict(lambda: [0, 0])

    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # headerの読み飛ばし
        for row in reader:
            create_timestamp, player_id, score = row
            result[player_id][0] += int(score)
            result[player_id][1] += 1

    return result

def get_average(scores: Dict[str, List[int]]) -> Dict[str, int]:
    """集計後のスコアから「プレイヤーID」毎の「平均スコア」を算出

    :param scores: 「プレイヤーID」毎に「スコア」「プレイ」回数を集計した辞書
    :type scores: Dict[str, List[int]]
    :returns result: 「プレイヤーID」毎の平均スコアを算出した辞書
    :rtype: Dict[str, int]
    """
    avg_scores: Dict[str, int] = {}

    for player_id, (total_score, count) in scores.items():
        avg_scores[player_id] = round(total_score / count)

    return avg_scores

def rank_dict(mean_playlog: Dict[str, int], max_rank: int) -> Dict[int, MeanGroup]:
    """「平均スコア」算出後のプレイログから「平均スコア」によるランキングを算出

    :param mean_playlog: プレイヤー毎に「平均スコア」が算出されたプレイログ
    :type mean_playlog: Dict[str, int]
    :param max_rank: 算出するランクの上限値
    :type max_rank: int
    :returns result: 「平均スコア」によるランク毎にプレイヤー情報をマップした辞書
    :rtype: Dict[int, MeanGroup]
    """
    # ランクをキー・平均グループオブジェクト（平均スコア・プレイヤーID郡）をバリューとした辞書型
    rank: int = 1
    result: Dict[int, MeanGroup] = {}

    # 「平均スコア」を降順で取得
    desc_mean_playlog: list[tuple[str, int]] = sorted(mean_playlog.items(), reverse=True, key=lambda x: x[1])
    # 「平均スコア」毎にグルーピング
    groupby_mean_playlog: groupby[int, tuple[str, int]] = itertools.groupby(desc_mean_playlog, lambda x: x[1])

    for mean_score, player_id_score in groupby_mean_playlog:
        mean_score: int
        player_id_score: Iterator[tuple[str, int]]

        # ランクの上限値を超えた場合に抜ける
        if max_rank < rank:
            break

        # 「平均スコア」でグルーピングされた「プレイヤーID」郡をリストで取得
        player_ids: list[str] = list(map(lambda x: x[0], list(player_id_score)))
        # ランクをキーにランクオブジェクト（平均スコア・プレイヤーID郡）をセット
        result[rank] = MeanGroup(mean_score, player_ids)
        # プレイヤー数分、ランクをインクリメント（同スコアが複数人の場合を考慮）
        rank += len(player_ids)

    return result

def print_playlog(rank_playlog: Dict[int, MeanGroup]) -> None:
    """「平均スコア」によるランキングを標準出力

    :param rank_playlog: 「平均スコア」によるランキング
    :type rank_playlog: Dict[int, MeanGroup]
    """
    # ヘッダ項目を標準出力
    print("rank,player_id,mean_score")

    for (rank, mean_group_obj) in rank_playlog.items():
        rank: int
        mean_group_obj: MeanGroup

        # 「プレイヤーID」を昇順で取得
        asc_player_ids: list[str] = sorted(mean_group_obj.player_ids)
        # 同順位のプレイヤーの「ランク」「プレイヤーID」「平均スコア」を出力
        for player_id in asc_player_ids:
            player_id: str

            print(f"{rank},{player_id},{mean_group_obj.score}")


if __name__ == "__main__":
    main()

