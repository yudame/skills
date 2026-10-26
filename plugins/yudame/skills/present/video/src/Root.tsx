import {Composition} from 'remotion';
import {Explainer, sceneFrames, type ExplainerProps, FPS} from './Explainer';
import manifest from '../public/vo/manifest.json';
import scenes from '../scenes.json';

// Narration timing comes from the TTS manifest; visuals come from scenes.json.
// Both are keyed by scene id, so re-running TTS after editing the script re-times the video.
const props: ExplainerProps = {
  scenes: scenes.map((s) => {
    const vo = manifest.scenes.find((m) => m.id === s.id);
    if (!vo) throw new Error(`No voiceover for scene "${s.id}": re-run tts.py on scenes.json`);
    return {...s, audio: `vo/${vo.file}`, seconds: vo.seconds};
  }),
};

// Landscape 16:9. For vertical, when asked, swap width and height and look at the frames again.
export const RemotionRoot = () => (
  <Composition
    id="Explainer"
    component={Explainer}
    defaultProps={props}
    fps={FPS}
    width={1920}
    height={1080}
    durationInFrames={1}
    calculateMetadata={({props}) => ({
      durationInFrames: props.scenes.reduce((sum, s) => sum + sceneFrames(s.seconds), 0),
    })}
  />
);
