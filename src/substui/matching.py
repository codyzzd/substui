from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Any

from guessit import guessit

ARTICLES = {
    "a",
    "an",
    "as",
    "das",
    "de",
    "do",
    "dos",
    "el",
    "la",
    "las",
    "le",
    "les",
    "o",
    "os",
    "the",
    "un",
    "une",
}


@dataclass(frozen=True, slots=True)
class MatchQuality:
    confidence: int
    label: str
    compatible: bool
    reasons: tuple[str, ...]


def normalize_title(value: str) -> str:
    text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    words = re.findall(r"[a-z0-9]+", text.lower())
    meaningful = [word for word in words if word not in ARTICLES]
    return " ".join(meaningful or words)


def title_similarity(left: str, right: str) -> float:
    left_normalized = normalize_title(left)
    right_normalized = normalize_title(right)
    if not left_normalized or not right_normalized:
        return 0.0
    sequence = SequenceMatcher(None, left_normalized, right_normalized).ratio()
    left_words = set(left_normalized.split())
    right_words = set(right_normalized.split())
    token_f1 = 2 * len(left_words & right_words) / (len(left_words) + len(right_words))
    return max(sequence, token_f1)


def rank_match(video: Any, release: str, matches: tuple[str, ...]) -> MatchQuality:
    """Turn Subliminal's technical matches into a user-facing confidence rank."""
    match_set = set(matches)
    if "hash" in match_set:
        return MatchQuality(100, "EXATO", True, ("hash do arquivo",))

    is_episode = hasattr(video, "series")
    kind = "episode" if is_episode else "movie"
    guessed = dict(guessit(release, {"type": kind})) if not release.isdecimal() else {}
    reasons: list[str] = []
    confidence = 0
    incompatible = False

    identity_key = "series" if is_episode else "title"
    video_title = str(getattr(video, identity_key, "") or "")
    guessed_title = str(guessed.get("title", "") or "")

    if identity_key in match_set:
        confidence += 45
        reasons.append("título")
    if {"imdb_id", "tmdb_id"} & match_set:
        confidence = max(confidence, 70)
        reasons.append("ID do filme")

    if guessed_title and video_title:
        similarity = title_similarity(video_title, guessed_title)
        if similarity >= 0.90:
            confidence += 15
            reasons.append("nome exato")
        elif similarity >= 0.70:
            confidence += 8
            reasons.append("nome parecido")
        elif similarity < 0.62 and not ({"imdb_id", "tmdb_id"} & match_set):
            confidence -= 35
            reasons.append("título divergente")

    video_year = getattr(video, "year", None)
    guessed_year = guessed.get("year")
    if guessed_year and video_year:
        if int(guessed_year) == int(video_year):
            confidence += 20
            reasons.append(str(video_year))
        else:
            confidence -= 60
            incompatible = True
            reasons.append(f"ano diferente ({guessed_year})")
    elif "year" in match_set:
        confidence += 20
        reasons.append(str(video_year or "ano"))

    if is_episode:
        for field, points, label in (
            ("season", 12, "temporada"),
            ("episode", 18, "episódio"),
        ):
            guessed_value = guessed.get(field)
            video_value = getattr(video, field, None)
            if field in match_set:
                confidence += points
                reasons.append(label)
            if guessed_value is not None and video_value is not None and guessed_value != video_value:
                incompatible = True
                confidence -= 50
                reasons.append(f"{label} diferente")

    guessed_technical = {
        "source": guessed.get("source"),
        "resolution": guessed.get("screen_size"),
        "video_codec": guessed.get("video_codec"),
    }
    for field, guessed_value in guessed_technical.items():
        video_value = getattr(video, field, None)
        if guessed_value and video_value and str(guessed_value).lower() != str(video_value).lower():
            penalty = 10 if field == "source" else 2
            confidence -= penalty
            label = {"source": "fonte", "resolution": "resolução", "video_codec": "vídeo"}[field]
            reasons.append(f"{label} diferente ({guessed_value})")

    technical = (
        ("release_group", 6, "grupo"),
        ("streaming_service", 5, "streaming"),
        ("source", 5, "fonte"),
        ("fps", 3, "FPS"),
        ("audio_codec", 3, "áudio"),
        ("resolution", 3, "resolução"),
        ("video_codec", 3, "vídeo"),
    )
    for field, points, label in technical:
        if field in match_set:
            confidence += points
            reasons.append(label)

    confidence = max(0, min(100, confidence))
    compatible = not incompatible and confidence >= 60
    if confidence >= 90:
        label = "ÓTIMO"
    elif confidence >= 75:
        label = "BOM"
    elif confidence >= 60:
        label = "POSSÍVEL"
    else:
        label = "BAIXO"
    return MatchQuality(confidence, label, compatible, tuple(dict.fromkeys(reasons)))

