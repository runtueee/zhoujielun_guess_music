#!/usr/bin/env python3
"""批量把下载的音频转成猜歌曲库格式并放入 总/

用法: python3 tools/add_songs.py <下载目录> [码率]
  码率: 默认 128k (一首约4MB), 想要 10MB 左右就传 320k

- 输入目录里的每个音频文件(不限格式)都会转成 MP3 放进 总/
- 输出文件名 = 源文件名, 所以下载后请先把文件重命名为 "歌名.mp3" 再运行
- 已存在的歌名自动跳过, 可重复运行
"""
import os
import subprocess
import sys

LIB_DIR = "总"
BITRATE = sys.argv[2] if len(sys.argv) > 2 else "128k"
EXT = {".mp3", ".m4a", ".flac", ".wav", ".aac", ".ogg"}


def main():
    if len(sys.argv) < 2:
        print("用法: python3 tools/add_songs.py <下载目录> [码率]")
        sys.exit(1)
    src_dir = sys.argv[1]
    files = sorted(f for f in os.listdir(src_dir) if os.path.splitext(f)[1].lower() in EXT)

    done = skipped = failed = 0
    for f in files:
        name = os.path.splitext(f)[0]
        out = os.path.join(LIB_DIR, name + ".mp3")
        if os.path.exists(out):
            print(f"[跳过] {name} 已存在")
            skipped += 1
            continue
        cmd = ["ffmpeg", "-y", "-i", os.path.join(src_dir, f), "-vn",
               "-codec:a", "libmp3lame", "-b:a", BITRATE, "-ar", "44100",
               "-ac", "2", out]
        r = subprocess.run(cmd, capture_output=True)
        if r.returncode == 0 and os.path.exists(out):
            size = os.path.getsize(out) / 1024 / 1024
            print(f"[完成] {name} ({size:.1f}MB)")
            done += 1
        else:
            print(f"[失败] {name}: {r.stderr.decode('utf-8', 'ignore')[-200:]}")
            failed += 1
    print(f"\n新增 {done} 首, 跳过 {skipped} 首, 失败 {failed} 首")


if __name__ == "__main__":
    main()
