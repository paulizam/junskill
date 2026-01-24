"""
生成讲解稿脚本 - 技术江湖风
根据输入内容自动生成幽默口语化的讲解稿
"""
import sys
import argparse

def generate_script(content_lines, title=""):
    """根据内容生成讲解稿"""
    script = []

    # 开场
    script.append(f"{title}，今天跟大家聊聊这个狠货。")

    # 主体内容
    for i, line in enumerate(content_lines):
        line = line.strip()
        if not line:
            continue

        # 根据内容风格添加讲解
        if "第" in line and ("章" in line or "节" in line):
            script.append(f"今天咱们来看{line}。")
        elif "：" in line or ":" in line:
            parts = line.split("：", 1) if "：" in line else line.split(":", 1)
            if len(parts) == 2:
                script.append(f"首先，{parts[0]}，{parts[1]}，小编给你说道说道。")
        else:
            script.append(f"{line}，这个知识点很关键，大家记住咯。")

    # 结尾
    script.append("好啦，今天的分享就到这儿，咱们下期再见！")
    script.append("关注我，带你一起涨知识，江湖路漫漫，咱们一起前行！")

    return "\n".join(script)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="输入文件路径")
    parser.add_argument("-o", "--output", default="script.txt", help="输出脚本文件")
    parser.add_argument("-t", "--title", default="这个主题", help="视频标题")
    args = parser.parse_args()

    # 读取输入文件
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        print(f"[ERROR] 无法读取文件: {args.input}")
        sys.exit(1)

    # 分割内容
    lines = content.split('\n')
    filtered_lines = [line.strip() for line in lines if line.strip()]

    # 生成脚本
    script = generate_script(filtered_lines, args.title)

    # 保存
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(script)

    print(f"[OK] 讲解稿已生成: {args.output}")
    print(f"[INFO] 共 {len(filtered_lines)} 个内容段落")
