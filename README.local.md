# Local Notes

## Pygbag Build For itch.io

This project already supports a browser-safe mode through `--itch`.

Important: `--itch` only disables desktop-only features. It does not by itself make the game browser-ready for pygbag runtime requirements.

Use that mode for local testing:

```bash
python main.py --itch
```

In browser/itch mode:

- save position is disabled
- load position is disabled
- save PGN is disabled
- load PGN is disabled
- native `tkinter` dialogs are not used

## Recommended venv setup

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

`pygbag` is already included in [`requirements.txt`](/Users/bradwyatt/Documents/GitHub/Chess/requirements.txt), so the same venv can run the game and build the web package.

## Build Command

Run this from the project root:

```bash
.venv/bin/python -m pygbag --build --archive main.py
```

What this does:

- builds the web output into `build/web/`
- creates `build/web.zip`
- packages the project for an itch.io HTML upload

`pygbag` treats `main.py` as the app entrypoint, and the browser build will automatically behave like `--itch`.

## Browser Compatibility Caveat

This repo now matches the core pygbag entrypoint requirements.

Aligned:

- the browser entry file is named `main.py`
- the entry file is at the project root
- `pygbag` is installed in `requirements.txt`
- the main game loop is async
- the frame loop includes `await asyncio.sleep(0)`
- the entrypoint uses `asyncio.run(main())`

The main remaining work for a real browser release is practical verification: run a pygbag build, open it locally, and confirm there are no web-only runtime issues.

## Files To Upload To itch.io

For itch.io, use:

```text
build/web.zip
```

That zip is the artifact you can upload directly on the itch.io project page for an HTML game.

## Suggested Upload Steps

1. Build the archive:

```bash
.venv/bin/python -m pygbag --build --archive main.py
```

2. Confirm the archive exists:

```bash
ls -lh build/web.zip
```

3. In itch.io, create or edit your project.

4. Choose project type `HTML`.

5. Upload `build/web.zip`.

6. Save the page and launch the game in browser.

## Clean Rebuild

If you want a fresh rebuild:

```bash
rm -rf build
.venv/bin/python -m pygbag --build --archive main.py
```

## Notes

- The project currently uses lowercase `sprites/` paths in code, which is safer for web builds on case-sensitive filesystems.
- If a browser build behaves differently than desktop mode, test with `python main.py --itch` first. That is the closest local behavior to the web build.
- Some pygbag guides reference `python -m pygbag --help`, but the installed `pygbag 0.9.3` in this environment does not expose a normal help screen and instead expects an app path or `main.py`.
