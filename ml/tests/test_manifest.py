import csv

import numpy as np
import pytest
import soundfile as sf

from rubble_ear.manifest import (
    assign_splits,
    build_manifest,
    load_audio16k,
    map_label,
    records_from_esc50,
    records_from_fsd50k,
    records_from_mimii,
    read_manifest,
)


def test_map_dataset_labels_to_project_classes():
    assert map_label("door_wood_knock", "ESC-50") == "tap_knock"
    assert map_label("Shout", "FSD50K") == "shout"
    assert map_label("Crumble", "FSD50K") == "rubble_settling"
    assert map_label("engine", "ESC-50") == "background"
    assert map_label("unmapped", "ESC-50") is None


def test_assign_splits_keeps_recordings_together_and_is_deterministic():
    recording_ids = [f"recording-{i}" for i in range(30)] + ["shared", "shared"]
    first = assign_splits(recording_ids, seed=17)
    second = assign_splits(recording_ids, seed=17)

    assert first == second
    assert first[-1] == first[-2]
    assert {"train", "validation", "test"} <= set(first)
    assert len({split for recording, split in zip(recording_ids, first) if recording == "shared"}) == 1


def test_build_and_read_manifest(tmp_path):
    records = [
        {
            "path": f"data/processed/clip-{i}.wav",
            "label": "tap_knock",
            "source": "fixture",
            "licence": "MIT",
            "recording_id": f"recording-{i // 2}",
        }
        for i in range(20)
    ]
    path = tmp_path / "manifest.csv"

    written = build_manifest(records, path, seed=5)
    loaded = read_manifest(path)

    assert len(written) == len(loaded) == len(records)
    assert all(row["recording_id"] == entry.recording_id for row, entry in zip(loaded, written))
    splits_by_recording = {}
    for row in loaded:
        splits_by_recording.setdefault(row["recording_id"], row["split"])
        assert splits_by_recording[row["recording_id"]] == row["split"]
    with path.open(newline="", encoding="utf-8") as manifest_file:
        assert next(csv.reader(manifest_file)) == [
            "path",
            "label",
            "source",
            "licence",
            "split",
            "recording_id",
        ]


def test_manifest_rejects_recording_split_leakage(tmp_path):
    records = [
        {
            "path": f"clip-{i}.wav",
            "label": "background",
            "source": "fixture",
            "licence": "MIT",
            "split": split,
            "recording_id": "shared-recording",
        }
        for i, split in enumerate(("train", "test"))
    ]

    with pytest.raises(ValueError, match="appears in multiple splits"):
        build_manifest(records, tmp_path / "manifest.csv")


def test_esc50_loader_uses_official_folds_and_skips_unmapped_classes(tmp_path):
    metadata = tmp_path / "esc50.csv"
    metadata.write_text(
        "filename,fold,category\n"
        "knock.wav,5,door_wood_knock\n"
        "engine.wav,1,engine\n"
        "dog.wav,3,dog\n",
        encoding="utf-8",
    )

    records = records_from_esc50(metadata, tmp_path / "audio")

    assert [(record["label"], record["split"]) for record in records] == [
        ("tap_knock", "test"),
        ("background", "train"),
    ]


def test_fsd50k_requires_per_clip_licence(tmp_path):
    metadata = tmp_path / "fsd.csv"
    metadata.write_text(
        "fname,labels,license\n1,Shout,CC BY 4.0\n2,Engine,\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="has no licence metadata"):
        records_from_fsd50k(metadata, tmp_path / "audio")


def test_mimii_loader_groups_clips_by_machine(tmp_path):
    audio_root = tmp_path / "mimii"
    (audio_root / "pump" / "id_00" / "normal").mkdir(parents=True)
    (audio_root / "pump" / "id_00" / "normal" / "clip.wav").touch()

    records = records_from_mimii(audio_root)

    assert len(records) == 1
    assert records[0]["label"] == "background"
    assert records[0]["recording_id"] == "pump/id_00"


def test_load_audio_resamples_to_mono_float32(tmp_path):
    source = tmp_path / "stereo.wav"
    signal = np.column_stack((np.ones(160), np.zeros(160))).astype(np.float32)
    sf.write(source, signal, 8000)

    audio = load_audio16k(source)

    assert audio.dtype == np.float32
    assert audio.shape == (320,)
    assert np.isfinite(audio).all()
