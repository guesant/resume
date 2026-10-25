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


Personal content is reserved. The software and automation are licensed separately under MIT.

