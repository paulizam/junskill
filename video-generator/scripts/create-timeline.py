"""
根据 Whisper 输出生成时间轴表格
"""
import json
import sys
import argparse

def create_timeline(whisper_json, output_file):
    """根据 Whisper JSON 创建时间轴"""
    with open(whisper_json, 'r', encoding='utf-8') as f:
        data = json.load(f)

    segments = data.get('segments', [])

    timeline = []
    for i, seg in enumerate(segments):
        # Whisper 返回的时间戳是数字（秒），直接使用
        start_sec = float(seg['start'])
        end_sec = float(seg['end'])

        text = seg['text'].strip()
        start_frame = int(start_sec * 30)
        end_frame = int(end_sec * 30)

        timeline.append({
            'index': i + 1,
            'start_sec': start_sec,
            'end_sec': end_sec,
            'start_frame': start_frame,
            'end_frame': end_frame,
            'duration_sec': end_sec - start_sec,
            'text': text
        })

    # 输出表格
    print("=" * 100)
    print(f"{'序号':<6}{'开始秒':<10}{'结束秒':<10}{'开始帧':<10}{'结束帧':<10}{'时长':<10}{'旁白内容'}")
    print("=" * 100)

    for item in timeline:
        text_short = item['text'][:40] + "..." if len(item['text']) > 40 else item['text']
        print(f"{item['index']:<6}{item['start_sec']:<10.2f}{item['end_sec']:<10.2f}{item['start_frame']:<10}{item['end_frame']:<10}{item['duration_sec']:<10.2f}{text_short}")

    print("=" * 100)
    print(f"总时长: {timeline[-1]['end_sec']:.2f}秒 = {timeline[-1]['end_frame']}帧 (30fps)")

    # 保存 JSON
    with open(output_file.replace('.txt', '.json'), 'w', encoding='utf-8') as f:
        json.dump(timeline, f, ensure_ascii=False, indent=2)

    print(f"[OK] 时间轴已保存到: {output_file.replace('.txt', '.json')}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("whisper_json", help="Whisper 输出的 JSON 文件")
    parser.add_argument("-o", "--output", default="timeline.txt", help="输出时间轴文件")
    args = parser.parse_args()

    create_timeline(args.whisper_json, args.output)
