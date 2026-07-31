# 周杰伦猜歌 · 巅峰挑战版

基于 Streamlit 的听音猜歌游戏，曲库为周杰伦 128 首 MP3。已部署在 https://runtue.streamlit.app（线上版要求 Python 3.12，见 `runtime.txt`）。

## 运行方式（必须从项目根目录启动）

```bash
cd /Users/runtue/Desktop/项目/zhoujielun_guess_music-master
streamlit run web_guess.py
```

注意：代码全部使用**相对路径**（`总/`、`win.mp3`、`lose.mp3`、`jackpot1.mp4`…）。从其他目录启动会因 `os.listdir("总")` 抛 `FileNotFoundError`，这是最常见的启动失败原因。

## 核心文件

- `web_guess.py` — 唯一入口程序（readme 里写的 `app.py` 是过时信息）
- `ChangeName.py` — 早期极速版原型（引用 `./music` 目录，已废弃，勿运行）
- `总/` — 128 首 MP3 曲库（带 `.mp3` 后缀）
- `音效/` — 含 `嘲笑.MP3`、`金币声.MP3`，**未被代码引用**，可忽略
- 根目录 `win.mp3` / `lose.mp3` — 答对/答错音效（已统一为小写扩展名，Linux 部署不会再失效）
- `jackpot1.mp4` / `jackpot2.mp4` — 10 连胜/20 连胜奖励视频
- `requirements.txt` — `streamlit`, `pydub`；`packages.txt` — `ffmpeg`（Streamlit Cloud 用）

## 环境依赖

- Python 3.13（本机 miniconda 环境）+ `streamlit 1.57.0` + `pydub` + 系统 `ffmpeg`（本机已装 8.0，已验证）
- 音频剪辑走 pydub → ffmpeg，**无 ffmpeg 时 `get_random_clip` 会报错**（会显示 `FFmpeg 处理错误`）

## web_guess.py 逻辑要点

1. 页面配置 → 剪辑函数 `get_random_clip(file_path, duration_sec)`（随机起点切段，导出为内存 MP3）。偶尔会切到首尾静音段，用户可点音频下方"🔁 这段听不清, 换一段"按钮重抽（只重新剪辑当前歌曲，不消耗进度；不要用 `detect_silence` 做自动检测，小内存机器跑不动）
2. 伪随机去重：`st.session_state.remaining_songs` 为打乱的待抽曲库，**只在开始新题时 pop**（存入 `current_song`），128 首出完前不重复。进度 = `answered_count`（答完一题 +1，见 `advance_to_next_question()`），切换难度/模式只清掉本局剪辑重新生成，**不消耗曲库**
3. 游戏状态全存 `st.session_state`：`total_score`、`combo_count`、`max_combo`、`lives`(3)、`is_game_over`、`answered_count`、`remaining_songs`、`current_song`、`clip_data`、`correct_name`、`options`、`last_result`、`is_answered`、`just_won`、`game_completed`、`last_config`
4. 计分：答对 `total_score += 10 * combo_count`（连胜加成）；答错连胜利清零 + **扣一条命**，生命耗尽 → `is_game_over` 显示结算页（积分/最高连胜/挑战数），点重新开始全量重置
5. 两种模式：选择题（四选一）/ 填空题（输入歌名，判题走 `is_correct_answer()`：归一化去标点空格后精确匹配，不中再用 `SequenceMatcher` 相似度 ≥0.85 容差——标点/全角空格/大小写都能容忍，同音错字不会放行）；三档难度 = 音频切片时长 10s/5s/2s
6. 模式/难度控件在**页面顶部主区域**（`st.columns` 一行：答题模式 / 选择难度 / 剩余生命），侧边栏只剩战绩与进度展示——手机上不用点左上角展开侧边栏；切换模式/难度会重置本局答题状态但保留曲库进度（`last_config` 比对 + `st.rerun()`）
7. 10/20 连胜解锁奖励视频；128 首全部出完显示通关页（`game_completed`，注意 `progress(songs_played / total_songs_count)` 在曲库为空时会除零崩溃，不要删 `总` 目录）

## 验证方法

```bash
python3 -c "
from streamlit.testing.v1 import AppTest
at = AppTest.from_file('web_guess.py', default_timeout=120)
at.run()
print('exceptions:', at.exception)
"
```
