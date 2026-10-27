# Gabriel R. Antunes, Curriculum

This repository contains the declarative source for the public curriculum of Gabriel R. Antunes.

RenderCV generates the PDF and HTML documents from the YAML files under `cv/` using the `sb2nov` theme. The generated site is published at [curriculum.guesant.net](https://curriculum.guesant.net).

The Portuguese and English files are maintained separately so that wording, dates, and links can be reviewed independently.

## Video selection

The selected videos are cataloged in `cv/videos.yaml`. The catalog stores each
video's original title, URL, owner, category, and evidence type. The localized
YAML files provide the surrounding prose and present each video only once.

Projects contain videos that demonstrate a concrete project. Technical
productions contain independent investigations and educational records under
`JipaCoding`. Categories such as infrastructure, graphics, browser tooling, and
algorithms group related videos without creating a generic videos section.

## Local rendering

The repository uses the pinned RenderCV container from the publishing workflow:

```sh
./scripts/render-resume.sh
```

The generated files are written under `build/`. The public site is assembled under `site/`.

## Sources

The rendering script also publishes `site/lobby.json`, a versioned static public index for the Lobby. Experiences, education, explicit skills, projects and cases come from the existing CV YAML, without a second editorial catalog. Public entries receive matching anchors in the generated curriculum HTML. The export omits contact details, rendering settings, highlights and arbitrary extra fields. Technologies are not inferred from project prose.

`scripts/test-export-lobby.py` tests the allowlist, visibility, stable identifiers and canonical anchors inside the RenderCV container through `scripts/validate-output.sh`.

Personal content is reserved. The software and automation are licensed separately under MIT.
