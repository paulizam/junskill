name: video-generator
description: 将任何内容（文本/书籍/文章）自动生成 Remotion 解说视频。支持 epub/txt/md 等格式，自动生成旁白、字幕、动效，添加背景音乐。适用于知识科普、书籍解读、教程制作等场景。

---

## 使用场景

当用户需要将内容转换为视频时使用此 skill，例如：
- "把这本书的第X章做成视频"
- "这篇文章生成个讲解视频"
- "把这个教程做成视频"
- "帮我把这个内容做成视频"

---

## 工作流程

### 第一步：获取和分析内容

1. **识别内容来源**
   - 如果是 `.epub` 文件：使用 Python ebooklib 解析
   - 如果是 `.txt/.md` 文件：直接读取
   - 如果是网址：使用 webReader 抓取内容

2. **分析内容结构**
   - 识别章节/段落结构
   - 提取核心要点
   - 评估内容体量，确定视频时长

### 第二步：生成讲解稿

根据内容生成"技术江湖风"讲解稿：
- 开场：吸引注意，介绍主题
- 主体：分点讲解，每部分 30-60 秒
- 结尾：总结+下期预告+关注提示

**讲解稿特点：**
- 口语化表达（"小编"、"哈哈"、"啦"等语气词）
- 生动比喻和类比
- 网络用语和梗（适度使用）
- 自嘲幽默

### 第三步：生成旁白语音

使用 edge-tts 将讲解稿转换为语音：
```bash
edge-tts --file script.txt --write-media narration.mp3 --voice zh-CN-YunxiNeural
```

**声音选择：**
- 男声：`zh-CN-YunxiNeural`（年轻活力）
- 女声：`zh-CN-XiaoxiaoNeural`（温柔知性）
- 或根据内容主题选择其他声音

### 第四步：获取时间戳

使用 Whisper 获取旁白的精确时间戳：
```bash
whisper narration.mp3 --model base --language zh --output_format json
```

### 第五步：制作时间轴

根据 Whisper 输出，制作旁白-画面对应表：
- 每句旁白对应一个或一组画面
- 场景之间添加过渡时间（12-15 帧）
- 记录开始帧和结束帧

### 第六步：开发 Remotion 组件

1. **创建组件文件** `src/{VideoName}.jsx`

2. **添加基础组件**
```jsx
import {AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, staticFile} from 'remotion';
import {Audio} from '@remotion/media';
```

3. **定义子组件**
   - `FadeInText` - 文字渐入
   - `Scene` - 场景容器（淡入淡出）
   - `Subtitle` - 字幕组件
   - 动效组件（按需）：`PulseCircle`、`FlowArrow`、`BattleScene` 等

4. **根据时间轴设置场景**
```jsx
<Scene startFrame={0} endFrame={291}>
  {/* 画面内容 */}
</Scene>
<Subtitle startFrame={0} endFrame={90} text="对应字幕" />
```

5. **添加音频**
```jsx
{/* 背景音乐 - 根据主题选择 */}
<Audio src={staticFile('bgm.mp3')} volume={0.25} loop />

{/* 讲解语音 */}
<Audio src={staticFile('narration.mp3')} volume={1.0} />
```

### 第七步：注册组件

在 `src/Root.jsx` 中注册新组件：
```jsx
import {VideoName} from './{VideoName}';

<Composition
  id="video-name"
  component={VideoName}
  durationInFrames={xxx}  // 根据语音时长计算
  fps={30}
  width={1920}
  height={1080}
/>
```

---

## 脚本使用

### generate-script.py

根据输入内容生成讲解稿。

**使用方法：**
```bash
python scripts/generate-script.py <input-file> <output-script.txt>
```

### extract-epub.py

从 epub 文件中提取指定章节内容。

**使用方法：**
```bash
python scripts/extract-epub.py <epub-file> <chapter-number>
```

### get-timestamps.py

使用 Whisper 获取音频时间戳。

**使用方法：**
```bash
python scripts/get-timestamps.py <audio-file>
```

### create-timeline.py

根据时间戳生成时间轴表格。

**使用方法：**
```/bash
python scripts/create-timeline.py <whisper-json>
```

---

## 背景音乐选择

根据内容主题选择合适的 BGM（存储在 `assets/bgm/` 目录）：

| 主题 | 推荐音乐 | 文件名 |
|------|----------|--------|
| 中国风/古风/历史 | 古琴/笛子/武侠风 | `chinese-ancient.mp3` |
| 科技/互联网/现代 | 电子/轻快节拍 | `tech-modern.mp3` |
| 情感/励志/温暖 | 轻音乐/钢琴 | `emotional.mp3` |
| 知识科普/教育 | 轻快明亮 | `educational.mp3` |
| 商业/职场/专业 | 商务电子 | `business.mp3` |
| 轻松/搞笑/趣味 | 活泼卡通 | `fun.mp3` |

**默认使用**：`chinese-ancient.mp3`

---

## 视频时长参考

| 内容量 | 预计时长 | 帧数 (30fps) |
|--------|----------|-------------|
| 短内容 (500字以内) | 1-2 分钟 | 1800-3600 帧 |
| 中等内容 (500-1500字) | 2-4 分钟 | 3600-7200 帧 |
| 长内容 (1500字以上) | 4-8 分钟 | 7200-14400 帧 |

---

## 动效组件库

根据需要选择合适的动效：

**强调类：**
- `PulseCircle` - 脉冲扩散圆圈（强调重点）
- `GlowText` - 发光文字（标题）

**流程类：**
- `FlowArrow` - 流动箭头（展示逻辑关系）
- `ConnectingLine` - 连线动画

**场景类：**
- `BattleScene` - 战斗剪影（武侠/冲突主题）
- `BalanceScale` - 天平（对比/权衡主题）
- `BrainWave` - 脑波（思考/谋略主题）

**装饰类：**
- `FloatingIcons` - 漂浮图标
- `ParticleField` - 粒子背景

---

## 调试和优化

1. **预览检查**
   - 打开 Remotion Studio 预览画面
   - 拖动时间轴检查同步情况
   - 调整文字大小、颜色、位置

2. **音量平衡**
   - 背景音乐：0.15-0.3
   - 讲解语音：1.0

3. **字幕位置**
   - 底部 30px
   - 避免遮挡重要内容

---

## 输出位置

- 组件文件：`src/{VideoName}.jsx`
- 旁白音频：`public/narration.mp3`
- 背景音乐：`public/bgm.mp3`
