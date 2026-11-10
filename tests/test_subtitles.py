from types import SimpleNamespace

from substui.subtitles import SubtitleService


def test_release_name_uses_first_available_field():
    subtitle = SimpleNamespace(release_info="Movie.2026.WEB-DL\nGROUP", id="42")

    assert SubtitleService._release_name(subtitle) == "Movie.2026.WEB-DL GROUP"


def test_release_name_supports_opensubtitles_fields():
    subtitle = SimpleNamespace(movie_release_name="The.Odyssey.2026.BluRay", id="42")

    assert SubtitleService._release_name(subtitle) == "The.Odyssey.2026.BluRay"

