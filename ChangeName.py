import streamlit as st
import os
import random
from pydub import AudioSegment
import io

st.title("🎵 周杰伦猜歌 · 极速版")

music_folder = "./music"
song_files = [f for f in os.listdir(music_folder) if f.endswith('.mp3')]

# 初始化游戏状态
if 'current_clip' not in st.session_state:
    st.session_state.current_clip = None
    st.session_state.correct_answer = ""
    st.session_state.options = []

def generate_new_question(duration_sec):
    # 1. 选歌
    target_file = random.choice(song_files)
    full_path = os.path.join(music_folder, target_file)
    song_name = os.path.splitext(target_file)[0]
    
    # 2. 使用 pydub 加载并剪辑
    audio = AudioSegment.from_mp3(full_path)
    total_ms = len(audio)
    
    # 随机起点 (毫秒)
    start_ms = random.randint(0, max(0, total_ms - (duration_sec * 1000) - 1000))
    clip = audio[start_ms : start_ms + (duration_sec * 1000)]
    
    # 3. 将剪好的音频转为字节流（不产生物理文件，速度更快）
    buffer = io.BytesIO()
    clip.export(buffer, format="mp3")
    
    # 4. 存入 session_state
    st.session_state.current_clip = buffer.getvalue()
    st.session_state.correct_answer = song_name
    
    # 生成选项
    others = [os.path.splitext(f)[0] for f in song_files if os.path.splitext(f)[0] != song_name]
    opts = [song_name] + random.sample(others, 3)
    random.shuffle(opts)
    st.session_state.options = opts

# 难度选择
level = st.sidebar.radio("难度", [10, 5, 2], index=1, format_func=lambda x: f"听 {x} 秒")

if st.button("🔔 开始抽题 / 换一题"):
    generate_new_question(level)

# 播放与答题
if st.session_state.current_clip:
    # 播放剪好的片段
    st.audio(st.session_state.current_clip, format="audio/mp3")
    
    with st.form("guess_form"):
        ans = st.radio("这首歌是？", st.session_state.options)
        if st.form_submit_button("提交"):
            if ans == st.session_state.correct_answer:
                st.success("正确！")
                st.balloons()
            else:
                st.error(f"错啦，是《{st.session_state.correct_answer}》")