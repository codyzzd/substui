# Como contribuir

Obrigado por ajudar o SubsTUI.

## Antes de começar

- Procure uma issue existente antes de abrir outra.
- Para mudanças grandes de interface ou comportamento, abra uma issue descrevendo a proposta.
- Não inclua credenciais, tokens, vídeos ou legendas protegidas por direitos autorais no repositório.

## Ambiente local

```bash
git clone https://github.com/codyzzd/substui.git
cd substui
python -m venv .venv
python -m pip install -e ".[dev]"
```

Antes de enviar um pull request:

```bash
python -m ruff check .
python -m pytest
python -m build
python -m twine check dist/*
```

## Pull requests

- Explique o problema resolvido e como testou a mudança.
- Mantenha o escopo pequeno e evite alterações não relacionadas.
- Adicione ou atualize testes quando mudar comportamento.
- Preserve compatibilidade com Windows e Linux.

Ao contribuir, você concorda que sua mudança será distribuída sob a licença MIT do projeto.

