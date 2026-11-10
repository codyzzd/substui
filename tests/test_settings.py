from substui.settings import Settings, SettingsStore


def test_settings_round_trip(tmp_path):
    store = SettingsStore(tmp_path / "settings.json")
    expected = Settings(language="en", start_path=str(tmp_path))

    store.save(expected)

    assert store.load() == expected


def test_invalid_settings_fall_back_to_defaults(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text("not json", encoding="utf-8")

    assert SettingsStore(path).load().language == "pt-BR"


def test_unwritable_settings_do_not_crash(monkeypatch, tmp_path):
    store = SettingsStore(tmp_path / "settings.json")

    def deny(*_args, **_kwargs):
        raise PermissionError

    monkeypatch.setattr(type(store.path), "mkdir", deny)

    assert store.save(Settings()) is False

