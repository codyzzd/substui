# SubsTUI

[![CI](https://github.com/codyzzd/substui/actions/workflows/ci.yml/badge.svg)](https://github.com/codyzzd/substui/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/substui?label=PyPI)](https://pypi.org/project/substui/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-a78bfa)](https://www.python.org/)
[![Licença MIT](https://img.shields.io/badge/licen%C3%A7a-MIT-86d6a2)](LICENSE)

Encontre a legenda certa sem sair do terminal.

O SubsTUI é um navegador de arquivos com interface TUI que pesquisa, compara e baixa legendas
ao lado dos seus vídeos. Ele usa o [Subliminal](https://github.com/Diaoul/subliminal) para consultar
múltiplos provedores e acrescenta um ranking próprio para separar o release correto de resultados
com título parecido, ano errado ou outra fonte de vídeo.

> O projeto está em fase alfa. A busca depende da disponibilidade e dos limites dos provedores.

## Comece com um comando

Com o [`uv`](https://docs.astral.sh/uv/) instalado, execute o SubsTUI sem clonar nem instalar o
projeto:

```bash
uvx --from git+https://github.com/codyzzd/substui.git substui
```

Depois da primeira publicação no PyPI, o comando fica ainda menor:

```bash
uvx substui
```

O `uvx` baixa o pacote e suas dependências em um ambiente isolado e abre a TUI. Ele funciona no
Windows, Linux e macOS. Assim como o `npx` requer Node, este método requer apenas o `uv`.

### Instalar o uv

Windows, com Winget:

```powershell
winget install --id=astral-sh.uv -e
```

macOS, com Homebrew:

```bash
brew install uv
```

Linux e macOS, com o instalador oficial:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

No Windows também é possível usar o instalador oficial:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Instalação permanente

Para deixar o comando `substui` disponível de qualquer pasta:

```bash
uv tool install git+https://github.com/codyzzd/substui.git
substui
```

Após a publicação no PyPI:

```bash
uv tool install substui
substui
```

O `pipx` continua disponível como alternativa para quem já usa Python:

```bash
pipx install substui
substui
```

Se o comando não aparecer imediatamente após uma instalação permanente, execute
`uv tool update-shell` e abra um terminal novo.

## O que ele faz

- Navega pelas pastas exibindo somente diretórios e arquivos de vídeo.
- Pesquisa em vários provedores, incluindo OpenSubtitles e OpenSubtitles.com.
- Ranqueia legendas por título, ano, hash, fonte, resolução, codecs e grupo de release.
- Classifica cada resultado como `EXATO`, `ÓTIMO`, `BOM`, `POSSÍVEL` ou `BAIXO`.
- Oculta resultados claramente incompatíveis, mas permite revisá-los com `F`.
- Baixa uma opção escolhida ou seleciona automaticamente o melhor match confiável.
- Salva idioma e última pasta entre execuções.
- Grava a legenda ao lado do vídeo, normalmente como `video.pt-BR.srt`.

## Como funciona o ranking

O score técnico do Subliminal é combinado com uma análise do nome real do release:

- Um hash igual recebe prioridade máxima.
- Título, ano, temporada e episódio definem a identidade do conteúdo.
- `BluRay`, `WEB-DL`, `TELESYNC`, resolução, codecs e grupo ajudam a identificar o corte correto.
- Ano, temporada ou episódio divergentes invalidam o resultado.
- Uma fonte diferente reduz a confiança porque pode indicar tempos e cortes diferentes.

Assim, uma legenda para `The.Odyssey.2026.1080p.BluRay` aparece acima de um making-of, de uma
versão de 2016 ou de outro filme que apenas contém “Odyssey” no nome.

## Atalhos

| Tecla | Ação |
|---|---|
| `↑` / `↓` / `Enter` | Navegar e selecionar |
| `R` | Buscar legendas novamente |
| `D` | Baixar a legenda selecionada |
| `B` | Baixar o melhor match confiável |
| `F` | Mostrar ou ocultar resultados fracos |
| `U` | Subir uma pasta |
| `Ctrl+L` | Digitar outro caminho |
| `Ctrl+Q` | Sair |

O idioma é escolhido no topo da interface. Português do Brasil (`pt-BR`) é o padrão.

## Provedores

Alguns provedores funcionam sem conta; outros podem exigir credenciais, limitar requisições ou
ficar temporariamente indisponíveis. O SubsTUI não hospeda legendas: ele consulta os provedores
configurados pelo Subliminal e salva somente o resultado escolhido pelo usuário.

## Desenvolvimento

```bash
git clone https://github.com/codyzzd/substui.git
cd substui
python -m venv .venv
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check .
python -m build
```

O CI testa o projeto no Windows e Linux com Python 3.10 e 3.13. Consulte
[RELEASING.md](RELEASING.md) para publicar uma nova versão no PyPI.

## Roadmap

- Tela para configurar provedores e credenciais.
- Pré-visualização de trechos antes do download.
- Download em lote para uma temporada ou pasta.
- Binários independentes para Windows, Linux e macOS.
- Instalação por gerenciadores como Winget e Homebrew.

## Contribuindo

Issues e pull requests são bem-vindos. Veja [CONTRIBUTING.md](CONTRIBUTING.md) antes de enviar uma
mudança maior.

## Licença

Distribuído sob a [licença MIT](LICENSE).

