import {AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, staticFile} from 'remotion';
import {Audio} from '@remotion/media';

// 文字渐入组件
const FadeInText = ({children, delay = 0, style, duration = 15}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const opacity = interpolate(
    frame,
    [delay, delay + duration],
    [0, 1],
    {extrapolateRight: 'clamp'}
  );

  const translateY = interpolate(
    frame,
    [delay, delay + duration],
    [15, 0],
    {extrapolateRight: 'clamp'}
  );

  return (
    <div style={{
      opacity,
      transform: `translateY(${translateY}px)`,
      ...style
    }}>
      {children}
    </div>
  );
};

// 场景容器（淡入淡出切换）
const Scene = ({children, startFrame, endFrame}) => {
  const frame = useCurrentFrame();
  const fadeDuration = 12;

  const opacity = interpolate(
    frame,
    [startFrame, startFrame + fadeDuration, endFrame - fadeDuration, endFrame],
    [0, 1, 1, 0],
    {extrapolateRight: 'clamp', extrapolateLeft: 'clamp'}
  );

  return (
    <div style={{
      opacity,
      position: 'absolute',
      width: '100%',
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: 100,
    }}>
      {children}
    </div>
  );
};

// 字幕组件
const Subtitle = ({text, startFrame, endFrame}) => {
  const frame = useCurrentFrame();
  const fadeDuration = 8;

  const opacity = interpolate(
    frame,
    [startFrame, startFrame + fadeDuration, endFrame - fadeDuration, endFrame],
    [0, 1, 1, 0],
    {extrapolateRight: 'clamp', extrapolateLeft: 'clamp'}
  );

  return (
    <div style={{
      position: 'absolute',
      bottom: 30,
      left: '50%',
      transform: 'translateX(-50%)',
      backgroundColor: 'rgba(0, 0, 0, 0.7)',
      padding: '12px 30px',
      borderRadius: 8,
      maxWidth: '80%',
      opacity,
    }}>
      <div style={{
        color: '#fff',
        fontSize: 28,
        textAlign: 'center',
        lineHeight: 1.6,
        textShadow: '0 1px 3px rgba(0,0,0,0.5)',
      }}>
        {text}
      </div>
    </div>
  );
};

export const {{VIDEO_NAME}} = () => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();

  return (
    <AbsoluteFill style={{
      background: `linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 50%, #1a1a1a 100%)`,
      fontFamily: "'Microsoft YaHei', 'PingFang SC', sans-serif',
      overflow: 'hidden',
    }}>
      {/* 装饰粒子 */}
      {[...Array(15)].map((_, i) => {
        const yPos = interpolate(frame, [0, durationInFrames], [-10, 110], {extrapolateRight: 'clamp'});
        return (
          <div key={i} style={{
            position: 'absolute',
            left: `${Math.random() * 100}%`,
            top: `${yPos + (i * 6) % 100}%`,
            width: Math.random() * 3 + 1,
            height: Math.random() * 3 + 1,
            borderRadius: '50%',
            background: `rgba(212, 175, 55, ${0.2 + Math.random() * 0.4})`,
            boxShadow: `0 0 ${Math.random() * 3 + 1}px rgba(212, 175, 55, 0.3)`,
          }} />
        );
      })}

      {/* 标题 */}
      <FadeInText delay={0} style={{
        fontSize: 90,
        color: '#D4AF37',
        fontWeight: 'bold',
        marginBottom: 40,
        textShadow: '0 4px 30px rgba(212, 175, 55, 0.5)',
      }}>
        {{VIDEO_TITLE}}
      </FadeInText>

      {{SCENES}}

      {/* 字幕 */}
      {{SUBTITLES}}

      {/* 进度条 */}
      <div style={{
        position: 'absolute',
        bottom: 0,
        left: 0,
        right: 0,
        height: 5,
        background: 'rgba(0,0,0,0.3)',
      }}>
        <div style={{
          height: '100%',
          width: `${(frame / durationInFrames) * 100}%`,
          background: 'linear-gradient(90deg, #C83030, #D4AF37)',
        }} />
      </div>

      {/* 背景音乐 */}
      <Audio src={staticFile('bgm.mp3')} volume={0.25} loop />

      {/* 讲解语音 */}
      <Audio src={staticFile('narration.mp3')} volume={1.0} />
    </AbsoluteFill>
  );
};
