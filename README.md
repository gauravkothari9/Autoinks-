# Autoinks

Autoinks is a MERN platform that makes drawing Shorts with Python and uploads them to YouTube automatically.

```
client/   React (Vite) UI: style cards, create panel, video library
server/   Express + MongoDB API: job queue, metadata, YouTube OAuth + upload
engine/   Python render engine: drawings, Pillow frames, moviepy encode
media/    rendered videos, previews, and your uploaded music library (media/music)
```

## How a Short is made

1. The user picks a style (or "Surprise me"). The server saves a `Job` in MongoDB.
2. The queue runs `python -m engine.render` as a separate process.
3. The chosen scene builds its picture (shapes, colors, positions, counts) from a random seed and palette. Each run gives a different video.
4. Every frame is drawn with Pillow at 2× resolution and scaled down for anti-aliasing. `engine/frame.py` adds a one-line quote (from `engine/quotes.json`, never repeating recent ones).
5. `engine/music.py` composes an original background track to the exact video length, in a mood that fits the style. moviepy then combines the frames and the track into a 1080×1920, 30 fps H.264/AAC MP4.
6. The server builds the title, description and tags. Your own tags come first, then the style's tags, then high-volume tags such as `shorts`, `drawing` and `satisfying`. The total is kept under YouTube's 500-character limit.
7. If auto-upload is on and a channel is connected, the video is uploaded through the YouTube Data API v3.

## Styles

There are 52 speed-drawing styles in 4 groups:

| Group           | Styles |
|-----------------|--------|
| Scenery         | Mountain Lake, Sunset Beach, Lighthouse, Cozy Cottage, Hot Air Balloon, Rocket Launch, Windmill, Campfire Night, Volcano, Fairy Castle, Sailboat, Rainbow Hills, Igloo Night, Pyramids, Mushroom House, Waterfall, Treehouse, City Night |
| Animals         | Cute Cat, Night Owl, Koi Pond, Happy Whale, Butterfly, Little Fox, Penguin, Panda, Sea Turtle, Bunny, Happy Frog, Honey Bee, Snail, Octopus, Little Dino, Hedgehog, Jellyfish, Puppy |
| Plants & Treats | Sunflower, Cactus, Ice Cream, Cupcake, Tulip Vase, Strawberries, Donut, Watermelon, Pizza Slice, Bonsai, Birthday Cake |
| Things          | Little Car, Teacup, Gift Box, Guitar, Robot |

The pictures live in `engine/drawings.py` through `engine/drawings4.py`. Each is drawn on a sheet of paper: a pen inks the outlines, a marker colors each shape, a brush adds shading, then final touches. The finished picture gets a slow zoom and sparkles.

`engine/sketch.py` is the speed-drawing engine. A picture is a `Sketch` built back to front with `shape` (outline + fill), `line`, `shade` and `detail`. Outlines hidden behind a shape in front are clipped away, and each fill is masked by the shapes in front of it, so the reveal order never breaks the layering. On top of the picture's own random choices, every video gets a `Variant`: a mirrored layout half the time, a gentle hand-drawn warp of every shape, a color mood (natural, pastel, vivid, warm, cool, dusk or dreamy), and a different pen and paper. So the same style never comes out the same twice. `engine/art.py` holds the shared toolkit: palettes, the canvas, easing, vector shapes (circles, splines, clouds, stars) and backgrounds. A picture inside a frame sets `bounds`, so nothing spills past the frame edge.

**Drawing length** (Profile → Video settings) sets how long the drawing takes; **Finale** adds time at the end that shows the finished picture.

To add a style:
1. Write a scene function `scene(rng, palette, duration, hold)` that returns `draw(canvas, t)`. Make all random choices up front with `rng`. For a speed drawing, build a `Sketch` and return `sk.scene(duration, hold)`.
2. Add it to `SCENES` in `engine/scenes.py`, and give it a music mood in `CATEGORY_MOODS` in `engine/music.py`.
3. Add an entry to `engine/categories.json` with `id`, `name`, `group`, `description`, `hashtags` and `titles`.

## App pages

- **Dashboard (`/`)**: all styles in a 4-column grid, with group filters, search and "Surprise me". Clicking a style opens the Create card.
- **Profile (`/profile/...`)** has four sections:
  - `account`: connect your YouTube channel and edit your tags
  - `shorts`: your Shorts, with status filters, publish, edit and download
  - `schedule`: repeating autopilot schedules (days, times, styles)
  - `settings`: video defaults
- **Header**: shows your channel name with a green dot when YouTube is connected. Otherwise it shows a "Connect YouTube" button.

## Accounts and subscriptions

- **Registration is free.** Sign-up (`/signup`) asks for name, email and password. Passwords are hashed with scrypt, and sessions are HttpOnly cookies.
- **The first account becomes the admin.** It inherits everything created before accounts existed (Shorts, schedules, settings, YouTube connection), has full access without paying, and is the only account that can change the platform's Google OAuth credentials.
- **Free accounts** can browse all styles and create **1 watermarked trial Short**. They can't upload it, schedule, or create more.
- **Plans** (Razorpay subscriptions in INR; yearly = 10× monthly):

  | Plan  | Monthly | Yearly  | Shorts / month | Schedules | Own music upload |
  |-------|---------|---------|----------------|-----------|------------------|
  | Basic | ₹500    | ₹5,000  | 30             | 1         | —                |
  | Pro   | ₹1,200  | ₹12,000 | 120            | 5         | ✓                |
  | Max   | ₹2,500  | ₹25,000 | 400            | unlimited | ✓                |

  Prices and limits are in `server/src/services/plans.js`. Pro and Max Shorts render first when the queue is busy.
- **Per-user data:** each user has their own Shorts, schedules, settings, music library and YouTube channel. Video files are only served to their owner.
- **Profile → Plan & billing:** shows usage and the renewal date, and has Change plan and Cancel. A cancelled plan keeps working until the end of the paid period.

### Razorpay setup

1. Create a Razorpay account. Test mode works immediately; live mode needs KYC.
2. Go to **Dashboard → Account & Settings → API Keys**, generate keys, and put `RAZORPAY_KEY_ID` / `RAZORPAY_KEY_SECRET` in `server/.env`. Use `rzp_test_…` keys while testing.
3. Go to **Dashboard → Webhooks** and add `https://<your-domain>/api/billing/webhook`:
   - Choose all `subscription.*` events.
   - Pick a secret and put the same value in `RAZORPAY_WEBHOOK_SECRET`.
   - The webhook needs a public URL. On localhost, skip it: a payment is still activated right after Checkout, and the Plan & billing page refreshes the status from Razorpay each time it opens.
4. Restart the server. Razorpay plans are created automatically the first time someone subscribes.
5. When the site runs on HTTPS, set `SECURE_COOKIES=true`.

## Music

Every new Short gets background music. You set this in **Profile → Video settings → Music**:

- **Generated** (default): each Short gets an original track synthesized in numpy.
  - The mood matches the video by default (**Match the video**; the map is `CATEGORY_MOODS` in `engine/music.py`):

    | Mood    | Styles |
    |---------|--------|
    | Chill   | mountain lake, cottage, sunflower, cactus, windmill, tulip vase, pyramids, teacup |
    | Upbeat  | sunset beach, hot air balloon, butterfly, ice cream, cupcake, rainbow hills, sailboat, strawberries, donut, watermelon, car, gift box |
    | Quirky  | cute cat, owl, whale, fox, penguin, panda, bunny, frog, bee, snail, octopus |
    | Calm    | lighthouse, koi pond, sea turtle |
    | Cosmic  | rocket, igloo |
    | Electro | spirograph, string art, harmonograph, lissajous, dragon curve |
    | Zen     | mandala, flower of life, koch snowflake, golden spiral, star polygons |
    | Dreamy  | fractal tree, rose curves, campfire, mushroom house |
    | Epic    | volcano |
    | Elegant | castle |

    You can also pick one mood for every Short (any of the moods above, plus chase, sporty, rock and workout), or random.
  - Each track has a random key, chord progression and tempo within its mood's range.
  - Each mood is a genre recipe: drum grooves, a bass line, pads or chord stabs, an arpeggio and/or a repeating lead melody, and reverb. Tracks open with a one-bar intro, add a drum fill and crash every four bars, and end on the home chord during the finale.
  - The music is royalty-free, so it won't trigger YouTube Content ID claims.
  - Preview plays a 14-second sample of the chosen mood (a random mood for Match the video).
- **My music**: each Short uses a random track from your uploads (stored in `media/music`). Short tracks loop and long ones are trimmed. If the library is empty, generated music is used instead. Only upload music you have the rights to.
- **Off**: Shorts are rendered silent.

The "Add music" button in the Music card adds a track to unpublished Shorts that were rendered without music. It only changes the audio and doesn't re-render the picture. Published Shorts can't get new music, because YouTube's API can't replace a video's audio.

## Scheduling

- **Profile → Schedule (`/profile/schedule`):** create repeating schedules. The Dashboard's **Autopilot** button opens a new one. Each schedule has:
  - days of the week
  - one or more times
  - a timezone
  - a visibility setting
  - how many Shorts per slot (1–3)
  - which styles to use: chosen styles take turns, or "Any style" picks at random
- **Create card:** under "Publish", choose **Right away**, **Once later** (one Short at a date and time you pick), or **Repeat**. Repeat creates a schedule for that style, every day or on the days you pick, at one or more times.
- **How a slot runs:** the server checks every 30 seconds and starts rendering 20 minutes before each slot.
  - **Public** Shorts are uploaded private with YouTube's `publishAt`. YouTube itself makes them public at the exact time, so the server can be off by then.
  - **Unlisted or private** Shorts can't use `publishAt`. They are held on the server and uploaded when the slot arrives, so the server must be running at that time.
- **If the server was off:** a slot missed by up to 2 hours still runs as soon as the server comes back. Older missed slots are skipped.
- **Timezones:** slot times use the IANA timezone you pick, so they stay correct across daylight saving changes.

## Setup (Windows)

Requirements: Node 20+, MongoDB running locally (or an Atlas URI), and [uv](https://docs.astral.sh/uv/) (it installs Python 3.14 and the engine dependencies).

```powershell
uv sync                                   # Python engine deps (moviepy, pillow, numpy)
cd server; npm install; copy .env.example .env; cd ..
cd client; npm install; npm run build; cd ..
cd server; npm start                      # http://localhost:5000
```

For development with hot reload, run `npm run dev` in both `server/` and `client/`, then open http://localhost:5173.

The first time the server starts, it renders a small looping preview for every style card. This takes a few minutes in total.

## Connecting YouTube

1. In Google Cloud Console, create a project and enable **YouTube Data API v3**.
2. Configure the **OAuth consent screen** as External and add your Google account as a test user.
3. Go to Credentials, click **Create OAuth client ID**, and choose **Web application**. Add this authorized redirect URI:
   `http://localhost:5000/api/youtube/callback`
4. Go to **Profile → Channel & Tags → Google API credentials**, paste the client ID and secret, and click Save. They are written to `server/.env` and take effect immediately, without a restart. You can also edit `server/.env` by hand and restart the server.
5. Click **Connect YouTube**.

Profile has no login in front of it. Keep the server on localhost. If you expose it to other people, add authentication first, because anyone who can open Profile can replace the credentials.

Important: YouTube locks videos uploaded by an **unverified** API project as *private*. To publish publicly, the project has to pass Google's API compliance audit. Until then, upload as private or unlisted.
The default quota (10,000 units a day) allows about 6 uploads a day. Each upload costs 1,600 units.

## Engine CLI

```powershell
uv run python -m engine.render --category mountain_lake --out media/test.mp4 --draw-seconds 20 --hold-seconds 3
# options: --seed, --palette, --width/--height, --fps, --glow, --crf, --hook "quote text", --no-hook,
#          --music generated|library|off, --mood auto|random|epic|chase|sporty|rock|funky|electro|workout|zen|quirky|chill|elegant|calm|dreamy|upbeat|cosmic
uv run python -m engine.music --out track.wav --duration 23 --mood epic      # just the music (or --category mandala)
uv run python -m engine.add_music --video media/videos/x.mp4                # add music to an existing video
```

## Deploying to AWS

See [deploy/DEPLOY.md](deploy/DEPLOY.md): an Ubuntu EC2 server with a free DuckDNS hostname and automatic HTTPS. No domain needed.
