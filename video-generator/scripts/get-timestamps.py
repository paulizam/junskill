"""
使用 Whisper 获取音频时间戳
"""
import subprocess
import sys
import argparse

def get_timestamps(audio_file):
    """使用 Whisper 获取时间戳"""
    try:
        result = subprocess.run([
            'whisper', audio_file,
            '--model', 'base',
            '--language', 'zh',
            '--output_format', 'json',
            '--output_dir', '.'
        ], capture_output=True, text=True, encoding='utf-8')

        if result.returncode == 0:
            print("[OK] Whisper 处理完成")
            print(result.stdout)
        else:
            print("[ERROR] Whisper 处理失败:")
            print(result.stderr)
            return False

    except Exception as e:
        print(f"[ERROR] {e}")
        return False

    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", help="音频文件路径")
    args = parser.parse_args()

    get_timestamps(args.audio)
