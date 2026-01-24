"""
视频生成主脚本 - 整合所有步骤
"""
import os
import sys
import subprocess
import argparse
import json
import shutil

# 项目路径
PROJECT_DIR = "D:/RemotionProject"
SRC_DIR = os.path.join(PROJECT_DIR, "src")
PUBLIC_DIR = os.path.join(PROJECT_DIR, "public")

def check_dependencies():
    """检查依赖是否安装"""
    print("[INFO] 检查依赖...")

    # 检查 edge-tts
    try:
        subprocess.run(['edge-tts', '--help'], capture_output=True)
        print("[OK] edge-tts 已安装")
    except:
        print("[WARN] edge-tts 未安装，正在安装...")
        subprocess.run(['pip', 'install', 'edge-tts', '-q'])
        print("[OK] edge-tts 安装完成")

    # 检查 whisper
    try:
        subprocess.run(['whisper', '--help'], capture_output=True)
        print("[OK] whisper 已安装")
    except:
        print("[WARN] whisper 未安装，正在安装...")
        subprocess.run(['pip', 'install', 'openai-whisper', '-q'])
        print("[OK] whisper 安装完成")

def step1_extract_content(input_file):
    """第一步：提取内容"""
    print("\n[步骤1] 提取内容...")

    if input_file.endswith('.epub'):
        # 提取 epub
        print(f"[INFO] 检测到 epub 文件")
        return extract_from_epub(input_file)
    else:
        # 直接读取
        with open(input_file, 'r', encoding='utf-8') as f:
            return f.read()

def extract_from_epub(epub_path):
    """从 epub 提取内容"""
    import ebooklib
    from ebooklib import epub
    import bs4

    book = epub.read_epub(epub_path)
    content_parts = []

    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            content = item.get_content()
            soup = bs4.BeautifulSoup(content, 'html.parser')
            text = soup.get_text()
            content_parts.append(text)

    return "\n".join(content_parts)

def step2_generate_script(content, title):
    """第二步：生成讲解稿"""
    print("\n[步骤2] 生成讲解稿...")

    lines = [line.strip() for line in content.split('\n') if line.strip()]
    script = []

    # 开场
    script.append(f"{title}，今天跟大家聊聊这个狠活儿。")

    # 主体
    for i, line in enumerate(lines):
        script.append(f"{line}，这个点很关键。")

    # 结尾
    script.append("好啦，今天的分享就到这儿。")
    script.append("关注我，带你一起涨知识，咱们下期再见！")

    script_text = "\n".join(script)

    with open('script.txt', 'w', encoding='utf-8') as f:
        f.write(script_text)

    print(f"[OK] 讲解稿已生成: script.txt")
    return script_text

def step3_generate_audio():
    """第三步：生成旁白语音"""
    print("\n[步骤3] 生成旁白语音...")

    subprocess.run([
        'edge-tts',
        '--file', 'script.txt',
        '--write-media', 'narration.mp3',
        '--voice', 'zh-CN-YunxiNeural'
    ], check=True)

    print("[OK] 语音已生成: narration.mp3")
    return 'narration.mp3'

def step4_get_timestamps(audio_file):
    """第四步：获取时间戳"""
    print("\n[步骤4] 获取时间戳...")

    subprocess.run([
        'whisper', audio_file,
        '--model', 'base',
        '--language', 'zh',
        '--output_format', 'json',
        '--output_dir', '.'
    ], check=True)

    print(f"[OK] 时间戳已生成")
    return f"{audio_file.rsplit('.', 1)[0]}.json"

def step5_create_timeline(whisper_json):
    """第五步：创建时间轴"""
    print("\n[步骤5] 创建时间轴...")

    with open(whisper_json, 'r', encoding='utf-8') as f:
        data = json.load(f)

    segments = data.get('segments', [])

    timeline = []
    for i, seg in enumerate(segments):
        # Whisper 返回的时间戳是数字（秒），直接使用
        start_sec = float(seg['start'])
        end_sec = float(seg['end'])

        timeline.append({
            'index': i + 1,
            'start_frame': int(start_sec * 30),
            'end_frame': int(end_sec * 30),
            'text': seg['text'].strip()
        })

    total_frames = timeline[-1]['end_frame']

    # 保存时间轴
    with open('timeline.json', 'w', encoding='utf-8') as f:
        json.dump(timeline, f, ensure_ascii=False, indent=2)

    print(f"[OK] 时间轴已创建，共 {len(timeline)} 段，{total_frames} 帧")
    return timeline, total_frames

def step6_create_component(timeline, video_name, video_title):
    """第六步：创建 Remotion 组件"""
    print("\n[步骤6] 创建 Remotion 组件...")

    # 读取模板
    template_path = os.path.join(os.path.dirname(__file__), 'video_template.jsx')
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()

    # 替换变量
    component = template.replace('{{VIDEO_NAME}}', video_name)
    component = component.replace('{{VIDEO_TITLE}}', video_title)

    # 生成场景和字幕
    scenes_code = []
    subtitles_code = []

    for item in timeline:
        start = item['start_frame']
        end = item['end_frame']

        # 场景
        scenes_code.append(f'''
      <Scene startFrame={start} endFrame={end}>
        <FadeInText delay={start} style={{fontSize: 48, color: '#fff', textAlign: 'center'}}>
          {item['text']}
        </FadeInText>
      </Scene>
''')

        # 字幕
        subtitles_code.append(f'      <Subtitle startFrame={start} endFrame={end} text="{item["text"]}" />\n')

    # 替换占位符
    component = component.replace('{{SCENES}}', ''.join(scenes_code))
    component = component.replace('{{SUBTITLES}}', ''.join(subtitles_code))

    # 保存组件
    component_path = os.path.join(SRC_DIR, f"{video_name}.jsx")
    with open(component_path, 'w', encoding='utf-8') as f:
        f.write(component)

    print(f"[OK] 组件已创建: {component_path}")

def step7_register_component(video_name, total_frames):
    """第七步：注册组件"""
    print("\n[步骤7] 注册组件...")

    root_path = os.path.join(SRC_DIR, 'Root.jsx')

    with open(root_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否已注册
    if f'./{video_name}' in content:
        print(f"[INFO] 组件 {video_name} 已注册，跳过")
        return

    # 添加 import
    import_line = f"import {{{video_name.capitalize()}}} from './{video_name}';"
    if import_line not in content:
        content = content.replace(
            "import {HelloWorld} from './HelloWorld';",
            f"import {{HelloWorld}} from './HelloWorld';\n{import_line}",
            1
        )

    # 添加 Composition
    composition = f'''
      <Composition
        id="{video_name}"
        component={{{{video_name.capitalize()}}}}
        durationInFrames={total_frames}
        fps={30}}
        width={1920}}
        height={1080}}
      />
'''

    # 找到 </> 前面插入
    insert_pos = content.rfind('</>')
    if insert_pos > 0:
        content = content[:insert_pos] + composition + content[insert_pos:]

    with open(root_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"[OK] 组件已注册: {video_name}")

def step8_setup_bgm(theme):
    """第八步：配置背景音乐"""
    print("\n[步骤8] 配置背景音乐...")

    # 根据主题选择 BGM
    bgm_map = {
        'chinese': 'assets/bgm/chinese-ancient.mp3',
        'history': 'assets/bgm/chinese-ancient.mp3',
        'ancient': 'assets/bgm/chinese-ancient.mp3',
        'literature': 'assets/bgm/chinese-ancient.mp3',
        'tech': 'assets/bgm/tech-modern.mp3',
        'modern': 'assets/bgm/tech-modern.mp3',
        'science': 'assets/bgm/educational.mp3',
        'business': 'assets/bgm/business.mp3',
        'fun': 'assets/bgm/fun.mp3',
    }

    # 自动判断主题
    theme_lower = theme.lower()
    bgm_file = bgm_map.get(theme_lower, 'assets/bgm/chinese-ancient.mp3')

    # 复制 BGM
    src_bgm = os.path.join(os.path.dirname(__file__), '..', 'assets', 'bgm', os.path.basename(bgm_file))
    dst_bgm = os.path.join(PUBLIC_DIR, 'bgm.mp3')

    if os.path.exists(src_bgm):
        shutil.copy2(src_bgm, dst_bgm)
        print(f"[OK] 背景音乐已配置: {os.path.basename(bgm_file)}")
    else:
        print(f"[WARN] 背景音乐不存在，使用默认")

def main(input_file, video_name, video_title, theme):
    """主流程"""
    print("=" * 60)
    print(f"[Video] 视频生成器")
    print(f"输入文件: {input_file}")
    print(f"视频名称: {video_name}")
    print(f"视频标题: {video_title}")
    print(f"主题: {theme}")
    print("=" * 60)

    # 检查依赖
    check_dependencies()

    # 切换到项目目录
    os.chdir(PROJECT_DIR)

    try:
        # 步骤
        content = step1_extract_content(input_file)
        script_text = step2_generate_script(content, video_title)
        audio_file = step3_generate_audio()
        whisper_json = step4_get_timestamps(audio_file)
        timeline, total_frames = step5_create_timeline(whisper_json)
        step6_create_component(timeline, video_name, video_title)
        step7_register_component(video_name, total_frames)
        step8_setup_bgm(theme)

        print("\n" + "=" * 60)
        print("[OK] 视频生成完成！")
        print("=" * 60)
        print(f"[INFO] 组件名称: {video_name}")
        print(f"[INFO] 访问地址: http://localhost:3002")
        print(f"[INFO] 在 Remotion Studio 中选择 '{video_name}' 组件预览")

    except Exception as e:
        print(f"\n[ERROR] 生成失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="自动生成 Remotion 视频")
    parser.add_argument("input", help="输入文件路径（支持 txt/md/epub）")
    parser.add_argument("-n", "--name", default="my-video", help="视频/组件名称（英文，不含特殊字符）")
    parser.add_argument("-t", "--title", default="知识分享", help="视频标题")
    parser.add_argument("--theme", choices=['chinese', 'history', 'tech', 'modern', 'science', 'business', 'fun'],
                      default='chinese', help="视频主题（用于选择 BGM）")

    args = parser.parse_args()

    main(args.input, args.name, args.title, args.theme)
