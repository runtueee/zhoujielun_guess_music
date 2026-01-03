import streamlit as st
import os
import random
from pydub import AudioSegment
import io
import base64

# 1. 页面配置
st.set_page_config(page_title="周杰伦猜歌·巅峰挑战版", page_icon="🎵", layout="wide")

# --- 辅助函数：将本地音频转为 base64 字符串 ---
def get_audio_html(file_path):
    if not os.path.exists(file_path): return ""
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    return f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">'

# --- 核心剪辑函数 ---
def get_random_clip(file_path, duration_sec=5):
    try:
        audio = AudioSegment.from_mp3(file_path)
        total_ms = len(audio)
        limit = max(0, total_ms - (duration_sec * 1000))
        start_ms = random.randint(0, limit)
        clip = audio[start_ms : start_ms + (duration_sec * 1000)]
        buffer = io.BytesIO()
        clip.export(buffer, format="mp3")
        return buffer.getvalue()
    except Exception as e:
        st.error(f"FFmpeg 处理错误: {e}")
        return None

# 2. 基础配置
music_folder = "总"
JACKPOT_1 = "jackpot1.mp4" 
JACKPOT_2 = "jackpot2.mp4"
song_files = [f for f in os.listdir(music_folder) if f.endswith('.mp3')]
total_songs_count = len(song_files)

# 3. Session State 状态初始化
if 'total_score' not in st.session_state: st.session_state.total_score = 0
if 'combo_count' not in st.session_state: st.session_state.combo_count = 0
if 'just_won' not in st.session_state: st.session_state.just_won = False
if 'play_sound' not in st.session_state: st.session_state.play_sound = None
if 'last_result' not in st.session_state: st.session_state.last_result = None
if 'is_answered' not in st.session_state: st.session_state.is_answered = False

# --- 伪随机：初始化待抽题库 ---
if 'remaining_songs' not in st.session_state or len(st.session_state.remaining_songs) == 0:
    st.session_state.remaining_songs = list(song_files)
    random.shuffle(st.session_state.remaining_songs)

# 4. 侧边栏
st.sidebar.header("🏆 战绩看板")
st.sidebar.metric("总积分", st.session_state.total_score)
st.sidebar.metric("当前连胜", st.session_state.combo_count, delta=f"Combo x{st.session_state.combo_count}")

# --- UI 进度显示 ---
st.sidebar.markdown("---")
st.sidebar.subheader("🎯 通关进度")
songs_played = total_songs_count - len(st.session_state.remaining_songs)
# 如果正在答题中，进度应该是已经完成的部分
st.sidebar.progress(songs_played / total_songs_count)
st.sidebar.write(f"已挑战: {songs_played} / {total_songs_count}")

st.sidebar.markdown("---")
game_mode = st.sidebar.selectbox("答题模式", ["选择题模式", "填空题模式"])
level = st.sidebar.radio("选择难度", ["简单 (10s)", "普通 (5s)", "地狱 (2s)"], index=1)
duration_map = {"简单 (10s)": 10, "普通 (5s)": 5, "地狱 (2s)": 2}

# --- 切换难度时重置所有状态 (保留题库进度) ---
if "last_config" not in st.session_state: st.session_state.last_config = (game_mode, level)
if st.session_state.last_config != (game_mode, level):
    for k in ['clip_data', 'correct_name', 'options', 'last_result', 'is_answered', 'just_won']:
        st.session_state.pop(k, None)
    st.session_state.last_config = (game_mode, level)
    st.rerun()

# 5. 生成题目 (加入伪随机逻辑)
if 'clip_data' not in st.session_state:
    # 从待抽池弹出一首歌
    target_song = st.session_state.remaining_songs.pop()
    
    st.session_state.clip_data = get_random_clip(os.path.join(music_folder, target_song), duration_map[level])
    st.session_state.correct_name = os.path.splitext(target_song)[0]
    
    # 生成干扰项
    others = [os.path.splitext(f)[0] for f in song_files if os.path.splitext(f)[0] != st.session_state.correct_name]
    st.session_state.options = random.sample(others, min(len(others), 3)) + [st.session_state.correct_name]
    random.shuffle(st.session_state.options)
    st.session_state.is_answered = False

# 6. UI 展示
st.title("🎵 周杰伦猜歌 · 闯关挑战")

# --- 音效反馈 ---
sound_placeholder = st.empty()
if st.session_state.play_sound:
    sound_placeholder.markdown(get_audio_html(st.session_state.play_sound), unsafe_allow_html=True)
    st.session_state.play_sound = None

# --- 视频奖励逻辑 (10/20连胜) ---
if st.session_state.just_won and (st.session_state.combo_count == 10 or st.session_state.combo_count == 20):
    reward_file = JACKPOT_1 if st.session_state.combo_count == 10 else JACKPOT_2
    st.markdown(f"## 🎊 {'10' if st.session_state.combo_count==10 else '20'}连胜解锁奖励！")
    if os.path.exists(reward_file):
        st.video(reward_file, autoplay=True)
        if st.button("关闭奖励并进入下一题"):
            st.session_state.just_won = False
            for k in ['clip_data', 'correct_name', 'options', 'is_answered', 'last_result']:
                st.session_state.pop(k, None)
            st.rerun()
    st.stop()

# --- 答题反馈文案 ---
if st.session_state.last_result == "correct":
    st.balloons()
    st.success(f"✅ 哎哟不错哦！答案是《{st.session_state.correct_name}》")
    if st.button("➡️ 下一首"):
        for k in ['clip_data', 'correct_name', 'options', 'is_answered', 'last_result']:
            st.session_state.pop(k, None)
        st.rerun()
elif st.session_state.last_result == "wrong":
    st.error(f"❌ 答错了！正确答案是《{st.session_state.correct_name}》")
    if st.button("➡️ 再试一题"):
        for k in ['clip_data', 'correct_name', 'options', 'is_answered', 'last_result']:
            st.session_state.pop(k, None)
        st.rerun()

# 7. 游戏核心界面 (答题后隐藏，显示反馈)
if not st.session_state.is_answered:
    if st.session_state.clip_data:
        st.write(f"### 听这段音频 ({level})")
        st.audio(st.session_state.clip_data, format='audio/mp3')

    with st.form("guess_form", clear_on_submit=True):
        if game_mode == "选择题模式":
            user_answer = st.radio("这首歌是？", st.session_state.options)
        else:
            user_answer = st.text_input("输入歌名")
        submitted = st.form_submit_button("提交答案")

    if submitted:
        st.session_state.is_answered = True
        actual = st.session_state.correct_name.strip().lower()
        u_input = user_answer.strip().lower()
        
        if u_input == actual:
            st.session_state.combo_count += 1
            st.session_state.total_score += (10 * st.session_state.combo_count)
            st.session_state.last_result = "correct"
            st.session_state.play_sound = "win.mp3"
            st.session_state.just_won = True
        else:
            st.session_state.combo_count = 0
            st.session_state.last_result = "wrong"
            st.session_state.play_sound = "lose.mp3"
        st.rerun()

# 8. 辅助操作
st.markdown("---")
if st.button("🗑️ 重置所有进度"):
    st.session_state.clear()
    st.rerun()