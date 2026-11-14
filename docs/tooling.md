# Tooling e proveniência

Os estágios actionlint, zizmor, Gitleaks, Trivy, uv e just e os presets
yamllint, Markdownlint e ast-grep têm origem no Lobby em
`089fc2754af91ba907663b0048960b3dffd2e646`. O Semgrep usa a mesma versão da
CLI, com regras fixadas em `16b9e6d45f10649f6a531ec4838ed9924372c3bc`. A regra
de pipefail veio do HL Infrastructure em `44f389124eb5524e9f0d5aebe9cf72cbb089872b`.

O Scorecard usa a action oficial fixada por SHA. Sua imagem interna
`v2.5.0` é a exceção registrada para preservar a publicação oficial.

Configure `RENOVATE_TOKEN` no environment `renovate` com um fine-grained PAT
restrito a este repositório. As execuções agendada e manual usam o modo normal
do Renovate e podem criar ou atualizar PRs. O PAT precisa de escrita em
Contents, Commit statuses, Issues, Pull requests e Workflows, além de leitura
dos alertas Dependabot.

ShellCheck segue o HL Infrastructure e shfmt segue a imagem fixada no Portfolio com indentação de dois espaços.

## Checagens locais

```sh
docker compose -f .config/compose.yaml run --build --rm quality
docker compose -f .config/compose.yaml run --build --rm semgrep
docker compose -f .config/compose.yaml build render
docker image save --output .local/scan-image.tar guesant-resume-render:local
docker compose -f .config/compose.yaml run --rm image-audit
```

Consulte os relatórios em `.local/reports`. O tar da imagem é uma entrada local
do scanner. No CI, o job de qualidade usa esses mesmos targets.

O Dependency Review e o envio de snapshots exigem o Dependency Graph
habilitado no GitHub. O relatório CycloneDX descreve o target RenderCV
usado para produzir o currículo.

A regra de pipefail original verifica YAML de automação. A variante
`script-pipefail` aplica a mesma política aos pipelines em scripts Bash
próprios.

Os estágios npm instalam cada ferramenta com o lockfile de
`.config/tooling/<ferramenta>`. O Docker reutiliza o cache de downloads entre
estágios. A imagem de qualidade reúne os executáveis desses estágios.
Os plugins do ESLint e as dependências do Vitest acompanham seus respectivos
executores.

A imagem da ferramenta pode ser executada pelo Compose. O comando abaixo
inspeciona apenas a extração local; os workflows do GitHub executam o Renovate
em modo normal:

```sh
docker compose -f .config/compose.yaml run --build --rm actionlint
docker compose -f .config/compose.yaml run --build --rm scorecard
docker compose -f .config/compose.yaml run --build --rm renovate --platform=local --dry-run=extract
```

O Scorecard local verifica o checkout. O workflow oficial separado publica
o resultado para o badge. O Dependency Review compara as revisões de cada
PR pelo Dependency Graph do GitHub.

O gate mantém os CycloneDX em `.local/reports` e o job de submissão
registra snapshots independentes para a aplicação e para cada lockfile
de tooling. Trivy bloqueia achados HIGH e CRITICAL da imagem de aplicação.
