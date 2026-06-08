from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from http import HTTPStatus
from pathlib import Path
from zipfile import BadZipFile, ZipFile


REPO_ROOT = Path(__file__).resolve().parents[3]
SOURCE_ROOT = REPO_ROOT / "background" / "four_pillars"
OUTPUT_PATH = REPO_ROOT / "features" / "four_pillars" / "knowledge" / "lesson-based-knowledge.md"
TOOL_ROOT = Path(__file__).resolve().parent
OCR_SWIFT = TOOL_ROOT / "ocr_image.swift"

DRAWING_NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
SLIDE_PATTERN = re.compile(r"ppt/slides/slide(\d+)\.xml$")
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}
AUDIO_SUFFIXES = {".mp3", ".wav", ".m4a", ".wma", ".aac"}


@dataclass
class SlideExtraction:
    slide_number: int
    text_blocks: list[str] = field(default_factory=list)
    note_blocks: list[str] = field(default_factory=list)
    image_paths: list[str] = field(default_factory=list)
    ocr_blocks: list[str] = field(default_factory=list)
    ocr_errors: list[str] = field(default_factory=list)


@dataclass
class AudioExtraction:
    media_path: str
    extension: str
    size_bytes: int
    duration: str | None = None
    transcript_status: str = "not_attempted"
    transcript: str = ""
    error: str | None = None
    transcript_provider: str | None = None
    transcript_model: str | None = None
    transcript_elapsed_seconds: float | None = None
    transcript_confidence: str | None = None
    transcript_quality: str | None = None


@dataclass
class LessonExtraction:
    file_name: str
    status: str
    error: str | None = None
    slides: list[SlideExtraction] = field(default_factory=list)
    images_total: int = 0
    audio: list[AudioExtraction] = field(default_factory=list)


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract Four Pillars PPTX lessons into markdown.")
    parser.add_argument("--source", type=Path, default=SOURCE_ROOT)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--skip-ocr", action="store_true")
    parser.add_argument("--skip-audio-transcript", action="store_true")
    parser.add_argument(
        "--audio-transcriber",
        choices=("whisper", "bailian", "auto"),
        default="whisper",
        help="Audio transcription backend. Bailian uses the admin-configured DashScope/Bailian API key.",
    )
    parser.add_argument("--bailian-asr-model", default="qwen3-asr-flash")
    parser.add_argument("--ocr-limit", type=int, default=0, help="Limit OCR images per file. 0 means no limit.")
    args = parser.parse_args()

    started_at = time.strftime("%Y-%m-%d %H:%M:%S")
    lessons = [
        extract_lesson(
            path,
            skip_ocr=args.skip_ocr,
            skip_audio_transcript=args.skip_audio_transcript,
            audio_transcriber=args.audio_transcriber,
            bailian_asr_model=args.bailian_asr_model,
            ocr_limit=args.ocr_limit,
        )
        for path in sorted(args.source.glob("*.pptx"))
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_markdown(lessons, started_at=started_at), encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


def extract_lesson(
    path: Path,
    *,
    skip_ocr: bool,
    skip_audio_transcript: bool,
    audio_transcriber: str,
    bailian_asr_model: str,
    ocr_limit: int,
) -> LessonExtraction:
    lesson = LessonExtraction(file_name=path.name, status="ok")
    try:
        with ZipFile(path) as deck:
            names = deck.namelist()
            slide_names = sorted(
                [name for name in names if SLIDE_PATTERN.match(name)],
                key=lambda item: int(SLIDE_PATTERN.match(item).group(1)),  # type: ignore[union-attr]
            )
            lesson.images_total = sum(1 for name in names if Path(name).suffix.lower() in IMAGE_SUFFIXES and name.startswith("ppt/media/"))
            media_by_slide = build_slide_media_map(deck)
            notes_by_slide = extract_notes(deck)
            ocr_by_image = extract_ocr(deck, media_by_slide, skip_ocr=skip_ocr, ocr_limit=ocr_limit)

            for slide_name in slide_names:
                slide_number = int(SLIDE_PATTERN.match(slide_name).group(1))  # type: ignore[union-attr]
                image_paths = media_by_slide.get(slide_number, [])
                slide = SlideExtraction(
                    slide_number=slide_number,
                    text_blocks=extract_text_blocks(deck.read(slide_name)),
                    note_blocks=notes_by_slide.get(slide_number, []),
                    image_paths=image_paths,
                )
                for image_path in image_paths:
                    ocr_result = ocr_by_image.get(image_path)
                    if not ocr_result:
                        continue
                    if ocr_result.get("status") == "ok" and str(ocr_result.get("text") or "").strip():
                        slide.ocr_blocks.append(str(ocr_result["text"]).strip())
                    elif ocr_result.get("status") != "skipped":
                        slide.ocr_errors.append(f"{image_path}: {ocr_result.get('error') or ocr_result.get('status')}")
                lesson.slides.append(slide)

            lesson.audio = extract_audio(
                deck,
                skip_transcript=skip_audio_transcript,
                transcriber=audio_transcriber,
                bailian_asr_model=bailian_asr_model,
            )
    except BadZipFile:
        lesson.status = "invalid_pptx_zip"
        lesson.error = "not_a_valid_ooxml_zip"
    except Exception as exc:  # keep extraction resilient across imperfect course files
        lesson.status = "failed"
        lesson.error = f"{type(exc).__name__}: {exc}"
    return lesson


def extract_text_blocks(xml_bytes: bytes) -> list[str]:
    root = ET.fromstring(xml_bytes)
    paragraphs: list[str] = []
    for paragraph in root.findall(".//a:p", DRAWING_NS):
        runs = [(node.text or "").strip() for node in paragraph.findall(".//a:t", DRAWING_NS)]
        text = "".join(part for part in runs if part)
        if text:
            paragraphs.append(text)
    return paragraphs


def build_slide_media_map(deck: ZipFile) -> dict[int, list[str]]:
    result: dict[int, list[str]] = {}
    for rel_name in deck.namelist():
        match = re.match(r"ppt/slides/_rels/slide(\d+)\.xml\.rels$", rel_name)
        if not match:
            continue
        slide_number = int(match.group(1))
        root = ET.fromstring(deck.read(rel_name))
        media_paths: list[str] = []
        for rel in root:
            target = str(rel.attrib.get("Target", ""))
            if not target.startswith("../media/"):
                continue
            normalized = f"ppt/media/{Path(target).name}"
            if Path(normalized).suffix.lower() in IMAGE_SUFFIXES:
                media_paths.append(normalized)
        result[slide_number] = media_paths
    return result


def extract_notes(deck: ZipFile) -> dict[int, list[str]]:
    notes_by_slide: dict[int, list[str]] = {}
    slide_to_notes: dict[int, str] = {}
    rel_ns = {"r": "http://schemas.openxmlformats.org/package/2006/relationships"}
    for rel_name in deck.namelist():
        match = re.match(r"ppt/slides/_rels/slide(\d+)\.xml\.rels$", rel_name)
        if not match:
            continue
        root = ET.fromstring(deck.read(rel_name))
        for rel in root.findall("r:Relationship", rel_ns):
            if "notesSlide" in str(rel.attrib.get("Type", "")):
                target = str(rel.attrib.get("Target", ""))
                slide_to_notes[int(match.group(1))] = f"ppt/notesSlides/{Path(target).name}"

    for slide_number, note_path in slide_to_notes.items():
        if note_path in deck.namelist():
            notes_by_slide[slide_number] = extract_text_blocks(deck.read(note_path))
    return notes_by_slide


def extract_ocr(deck: ZipFile, media_by_slide: dict[int, list[str]], *, skip_ocr: bool, ocr_limit: int) -> dict[str, dict[str, str]]:
    image_paths: list[str] = []
    for paths in media_by_slide.values():
        for path in paths:
            if path not in image_paths:
                image_paths.append(path)
    if skip_ocr:
        return {path: {"status": "skipped", "error": "skip_ocr_enabled"} for path in image_paths}
    if not image_paths:
        return {}
    if not OCR_SWIFT.exists() or shutil.which("swift") is None:
        return {path: {"status": "failed", "error": "vision_ocr_unavailable"} for path in image_paths}
    if ocr_limit > 0:
        skipped = image_paths[ocr_limit:]
        image_paths = image_paths[:ocr_limit]
    else:
        skipped = []

    results: dict[str, dict[str, str]] = {path: {"status": "skipped", "error": "ocr_limit"} for path in skipped}
    with tempfile.TemporaryDirectory(prefix="four-pillars-ocr-") as tmp_dir:
        tmp_root = Path(tmp_dir)
        tmp_paths: list[Path] = []
        source_by_tmp: dict[str, str] = {}
        for image_path in image_paths:
            tmp_path = tmp_root / Path(image_path).name
            tmp_path.write_bytes(deck.read(image_path))
            tmp_paths.append(tmp_path)
            source_by_tmp[str(tmp_path)] = image_path
        proc = subprocess.run(
            ["swift", str(OCR_SWIFT), *[str(path) for path in tmp_paths]],
            text=True,
            capture_output=True,
            check=False,
            timeout=180,
        )
        if proc.returncode != 0:
            return {path: {"status": "failed", "error": "vision_ocr_failed"} for path in image_paths}
        for line in proc.stdout.splitlines():
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            source = source_by_tmp.get(str(payload.get("path") or ""))
            if source:
                results[source] = {
                    "status": str(payload.get("status") or "failed"),
                    "text": str(payload.get("text") or ""),
                    "error": str(payload.get("error") or ""),
                }
    return results


def extract_audio(deck: ZipFile, *, skip_transcript: bool, transcriber: str, bailian_asr_model: str) -> list[AudioExtraction]:
    audio_items: list[AudioExtraction] = []
    for media_path in sorted(name for name in deck.namelist() if name.startswith("ppt/media/") and Path(name).suffix.lower() in AUDIO_SUFFIXES):
        data = deck.read(media_path)
        audio = AudioExtraction(
            media_path=media_path,
            extension=Path(media_path).suffix.lower().lstrip("."),
            size_bytes=len(data),
        )
        audio.duration = probe_audio_duration(media_path, data)
        if skip_transcript:
            audio.transcript_status = "skipped"
            audio.error = "skip_audio_transcript_enabled"
        else:
            transcript, status, error, metadata = transcribe_audio(media_path, data, transcriber=transcriber, bailian_asr_model=bailian_asr_model)
            audio.transcript = transcript
            audio.transcript_status = status
            audio.error = error
            audio.transcript_provider = metadata.get("provider")
            audio.transcript_model = metadata.get("model")
            audio.transcript_elapsed_seconds = metadata.get("elapsed_seconds")
            audio.transcript_confidence = metadata.get("confidence")
            audio.transcript_quality = metadata.get("quality")
        audio_items.append(audio)
    return audio_items


def probe_audio_duration(media_path: str, data: bytes) -> str | None:
    if shutil.which("afinfo") is None:
        return None
    with tempfile.TemporaryDirectory(prefix="four-pillars-audio-") as tmp_dir:
        tmp_path = Path(tmp_dir) / Path(media_path).name
        tmp_path.write_bytes(data)
        proc = subprocess.run(["afinfo", str(tmp_path)], text=True, capture_output=True, check=False, timeout=30)
    if proc.returncode != 0:
        return None
    match = re.search(r"estimated duration:\s*([0-9.]+ sec)", proc.stdout)
    return match.group(1) if match else None


def transcribe_audio(media_path: str, data: bytes, *, transcriber: str, bailian_asr_model: str) -> tuple[str, str, str | None, dict[str, object]]:
    normalized_transcriber = transcriber.strip().lower() or "whisper"
    if normalized_transcriber == "bailian":
        return transcribe_audio_with_bailian(media_path, data, model=bailian_asr_model)
    if normalized_transcriber == "auto":
        transcript, status, error, metadata = transcribe_audio_with_bailian(media_path, data, model=bailian_asr_model)
        if status in {"ok", "empty"}:
            return transcript, status, error, metadata
        whisper_transcript, whisper_status, whisper_error, whisper_metadata = transcribe_audio_with_whisper(media_path, data)
        if whisper_status == "ok":
            return whisper_transcript, whisper_status, whisper_error, whisper_metadata
        return transcript, status, error, metadata
    return transcribe_audio_with_whisper(media_path, data)


def transcribe_audio_with_whisper(media_path: str, data: bytes) -> tuple[str, str, str | None, dict[str, object]]:
    started = time.monotonic()
    whisper_cli = shutil.which("whisper") or shutil.which("mlx_whisper")
    metadata: dict[str, object] = {"provider": "whisper_cli", "model": Path(whisper_cli).name if whisper_cli else "unavailable"}
    if whisper_cli is None:
        metadata["elapsed_seconds"] = round(time.monotonic() - started, 3)
        return "", "unavailable", "whisper_cli_unavailable", metadata

    with tempfile.TemporaryDirectory(prefix="four-pillars-transcribe-") as tmp_dir:
        tmp_root = Path(tmp_dir)
        audio_path = tmp_root / Path(media_path).name
        audio_path.write_bytes(data)
        try:
            if Path(whisper_cli).name == "mlx_whisper":
                proc = subprocess.run(
                    [whisper_cli, str(audio_path), "--language", "Chinese", "--output-dir", str(tmp_root)],
                    text=True,
                    capture_output=True,
                    check=False,
                    timeout=1800,
                )
            else:
                proc = subprocess.run(
                    [whisper_cli, str(audio_path), "--language", "Chinese", "--output_format", "txt", "--output_dir", str(tmp_root)],
                    text=True,
                    capture_output=True,
                    check=False,
                    timeout=1800,
                )
        except subprocess.TimeoutExpired:
            metadata["elapsed_seconds"] = round(time.monotonic() - started, 3)
            return "", "failed", "transcription_timeout", metadata
        if proc.returncode != 0:
            metadata["elapsed_seconds"] = round(time.monotonic() - started, 3)
            return "", "failed", "transcription_command_failed", metadata
        txt_files = sorted(tmp_root.glob("*.txt"))
        if not txt_files:
            metadata["elapsed_seconds"] = round(time.monotonic() - started, 3)
            return "", "failed", "transcription_output_missing", metadata
        metadata["elapsed_seconds"] = round(time.monotonic() - started, 3)
        transcript = txt_files[0].read_text(encoding="utf-8", errors="ignore").strip()
        metadata["quality"] = classify_audio_transcript_quality(transcript)
        return transcript, "ok", None, metadata


def transcribe_audio_with_bailian(media_path: str, data: bytes, *, model: str) -> tuple[str, str, str | None, dict[str, object]]:
    started = time.monotonic()
    metadata: dict[str, object] = {"provider": "bailian", "model": model, "confidence": "not_provided"}
    try:
        import dashscope  # type: ignore[import-not-found]
    except ImportError:
        metadata["elapsed_seconds"] = round(time.monotonic() - started, 3)
        return "", "unavailable", "dashscope_sdk_unavailable", metadata

    api_key = resolve_bailian_api_key()
    if not api_key:
        metadata["elapsed_seconds"] = round(time.monotonic() - started, 3)
        return "", "unavailable", "bailian_api_key_unavailable", metadata

    with tempfile.TemporaryDirectory(prefix="four-pillars-bailian-asr-") as tmp_dir:
        tmp_root = Path(tmp_dir)
        source_path = tmp_root / Path(media_path).name
        source_path.write_bytes(data)
        audio_path, prepare_error = prepare_bailian_asr_audio(source_path)
        if prepare_error:
            metadata["elapsed_seconds"] = round(time.monotonic() - started, 3)
            return "", "failed", prepare_error, metadata
        if audio_path.stat().st_size > 10 * 1024 * 1024:
            metadata["elapsed_seconds"] = round(time.monotonic() - started, 3)
            return "", "failed", "bailian_asr_audio_exceeds_10mb_after_prepare", metadata

        try:
            response = dashscope.MultiModalConversation.call(
                api_key=api_key,
                model=model,
                messages=[{"role": "user", "content": [{"audio": "file://" + str(audio_path.resolve())}]}],
                result_format="message",
                asr_options={"language": "zh", "enable_itn": False},
            )
        except Exception as exc:
            metadata["elapsed_seconds"] = round(time.monotonic() - started, 3)
            return "", "failed", f"bailian_asr_exception:{type(exc).__name__}", metadata

    metadata["elapsed_seconds"] = round(time.monotonic() - started, 3)
    if getattr(response, "status_code", None) != HTTPStatus.OK:
        code = str(getattr(response, "code", "") or "unknown")
        message = str(getattr(response, "message", "") or "").strip()
        error = f"bailian_asr_http_{getattr(response, 'status_code', 'unknown')}:{code}"
        if message:
            error = f"{error}:{message[:160]}"
        return "", "failed", error, metadata

    transcript = extract_bailian_asr_text(getattr(response, "output", None)).strip()
    if not transcript:
        metadata["quality"] = "empty"
        return "", "empty", "bailian_asr_empty_text", metadata
    metadata["quality"] = classify_audio_transcript_quality(transcript)
    return transcript, "ok", None, metadata


def resolve_bailian_api_key() -> str:
    try:
        if str(REPO_ROOT) not in sys.path:
            sys.path.insert(0, str(REPO_ROOT))
        from product.backend.api.config import get_bailian_tts_api_key

        return str(get_bailian_tts_api_key() or "").strip()
    except Exception:
        return ""


def prepare_bailian_asr_audio(source_path: Path) -> tuple[Path, str | None]:
    if shutil.which("afconvert") is None:
        return source_path, None
    converted_path = source_path.with_name(f"{source_path.stem}_16k_mono.wav")
    proc = subprocess.run(
        ["afconvert", str(source_path), str(converted_path), "-f", "WAVE", "-d", "LEI16@16000", "-c", "1"],
        text=True,
        capture_output=True,
        check=False,
        timeout=120,
    )
    if proc.returncode == 0 and converted_path.exists() and converted_path.stat().st_size > 0:
        return converted_path, None
    if source_path.stat().st_size <= 10 * 1024 * 1024:
        return source_path, None
    return source_path, "bailian_asr_audio_prepare_failed"


def extract_bailian_asr_text(output: object) -> str:
    if output is None:
        return ""
    try:
        output_data = json.loads(json.dumps(output, ensure_ascii=False))
    except TypeError:
        output_data = output
    if not isinstance(output_data, dict):
        return str(output_data or "")
    direct_text = output_data.get("text")
    if isinstance(direct_text, str) and direct_text.strip():
        return direct_text
    parts: list[str] = []
    choices = output_data.get("choices")
    if isinstance(choices, list):
        for choice in choices:
            if not isinstance(choice, dict):
                continue
            message = choice.get("message")
            if not isinstance(message, dict):
                continue
            content = message.get("content")
            if isinstance(content, str):
                parts.append(content)
            elif isinstance(content, list):
                for item in content:
                    if not isinstance(item, dict):
                        continue
                    for key in ("text", "transcript"):
                        text = item.get(key)
                        if isinstance(text, str) and text.strip():
                            parts.append(text)
                            break
    return "\n".join(part.strip() for part in parts if part.strip())


def classify_audio_transcript_quality(transcript: str) -> str:
    normalized = re.sub(r"[\s。！？!?,，、；;：:….\-—_~`'\"“”‘’（）()\[\]{}]+", "", transcript or "")
    if not normalized:
        return "empty"
    low_information_chars = set("啊嗯噔咚啦呃哦唔哼")
    unique_chars = set(normalized)
    if unique_chars.issubset(low_information_chars):
        return "low_information_audio"
    if len(normalized) <= 12 and len(unique_chars) <= 3:
        return "low_information_audio"
    return "usable_lesson_text"


def render_markdown(lessons: list[LessonExtraction], *, started_at: str) -> str:
    total_slides = sum(len(lesson.slides) for lesson in lessons)
    total_audio = sum(len(lesson.audio) for lesson in lessons)
    total_audio_transcribed = sum(1 for lesson in lessons for audio in lesson.audio if audio.transcript_status == "ok")
    total_audio_low_information = sum(1 for lesson in lessons for audio in lesson.audio if audio.transcript_quality == "low_information_audio")
    total_ocr_blocks = sum(len(slide.ocr_blocks) for lesson in lessons for slide in lesson.slides)
    lines = [
        "# Four Pillars Lesson-Based Knowledge",
        "",
        f"Generated at: `{started_at}`",
        "",
        "## Extraction Summary",
        "",
        f"- Source directory: `{SOURCE_ROOT}`",
        f"- Lesson files: {len(lessons)}",
        f"- Parsed slides: {total_slides}",
        f"- OCR text blocks: {total_ocr_blocks}",
        f"- Embedded audio files: {total_audio}",
        f"- Audio transcripts: {total_audio_transcribed}",
        f"- Low-information audio transcripts: {total_audio_low_information}",
        "",
        "## File Inventory",
        "",
        "| File | Status | Slides | Images | Audio | Notes |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for lesson in lessons:
        note = lesson.error or ""
        lines.append(
            f"| {escape_md(lesson.file_name)} | `{lesson.status}` | {len(lesson.slides)} | {lesson.images_total} | {len(lesson.audio)} | {escape_md(note)} |"
        )

    lines.extend(["", "## Lessons", ""])
    for lesson in lessons:
        lines.extend([f"### {lesson.file_name}", "", f"- status: `{lesson.status}`"])
        if lesson.error:
            lines.append(f"- extraction_error: `{lesson.error}`")
        lines.append("")

        if lesson.audio:
            lines.extend(["#### Embedded Audio", ""])
            for index, audio in enumerate(lesson.audio, start=1):
                lines.extend(
                    [
                        f"##### Audio {index}: `{audio.media_path}`",
                        "",
                        f"- format: `{audio.extension}`",
                        f"- size_bytes: {audio.size_bytes}",
                        f"- duration: {audio.duration or 'unknown'}",
                        f"- transcript_status: `{audio.transcript_status}`",
                    ]
                )
                if audio.transcript_provider:
                    lines.append(f"- transcript_provider: `{audio.transcript_provider}`")
                if audio.transcript_model:
                    lines.append(f"- transcript_model: `{audio.transcript_model}`")
                if audio.transcript_elapsed_seconds is not None:
                    lines.append(f"- transcript_elapsed_seconds: {audio.transcript_elapsed_seconds}")
                if audio.transcript_confidence:
                    lines.append(f"- transcript_confidence: `{audio.transcript_confidence}`")
                if audio.transcript_quality:
                    lines.append(f"- transcript_quality: `{audio.transcript_quality}`")
                if audio.error:
                    lines.append(f"- transcript_error: `{audio.error}`")
                if audio.transcript:
                    lines.extend(["", audio.transcript, ""])
                else:
                    lines.append("")

        for slide in lesson.slides:
            lines.extend([f"#### Slide {slide.slide_number}", ""])
            if slide.text_blocks:
                lines.extend(["##### PPT Text", ""])
                lines.extend(f"- {block}" for block in slide.text_blocks)
                lines.append("")
            if slide.note_blocks:
                lines.extend(["##### Notes", ""])
                lines.extend(f"- {block}" for block in slide.note_blocks)
                lines.append("")
            if slide.ocr_blocks:
                lines.extend(["##### OCR Text", ""])
                for block in slide.ocr_blocks:
                    lines.extend([block, ""])
            if slide.ocr_errors:
                lines.extend(["##### OCR Issues", ""])
                lines.extend(f"- `{item}`" for item in slide.ocr_errors)
                lines.append("")
            if not slide.text_blocks and not slide.note_blocks and not slide.ocr_blocks:
                lines.extend(["_No extractable text captured for this slide._", ""])

    lines.extend(
        [
            "## Productization Notes",
            "",
            "- This file is a source-derived knowledge dump, not the final prompt pack.",
            "- Move stable rules into structured knowledge packs before using them in production prompts.",
            "- Keep course/source wording out of user-facing model outputs.",
            "",
        ]
    )
    return "\n".join(lines)


def escape_md(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
