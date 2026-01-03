# 周杰伦猜歌 · 巅峰挑战版 (Jay Chou Guess Master)

在线游玩地址: https://runtue.streamlit.app

## 项目新特性
* 在线即玩: 基于 Streamlit Cloud 部署，支持手机与电脑浏览器。
* 伪随机去重: 引入去重抽样算法，保证在完整轮空曲库前绝不出现重复歌曲。
* 通关进度条: 侧边栏实时追踪 128 首经典作品的挑战进度。
* 连胜奖励系统: 10/20 连胜可解锁特殊的视频奖励。
* 三级难度挑战: 提供简单 (10s)、普通 (5s)、地狱 (2s) 三种音频切片时长。

## 游戏规则
1. 听音辨曲: 系统随机截取歌曲中的片段，完全考验听力。
2. 双模式切换:
   - 选择题模式: 四选一，适合休闲娱乐。
   - 填空题模式: 直接输入歌名，挑战资深粉丝。
3. 积分算法: 答对获得基础分，连胜次数越高，单题积分加成越高。

## 快速部署 (开发者参考)
1. 安装依赖:
   pip install streamlit pydub
2. 安装 FFmpeg:
   确保系统已安装音频处理工具 FFmpeg。
3. 启动应用:
   streamlit run web_guess.py

## 目录结构
- 总/: 128首 MP3 曲库文件夹
- app.py: 核心程序代码
- requirements.txt: Python 依赖清单 (streamlit, pydub)
- packages.txt: 系统级依赖 (ffmpeg)
- runtime.txt: 环境版本声明 (python-3.11)
- win.mp3 / lose.mp3: 反馈音效
- jackpot1.mp4 / jackpot2.mp4: 连胜奖励视频

## 免责声明
1. 本项目仅供学习、交流使用，严禁用于任何商业用途。
2. 所有音乐资源版权归周杰伦先生及所属唱片公司所有，请支持正版音乐。

---
联系方式: 2579633870@qq.com