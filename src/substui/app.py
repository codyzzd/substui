from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import ClassVar

from rich.text import Text
from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import (
    Button,
    DataTable,
    DirectoryTree,
    Footer,
    Header,
    Input,
    Label,
    Select,
    Static,
)

from substui.settings import SettingsStore
from substui.subtitles import SearchResult, SubtitleCandidate, SubtitleService

VIDEO_EXTENSIONS = {
    ".3g2", ".3gp", ".avi", ".flv", ".m2ts", ".m4v", ".mkv", ".mov",
    ".mp4", ".mpeg", ".mpg", ".mts", ".ogm", ".ogv", ".rm", ".rmvb",
    ".ts", ".vob", ".webm", ".wmv",
}

LANGUAGES = (
    ("Português (Brasil)", "pt-BR"),
    ("Português", "pt"),
    ("English", "en"),
    ("Español", "es"),
    ("Français", "fr"),
    ("Deutsch", "de"),
    ("Italiano", "it"),
)


class VideoTree(DirectoryTree):
    @staticmethod
    def filter_paths(paths: Iterable[Path]) -> Iterable[Path]:
        return [path for path in paths if path.is_dir() or path.suffix.lower() in VIDEO_EXTENSIONS]


class SubsTui(App[None]):
    TITLE = "SubsTUI"
    SUB_TITLE = "Legendas sem sair do terminal"
    CSS = """
    Screen { background: #0d0b12; color: #e9e4f5; }
    Header { background: #16131d; color: #d8b4fe; }
    Footer { background: #16131d; color: #b9a7e6; }
    Footer > .footer--key { background: #a78bfa; color: #0d0b12; }
    #toolbar { height: 5; padding: 1 2; background: #16131d; }
    #path { width: 1fr; }
    #language { width: 24; margin-left: 1; }
    Input { border: tall #6b6577; background: #0d0b12; color: #e9e4f5; }
    Input:focus { border: tall #a78bfa; }
    Select { border: tall #6b6577; background: #0d0b12; color: #e9e4f5; }
    Select:focus { border: tall #a78bfa; }
    #main { height: 1fr; padding: 1; }
    #browser-pane {
        width: 38%; min-width: 36; margin-right: 1;
        border: round #6b6577; background: #100e16;
    }
    #tree { height: 1fr; padding: 0 1; }
    DirectoryTree > .directory-tree--extension { color: #6b6577; }
    DirectoryTree > .directory-tree--folder { color: #b9a7e6; }
    Tree > .tree--cursor { background: #302741; color: #e9e4f5; }
    .pane-title { height: 3; padding: 1 2; color: #d8b4fe; text-style: bold; }
    #results-pane { width: 1fr; padding: 0 1; border: round #6b6577; background: #100e16; }
    #selected { height: 3; padding: 1; color: #d8b4fe; text-style: bold; }
    #status { height: 3; padding: 1 2; background: #16131d; color: #b9a7e6; }
    #results { height: 1fr; }
    DataTable > .datatable--header { background: #241e30; color: #d8b4fe; text-style: bold; }
    DataTable > .datatable--cursor { background: #3b3150; color: #e9e4f5; }
    DataTable > .datatable--odd-row { background: #14111b; }
    #actions { height: 3; align: right middle; padding-right: 1; }
    Button { margin-left: 1; background: #241e30; color: #e9e4f5; border: none; }
    Button:hover { background: #3b3150; }
    Button.-primary { background: #a78bfa; color: #0d0b12; }
    Button.-success { background: #86d6a2; color: #0d0b12; }
    .busy { color: #f0c560; }
    .success { color: #86d6a2; }
    .error { color: #ee7d92; }
    """

    BINDINGS: ClassVar[list[Binding]] = [
        Binding("ctrl+q", "quit", "Sair"),
        Binding("r", "search", "Buscar"),
        Binding("b", "best", "Baixar melhor"),
        Binding("d", "download", "Baixar selecionada"),
        Binding("f", "toggle_all", "Mostrar todos"),
        Binding("u", "up", "Pasta acima"),
        Binding("ctrl+l", "focus_path", "Ir para pasta"),
    ]

    def __init__(self, settings_store: SettingsStore | None = None) -> None:
        super().__init__()
        self.store = settings_store or SettingsStore()
        self.settings = self.store.load()
        self.service = SubtitleService()
        self.video_path: Path | None = None
        self.search_result: SearchResult | None = None
        self.candidates: dict[str, SubtitleCandidate] = {}
        self.show_all_results = False

    def compose(self) -> ComposeResult:
        start = self._valid_start_path()
        yield Header()
        with Horizontal(id="toolbar"):
            yield Input(str(start), placeholder="Digite uma pasta e pressione Enter", id="path")
            yield Select(LANGUAGES, value=self.settings.language, allow_blank=False, id="language")
            yield Button("Abrir", id="open-path", variant="primary")
        with Horizontal(id="main"):
            with Vertical(id="browser-pane"):
                yield Label("▌ ARQUIVOS DE VÍDEO", classes="pane-title")
                yield VideoTree(start, id="tree")
            with Vertical(id="results-pane"):
                yield Static("▌ Selecione um arquivo de vídeo", id="selected")
                yield DataTable(id="results", cursor_type="row", zebra_stripes=True)
                with Horizontal(id="actions"):
                    yield Button("Mostrar todos", id="toggle-all")
                    yield Button("Buscar", id="search")
                    yield Button("Baixar melhor", id="best", variant="primary")
                    yield Button("Baixar selecionada", id="download", variant="success")
                yield Static("Pronto.", id="status")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#results", DataTable)
        table.add_columns("#", "MATCH", "FONTE", "IDIOMA", "RELEASE · SINAIS")

    def _valid_start_path(self) -> Path:
        path = Path(self.settings.start_path).expanduser()
        return path if path.is_dir() else Path.home()

    @property
    def language(self) -> str:
        value = self.query_one("#language", Select).value
        return str(value) if value is not Select.BLANK else "pt-BR"

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        if event.path.suffix.lower() not in VIDEO_EXTENSIONS:
            return
        self.video_path = event.path
        self.query_one("#selected", Static).update(f"▌ {event.path.name}")
        self.run_search()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "path":
            self.open_path(event.value)

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id != "language" or event.value is Select.BLANK:
            return
        self.settings.language = str(event.value)
        self.store.save(self.settings)
        self.set_status(f"Idioma alterado para {event.value}.", "success")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        actions = {
            "open-path": lambda: self.open_path(self.query_one("#path", Input).value),
            "search": self.action_search,
            "best": self.action_best,
            "download": self.action_download,
            "toggle-all": self.action_toggle_all,
        }
        action = actions.get(event.button.id or "")
        if action:
            action()

    def open_path(self, raw_path: str) -> None:
        path = Path(raw_path.strip().strip('"')).expanduser().resolve()
        if not path.is_dir():
            self.set_status(f"Pasta inexistente: {path}", "error")
            return
        tree = self.query_one("#tree", VideoTree)
        tree.path = path
        tree.reload()
        self.query_one("#path", Input).value = str(path)
        self.settings.start_path = str(path)
        self.store.save(self.settings)
        self.set_status(f"Pasta aberta: {path}", "success")

    def action_up(self) -> None:
        current = Path(self.query_one("#path", Input).value)
        self.open_path(str(current.parent))

    def action_focus_path(self) -> None:
        self.query_one("#path", Input).focus()

    def action_search(self) -> None:
        if self.video_path:
            self.run_search()
        else:
            self.set_status("Selecione um vídeo primeiro.", "error")

    def action_best(self) -> None:
        if not self.video_path:
            self.set_status("Selecione um vídeo primeiro.", "error")
            return
        self.run_download_best()

    def action_download(self) -> None:
        table = self.query_one("#results", DataTable)
        if not self.search_result or table.row_count == 0:
            self.set_status("Faça uma busca e selecione uma legenda.", "error")
            return
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        candidate = self.candidates.get(str(row_key.value))
        if candidate:
            self.run_download(candidate)

    def action_toggle_all(self) -> None:
        if not self.search_result:
            self.set_status("Faça uma busca primeiro.", "error")
            return
        self.show_all_results = not self.show_all_results
        self.render_results()

    def set_status(self, message: str, kind: str = "") -> None:
        status = self.query_one("#status", Static)
        status.set_classes(kind)
        status.update(message)

    @work(thread=True, exclusive=True, group="subtitle")
    def run_search(self) -> None:
        assert self.video_path is not None
        video_path = self.video_path
        language = self.language
        self.call_from_thread(self.set_status, f"Buscando legendas em {language}…", "busy")
        try:
            result = self.service.search(video_path, language)
        # Falhas de rede e parsing variam entre os plugins dos provedores.
        except Exception as error:  # noqa: BLE001
            self.call_from_thread(self.set_status, f"Falha na busca: {error}", "error")
            return
        self.call_from_thread(self.show_results, result)

    def show_results(self, result: SearchResult) -> None:
        self.search_result = result
        self.candidates = {candidate.key: candidate for candidate in result.candidates}
        self.show_all_results = False
        self.render_results()

    def render_results(self) -> None:
        assert self.search_result is not None
        table = self.query_one("#results", DataTable)
        table.clear()
        all_candidates = self.search_result.candidates
        compatible = [candidate for candidate in all_candidates if candidate.compatible]
        visible = all_candidates if self.show_all_results else compatible
        for rank, candidate in enumerate(visible, start=1):
            color = (
                "#86d6a2"
                if candidate.confidence >= 90
                else "#f0c560"
                if candidate.compatible
                else "#ee7d92"
            )
            quality = Text(f"{candidate.confidence:>3}% {candidate.rank_label}", style=f"bold {color}")
            detail = Text(candidate.release, style="#e9e4f5")
            if candidate.reasons:
                detail.append(f"  ·  {' · '.join(candidate.reasons)}", style="#b9a7e6")
            table.add_row(
                Text(f"{rank:>2}", style="#6b6577"),
                quality,
                Text(candidate.provider, style="#a78bfa"),
                candidate.language,
                detail,
                key=candidate.key,
            )
        toggle = self.query_one("#toggle-all", Button)
        toggle.label = "Ocultar fracos" if self.show_all_results else "Mostrar todos"
        total = len(all_candidates)
        good = len(compatible)
        hidden = total - good
        if good:
            suffix = f" · {hidden} resultado(s) fraco(s) ocultado(s)" if hidden else ""
            self.set_status(
                f"✓ {good} compatível(is) de {total}{suffix}. Selecione e pressione D.",
                "success",
            )
        elif total:
            self.set_status(
                f"⚠ Nenhum match confiável entre {total} resultado(s). Pressione F para revisar.",
                "error",
            )
        else:
            self.set_status(f"Nenhuma legenda encontrada em {self.language}.", "error")

    @work(thread=True, exclusive=True, group="subtitle")
    def run_download(self, candidate: SubtitleCandidate) -> None:
        assert self.search_result is not None
        self.call_from_thread(self.set_status, f"Baixando de {candidate.provider}…", "busy")
        try:
            path = self.service.download(self.search_result, candidate)
        except Exception as error:  # noqa: BLE001
            self.call_from_thread(self.set_status, f"Falha no download: {error}", "error")
            return
        self.call_from_thread(self.set_status, f"Legenda salva em {path}", "success")

    @work(thread=True, exclusive=True, group="subtitle")
    def run_download_best(self) -> None:
        assert self.video_path is not None
        video_path = self.video_path
        language = self.language
        self.call_from_thread(self.set_status, "Buscando e baixando a melhor legenda…", "busy")
        try:
            path = self.service.download_best(video_path, language)
        except Exception as error:  # noqa: BLE001
            self.call_from_thread(self.set_status, f"Falha no download: {error}", "error")
            return
        self.call_from_thread(self.set_status, f"Legenda salva em {path}", "success")


def main() -> None:
    SubsTui().run()


if __name__ == "__main__":
    main()

