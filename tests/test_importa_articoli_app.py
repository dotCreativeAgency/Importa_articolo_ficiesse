import importlib


def test_menu_dispatch_import(monkeypatch, capsys):
    calls = {}

    class Dummy:
        def main(self):
            calls["import_called"] = True

    monkeypatch.setattr(
        "importlib.import_module",
        lambda name: (
            Dummy()
            if name == "import_articoli_to_sqlite"
            else importlib.import_module(name)
        ),
    )

    inputs = iter(["1", "", "3"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    import importa_articoli_app as app

    app.main([])

    assert calls.get("import_called", False) is True


def test_menu_dispatch_export(monkeypatch, capsys):
    calls = {}

    class Dummy:
        def main(self):
            calls["export_called"] = True

    # For esplora
    monkeypatch.setattr(
        "importlib.import_module",
        lambda name: (
            Dummy() if name == "esplora_articoli" else importlib.import_module(name)
        ),
    )

    inputs = iter(["2", "", "3"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    import importa_articoli_app as app

    app.main([])

    assert calls.get("export_called", False) is True
