"""Recording-safe dataset manifests and audio loading for real-data ingestion."""
from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from math import gcd
from pathlib import Path
from typing import Iterable, Mapping

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

CLASSES = ("tap_knock", "shout", "rubble_settling", "background")
SPLITS = ("train", "validation", "test")
MANIFEST_FIELDS = ("path", "label", "source", "licence", "split", "recording_id")

_LABEL_ALIASES = {
    "tap_knock": "tap_knock",
    "door_wood_knock": "tap_knock",
    "knock": "tap_knock",
    "knocking": "tap_knock",
    "tap": "tap_knock",
    "thump": "tap_knock",
    "bang": "tap_knock",
    "click": "tap_knock",
    "mouse_click": "tap_knock",
    "keyboard": "tap_knock",
    "shout": "shout",
    "yell": "shout",
    "scream": "shout",
    "rubble_settling": "rubble_settling",
    "crack": "rubble_settling",
    "crumble": "rubble_settling",
    "rattle": "rubble_settling",
    "rock": "rubble_settling",
    "settling": "rubble_settling",
    "background": "background",
    "engine": "background",
    "engine_idling": "background",
    "generator": "background",
    "wind": "background",
    "chainsaw": "background",
    "drilling": "background",
    "jackhammer": "background",
    "pump": "background",
    "fan": "background",
    "valve": "background",
    "machinery": "background",
}


@dataclass(frozen=True)
class ManifestEntry:
    path: str
    label: str
    source: str
    licence: str
    split: str
    recording_id: str


def _normalize_label(value: str) -> str:
    return "_".join(value.strip().lower().replace("-", " ").split())


def map_label(value: str, source: str | None = None) -> str | None:
    """Map a dataset class/tag to one of the four project classes."""
    del source
    labels = [_LABEL_ALIASES.get(_normalize_label(part)) for part in value.replace(";", ",").split(",")]
    mapped = {label for label in labels if label is not None}
    return next((label for label in CLASSES if label in mapped), None)


def assign_splits(
    recording_ids: Iterable[str],
    seed: int = 1337,
    validation_fraction: float = 0.15,
    test_fraction: float = 0.15,
) -> list[str]:
    """Assign one deterministic split per recording, preserving input order."""
    if validation_fraction < 0 or test_fraction < 0 or validation_fraction + test_fraction >= 1:
        raise ValueError("Validation and test fractions must be non-negative and sum to less than 1.")

    ids = list(recording_ids)
    if any(not recording_id for recording_id in ids):
        raise ValueError("Every manifest record must have a recording_id.")

    unique_ids = list(dict.fromkeys(ids))
    rng = np.random.default_rng(seed)
    rng.shuffle(unique_ids)
    n = len(unique_ids)
    n_test = int(round(n * test_fraction))
    n_validation = int(round(n * validation_fraction))
    if n >= 3:
        n_test = max(1, n_test)
        n_validation = max(1, n_validation)
        if n_test + n_validation >= n:
            n_test = n_validation = 1

    assignments = {
        recording_id: (
            "test" if index < n_test else
            "validation" if index < n_test + n_validation else
            "train"
        )
        for index, recording_id in enumerate(unique_ids)
    }
    return [assignments[recording_id] for recording_id in ids]


def build_manifest(
    records: Iterable[Mapping[str, str]],
    destination: str | Path,
    seed: int = 1337,
) -> list[ManifestEntry]:
    """Validate, split by recording, and write normalized manifest rows."""
    normalized: list[dict[str, str]] = []
    split_by_recording: dict[str, str] = {}
    recording_order: list[str] = []
    seen_paths: set[str] = set()

    for record in records:
        row = {field: str(record.get(field, "")).strip() for field in MANIFEST_FIELDS}
        for field in ("path", "source", "licence", "recording_id"):
            if not row[field]:
                raise ValueError(f"Manifest record is missing required field '{field}'.")
        if row["path"] in seen_paths:
            raise ValueError(f"Duplicate manifest path: {row['path']}")
        seen_paths.add(row["path"])
        if row["recording_id"] not in recording_order:
            recording_order.append(row["recording_id"])

        label = map_label(row["label"], row["source"])
        if label is None:
            raise ValueError(f"Unmapped label '{row['label']}' for source '{row['source']}'.")
        row["label"] = label

        split = row["split"]
        if split and split not in SPLITS:
            raise ValueError(f"Unsupported split '{split}'; expected one of {SPLITS}.")
        if split:
            previous = split_by_recording.setdefault(row["recording_id"], split)
            if previous != split:
                raise ValueError(f"Recording '{row['recording_id']}' appears in multiple splits.")
        normalized.append(row)

    unsplit_recordings = [recording_id for recording_id in recording_order if recording_id not in split_by_recording]
    assigned = assign_splits(unsplit_recordings, seed=seed)
    split_by_recording.update(dict(zip(unsplit_recordings, assigned)))
    entries = [
        ManifestEntry(**{**row, "split": split_by_recording[row["recording_id"]]})
        for row in normalized
    ]

    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as manifest_file:
        writer = csv.DictWriter(manifest_file, fieldnames=MANIFEST_FIELDS)
        writer.writeheader()
        writer.writerows(asdict(entry) for entry in entries)
    return entries


def _official_fold_split(fold: str, source: str) -> str:
    try:
        fold_number = int(fold)
    except ValueError as exc:
        raise ValueError(f"Invalid fold '{fold}' for {source}.") from exc
    if source == "ESC-50":
        if fold_number not in range(1, 6):
            raise ValueError(f"ESC-50 fold must be between 1 and 5, got {fold_number}.")
        return "train" if fold_number <= 3 else "validation" if fold_number == 4 else "test"
    if source == "UrbanSound8K":
        if fold_number not in range(1, 11):
            raise ValueError(f"UrbanSound8K fold must be between 1 and 10, got {fold_number}.")
        return "train" if fold_number <= 8 else "validation" if fold_number == 9 else "test"
    raise ValueError(f"No official fold mapping is defined for {source}.")


def records_from_esc50(
    metadata_csv: str | Path,
    audio_root: str | Path,
    licence: str = "CC BY-NC; verify per-clip terms",
) -> list[dict[str, str]]:
    """Read labelled ESC-50 rows while keeping the dataset's official folds."""
    root = Path(audio_root)
    records = []
    with Path(metadata_csv).open(newline="", encoding="utf-8") as metadata_file:
        for row in csv.DictReader(metadata_file):
            label = map_label(row.get("category", ""), "ESC-50")
            if label is None:
                continue
            filename = row["filename"]
            path = root / filename
            records.append({
                "path": path.as_posix(),
                "label": label,
                "source": "ESC-50",
                "licence": row.get("licence") or row.get("license") or licence,
                "split": _official_fold_split(row["fold"], "ESC-50"),
                "recording_id": Path(filename).stem,
            })
    return records


def records_from_urbansound8k(
    metadata_csv: str | Path,
    audio_root: str | Path,
    licence: str = "CC BY-NC 3.0",
) -> list[dict[str, str]]:
    """Read UrbanSound8K metadata and preserve its official folds."""
    root = Path(audio_root)
    records = []
    with Path(metadata_csv).open(newline="", encoding="utf-8") as metadata_file:
        for row in csv.DictReader(metadata_file):
            label = map_label(row.get("class", ""), "UrbanSound8K")
            if label is None:
                continue
            filename = row["slice_file_name"]
            fold = row["fold"]
            records.append({
                "path": (root / f"fold{fold}" / filename).as_posix(),
                "label": label,
                "source": "UrbanSound8K",
                "licence": row.get("licence") or row.get("license") or licence,
                "split": _official_fold_split(fold, "UrbanSound8K"),
                "recording_id": row["fsID"],
            })
    return records


def records_from_fsd50k(
    metadata_csv: str | Path,
    audio_root: str | Path,
    split: str = "",
) -> list[dict[str, str]]:
    """Read FSD50K clip metadata; per-clip licence is required to avoid licence guessing."""
    if split and split not in SPLITS:
        raise ValueError(f"Unsupported split '{split}'; expected one of {SPLITS}.")
    root = Path(audio_root)
    records = []
    with Path(metadata_csv).open(newline="", encoding="utf-8") as metadata_file:
        for row in csv.DictReader(metadata_file):
            label = map_label(row.get("labels", ""), "FSD50K")
            if label is None:
                continue
            licence = row.get("licence") or row.get("license")
            if not licence:
                raise ValueError(f"FSD50K clip '{row.get('fname', '')}' has no licence metadata.")
            filename = row["fname"]
            if Path(filename).suffix.lower() != ".wav":
                filename = f"{filename}.wav"
            records.append({
                "path": (root / filename).as_posix(),
                "label": label,
                "source": "FSD50K",
                "licence": licence,
                "split": split or row.get("split", ""),
                "recording_id": Path(filename).stem,
            })
    return records


def records_from_mimii(
    audio_root: str | Path,
    licence: str = "CC BY-SA 4.0",
) -> list[dict[str, str]]:
    """Treat machine recordings as background and group splits by machine identity."""
    root = Path(audio_root)
    records = []
    for path in sorted(root.rglob("*.wav")):
        relative = path.relative_to(root)
        machine = next((part for part in relative.parts if part.startswith("id_")), None)
        if machine is not None:
            machine_index = relative.parts.index(machine)
            recording_id = "/".join(relative.parts[:machine_index + 1])
        else:
            recording_id = "/".join(relative.parts[:-1]) or relative.stem
        records.append({
            "path": path.as_posix(),
            "label": "background",
            "source": "MIMII",
            "licence": licence,
            "split": "",
            "recording_id": recording_id,
        })
    return records


def read_manifest(path: str | Path) -> list[dict[str, str]]:
    """Read and validate a previously generated manifest."""
    with Path(path).open(newline="", encoding="utf-8") as manifest_file:
        reader = csv.DictReader(manifest_file)
        if reader.fieldnames != list(MANIFEST_FIELDS):
            raise ValueError(f"Manifest columns must be {list(MANIFEST_FIELDS)}.")
        rows = list(reader)
    if any(row["split"] not in SPLITS or row["label"] not in CLASSES for row in rows):
        raise ValueError("Manifest contains an unsupported label or split.")
    return rows


def load_audio16k(path: str | Path, target_sr: int = 16000) -> np.ndarray:
    """Load a WAV file as mono float32 at the requested sample rate."""
    if target_sr <= 0:
        raise ValueError("target_sr must be positive.")
    audio, sample_rate = sf.read(path, dtype="float32", always_2d=True)
    if sample_rate <= 0:
        raise ValueError("Audio sample rate must be positive.")
    mono = audio.mean(axis=1, dtype=np.float32)
    if sample_rate != target_sr:
        divisor = gcd(sample_rate, target_sr)
        mono = resample_poly(mono, target_sr // divisor, sample_rate // divisor).astype(np.float32)
    return np.asarray(mono, dtype=np.float32)
