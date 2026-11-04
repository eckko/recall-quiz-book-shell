# Recall Quiz book shell

The smallest possible site for one book. It holds only the book's own
files; all the quiz code (screens, themes, spaced repetition, sync) is
loaded from a tagged copy of
[`eckko/recall-quiz-site-template`](https://github.com/eckko/recall-quiz-site-template)
on jsDelivr. Use this repository as the starting point for each new book.

## What is in it

| Path | What it is |
|---|---|
| `index.html` | A tiny loader: shows the favicon, reads `book.json` and loads the quiz from the template on the CDN |
| `book.json` | Book settings. `templateVersion` says which template version to load (`3` or `3.1.0`) |
| `questions.json` | The question bank. This is a **sample** (2 ideas, 13 questions); replace it |
| `images/favicon.png` | The browser-tab icon (replace with the book's) |
| `media/` | The book's pictures, encrypted (`media/<id>.enc`). The sample holds one figure and one cover |
| `book-structure/` | The chapter map the bank is built from (sample) |
| `tools/set_template_tag.py` | Writes `templateVersion` into `book.json` |

Nothing else belongs here: no `css/`, `js/`, `htrab/`, `themes/` or
`vendor/` folders. If the book uses extra banks (`?bank=banks/name.json`),
add a `banks/` folder; it is read from this site too.

## Start a new book

1. On GitHub, press **Use this template → Create a new repository**
   (or copy these files into a new repository).
2. Replace `questions.json` with the book's bank, `images/favicon.png`
   with its icon, and `book-structure/` with its chapter map. Build the
   bank with the `quiz-htrab` skill, or by hand following the template's
   `ai-context/` notes. Keep every question's `id` stable once readers
   have progress.
3. Put the book's pictures in `media/` (see below), or delete `media/` and
   the `cover` and `media` entries in `questions.json` if there are none.
4. Turn on Pages: **Settings → Pages → Deploy from a branch**, branch
   `main`, folder `/ (root)`. The site is at
   `https://<user>.github.io/<repository>/`.
5. If you use Google sign-in sync, its settings are in the template's
   `js/sync/sync-config.js` and apply to every book. Nothing to do here.

## Pictures (`media/`)

A picture is stored as `media/<id>.enc` (12-byte nonce plus AES-GCM data)
and opens only with the book key, so the book's figures are not freely
downloadable from the repository. Write them with the template's tool
(run it in a checkout of the template):

```
python3 tools/encrypt_media.py KEYFILE sample/fig-clock figure.png --out ../my-book/media
```

`KEYFILE` is the word `placeholder` for a public stand-in key (files are
then hidden but not secret, and can be re-keyed later with
`tools/reencrypt_media.py`) or a file holding the book key. Without a key
the quiz shows each picture's `alt` text instead. The sample files here use
the placeholder key. Details: the template's `ai-context/data-formats.md`.

## Choose the template version

`book.json` holds one setting, `templateVersion`:

```json
{ "templateVersion": "3" }
```

| Value | Meaning |
|---|---|
| `"3"` | The newest `3.x.x` release. Fixes and features of major version 3 reach the book by themselves; a move to 4 is always your choice. |
| `"3.1.0"` | Exactly that release. It never changes, so the site never changes under you. |

Edit `book.json` by hand, or run `python3 tools/set_template_tag.py 3`
(or `3.1.0`), then commit `book.json`. Never use a branch name such as
`main`.

If `book.json` is missing or the value is not like `3` or `3.1.0`, the page
falls back to the default major version written in `index.html`
(`DEFAULT_VERSION`) and logs a warning in the browser console.

jsDelivr resolves a major version to the newest matching tag and caches
that answer, so a new template release can take up to about 12 hours to
reach a book that uses `"3"`. Use an exact version when you need a change
to appear immediately or a site that must not move.

## GitHub workflows

| File | What it does |
|---|---|
| `.github/workflows/publish-to-subject.yml` | Builds the encrypted site and publishes it into a subject site. Starts on a push to `main` that changes the book, by hand or a script (`gh workflow run publish-to-subject.yml -f SUBJECT_REPO=habit-reader -f TEMPLATE_TAG=3.2.5`), or from another workflow (`uses: ...publish-to-subject.yml@main` with `secrets: inherit`). Both inputs are optional: `SUBJECT_REPO` defaults to the repository variable of that name, `TEMPLATE_TAG` to the value in the file (an exact tag, not a major version, because it is checked out for the build tools). |
| `.github/workflows/auto-pr.yml` | Opens a pull request into the default branch when a `feat/**` branch is pushed, unless one is already open. Needs Settings > Actions > General > "Allow GitHub Actions to create and approve pull requests". |

## Try it on your computer

Run `python3 -m http.server` in this folder and open
<http://localhost:8000/>. It needs an internet connection, because the
code comes from the CDN.

## Limits

- The page needs the CDN. If jsDelivr is unreachable the quiz shows
  "The quiz could not be loaded" instead.
- Pages written for template tags before 2.1.0 cannot be used: they have no
  `js/boot.js`.
