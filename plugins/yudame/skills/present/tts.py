# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["kokoro-onnx>=0.4", "soundfile"]
# ///
"""Text to speech for the present skill: Kokoro (local neural) first, macOS `say` as fallback.

One clip:   uv run tts.py --text "Hello." --out brief.m4a
Scenes:     uv run tts.py --scenes scenes.json --out-dir public/vo
            scenes.json is [{"id": "intro", "text": "..."}, ...]; writes
            <id>.wav per scene plus manifest.json with each duration in seconds.

Prints a JSON result on stdout. Exits non-zero, with the reason on stderr, when
no engine can synthesize.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

MODELS = Path(os.environ.get("KOKORO_MODELS_DIR", Path.home() / ".cache/kokoro-onnx"))
MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0"
DEFAULT_KOKORO_VOICE = "am_michael"
DEFAULT_SAY_VOICE = "Daniel"

# Names espeak says wrong, as Kokoro phonemes. The text, captions and manifest
# keep the real spelling; only the sound changes. Engels as in Friedrich Engels
# (ENG-gulz), Yudame as in Spanish "ayudame" without the a (yoo-DAH-meh).
LEXICON = {
    "engels": "ˈɛŋɡəlz",
    "yudame": "judˈɑːmeɪ",
    "yuda.me": "judˈɑːmeɪ",
}
NAMES = re.compile(
    r"(?P<name>" + "|".join(re.escape(k) for k in sorted(LEXICON, key=len, reverse=True)) + r")(?P<pos>['’]s)?"
    r"|(?<=\w)\.(?=\w)",  # a dot inside a domain, said "dot"
    re.IGNORECASE,
)


def duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True,
        text=True,
        check=True,
    )
    return round(float(out.stdout.strip()), 3)


def to_format(wav: Path, out: Path) -> None:
    """Transcode a WAV to whatever the output extension asks for."""
    if out.suffix.lower() == ".wav":
        shutil.move(wav, out)
        return
    codec = {
        ".m4a": ["-c:a", "aac", "-b:a", "128k"],
        ".mp3": ["-c:a", "libmp3lame", "-q:a", "3"],
        ".ogg": ["-c:a", "libopus", "-b:a", "48k"],
    }.get(out.suffix.lower())
    if codec is None:
        sys.exit(f"Error: unsupported output extension {out.suffix} (use .wav, .m4a, .mp3 or .ogg)")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), *codec, str(out)], check=True)
    wav.unlink()


def splice(text: str, phonemize) -> str | None:
    """Phonemes for `text` with each LEXICON name said as listed, or None when
    no name occurs. `phonemize` strips its input, as kokoro's does, so the
    spaces around each piece are put back here."""
    out, plain, found = [], [], False

    def flush() -> None:
        piece = "".join(plain)
        plain.clear()
        if not piece.strip():
            out.append(" " if piece else "")
            return
        core = piece.strip()
        sound = core if re.fullmatch(r"[^\w\s]+", core) else phonemize(core)
        out.append((" " if piece[0].isspace() else "") + sound + (" " if piece[-1].isspace() else ""))

    at = 0
    for m in NAMES.finditer(text):
        plain.append(text[at : m.start()])
        at = m.end()
        if not m.group("name"):
            plain.append(" dot ")
            continue
        found = True
        flush()
        sound = LEXICON[m.group("name").lower()]
        if m.group("pos"):
            sound += "ᵻz" if sound.endswith(("s", "z")) else "z"
        if out and out[-1] and not out[-1].endswith(" "):
            out.append(" ")  # a name glued to the word before it, as in valorengels
        out.append(sound)
        if text[at : at + 1].isalnum():
            out.append(" ")
    plain.append(text[at:])
    flush()
    return re.sub(" +", " ", "".join(out)).strip() if found else None


class Kokoro:
    name = "kokoro"

    def __init__(self, voice: str):
        model, voices = MODELS / "kokoro-v1.0.onnx", MODELS / "voices-v1.0.bin"
        if not (model.exists() and voices.exists()):
            raise RuntimeError(
                f"Kokoro models missing in {MODELS}; download kokoro-v1.0.onnx and voices-v1.0.bin from {MODEL_URL}"
            )
        from kokoro_onnx import Kokoro as K  # imported late so `say` still works if this fails

        self.k, self.voice = K(str(model), str(voices)), voice or DEFAULT_KOKORO_VOICE
        self.lang = "en-gb" if self.voice.startswith("b") else "en-us"

    def wav(self, text: str, path: Path) -> None:
        import soundfile as sf

        phonemes = splice(text, lambda t: self.k.tokenizer.phonemize(t, self.lang))
        if phonemes is None:
            samples, rate = self.k.create(text, voice=self.voice, speed=1.0, lang=self.lang)
        else:
            samples, rate = self.k.create(phonemes, voice=self.voice, speed=1.0, lang=self.lang, is_phonemes=True)
        sf.write(str(path), samples, rate)


class Say:
    name = "say"

    def __init__(self, voice: str):
        if not shutil.which("say"):
            raise RuntimeError("macOS `say` not found")
        self.voice = voice or DEFAULT_SAY_VOICE

    def wav(self, text: str, path: Path) -> None:
        subprocess.run(["say", "-v", self.voice, "-o", str(path), "--data-format=LEI16@24000", text], check=True)


def engine(choice: str, voice: str):
    errors = []
    for cls in {"kokoro": [Kokoro], "say": [Say], "auto": [Kokoro, Say]}[choice]:
        try:
            # A voice name belongs to one engine; never hand a Kokoro voice to `say`.
            return cls(voice if (cls is Kokoro) == ("_" in (voice or "_")) else "")
        except Exception as e:  # noqa: BLE001 - any failure means try the next engine
            errors.append(f"{cls.name}: {e}")
            print(f"tts: {cls.name} unavailable ({e}), trying next engine", file=sys.stderr)
    sys.exit("Error: no TTS engine available. " + "; ".join(errors))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--text", help="text for a single clip")
    src.add_argument("--scenes", type=Path, help='JSON list of {"id", "text"}')
    p.add_argument("--out", type=Path, help="single-clip output (.wav, .m4a, .mp3, .ogg)")
    p.add_argument("--out-dir", type=Path, help="scene mode output directory")
    p.add_argument("--engine", choices=["auto", "kokoro", "say"], default="auto")
    p.add_argument(
        "--voice",
        default="",
        help=f"Kokoro voice (default {DEFAULT_KOKORO_VOICE}) or `say` voice (default {DEFAULT_SAY_VOICE})",
    )
    a = p.parse_args()

    tts = engine(a.engine, a.voice)
    if a.text is not None:
        if not a.out:
            p.error("--out is required with --text")
        a.out.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory() as tmp:
            wav = Path(tmp) / "clip.wav"
            tts.wav(a.text, wav)
            to_format(wav, a.out)
        print(json.dumps({"path": str(a.out), "seconds": duration(a.out), "engine": tts.name, "voice": tts.voice}))
        return

    if not a.out_dir:
        p.error("--out-dir is required with --scenes")
    a.out_dir.mkdir(parents=True, exist_ok=True)
    scenes = json.loads(a.scenes.read_text())
    manifest = {"engine": tts.name, "voice": tts.voice, "scenes": []}
    for s in scenes:
        path = a.out_dir / f"{s['id']}.wav"
        tts.wav(s["text"], path)
        manifest["scenes"].append({"id": s["id"], "file": path.name, "seconds": duration(path), "text": s["text"]})
    (a.out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(json.dumps(manifest))


if __name__ == "__main__":
    main()
