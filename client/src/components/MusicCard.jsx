import { useCallback, useEffect, useRef, useState } from 'react';
import { Loader2, Music, Play, Trash2, Upload, Wand2 } from 'lucide-react';
import { Link } from 'react-router-dom';
import { api } from '../api';
import { useStore } from '../store';

const MODES = [
  { id: 'generated', label: 'Generated', hint: 'An original royalty-free track composed for every Short, in a style that fits the video. No copyright claims.' },
  { id: 'library', label: 'My music', hint: 'A random track from your uploads. Use only music you have the rights to.' },
  { id: 'off', label: 'Off', hint: 'Shorts are rendered silent.' },
];
const MOODS = ['auto', 'random', 'epic', 'chase', 'sporty', 'rock', 'funky', 'electro', 'workout', 'quirky',
  'chill', 'zen', 'elegant', 'upbeat', 'calm', 'dreamy', 'cosmic'];
const moodLabel = (m) => ({ auto: 'Match the video', random: 'Random each time' }[m] || m[0].toUpperCase() + m.slice(1));

export default function MusicCard() {
  const { settings, saveSettings, notify, loadJobs } = useStore();
  const [tracks, setTracks] = useState([]);
  const [canUpload, setCanUpload] = useState(false);
  const [sample, setSample] = useState(null);
  const [sampling, setSampling] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [backfill, setBackfill] = useState(null);
  const fileRef = useRef(null);

  const loadTracks = useCallback(() => api.musicTracks().then((d) => {
    setTracks(d.tracks);
    setCanUpload(d.canUpload);
  }).catch(() => {}), []);
  const loadBackfill = useCallback(() => api.backfillStatus().then(setBackfill).catch(() => {}), []);
  useEffect(() => {
    loadTracks();
    loadBackfill();
  }, [loadTracks, loadBackfill]);
  useEffect(() => {
    if (!backfill?.running) return undefined;
    const id = setInterval(() => {
      loadBackfill();
      loadJobs();
    }, 2000);
    return () => clearInterval(id);
  }, [backfill?.running, loadBackfill, loadJobs]);

  const mode = settings.musicMode;

  const preview = async () => {
    setSampling(true);
    try {
      setSample(await api.musicSample(['auto', 'random'].includes(settings.musicMood) ? undefined : settings.musicMood));
    } catch (e) {
      notify(e.message, 'error');
    } finally {
      setSampling(false);
    }
  };

  const upload = async (files) => {
    setUploading(true);
    try {
      for (const file of files) await api.uploadTrack(file);
      notify(`${files.length} track${files.length > 1 ? 's' : ''} added`);
      loadTracks();
    } catch (e) {
      notify(e.message, 'error');
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = '';
    }
  };

  const runBackfill = async () => {
    try {
      setBackfill(await api.startBackfill());
      notify('Adding music to your Shorts…');
    } catch (e) {
      notify(e.message, 'error');
    }
  };

  return (
    <section className="card">
      <div className="card-head">
        <span className="card-icon"><Music size={18} /></span>
        <div>
          <h2>Music</h2>
          <p className="muted">Background music added to every new Short.</p>
        </div>
      </div>

      <div className="segmented three">
        {MODES.map((m) => (
          <button key={m.id} type="button" className={mode === m.id ? 'on' : ''} onClick={() => saveSettings({ musicMode: m.id })}>
            {m.label}
          </button>
        ))}
      </div>
      <span className="hint">{MODES.find((m) => m.id === mode)?.hint}</span>

      {mode === 'generated' && (
        <div className="music-row">
          <label className="stack grow">
            <span className="label">Mood</span>
            <select value={settings.musicMood} onChange={(e) => {
              saveSettings({ musicMood: e.target.value });
              setSample(null);
            }}>
              {MOODS.map((m) => <option key={m} value={m}>{moodLabel(m)}</option>)}
            </select>
          </label>
          <button type="button" className="btn ghost" onClick={preview} disabled={sampling}>
            {sampling ? <Loader2 className="spin" size={15} /> : <Play size={15} />} Preview
          </button>
        </div>
      )}
      {mode === 'generated' && sample && (
        <div className="sample">
          <span className="muted small">Sample · {sample.mood}</span>
          <audio key={sample.url} src={sample.url} controls autoPlay />
        </div>
      )}

      {mode === 'library' && (
        <div className="library">
          {tracks.length === 0 ? (
            <p className="hint warn">No tracks yet. Until you add some, generated music is used.</p>
          ) : (
            <ul className="track-list">
              {tracks.map((t) => (
                <li key={t.name}>
                  <span className="track-name" title={t.name}>{t.name}</span>
                  <audio src={t.url} controls preload="none" />
                  <button className="btn ghost sm icon danger" title="Remove" onClick={async () => {
                    await api.deleteTrack(t.name).catch((e) => notify(e.message, 'error'));
                    loadTracks();
                  }}><Trash2 size={14} /></button>
                </li>
              ))}
            </ul>
          )}
          <input ref={fileRef} type="file" accept="audio/*" multiple hidden onChange={(e) => e.target.files.length && upload([...e.target.files])} />
          {canUpload ? (
            <button type="button" className="btn ghost" disabled={uploading} onClick={() => fileRef.current?.click()}>
              {uploading ? <Loader2 className="spin" size={15} /> : <Upload size={15} />} Upload tracks
            </button>
          ) : (
            <span className="hint">Uploading your own music is part of the <Link to="/pricing" className="link">Pro and Max plans</Link>.</span>
          )}
        </div>
      )}

      {backfill && mode !== 'off' && (backfill.pending > 0 || backfill.running) && (
        <div className="connected-row">
          <Wand2 size={18} className="accent" />
          <div>
            <strong>
              {backfill.running ? `Adding music… ${backfill.done}/${backfill.total}` : `${backfill.pending} Short${backfill.pending > 1 ? 's' : ''} without music`}
            </strong>
            <span className="muted">Unpublished Shorts made before music was on can get a track added.</span>
          </div>
          {!backfill.running && <button className="btn primary sm" onClick={runBackfill}>Add music</button>}
        </div>
      )}
      {backfill?.published > 0 && (
        <span className="hint">{backfill.published} already-published Short{backfill.published > 1 ? 's' : ''} can't be changed. YouTube doesn't allow replacing a video's audio through the API.</span>
      )}
    </section>
  );
}
