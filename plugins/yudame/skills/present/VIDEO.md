# Narrated explainer video

Videos are built with [Remotion](https://www.remotion.dev) (React components rendered frame by frame to MP4 from the CLI) from the template in `video/`. It was chosen because scenes are plain code, a composition can compute its own length from data before rendering, and `npx remotion render` produces an H.264/AAC MP4 headlessly with no editor open.

**Licence.** Remotion is free, commercial use included, for individuals and for-profit companies with up to 3 employees; a larger company needs a Company Licence from remotion.pro. Check the licence terms against your own company's size before shipping a video. A video made for a client that runs the template itself is the client's licence question, so say so before handing them the source.

## How the template works

`scenes.json` is the script: one entry per scene with `id`, `title` (the on-screen conclusion), optional `points` (short on-screen phrases), and `text` (the narration). `tts.py --scenes` turns it into `public/vo/<id>.wav` plus `public/vo/manifest.json` with each clip's measured duration. `src/Root.tsx` imports both and joins them by `id`, and `calculateMetadata` sets the video's length to the sum of the scenes. Each scene lasts its narration plus a 10-frame lead-in and an 18-frame tail (`sceneFrames` in `src/Explainer.tsx`), and its points appear at even shares of the narration so the screen keeps pace with the voice. Change the narration and the timing follows when you re-run TTS; nothing is hand-timed.

The video is vertical, 1080×1920, so it fills an upright phone; for landscape, when someone asks for it, swap `width` and `height` in `src/Root.tsx` and look at the frames again. `src/Explainer.tsx` holds the visuals in the house-style skill (cream, ink, Lora headings, one red accent). Replace the colour and font constants when the project has its own style, and write new scene components when an idea needs a diagram or a chart instead of a title and points; keep `sceneFrames` as the single source of a scene's length. When a visual must land on a particular phrase, split the narration into two scenes rather than guessing word timestamps.

## Commands

Work in a directory outside any git repo (a scratchpad, or a project folder the user names), because `node_modules` is about 1 GB:

```bash
cp -R <skill dir>/video <work dir> && cd <work dir>
# write scenes.json
uv run <skill dir>/tts.py --scenes scenes.json --out-dir public/vo
npm install --no-audit --no-fund                   # once per work dir, ~40 s
npx remotion render Explainer out/explainer.mp4    # 18 s of video rendered in ~30 s on an Apple-silicon Mac
ffprobe -v error -show_entries format=duration -of csv=p=0 out/explainer.mp4
```

`npx remotion studio` opens a live preview in the browser when iterating on visuals.

## Gotchas

- Run TTS before `render` or `studio`: `Root.tsx` imports `public/vo/manifest.json` at bundle time, so a missing manifest fails the bundle, and a scene with no voiceover throws an error naming its id.
- The first render downloads Chrome Headless Shell into `node_modules/.remotion`; it needs the network once, and the Google Fonts loader needs it on every render.
- npm warns that esbuild's install script was not approved under `allowScripts`. The render works without it; leave it.
- The first `uv run` of `tts.py` installs onnxruntime and Kokoro into uv's cache (about 10 s); later runs start fast. If `~/.cache/kokoro-onnx` lacks `kokoro-v1.0.onnx` and `voices-v1.0.bin` (about 350 MB), the error names the download URL; get them rather than shipping a `say` voiceover in a video.

## Done

The MP4 exists, `ffprobe` reports a duration equal to the sum of the scene lengths (frames / 30), and the audio is not silent (`ffmpeg -i out/explainer.mp4 -af volumedetect -vn -f null -` shows a `mean_volume` well above -60 dB). Extract a frame from the middle of each scene (`ffmpeg -ss <t> -i out/explainer.mp4 -frames:v 1 f.png`) and look at it: text fits, nothing overlaps, fonts loaded. Report the path and duration.
