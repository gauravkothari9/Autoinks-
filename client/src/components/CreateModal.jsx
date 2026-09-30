import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { CalendarClock, Crown, Loader2, Lock, Plus, Repeat, Wand2, X } from 'lucide-react';
import { api } from '../api';
import { useStore } from '../store';

const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']; // ISO weekday 1..7
const PRESETS = { 'Every day': [1, 2, 3, 4, 5, 6, 7], Weekdays: [1, 2, 3, 4, 5], Weekends: [6, 7] };

// <input type="datetime-local"> wants local "YYYY-MM-DDTHH:mm"
function toLocalInput(date) {
  const pad = (n) => String(n).padStart(2, '0');
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

export default function CreateModal({ category, onClose }) {
  const { settings, loadJobs, notify, hasPlan, account } = useStore();
  const trialLeft = !hasPlan && account?.usage?.trialLeft > 0;
  const navigate = useNavigate();
  const [count, setCount] = useState(1);
  const [privacy, setPrivacy] = useState(settings?.privacy || 'public');
  const [submitting, setSubmitting] = useState(false);
  const [when, setWhen] = useState('now'); // 'now' | 'once' | 'repeat'
  const [publishAt, setPublishAt] = useState(() => toLocalInput(new Date(Date.now() + 2 * 3600 * 1000)));
  const [days, setDays] = useState(PRESETS['Every day']);
  const [times, setTimes] = useState(['18:00']);
  const yt = settings?.youtube;
  const perSlot = Math.min(count, 3);

  useEffect(() => {
    const onKey = (e) => e.key === 'Escape' && onClose();
    document.addEventListener('keydown', onKey);
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', onKey);
      document.body.style.overflow = '';
    };
  }, [onClose]);

  const toggleDay = (d) => setDays((cur) => (cur.includes(d) ? cur.filter((x) => x !== d) : [...cur, d].sort()));

  const startAutopilot = async () => {
    if (!days.length) return notify('Pick at least one day', 'error');
    await api.createSchedule({
      name: `${category.name} · ${days.length === 7 ? 'daily' : days.map((d) => DAYS[d - 1]).join(' ')}`,
      categories: [category.id],
      days,
      times: times.filter(Boolean),
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      privacy,
      perSlot,
    });
    notify(`Autopilot on: ${category.name} ${days.length === 7 ? 'every day' : 'on your chosen days'}`);
    onClose();
    navigate('/profile/schedule');
  };

  const generate = async () => {
    const scheduledFor = when === 'once' ? new Date(publishAt).toISOString() : undefined;
    const created = await api.createJobs({ category: category.id, count, privacy, scheduledFor });
    const what = `${created.length} ${category.name} Short${created.length > 1 ? 's' : ''}`;
    notify(scheduledFor ? `${what} scheduled for ${new Date(publishAt).toLocaleString()}` : `Creating ${what}. Upload it from Your Shorts when ready.`);
    loadJobs();
    onClose();
    navigate('/profile/shorts');
  };

  const submit = async () => {
    setSubmitting(true);
    try {
      await (when === 'repeat' ? startAutopilot() : generate());
    } catch (e) {
      notify(e.message, 'error');
    } finally {
      setSubmitting(false);
    }
  };

  const shorts = (n) => `${n > 1 ? `${n} Shorts` : 'Short'}`;
  const label = when === 'repeat' ? 'Start autopilot' : when === 'once' ? `Schedule ${shorts(count)}` : `Create ${shorts(count)}`;
  const Icon = when === 'repeat' ? Repeat : when === 'once' ? CalendarClock : Wand2;

  return (
    <div className="modal-backdrop" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal" role="dialog" aria-modal="true" aria-labelledby="create-title">
        <button className="modal-close" onClick={onClose} aria-label="Close"><X size={18} /></button>
        <div className="modal-media">
          {category.previewUrl ? (
            <video src={category.previewUrl} poster={category.posterUrl} autoPlay muted loop playsInline />
          ) : (
            <div className="preview-pending"><Loader2 className="spin" size={22} /></div>
          )}
        </div>
        <div className="modal-body">
          <span className="eyebrow">{category.group}</span>
          <h2 id="create-title">Create {category.name}</h2>
          <p className="muted">{category.description} Every video gets new random moves, colors and music.</p>

          <div className="field">
            <span className="label">Tags added to every Short</span>
            <div className="tag-preview">
              {settings?.userTags?.length
                ? settings.userTags.map((t) => <span key={t} className="chip">#{t}</span>)
                : <span className="muted">No personal tags yet.</span>}
              <Link to="/profile/account" onClick={onClose} className="link">Edit in Profile</Link>
            </div>
            <span className="hint">Style tags ({category.hashtags.slice(0, 3).map((h) => `#${h.replace(/\s+/g, '')}`).join(' ')}) and popular tags are added automatically.</span>
          </div>

          <div className="field">
            <span className="label">Publish</span>
            <div className="segmented three">
              <button type="button" className={when === 'now' ? 'on' : ''} onClick={() => setWhen('now')}>
                <Wand2 size={14} /> Create now
              </button>
              <button type="button" className={when === 'once' ? 'on' : ''} disabled={!hasPlan} title={hasPlan ? '' : 'Needs a plan'} onClick={() => setWhen('once')}>
                {!hasPlan && <Lock size={12} />}
                <CalendarClock size={14} /> Once later
              </button>
              <button type="button" className={when === 'repeat' ? 'on' : ''} disabled={!hasPlan} title={hasPlan ? '' : 'Needs a plan'} onClick={() => setWhen('repeat')}>
                {!hasPlan && <Lock size={12} />}
                <Repeat size={14} /> Repeat
              </button>
            </div>

            {when === 'once' && (
              <>
                <input type="datetime-local" value={publishAt} min={toLocalInput(new Date(Date.now() + 15 * 60 * 1000))}
                  onChange={(e) => setPublishAt(e.target.value)} />
                <span className="hint">Renders now and goes live at this time.</span>
              </>
            )}

            {when === 'repeat' && (
              <div className="repeat-box">
                <div className="day-picker">
                  {DAYS.map((d, i) => (
                    <button key={d} type="button" className={days.includes(i + 1) ? 'on' : ''} aria-pressed={days.includes(i + 1)}
                      onClick={() => toggleDay(i + 1)}>{d}</button>
                  ))}
                </div>
                <div className="row">
                  {Object.entries(PRESETS).map(([name, preset]) => (
                    <button key={name} type="button"
                      className={`filter-chip${days.join() === preset.join() ? ' active' : ''}`}
                      onClick={() => setDays(preset)}>{name}</button>
                  ))}
                </div>
                <div className="time-list">
                  {times.map((t, i) => (
                    <span key={i} className="time-input">
                      <input type="time" value={t} required aria-label={`Post time ${i + 1}`}
                        onChange={(e) => setTimes(times.map((x, j) => (j === i ? e.target.value : x)))} />
                      {times.length > 1 && (
                        <button type="button" aria-label="Remove time" onClick={() => setTimes(times.filter((_, j) => j !== i))}>
                          <X size={13} />
                        </button>
                      )}
                    </span>
                  ))}
                  {times.length < 6 && (
                    <button type="button" className="btn ghost sm" onClick={() => setTimes([...times, '12:00'])}>
                      <Plus size={14} /> Add time
                    </button>
                  )}
                </div>
                <span className="hint">
                  A fresh {category.name} is made and uploaded automatically at each time
                  ({Intl.DateTimeFormat().resolvedOptions().timeZone}). Manage it on the{' '}
                  <Link to="/profile/schedule" onClick={onClose} className="link">Schedule</Link> in Profile.
                </span>
              </div>
            )}
          </div>

          <div className="field two">
            <label>
              <span className="label">Visibility</span>
              <select value={privacy} onChange={(e) => setPrivacy(e.target.value)}>
                <option value="public">Public</option>
                <option value="unlisted">Unlisted</option>
                <option value="private">Private</option>
              </select>
            </label>
            <label>
              <span className="label">{when === 'repeat' ? 'Shorts each time' : 'How many'}</span>
              <select value={when === 'repeat' ? perSlot : count} onChange={(e) => setCount(Number(e.target.value))}>
                {(when === 'repeat' ? [1, 2, 3] : [1, 2, 3, 5, 10]).map((n) => <option key={n} value={n}>{n}</option>)}
              </select>
            </label>
          </div>

          {when === 'now' && (
            <p className="hint">Creates the video only. Upload it from Your Shorts when you're happy with it.</p>
          )}
          {when !== 'now' && !yt?.connected && (
            <p className="hint warn">
              YouTube isn't connected. Videos will wait in Your Shorts until you <Link to="/profile/account" onClick={onClose} className="link">connect</Link>.
            </p>
          )}

          {!hasPlan && (
            <div className="plan-note">
              <Crown size={16} />
              <span>
                {trialLeft
                  ? 'Free account: you can create 1 trial Short (watermarked, not uploadable). Plans unlock uploads, scheduling and more Shorts.'
                  : "You've used your free trial Short. Choose a plan to keep creating."}
              </span>
            </div>
          )}
          {!hasPlan && !trialLeft ? (
            <Link to="/pricing" onClick={onClose} className="btn primary block lg"><Crown size={16} /> See plans</Link>
          ) : (
            <button className="btn primary block lg" disabled={submitting} onClick={submit}>
              {submitting ? <Loader2 className="spin" size={16} /> : <Icon size={16} />} {hasPlan ? label : 'Create free trial Short'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
