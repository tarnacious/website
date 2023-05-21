Custom static site generator for tarnbarford.net.

Pull submodules (content for the site)

```
git submodule update --recursive
```

Install dependencies:

```
pip install -r requirements
```

Generate the site:

```
python src/generate.py
```

Serve the site locally.

```
python -m http.server --directory build/
```
