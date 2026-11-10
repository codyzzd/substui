import asyncio
from pathlib import Path

from textual.widgets import DataTable

from substui.app import SubsTui, VideoTree
from substui.settings import Settings, SettingsStore


def test_video_tree_filters_non_video_files(tmp_path):
    directory = tmp_path / "season"
    directory.mkdir()
    video = tmp_path / "episode.mkv"
    video.touch()
    text = tmp_path / "notes.txt"
    text.touch()

    assert list(VideoTree.filter_paths([directory, video, text])) == [directory, video]


def test_app_mounts_with_results_table(tmp_path):
    media = tmp_path / "media"
    media.mkdir()
    store = SettingsStore(tmp_path / "settings.json")
    store.save(Settings(start_path=str(tmp_path)))
    app = SubsTui(store)

    async def run() -> None:
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            table = app.query_one("#results", DataTable)
            assert len(table.columns) == 5
            assert app.query_one("#tree", VideoTree).path == Path(tmp_path)
            app.open_path(str(media))
            await pilot.pause()
            assert app.query_one("#tree", VideoTree).path == media

    asyncio.run(run())
