# Miguel Lopez: consulting website

A small static site: plain HTML, CSS and JavaScript, no framework and no page builder. Hosted free on GitHub Pages at https://lopemige.github.io.

It is in English, with a Spanish version. A button in the menu switches language. A visitor whose browser is set to Spanish sees Spanish first. A link ending in `?lang=es` opens the Spanish version, and `?lang=en` the English one.

## How it is built

The pages are generated from one file, so the menu, footer and every Spanish sentence live in one place.

```
python3 tools/build.py
```

- Edit text in `tools/build.py` (English first, Spanish second in each pair), then run the command above.
- The command rewrites every `.html` file and `js/i18n.js`. Do not edit those by hand; the next build overwrites them.
- After changing `css/styles.css` or a `.js` file, change `VERSION` at the top of `tools/build.py` (for example `20261201a`) and build again. This makes visitors' browsers load the new file.

```
index.html  services.html  experience.html  about.html  contact.html  404.html
css/styles.css       all the styling
js/site.js           language switch, footer year, contact form
js/i18n.js           the Spanish text (generated)
tools/build.py       the page generator
tools/art.py         draws the pictures in assets/ (scenes, icons, map, round badge)
tools/art_cards.py   draws the 14 picture cards: one per job and one per service (art.py runs it)
assets/              the pictures: scenes/, cards/, icons/, about/
favicon.svg          the small icon in the browser tab
```

## Pictures

Every picture is drawn by `tools/art.py` (and `tools/art_cards.py` for the job and service cards in `assets/cards/`), so there is no stock photo and no licence to worry about. Run `python3 tools/art.py` to redraw them (the map also needs the free Natural Earth country data, see the top of the file).

To put a real photo in the round picture on the About page, save it as `assets/about/miguel-lopez.jpg` (square, at least 640 x 640 pixels), then in `page_about` in `tools/build.py` change `assets/about/profile-badge.svg` to `assets/about/miguel-lopez.jpg`, write a new description of the photo for the alt text (English and Spanish), and build again.

## Turn on the contact form

The form uses Web3Forms, so no email address is ever written on the site.

1. Go to https://web3forms.com and ask for an access key for the inbox that should receive the messages.
2. In `tools/build.py`, find `YOUR_ACCESS_KEY_HERE` (in `page_contact`) and replace it with the key. The key is public by design: it only lets people send messages to that inbox.
3. Run `python3 tools/build.py`, commit and push.
4. Send one test message and check that it arrives (look in spam too).

Until then the form shows "This form is not switched on yet."

## Search engines

Every page has `<meta name="robots" content="noindex, nofollow">`, so Google and Bing should not list the site. It is still public: anyone with the address can open it. To let search engines list it, set `indexable=True` in the `shell()` calls in `tools/build.py` and rebuild.

## Accessibility

The site aims at WCAG 2.2 level AA. It has not been certified or tested with a screen reader. Keep every picture's `alt` text, keep text contrast at 4.5:1 or better (3:1 for large text), keep tap targets at least 24 px high, and check new pages at 320 px wide.

To change the picture of one job or service, edit its function in `tools/art_cards.py` (the list at the bottom says which card belongs to which job or service), run `python3 tools/art.py`, and look at `assets/cards/`. A real photo can replace a card the same way as the round picture: save it in `assets/cards/` and change the path in `page_experience` or `page_services` in `tools/build.py`.
