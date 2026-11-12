FROM hadolint/hadolint:v2.15.1@sha256:32dac94127fd60b7b7e3fbfc65e1383b9b5e25c9bfd7b8536de7a539fe68a12d AS hadolint
FROM ghcr.io/google/osv-scanner:v2.5.1@sha256:8108ae94eadea5a02c9bec6e646909d5b790b44bd62d7f5b7f0b1d6d0ffc7734 AS osv-scanner
FROM ghcr.io/ossf/scorecard:v5.4.0@sha256:546c3f019eb24974abda92004a9003e4059a10e9ee13b1c3ab40d29f4f32f764 AS scorecard
FROM ghcr.io/renovatebot/renovate:44.201.1-full@sha256:eb95a37c0350651d7cc0dc5b383450cbbfeb0fc2ecba69cb13bd4839def31e1d AS renovate
ENTRYPOINT ["/usr/local/sbin/renovate-entrypoint.sh", "renovate"]
CMD []

FROM rhysd/actionlint:1.7.12@sha256:b1934ee5f1c509618f2508e6eb47ee0d3520686341fec936f3b79331f9315667 AS actionlint
FROM ghcr.io/zizmorcore/zizmor:1.31.1@sha256:42d409dbb851d4c5d35a058cf042b828bea1e3f2884378c526eb0974780e18d9 AS zizmor
FROM zricethezav/gitleaks:v8.30.1@sha256:c00b6bd0aeb3071cbcb79009cb16a60dd9e0a7c60e2be9ab65d25e6bc8abbb7f AS gitleaks
FROM aquasec/trivy:0.74.0@sha256:62b1e65e8869bc4b4c6aa4fa2b21595256c7c2f6018a9d9ad61caf87187c1969 AS trivy
FROM ghcr.io/astral-sh/uv:0.13.6@sha256:af22a52f5eafef3d78e551599d405c02df61919d18028f0cea8eda93bc9986d0 AS uv
FROM ghcr.io/casey/just:1.59.0@sha256:014cbe6e6de678864004e2fd8b0405f77ce43b20b225e816feb330f2fb575c01 AS just
FROM koalaman/shellcheck:v0.11.0@sha256:61862eba1fcf09a484ebcc6feea46f1782532571a34ed51fedf90dd25f925a8d AS shellcheck
FROM mvdan/shfmt:v3.14.1@sha256:8c06884a35683d8763fba6c0d9484d11a61a96da65f8d497d6f625825a6043f2 AS shfmt
FROM semgrep/semgrep:1.183.0@sha256:2e45517a85e13a9cca14a2a00df6bb48affd66b8ebfae1b0991cd57578362fb0 AS semgrep

FROM python:3.12-alpine3.24@sha256:e064671ca452259bab50e8e2c7bd896e39e9a343bb06ca25234adf6fe18d0fc7 AS python-base
RUN apk add --no-cache krb5-libs=1.22.3-r0 \
  && printf '%s\n' 'pip==26.3 --hash=sha256:f3b60b20ffaadd4415ed7957212a38ac63fa4c5fa375bd0f4a797777940fad13' \
  > /tmp/pip-requirements.txt \
  && python -m pip install --no-cache-dir --no-deps --require-hashes -r /tmp/pip-requirements.txt \
  && rm /tmp/pip-requirements.txt

FROM node:24.15.0-bookworm@sha256:f22d6a1f082c02f292e86929b5b0442ac2e5eaf438a5dea9b1566601c3e05940 AS node-tools
ADD --checksum=sha256:9128cfe26aee0c99f4fc68c15c6b8b12309a68be0de2c012cdfea2a463cb722f https://github.com/nodejs/corepack/releases/download/v0.36.0/corepack.tgz /tmp/corepack.tgz
RUN mkdir -p /opt/corepack \
  && tar -xzf /tmp/corepack.tgz -C /opt/corepack --strip-components=1 \
  && node /opt/corepack/dist/corepack.js enable pnpm --install-directory /usr/local/bin \
  && rm /tmp/corepack.tgz
ENV PNPM_CONFIG_STORE_DIR=/pnpm/store
WORKDIR /workspace

FROM node-tools AS dependency-submission

FROM node-tools AS yamllint
COPY --from=uv /uv /usr/local/bin/uv
COPY .config/python/pyproject.toml .config/python/uv.lock /opt/python/
RUN uv sync --project /opt/python --locked --no-install-project

FROM node-tools AS ast-grep
WORKDIR /opt/tools/ast-grep
COPY .config/tooling/ast-grep/package.json .config/tooling/ast-grep/pnpm-lock.yaml .config/tooling/ast-grep/pnpm-workspace.yaml ./
RUN --mount=type=cache,id=guesant-tooling-pnpm,target=/tool-cache,sharing=locked pnpm install --frozen-lockfile --store-dir /tool-cache
ENV PATH="/opt/tools/ast-grep/node_modules/.bin:${PATH}"
WORKDIR /workspace

FROM node-tools AS markdownlint
WORKDIR /opt/tools/markdownlint
COPY .config/tooling/markdownlint/package.json .config/tooling/markdownlint/pnpm-lock.yaml .config/tooling/markdownlint/pnpm-workspace.yaml ./
RUN --mount=type=cache,id=guesant-tooling-pnpm,target=/tool-cache,sharing=locked pnpm install --frozen-lockfile --store-dir /tool-cache
ENV PATH="/opt/tools/markdownlint/node_modules/.bin:${PATH}"
WORKDIR /workspace

FROM node-tools AS jscpd
WORKDIR /opt/tools/jscpd
COPY .config/tooling/jscpd/package.json .config/tooling/jscpd/pnpm-lock.yaml .config/tooling/jscpd/pnpm-workspace.yaml ./
RUN --mount=type=cache,id=guesant-tooling-pnpm,target=/tool-cache,sharing=locked pnpm install --frozen-lockfile --store-dir /tool-cache
ENV PATH="/opt/tools/jscpd/node_modules/.bin:${PATH}"
WORKDIR /workspace

FROM node-tools AS repository-tools
COPY --from=ast-grep /root/.cache/node/corepack /opt/corepack-cache
ENV COREPACK_HOME=/opt/corepack-cache
COPY --from=yamllint /opt/python/.venv /opt/python/.venv
ENV PATH="/opt/tooling-modules/.bin:/opt/python/.venv/bin:${PATH}"
COPY --from=actionlint /usr/local/bin/actionlint /usr/local/bin/actionlint
COPY --from=zizmor /usr/bin/zizmor /usr/local/bin/zizmor
COPY --from=gitleaks /usr/bin/gitleaks /usr/local/bin/gitleaks
COPY --from=trivy /usr/local/bin/trivy /usr/local/bin/trivy
COPY --from=just /just /usr/local/bin/just
COPY --from=shellcheck /bin/shellcheck /usr/local/bin/shellcheck
COPY --from=shfmt /bin/shfmt /usr/local/bin/shfmt

COPY --from=hadolint /bin/hadolint /usr/local/bin/hadolint

COPY --from=osv-scanner /osv-scanner /usr/local/bin/osv-scanner

COPY --from=ast-grep /opt/tools/ast-grep /opt/tools/ast-grep
COPY --from=markdownlint /opt/tools/markdownlint /opt/tools/markdownlint
COPY --from=jscpd /opt/tools/jscpd /opt/tools/jscpd
COPY .config/link-tool-modules.mjs /opt/link-tool-modules.mjs
RUN node /opt/link-tool-modules.mjs /opt/tooling-modules /opt/tools

FROM repository-tools AS quality
CMD ["bash", ".config/check.sh"]

FROM python-base AS render-dependencies
COPY --from=uv /uv /usr/local/bin/uv
COPY .config/render/pyproject.toml .config/render/uv.lock /opt/render/
RUN uv sync --project /opt/render --locked --no-dev --no-install-project

FROM python-base AS render
RUN apk add --no-cache bash=5.3.9-r1 readline=8.3.3-r1 libncursesw=6.6_p20260516-r0 ncurses-terminfo-base=6.6_p20260516-r0
COPY --from=render-dependencies /opt/render/.venv /opt/render/.venv
RUN /usr/local/bin/python -m pip uninstall --yes pip
ENV PATH="/opt/render/.venv/bin:${PATH}"
WORKDIR /workspace
ENV PYTHONDONTWRITEBYTECODE=1
ENV HOME=/tmp
USER 999:999
ENTRYPOINT []
CMD ["bash", "scripts/build.sh"]
