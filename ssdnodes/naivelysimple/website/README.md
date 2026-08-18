# Naively Simple website

This is the static website for the Naively Simple open-source initiative.
The deployment playbook uses Pandoc to build the manifesto page from
`../manifesto.md`. The deployed site has no runtime dependencies.

To preview it locally, serve this directory with any static HTTP server.
For example:

```sh
python -m http.server 8000
```

Then open <http://localhost:8000>.
