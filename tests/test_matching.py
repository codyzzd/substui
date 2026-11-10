from subliminal.video import Video

from substui.matching import rank_match, title_similarity


def odyssey_video():
    return Video.fromname("The.Odyssey.2026.1080p.BluRay.x264.AAC5.1-YTS.mp4")


def test_exact_release_ranks_above_making_of():
    video = odyssey_video()
    provider_matches = ("title", "year", "source", "resolution", "video_codec")

    exact = rank_match(
        video,
        "The.Odyssey.2026.IMAX.1080p.BluRay.DDP5.1.x264-FaS",
        provider_matches,
    )
    making_of = rank_match(
        video,
        "The.Odyssey.The.Making.of.an.Epic.2026.1080p.AMZN.WEB-DL.H264-Kitsune",
        provider_matches,
    )

    assert exact.compatible is True
    assert exact.confidence > making_of.confidence
    assert making_of.compatible is False


def test_wrong_year_is_incompatible():
    quality = rank_match(
        odyssey_video(),
        "The.Odyssey.2016.1080p.BRRip.x264.AC3.HORiZON-ArtSubs",
        ("title", "resolution", "video_codec"),
    )

    assert quality.compatible is False
    assert "ano diferente (2016)" in quality.reasons


def test_hash_match_is_always_exact():
    quality = rank_match(odyssey_video(), "1962733704", ("hash",))

    assert quality.confidence == 100
    assert quality.label == "EXATO"
    assert quality.compatible is True


def test_numeric_release_can_use_provider_metadata():
    quality = rank_match(
        odyssey_video(),
        "1962733704",
        ("title", "year", "source", "resolution", "video_codec", "audio_codec"),
    )

    assert quality.compatible is True
    assert quality.confidence >= 75


def test_title_similarity_penalizes_extra_title_words():
    exact = title_similarity("The Odyssey", "The Odyssey")
    making = title_similarity("The Odyssey", "The Odyssey The Making of an Epic")

    assert exact == 1.0
    assert making < 0.62


def test_different_source_lowers_but_does_not_hide_same_movie():
    video = odyssey_video()
    matches = ("title", "year", "resolution", "video_codec")
    bluray = rank_match(video, "The.Odyssey.2026.1080p.BluRay.x264-GROUP", matches)
    web = rank_match(video, "The.Odyssey.2026.1080p.AMZN.WEB-DL.x264-GROUP", matches)

    assert bluray.confidence > web.confidence
    assert web.compatible is True
    assert "fonte diferente (Web)" in web.reasons
