# Matrix documentation source

`index.md` is the public documentation source. `template.html` is the Pandoc
template. Files in `static/` are copied unchanged to `/assets/` on the public
site.

`matrix/setup.yaml` builds `index.md` with Pandoc on the Ansible control
machine, then uploads only the generated HTML and `static/` assets to brighid.
The generated `build/` directory is intentionally ignored by Git.

To add page-specific CSS or JavaScript, add files under `static/` and list them
in the Markdown front matter:

```yaml
css:
  - assets/site.css
  - assets/extra.css
scripts:
  - assets/site.js
  - assets/extra.js
```
