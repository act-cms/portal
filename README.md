# Website for the ACT-CMS Portal

You can see the portal [here](http://act-cms.molssi.org/portal/)!

## Local Testing

```bash
cd portal

# Install dependencies (first time only)
pip install pyyaml jinja2

# Build the static site (outputs to site/)
python scripts/build_site.py

# Serve the site locally
python -m http.server 8000 --directory site
```

Then open http://localhost:8000 in your browser.

Whenever you change a lesson YAML, `paths.yml`, `index.html`, or a template, re-run `build_site.py` and refresh the browser.
