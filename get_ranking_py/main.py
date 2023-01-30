# -*- coding: utf-8 -*-

import sys
import os
import csv
from argparse import ArgumentParser, Namespace
from collections import defaultdict
from typing import List, Dict, Tuple

def main():
    try:
        # コマンドライン引数からcsvファイルパスを取得
        csv_file_path: str = get_file_path()

        # csvファイルパスから「プレイヤーID」毎に「スコア」「プレイ回数」を集計
        scores: Dict[str, List[int]] = summarize_csv_scores(csv_file_path)

        # 集計後のスコアから「プレイヤーID」毎の「平均スコア」を算出
        avarage_scores: Dict[str, int] = get_average(scores)

        # 「プレイヤーID」毎の「平均スコア」からランキング（10位以内）を算出
        ranked_average = get_ranked_average(avarage_scores, 10)

        # 「平均スコア」によるランキングを標準出力
        print_ranked_average(ranked_average)
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
    :returns result: 「プレイヤーID」毎の「平均スコア」を算出した辞書
    :rtype: Dict[str, int]
    """
    result: Dict[str, int] = {}

    for player_id, (total_score, count) in scores.items():
        result[player_id] = round(total_score / count)

    return result

def get_ranked_average(avg_scores: Dict[str, int], rank_limit: int) -> List[Tuple[int, str, int]]:
    """「プレイヤーID」毎の「平均スコア」からランキング（10位以内）を算出

    :param avg_scores: 「プレイヤーID」毎の「平均スコア」を算出した辞書
    :type avg_scores: Dict[str, int]
    :param max_rank: 算出するランクの上限値
    :type max_rank: int
    :returns result: 「平均スコア」によるランキング（降順）をプレイヤー単位（昇順）で格納したタプル
    :rtype: List[Tuple[int, str, int]]
    """
    result: List[Tuple[int, str, int]] = []
    rank: int = 1
    ranked_scores: List[Tuple[str, int]] = sorted(avg_scores.items(), key=lambda x: (-x[1], x[0]))

    for i, (player_id, avg_score) in enumerate(ranked_scores):
        if i > 0 and avg_score < ranked_scores[i - 1][1]:
            rank = i + 1
        if rank_limit < rank:  # ランクの上限値を超えた場合に抜ける
            break
        result.append((rank, player_id, avg_score))

    return result

def print_ranked_average(ranked_average: List[Tuple[int, str, int]]) -> None:
    """「平均スコア」によるランキングを標準出力

    :param ranked_average: 「平均スコア」によるランキングをプレイヤー単位で格納したタプル
    :type ranked_average: List[Tuple[int, str, int]]
    """
    print("rank,player_id,mean_score")  # ヘッダ項目を標準出力

    for rank, player_id, avg_score in ranked_average:
        print(f"{rank},{player_id},{avg_score}")


if __name__ == "__main__":
    main()

