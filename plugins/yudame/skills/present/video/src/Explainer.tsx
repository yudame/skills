import {AbsoluteFill, Audio, Sequence, Series, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {loadFont as loadLora} from '@remotion/google-fonts/Lora';
import {loadFont as loadInter} from '@remotion/google-fonts/Inter';

// House style fallback (the house-style skill). Replace these when the project has its own style.
const INK = '#1A1A1A';
const CREAM = '#FAF9F6';
const RED = '#C8102E';
const HAIRLINE = 'rgba(26,26,26,0.18)';
const {fontFamily: serif} = loadLora('normal', {weights: ['600'], subsets: ['latin']});
const {fontFamily: sans} = loadInter('normal', {weights: ['400'], subsets: ['latin']});

export const FPS = 30;
const LEAD_IN = 10; // frames of silence before the narration starts, so the title lands first
const TAIL = 18; // frames held after the narration ends, so a cut never clips the last word

// A scene lasts exactly as long as its narration plus the lead-in and tail.
export const sceneFrames = (seconds: number) => LEAD_IN + Math.ceil(seconds * FPS) + TAIL;

type Scene = {id: string; title: string; points?: string[]; text: string; audio: string; seconds: number};
export type ExplainerProps = {scenes: Scene[]};

const SceneView = ({scene, index}: {scene: Scene; index: number}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const enter = spring({frame, fps, config: {damping: 200}});
  const narration = Math.ceil(scene.seconds * FPS);
  return (
    <AbsoluteFill style={{background: CREAM, color: INK, padding: '140px 180px', fontFamily: sans}}>
      <div style={{fontSize: 28, letterSpacing: 4, textTransform: 'uppercase', opacity: 0.6, fontFamily: 'monospace'}}>
        {String(index + 1).padStart(2, '0')}
      </div>
      <div style={{height: 1, background: HAIRLINE, margin: '28px 0 56px', width: `${enter * 100}%`}} />
      <h1
        style={{
          fontFamily: serif,
          fontSize: 92,
          lineHeight: 1.1,
          margin: 0,
          maxWidth: 1400,
          opacity: enter,
          transform: `translateY(${(1 - enter) * 30}px)`,
        }}
      >
        {scene.title}
      </h1>
      <ul style={{listStyle: 'none', padding: 0, marginTop: 72}}>
        {(scene.points ?? []).map((p, i) => {
          // Reveal each point at an even share of the narration, so the screen keeps pace with the voice.
          const at = LEAD_IN + Math.round(((i + 1) * narration) / ((scene.points?.length ?? 0) + 1));
          const o = interpolate(frame, [at, at + 12], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
          return (
            <li key={p} style={{fontSize: 48, margin: '0 0 28px', opacity: o, display: 'flex', gap: 28}}>
              <span style={{color: i === 0 ? RED : INK}}>—</span>
              {p}
            </li>
          );
        })}
      </ul>
      <Sequence from={LEAD_IN} layout="none">
        <Audio src={staticFile(scene.audio)} />
      </Sequence>
    </AbsoluteFill>
  );
};

export const Explainer = ({scenes}: ExplainerProps) => (
  <Series>
    {scenes.map((s, i) => (
      <Series.Sequence key={s.id} durationInFrames={sceneFrames(s.seconds)}>
        <SceneView scene={s} index={i} />
      </Series.Sequence>
    ))}
  </Series>
);
