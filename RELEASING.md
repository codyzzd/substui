# Publicação do SubsTUI

## 1. Criar o repositório

O repositório oficial é `codyzzd/substui`. Envie a branch `main`:

```bash
git remote add origin https://github.com/codyzzd/substui.git
git push -u origin main
```

## 2. Conectar GitHub ao PyPI

Em [PyPI Trusted Publishing](https://pypi.org/manage/account/publishing/), cadastre um
*pending publisher* com:

- PyPI project name: `substui`
- Owner: `codyzzd`
- Repository: `substui`
- Workflow: `publish.yml`
- Environment: `pypi`

No GitHub, crie também o environment `pypi` em **Settings → Environments**. É recomendável
exigir aprovação manual para proteger cada publicação.

## 3. Fazer uma release

Atualize a versão em `pyproject.toml` e `src/substui/__init__.py`, faça commit e crie uma GitHub
Release com uma tag correspondente, por exemplo `v0.1.0`. O workflow `Publish to PyPI` constrói,
verifica e publica o pacote sem armazenar senha ou token no GitHub.

Depois da primeira publicação:

```bash
pipx install substui
substui
```

