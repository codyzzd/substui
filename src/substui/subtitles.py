from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from substui.matching import rank_match


@dataclass(slots=True)
class SubtitleCandidate:
    key: str
    provider: str
    language: str
    score: int
    confidence: int
    rank_label: str
    compatible: bool
    reasons: tuple[str, ...]
    matches: tuple[str, ...]
    release: str
    raw: Any


@dataclass(slots=True)
class SearchResult:
    video: Any
    candidates: list[SubtitleCandidate]


class SubtitleService:
    """Pequena fachada sobre o Subliminal para manter a UI desacoplada."""

    def __init__(self) -> None:
        self._configure_cache()

    @staticmethod
    def _configure_cache() -> None:
        from subliminal import region

        if not region.is_configured:
            region.configure("dogpile.cache.memory")

    @staticmethod
    def _language(code: str) -> Any:
        from babelfish import Language

        return Language.fromietf(code)

    def search(self, video_path: Path, language: str) -> SearchResult:
        from subliminal import compute_score, list_subtitles, scan_video

        video = scan_video(str(video_path))
        found = list_subtitles([video], {self._language(language)}).get(video, [])
        candidates: list[SubtitleCandidate] = []
        for index, subtitle in enumerate(found):
            matches = tuple(sorted(subtitle.get_matches(video)))
            release = self._release_name(subtitle)
            quality = rank_match(video, release, matches)
            candidates.append(
                SubtitleCandidate(
                    key=f"{subtitle.provider_name}:{subtitle.id}:{index}",
                    provider=subtitle.provider_name,
                    language=str(subtitle.language),
                    score=int(compute_score(subtitle, video)),
                    confidence=quality.confidence,
                    rank_label=quality.label,
                    compatible=quality.compatible,
                    reasons=quality.reasons,
                    matches=matches,
                    release=release,
                    raw=subtitle,
                )
            )
        candidates.sort(
            key=lambda candidate: (
                candidate.compatible,
                candidate.confidence,
                candidate.score,
            ),
            reverse=True,
        )
        return SearchResult(video=video, candidates=candidates)

    @staticmethod
    def _release_name(subtitle: Any) -> str:
        for attribute in (
            "release_info",
            "movie_release_name",
            "release",
            "file_name",
            "filename",
            "movie_full_name",
            "movie_name",
            "movie_title",
            "title",
        ):
            value = getattr(subtitle, attribute, None)
            if value:
                return str(value).replace("\n", " ")
        return str(getattr(subtitle, "id", "—"))

    def download(self, result: SearchResult, candidate: SubtitleCandidate) -> Path:
        from subliminal import download_subtitles, save_subtitles

        download_subtitles([candidate.raw])
        target = Path(candidate.raw.get_path(result.video))
        saved = save_subtitles(result.video, [candidate.raw])
        if not saved:
            raise RuntimeError("O provedor não retornou conteúdo para salvar.")
        return target

    def download_best(self, video_path: Path, language: str) -> Path:
        result = self.search(video_path, language)
        candidate = next((item for item in result.candidates if item.compatible), None)
        if candidate is None:
            raise LookupError(f"Nenhuma legenda compatível encontrada em {language}.")
        return self.download(result, candidate)


