# vocab-trainer 📚

命令行背单词小工具:按艾宾浩斯遗忘曲线,每天自动安排该复习的单词。
A command-line vocabulary trainer that schedules daily reviews with spaced repetition (Ebbinghaus intervals).

## 功能 / Features

- 添加单词、批量导入词表(CSV)/ Add words one by one, or import a CSV list
- 每天列出到期单词;按「认识 / 模糊 / 不认识」反馈决定下次复习时间
  / A daily review queue; your feedback (known / fuzzy / forgot) decides each word's next interval
- 答对间隔逐级拉长:1 → 2 → 4 → 7 → 15 → 30 天,全部通过即「毕业」
  / Intervals grow 1 → 2 → 4 → 7 → 15 → 30 days; words "graduate" after the final review
- 进度统计 / Progress stats
- 纯 Python 标准库,无第三方依赖 / Pure standard library, no dependencies

## 快速开始 / Quick Start

需要 Python 3.8+ / Requires Python 3.8+。

```bash
python trainer.py import words.csv   # 导入 46 个高考高频词 / import the seed word list
python trainer.py add apple n.苹果   # 手动添加单词 / add one word
python trainer.py review             # 开始今天的复习 / start today's review
python trainer.py today              # 看看今天该复习哪些 / list words due today
python trainer.py stats              # 查看整体进度 / show overall progress
```

## 复习界面 / Review session

```text
$ python trainer.py review
今天要复习 3 个单词。按 Ctrl+C 可随时退出,进度会保存。

[1/3] abandon
  想好意思后按回车看答案 >
  → vt.放弃;抛弃
  认识吗? 1=认识  2=模糊  3=不认识 > 1
  ✓ 认识:下次复习 2026-10-06
```

## 数据说明 / Data

进度保存在本目录的 `progress.json`,只存在你自己的电脑上,不会被上传。
Progress is stored locally in `progress.json` and never uploaded.

## Roadmap

- [ ] v2:图形界面 / GUI version
- [ ] v3:网页版,手机也能复习 / web version, reviewable on phone
- [ ] 单词发音 / pronunciation

## 协议 / License

[MIT](LICENSE)
