"""Generative background music, synthesized from scratch with numpy.

Every track is original (random key, progression, tempo, groove and melody), so it is royalty-free
and won't trigger YouTube Content ID claims. Each mood is a small genre recipe: drum patterns on a
16-step grid, a bass line, chord pads or stabs, an arpeggio and/or a two-bar lead motif that
repeats with a varied ending. Tracks start with a one-bar intro, add a drum fill and crash every
four bars, and hold the tonic at the end so the music resolves while the finale is on screen.

With no mood given, the mood matches the video's style (CATEGORY_MOODS): cute drawings get a light
upbeat or chill track, animals a quirky tune, a robot an electro track, a bonsai a zen one, and so on.
"""

import random
import wave

import numpy as np

SR = 44100
MAJOR = [0, 2, 4, 5, 7, 9, 11]
MINOR = [0, 2, 3, 5, 7, 8, 10]
DORIAN = [0, 2, 3, 5, 7, 9, 10]

# Drum patterns: 16 steps per bar (sixteenth notes), "x" = hit.
FOUR = "x...x...x...x..."
BACKBEAT = "....x.......x..."
EIGHTHS = "x.x.x.x.x.x.x.x."
SIXTEENTHS = "x" * 16
OFFBEAT = "..x...x...x...x."


def _mood(scale, bpm, progs, **kw):
    base = dict(scale=scale, bpm=bpm, progs=progs, pad="soft", pad_level=0.16, chord_notes=3,
                stab=None, stab_voice="organ", stab_level=0.10, power=False,
                arp=None, arp_voice="pluck", arp_level=0.18,
                lead=None, lead_voice="pluck", lead_level=0.16, lead_octave=0,
                bass="x.......x.......", bass_voice="sub", bass_mode="root", bass_level=0.35,
                drums={}, fill="snare", swing=0.0, pump=0.0, crackle=False, reverb=0.9)
    base.update(kw)
    return base


MOODS = {
    # The original four ambient moods.
    "calm": _mood(MAJOR, (64, 76), [[0, 4, 5, 3], [0, 5, 3, 4], [3, 4, 0, 0]], arp=1.0),
    "dreamy": _mood(MINOR, (70, 84), [[0, 5, 2, 6], [0, 6, 5, 6], [0, 3, 5, 4]], arp=0.5),
    "upbeat": _mood(MAJOR, (100, 118), [[0, 4, 5, 3], [5, 3, 0, 4], [0, 3, 4, 3]], arp=0.5,
                    drums={"kick": "x.......x.......", "hat": OFFBEAT}),
    "cosmic": _mood(MINOR, (78, 92), [[0, 5, 6, 4], [0, 2, 5, 6], [0, 6, 3, 4]], arp=0.25),
    # Genre moods matched to the video styles.
    "epic": _mood(MINOR, (86, 98), [[0, 5, 2, 6], [0, 5, 3, 4], [0, 6, 5, 4]],
                  pad="strings", pad_level=0.13, lead=0.45, lead_voice="brass", lead_level=0.12,
                  bass="x.x.x.x.x.x.x.x.", bass_voice="saw", bass_level=0.22,
                  drums={"kick": "x.....x...x.....", "snare": BACKBEAT, "tom": "x..x..x.........",
                         "hat": EIGHTHS},
                  fill="tom", reverb=1.2),
    "chase": _mood(MINOR, (150, 168), [[0, 5, 6, 4], [0, 6, 5, 4], [0, 3, 6, 5]],
                   pad="strings", pad_level=0.08, arp=0.25, arp_voice="square", arp_level=0.09,
                   bass="x.x.x.x.x.x.x.x.", bass_voice="saw", bass_mode="octave", bass_level=0.22,
                   drums={"kick": FOUR, "snare": BACKBEAT, "hat": EIGHTHS}, reverb=0.6),
    "sporty": _mood(MAJOR, (118, 130), [[0, 4, 5, 3], [0, 3, 4, 4], [5, 3, 0, 4]],
                    pad="soft", pad_level=0.10, lead=0.55, lead_voice="pluck", lead_level=0.18,
                    lead_octave=12, bass="x.x.x.x.x.x.x.x.", bass_voice="saw", bass_level=0.22,
                    stab=OFFBEAT, stab_voice="organ", stab_level=0.05,
                    drums={"kick": "x.....x.x.......", "snare": BACKBEAT, "hat": EIGHTHS}),
    "funky": _mood(DORIAN, (98, 110), [[0, 3, 0, 3], [0, 6, 3, 4], [1, 4, 0, 0]],
                   pad="none", chord_notes=4, stab="..x...x...x..x..", stab_voice="organ",
                   stab_level=0.09, lead=0.4, lead_voice="square", lead_level=0.08, lead_octave=12,
                   bass="x..x..x...x.x..x", bass_voice="square", bass_mode="octave", bass_level=0.26,
                   drums={"kick": "x......x..x.....", "clap": BACKBEAT, "hat": SIXTEENTHS,
                          "ohat": "..............x."},
                   swing=0.22, reverb=0.5),
    "electro": _mood(MINOR, (122, 128), [[0, 5, 6, 4], [0, 0, 5, 6], [0, 3, 5, 4]],
                     pad="strings", pad_level=0.10, arp=0.25, arp_voice="saw", arp_level=0.07,
                     bass=OFFBEAT, bass_voice="saw", bass_level=0.25,
                     drums={"kick": FOUR, "clap": BACKBEAT, "ohat": OFFBEAT, "hat": EIGHTHS},
                     pump=0.65, reverb=0.8),
    "workout": _mood(MINOR, (128, 138), [[0, 5, 6, 6], [0, 6, 5, 4], [0, 3, 6, 5]],
                     pad="strings", pad_level=0.09, stab="x..x..x...x..x..", stab_voice="saw",
                     stab_level=0.06, bass=OFFBEAT, bass_voice="saw", bass_level=0.26,
                     drums={"kick": FOUR, "clap": BACKBEAT, "hat": SIXTEENTHS, "ohat": OFFBEAT},
                     pump=0.6, reverb=0.6),
    "zen": _mood(MAJOR, (58, 68), [[0, 3, 0, 4], [0, 5, 3, 0], [3, 0, 4, 0]],
                 pad="soft", pad_level=0.15, lead=0.25, lead_voice="bell", lead_level=0.12,
                 lead_octave=12, bass="x...............", bass_level=0.25, reverb=1.6),
    "quirky": _mood(MAJOR, (112, 126), [[0, 3, 4, 0], [0, 5, 3, 4], [0, 0, 4, 4]],
                    pad="none", stab=OFFBEAT, stab_voice="organ", stab_level=0.07,
                    lead=0.5, lead_voice="pizz", lead_level=0.20, lead_octave=12,
                    bass=FOUR, bass_voice="square", bass_mode="fifth", bass_level=0.26,
                    drums={"wood": "x..x..x...x.x...", "snare": "............x..."},
                    fill="wood", reverb=0.4),
    "elegant": _mood(MAJOR, (76, 88), [[0, 5, 3, 4], [0, 3, 4, 0], [0, 5, 1, 4]],
                     pad="strings", pad_level=0.11, lead=0.6, lead_voice="musicbox", lead_level=0.16,
                     lead_octave=12, arp=1.0, arp_voice="pluck", arp_level=0.08,
                     bass="x.......x.......", bass_level=0.28, reverb=1.4),
    "rock": _mood(MINOR, (122, 138), [[0, 5, 6, 0], [0, 3, 5, 6], [0, 6, 5, 4]],
                  pad="none", power=True, stab=EIGHTHS, stab_voice="guitar", stab_level=0.10,
                  lead=0.35, lead_voice="lead", lead_level=0.07, lead_octave=12,
                  bass=EIGHTHS, bass_voice="saw", bass_level=0.24,
                  drums={"kick": "x.....x.x.......", "snare": BACKBEAT, "hat": EIGHTHS}, reverb=0.5),
    "chill": _mood(MAJOR, (78, 90), [[0, 5, 3, 4], [3, 2, 1, 4], [0, 3, 5, 4]],
                   pad="rhodes", pad_level=0.13, chord_notes=4, lead=0.3, lead_voice="rhodes",
                   lead_level=0.10, lead_octave=12, bass="x......x..x.....", bass_level=0.30,
                   drums={"kick": "x......x..x.....", "snare": BACKBEAT, "hat": EIGHTHS},
                   swing=0.0, crackle=True, reverb=0.9),
}
MOOD_NAMES = list(MOODS)

# The mood each video style gets when no mood is chosen. Ids match engine/categories.json.
CATEGORY_MOODS = {
    **dict.fromkeys(["mountain_lake", "cottage", "sunflower", "cactus", "windmill", "tulip_vase", "pyramids", "teacup",
                     "treehouse", "guitar"],
                    "chill"),
    **dict.fromkeys(["sunset_beach", "hot_air_balloon", "butterfly", "ice_cream", "cupcake", "rainbow_hills", "sailboat",
                     "strawberry", "donut", "watermelon", "car", "gift_box", "pizza", "birthday_cake"], "upbeat"),
    **dict.fromkeys(["cute_cat", "owl", "whale", "fox", "penguin", "panda", "bunny", "frog", "bee", "snail", "octopus",
                     "dinosaur", "hedgehog", "puppy"], "quirky"),
    **dict.fromkeys(["lighthouse", "koi_pond", "sea_turtle", "waterfall", "jellyfish"], "calm"),
    **dict.fromkeys(["rocket", "igloo"], "cosmic"),
    "robot": "electro",
    "bonsai": "zen",
    **dict.fromkeys(["city_night", "campfire", "mushroom_house"], "dreamy"),
    "volcano": "epic",
    "castle": "elegant",
}


def resolve_mood(mood, category, rng):
    """A named mood wins; "random" picks any; otherwise ("auto" or None) match the category."""
    if mood in MOODS:
        return mood
    if mood != "random" and category in CATEGORY_MOODS:
        return CATEGORY_MOODS[category]
    return rng.choice(MOOD_NAMES)


def _freq(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def _chord(scale, degree, notes=3):
    """Chord stacked in thirds on a scale degree, as semitone offsets from the key root."""
    return [scale[(degree + 2 * k) % 7] + 12 * ((degree + 2 * k) // 7) for k in range(notes)]


def _degree(scale, degree):
    return scale[degree % 7] + 12 * (degree // 7)


def _tone(freq, n, harmonics=(1.0, 0.5, 0.25), detune=0.0):
    t = np.arange(n) / SR
    out = np.zeros(n)
    for h, amp in enumerate(harmonics, 1):
        if amp and freq * h < SR / 2.2:
            out += amp * np.sin(2 * np.pi * freq * h * (1 + detune) * t)
    return out


def _add(buf, start, signal, gain=1.0):
    start = int(start)
    if start >= len(buf) or start < 0:
        return
    end = min(len(buf), start + len(signal))
    buf[start:end] += signal[:end - start] * gain


def _adsr(n, attack=0.01, release=0.08):
    i = np.arange(n)
    return np.minimum(1, i / max(1, attack * SR)) * np.minimum(1, (n - i) / max(1, release * SR))


def _decay(n, seconds):
    env = np.exp(-np.arange(n) / SR / seconds)
    a = min(n, int(0.004 * SR))
    env[:a] *= np.linspace(0, 1, a)  # tiny attack avoids clicks
    return env


SAW = tuple(1 / k for k in range(1, 9))
SQUARE = tuple((1 / k if k % 2 else 0) for k in range(1, 10))


def _voice(name, freq, seconds):
    """One note of an instrument, `seconds` long (plucked voices ring out on their own)."""
    n = max(1, int(seconds * SR))
    if name == "pluck":
        return _tone(freq, n, (1.0, 0.35, 0.12)) * _decay(n, 0.3)
    if name == "pizz":
        return _tone(freq, n, (1.0, 0.5, 0.2, 0.1)) * _decay(n, 0.09)
    if name == "musicbox":
        return (_tone(freq, n, (1.0, 0, 0, 0.15)) * _decay(n, 0.7)
                + _tone(freq * 2, n, (0.25,)) * _decay(n, 0.2))
    if name == "bell":
        t = np.arange(n) / SR
        out = sum(a * np.sin(2 * np.pi * freq * r * t) * np.exp(-t / d)
                  for r, a, d in ((1, 1.0, 2.0), (2.0, 0.4, 1.0), (2.76, 0.3, 0.6), (5.4, 0.12, 0.25)))
        return out * _decay(n, 10)
    if name == "rhodes":
        t = np.arange(n) / SR
        return (_tone(freq, n, (1.0, 0.25, 0.08)) * (1 + 0.15 * np.sin(2 * np.pi * 4.5 * t))
                * _decay(n, 1.1) * _adsr(n, 0.005, 0.1))
    if name == "brass":
        return sum(_tone(freq, n, SAW[:6], d) for d in (-0.002, 0.002)) / 2 * _adsr(n, 0.05, 0.12)
    if name in ("saw", "lead"):
        detunes = (-0.004, 0.004) if name == "saw" else (0.0,)
        out = sum(_tone(freq, n, SAW, d) for d in detunes) / len(detunes)
        return out * _adsr(n, 0.005, 0.05)
    if name == "square":
        return _tone(freq, n, SQUARE) * _adsr(n, 0.004, 0.04)
    if name == "organ":
        return _tone(freq, n, (1.0, 0.6, 0.4, 0.25)) * _adsr(n, 0.004, 0.05) * _decay(n, 0.4)
    if name == "guitar":
        raw = _tone(freq, n, SAW[:6])
        return np.tanh(3.5 * raw) * _decay(n, 0.5) * _adsr(n, 0.003, 0.03)
    return _tone(freq, n, (1.0, 0.4, 0.15)) * _decay(n, 0.6)  # "sub" bass


def _drum_kit(rng):
    """One sample per drum, synthesized once per track."""

    def t(sec):
        return np.arange(int(sec * SR)) / SR

    def noise(n):
        return np.diff(rng.standard_normal(n + 1))  # differentiated noise = brighter, less rumble

    k = t(0.35)
    kick_f = 48 + 120 * np.exp(-k / 0.03)
    kick = np.sin(2 * np.pi * np.cumsum(kick_f) / SR) * np.exp(-k / 0.16)
    s = t(0.22)
    snare = noise(len(s)) * np.exp(-s / 0.07) * 0.35 + np.sin(2 * np.pi * 185 * s) * np.exp(-s / 0.05) * 0.5
    c = t(0.3)
    burst = sum(np.where(c >= d, np.exp(-(c - d) / 0.007), 0) for d in (0, 0.011, 0.022))
    clap = noise(len(c)) * (burst + 0.5 * np.exp(-c / 0.09)) * 0.3
    h = t(0.06)
    hat = np.diff(noise(len(h) + 1)) * np.exp(-h / 0.014) * 0.1
    o = t(0.3)
    ohat = np.diff(noise(len(o) + 1)) * np.exp(-o / 0.1) * 0.07
    m = t(0.45)
    tom = np.sin(2 * np.pi * np.cumsum(85 + 70 * np.exp(-m / 0.1)) / SR) * np.exp(-m / 0.22) * 0.8
    w = t(0.08)
    wood = (np.sin(2 * np.pi * 950 * w) + 0.5 * np.sin(2 * np.pi * 1620 * w)) * np.exp(-w / 0.018) * 0.35
    r = t(1.6)
    crash = np.diff(noise(len(r) + 1)) * np.exp(-r / 0.55) * 0.05
    kit = dict(kick=kick, snare=snare, clap=clap, hat=hat, ohat=ohat, tom=tom, wood=wood, crash=crash)
    for name, sample in kit.items():
        a = min(len(sample), 40)
        sample[:a] *= np.linspace(0, 1, a)
    return kit


def _motif(rng, density, bars=2):
    """A lead phrase: (eighth-note slot, length in eighths, scale-degree offset from the chord root)."""
    slots = [0] + [s for s in range(1, 8 * bars) if rng.random() < density]
    notes = []
    for i, s in enumerate(slots):
        length = min((slots[i + 1] if i + 1 < len(slots) else 8 * bars) - s, 4)
        strong = s % 4 == 0
        offset = rng.choice([0, 2, 4, 7] if strong else [0, 1, 2, 3, 4, 5, 7])
        notes.append((s, length, offset))
    return notes


def generate_music(duration, out_path, seed=None, mood=None, hold=3.0, category=None):
    """Write a stereo 16-bit WAV of `duration` seconds; returns (path, description)."""
    rng_py = random.Random(seed)
    rng = np.random.default_rng(rng_py.randrange(1 << 30))
    mood = resolve_mood(mood, category, rng_py)
    m = MOODS[mood]
    scale = m["scale"]
    bpm = rng_py.uniform(*m["bpm"])
    root = rng_py.randint(57, 64)  # A3..E4
    prog = rng_py.choice(m["progs"])
    beat = 60 / bpm
    step = beat / 4
    bar = 4 * beat
    total = int(duration * SR)
    kit = _drum_kit(rng)

    layers = {k: np.zeros(total) for k in ("pad", "stab", "lead", "arp", "bass", "drums", "hats")}
    kick_times = []

    def at(s):
        """Time of a sixteenth step inside a bar, with swing on the off-sixteenths."""
        return s * step + (m["swing"] * step if s % 2 else 0)

    body_end = max(bar, duration - hold)  # after this, hold the tonic
    bars = int(np.ceil(body_end / bar))
    has_drums = bool(m["drums"])
    intro = 1 if has_drums and bars >= 4 else 0
    arp_pattern = rng_py.choice([[0, 1, 2, 1], [0, 1, 2, 3], [0, 2, 1, 2], [2, 1, 0, 1], [0, 2, 3, 2]])
    motif = _motif(rng_py, m["lead"] or 0)
    alt_end = _motif(rng_py, m["lead"] or 0, bars=1)  # varied second bar for every other phrase

    for b in range(bars + 1):
        is_final = b == bars
        start = b * bar
        if start >= duration:
            break
        degree = 0 if is_final else prog[b % len(prog)]
        chord = _chord(scale, degree, m["chord_notes"])
        seg = (duration - start) if is_final else bar
        t0 = start * SR

        # pad: sustained chord, overlapping into the next bar for a smooth crossfade
        if m["pad"] != "none":
            n = int((seg + 0.6) * SR)
            env = np.minimum(1, np.arange(n) / (0.5 * SR)) * np.minimum(1, (n - np.arange(n)) / (0.6 * SR))
            for off in chord:
                f = _freq(root - 12 + off)
                if m["pad"] == "rhodes":
                    note = _voice("rhodes", f * 2, seg + 0.6)
                else:
                    harm = SAW[:5] if m["pad"] == "strings" else (1.0, 0.3, 0.1)
                    note = sum(_tone(f, n, harm, d) for d in (-0.003, 0.0, 0.003)) / 3 * env
                _add(layers["pad"], t0, note, m["pad_level"])

        # bass line
        hits = [s for s, ch in enumerate(m["bass"]) if ch == "x"]
        if is_final:
            hits = [0]
        for i, s in enumerate(hits):
            nxt = hits[i + 1] if i + 1 < len(hits) else 16
            length = (seg if is_final else (nxt - s) * step * 0.9)
            bass_note = root - 24 + chord[0]
            if m["bass_mode"] == "octave" and i % 2:
                bass_note += 12
            elif m["bass_mode"] == "fifth" and i % 2:
                bass_note += 7
            _add(layers["bass"], (start + at(s)) * SR, _voice(m["bass_voice"], _freq(bass_note), length),
                 m["bass_level"])

        if is_final:
            # resolve: tonic chord hit, crash, and the lead lands on the root
            if m["stab"]:
                for off in ([chord[0], chord[0] + 7, chord[0] + 12] if m["power"] else chord):
                    _add(layers["stab"], t0, _voice(m["stab_voice"], _freq(root + off), seg), m["stab_level"])
            if m["lead"]:
                _add(layers["lead"], t0, _voice(m["lead_voice"], _freq(root + m["lead_octave"]), min(seg, 2.5)),
                     m["lead_level"])
            if has_drums:
                _add(layers["drums"], t0, kit["kick"])
                _add(layers["drums"], t0, kit["crash"], 1.5)
                kick_times.append(start)
            continue

        # chord stabs (or power-chord guitar)
        if m["stab"]:
            tones = [chord[0], chord[0] + 7, chord[0] + 12] if m["power"] else chord
            stab_hits = [s for s, ch in enumerate(m["stab"]) if ch == "x"]
            for i, s in enumerate(stab_hits):
                nxt = stab_hits[i + 1] if i + 1 < len(stab_hits) else 16
                length = (nxt - s) * step * (0.95 if m["power"] else 0.6)
                for off in tones:
                    _add(layers["stab"], (start + at(s)) * SR, _voice(m["stab_voice"], _freq(root + off), length),
                         m["stab_level"])

        # arpeggio over chord tones, climbing an octave in the second half of each bar
        if m["arp"]:
            steps = int(4 / m["arp"])
            for s in range(steps):
                if rng_py.random() < 0.1:
                    continue  # small gaps keep it human
                p = arp_pattern[s % len(arp_pattern)]
                tone = chord[p % len(chord)] + (12 if p == 3 else 0)
                octave = 12 if s >= steps // 2 and mood != "calm" else 0
                f = _freq(root + tone + octave)
                _add(layers["arp"], (start + s * m["arp"] * beat) * SR,
                     _voice(m["arp_voice"], f, max(0.15, m["arp"] * beat * 1.1)), m["arp_level"])

        # lead: a two-bar motif (A A'), entering after the intro
        if m["lead"] and b >= intro:
            half = (b - intro) % 2
            phrase = (b - intro) // 2
            notes = [(s - 8, ln, off) for s, ln, off in motif if s >= 8] if half else [n for n in motif if n[0] < 8]
            if half and phrase % 2:
                notes = alt_end
            for s, ln, off in notes:
                midi = root + m["lead_octave"] + _degree(scale, degree + off)
                if midi > root + m["lead_octave"] + 14:
                    midi -= 12  # keep the melody in a singable range
                _add(layers["lead"], (start + at(2 * s)) * SR, _voice(m["lead_voice"], _freq(midi), ln * 2 * step),
                     m["lead_level"])

        # drums: silent intro (hats only), a fill every fourth bar, a crash on each new phrase
        if has_drums:
            fill_bar = b % 4 == 3 and b + 1 < bars
            for name, pattern in m["drums"].items():
                if b < intro and name not in ("hat", "wood"):
                    continue
                for s, ch in enumerate(pattern):
                    if ch != "x" or (fill_bar and s >= 12 and name in ("kick", "snare", "clap", "tom")):
                        continue
                    dest = "hats" if name in ("hat", "ohat") else "drums"
                    _add(layers[dest], (start + at(s)) * SR, kit[name])
                    if name == "kick":
                        kick_times.append(start + at(s))
            if fill_bar:
                for s in range(12, 16):
                    _add(layers["drums"], (start + at(s)) * SR, kit[m["fill"]], 0.6 + 0.12 * (s - 12))
            if b > intro and (b - intro) % 4 == 0:
                _add(layers["drums"], t0, kit["crash"])

    # sidechain "pump": duck the pads and chords under each kick (electro/workout)
    if m["pump"] and kick_times:
        duck = np.ones(total)
        n = int(0.25 * SR)
        shape = 1 - m["pump"] * np.exp(-np.arange(n) / SR / 0.07)
        for kt in kick_times:
            i = int(kt * SR)
            if i < total:
                j = min(total, i + n)
                duck[i:j] = np.minimum(duck[i:j], shape[: j - i])
        for k in ("pad", "stab", "arp"):
            layers[k] *= duck

    # dotted-eighth echo on the arpeggio and lead
    delay = int(beat * 0.75 * SR)
    for k in ("arp", "lead"):
        src = layers[k].copy()
        for e in range(1, 4):
            layers[k][delay * e:] += src[: total - delay * e] * (0.3 ** e)

    if m["crackle"]:  # vinyl texture for the lo-fi mood
        pops = (rng.random(total) < 0.00025) * rng.standard_normal(total) * 0.25
        layers["hats"] += pops + np.diff(rng.standard_normal(total + 1)) * 0.004

    dry_c = layers["pad"] + layers["stab"] + layers["bass"] + layers["drums"]
    wet_src = layers["pad"] + layers["arp"] + layers["lead"] + 0.4 * layers["stab"] + 0.15 * layers["drums"]
    rv = m["reverb"]
    left = dry_c + layers["lead"] * 0.9 + layers["arp"] * 1.1 + layers["hats"] * 1.1 + _reverb(wet_src, 1.8, rng) * rv
    right = dry_c + layers["lead"] * 1.1 + layers["arp"] * 0.9 + layers["hats"] * 0.9 + _reverb(wet_src, 1.8, rng) * rv
    mix = np.stack([left, right], axis=1)

    fade_in, fade_out = int(0.3 * SR), int(min(2.5, duration / 4) * SR)
    mix[:fade_in] *= np.linspace(0, 1, fade_in)[:, None]
    mix[-fade_out:] *= np.linspace(1, 0, fade_out)[:, None]
    # soft-clip with more drive on peaky (drum-heavy) mixes so every mood plays at a similar loudness
    mix /= np.abs(mix).max() or 1
    drive = float(np.clip(0.3 / (np.sqrt((mix ** 2).mean()) or 1), 1.2, 3.5))
    mix = np.tanh(drive * mix) / np.tanh(drive) * 0.88

    with wave.open(str(out_path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype("<i2").tobytes())
    names = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
    key = names[(root - 57) % 12] + ("m" if scale is not MAJOR else "")
    return out_path, f"Generated · {mood} · {key} · {round(bpm)} BPM"


def _reverb(signal, seconds, rng):
    n = int(seconds * SR)
    ir = rng.standard_normal(n) * np.exp(-np.arange(n) / SR / (seconds / 4))
    ir[0] = 0
    ir /= np.abs(ir).sum() / 6
    size = 1 << int(np.ceil(np.log2(len(signal) + n)))
    return np.fft.irfft(np.fft.rfft(signal, size) * np.fft.rfft(ir, size), size)[: len(signal)]


MOOD_CHOICES = ["auto", "random", *MOOD_NAMES]

if __name__ == "__main__":
    import argparse
    import json

    p = argparse.ArgumentParser(description="Synthesize a background track")
    p.add_argument("--out", required=True)
    p.add_argument("--duration", type=float, default=23)
    p.add_argument("--seed", type=int)
    p.add_argument("--mood", choices=MOOD_CHOICES)
    p.add_argument("--category", help="video style id; picks the matching mood when --mood is auto")
    a = p.parse_args()
    _, label = generate_music(a.duration, a.out, a.seed, a.mood, category=a.category)
    print(json.dumps({"event": "done", "music": label}), flush=True)
