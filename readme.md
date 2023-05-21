Custom static site generator for tarnbarford.net.

Install dependencies:

```
pip install -r requirements
```

Clone posts repository

```
git clone https://github.com/tarnacious/posts
```

Generate the site:

```
python src/generate.py
```

Serve the site locally.

```
python -m http.server --directory build/
```
