#!/usr/bin/env python3
"""vocab-trainer —— 命令行背单词小工具。

按艾宾浩斯遗忘曲线安排复习:答对一次,复习间隔就拉长一档
(1 → 2 → 4 → 7 → 15 → 30 天,最后答对即毕业);答错或模糊则明天再看。
进度保存在本目录的 progress.json 里。

用法:
  python trainer.py add <单词> <意思>      添加一个单词,如:python trainer.py add apple n.苹果
  python trainer.py import <词表.csv>      批量导入,CSV 每行格式:单词,意思
  python trainer.py review                 复习今天到期的单词
  python trainer.py today                  看看今天该复习哪些
  python trainer.py stats                  查看整体进度
"""

import argparse
import csv
import json
import sys
from datetime import date, timedelta
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "progress.json"

# 复习间隔档位(天):第 0 档是新词,答对升一档;最后一档答对就毕业
INTERVALS = [1, 2, 4, 7, 15, 30]
GRADUATED = len(INTERVALS)


def load_data() -> dict:
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return {"words": []}


def save_data(data: dict) -> None:
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def find(data: dict, word: str):
    for rec in data["words"]:
        if rec["word"] == word:
            return rec
    return None


def new_record(word: str, meaning: str, today: date) -> dict:
    return {
        "word": word,
        "meaning": meaning,
        "stage": 0,
        "due": (today + timedelta(days=INTERVALS[0])).isoformat(),
        "learned": today.isoformat(),
        "right": 0,
        "wrong": 0,
    }


def due_words(data: dict, today: date) -> list:
    t = today.isoformat()
    return sorted(
        (r for r in data["words"] if r["due"] is not None and r["due"] <= t),
        key=lambda r: (r["due"], r["word"]),
    )


def cmd_add(args) -> None:
    data = load_data()
    rec = find(data, args.word)
    if rec:
        rec["meaning"] = args.meaning
        print(f"已更新「{args.word}」的意思(学习进度保留)。")
    else:
        data["words"].append(new_record(args.word, args.meaning, date.today()))
        print(f"已添加「{args.word}」,明天开始安排第一次复习。")
    save_data(data)


def cmd_import(args) -> None:
    data = load_data()
    today = date.today()
    added = updated = skipped = 0
    # utf-8-sig 兼容带 BOM 的文件(用 Excel 另存的 CSV 常带 BOM)
    with open(args.file, encoding="utf-8-sig", newline="") as f:
        for row in csv.reader(f):
            if not row or not row[0].strip():
                continue
            if len(row) < 2 or not row[1].strip():
                skipped += 1
                continue
            word = row[0].strip()
            meaning = ",".join(x.strip() for x in row[1:])
            rec = find(data, word)
            if rec:
                rec["meaning"] = meaning
                updated += 1
            else:
                data["words"].append(new_record(word, meaning, today))
                added += 1
    save_data(data)
    print(f"导入完成:新增 {added} 个,更新 {updated} 个,跳过 {skipped} 行格式有问题的。")


def cmd_review(args) -> None:
    data = load_data()
    today = date.today()
    queue = due_words(data, today)
    if not queue:
        print("今天没有到期的单词,休息一下 ☕")
        return
    print(f"今天要复习 {len(queue)} 个单词。按 Ctrl+C 可随时退出,进度会保存。")
    for i, rec in enumerate(queue, 1):
        print(f"\n[{i}/{len(queue)}] {rec['word']}")
        input("  想好意思后按回车看答案 > ")
        print(f"  → {rec['meaning']}")
        while True:
            ans = input("  认识吗? 1=认识  2=模糊  3=不认识 > ").strip()
            if ans in ("1", "2", "3"):
                break
            print("  请输入 1、2 或 3")
        if ans == "1":
            rec["right"] += 1
            if rec["stage"] >= len(INTERVALS) - 1:
                rec["stage"] = GRADUATED
                rec["due"] = None
                save_data(data)
                print("  ✓ 太棒了,这个词毕业了!🎓")
                continue
            rec["stage"] += 1
            rec["due"] = (today + timedelta(days=INTERVALS[rec["stage"]])).isoformat()
            print(f"  ✓ 认识:下次复习 {rec['due']}")
        elif ans == "2":
            rec["due"] = (today + timedelta(days=1)).isoformat()
            print(f"  - 模糊:明天再看一次({rec['due']})")
        else:
            rec["wrong"] += 1
            rec["stage"] = 0
            rec["due"] = (today + timedelta(days=1)).isoformat()
            print(f"  ✗ 没关系,明天从头再来({rec['due']})")
        save_data(data)
    print("\n今日复习完成,坚持就是胜利 💪")


def cmd_today(args) -> None:
    queue = due_words(load_data(), date.today())
    if not queue:
        print("今天没有到期的单词。")
        return
    print(f"今天该复习 {len(queue)} 个单词:")
    for rec in queue:
        print(f"  {rec['word']:<20} {rec['meaning']}  (第{rec['stage'] + 1}档)")
    print("运行 `python trainer.py review` 开始。")


def cmd_stats(args) -> None:
    data = load_data()
    words = data["words"]
    graduated = sum(1 for r in words if r["stage"] >= GRADUATED)
    due = len(due_words(data, date.today()))
    print(f"词库共 {len(words)} 个单词:已毕业 {graduated} | 学习中 {len(words) - graduated}")
    if due:
        print(f"今日到期 {due} 个 —— 运行 `python trainer.py review` 开始!")
    names = [f"第{i + 1}档({INTERVALS[i]}天)" for i in range(len(INTERVALS))] + ["已毕业"]
    for i, name in enumerate(names):
        n = sum(1 for r in words if r["stage"] == i)
        if n:
            print(f"  {name}: {n} 个")


def main() -> None:
    parser = argparse.ArgumentParser(description="按艾宾浩斯遗忘曲线背单词的命令行小工具")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("add", help="添加一个单词")
    p.add_argument("word", help="单词")
    p.add_argument("meaning", help="意思,如:n.苹果")
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("import", help="批量导入 CSV(每行:单词,意思)")
    p.add_argument("file", help="CSV 文件路径")
    p.set_defaults(func=cmd_import)

    p = sub.add_parser("review", help="复习今天到期的单词")
    p.set_defaults(func=cmd_review)

    p = sub.add_parser("today", help="看看今天该复习哪些")
    p.set_defaults(func=cmd_today)

    p = sub.add_parser("stats", help="查看整体进度")
    p.set_defaults(func=cmd_stats)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n已退出,进度已保存。")
