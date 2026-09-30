import { useState } from 'react';
import { Link, Navigate, useNavigate, useSearchParams } from 'react-router-dom';
import { Eye, EyeOff, Loader2 } from 'lucide-react';
import { api } from '../api';
import { useStore } from '../store';

function safeNext(params) {
  const next = params.get('next') || '/';
  return next.startsWith('/') && !next.startsWith('//') ? next : '/';
}

function AuthShell({ title, subtitle, children, footer }) {
  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-brand"><img src="/logo.png" alt="Stick Reels" /></div>
        <h1>{title}</h1>
        <p className="muted">{subtitle}</p>
        {children}
        <p className="auth-footer muted">{footer}</p>
      </div>
    </div>
  );
}

function PasswordInput({ value, onChange, autoComplete, placeholder }) {
  const [show, setShow] = useState(false);
  return (
    <span className="password-field">
      <input type={show ? 'text' : 'password'} value={value} onChange={onChange} autoComplete={autoComplete}
        placeholder={placeholder} required minLength={autoComplete === 'new-password' ? 8 : undefined} />
      <button type="button" onClick={() => setShow((s) => !s)} aria-label={show ? 'Hide password' : 'Show password'}>
        {show ? <EyeOff size={16} /> : <Eye size={16} />}
      </button>
    </span>
  );
}

export function Login() {
  const { account, setAccount } = useStore();
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  if (account) return <Navigate to={safeNext(params)} replace />;

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError('');
    try {
      setAccount(await api.login(form));
      navigate(safeNext(params), { replace: true });
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  };

  return (
    <AuthShell title="Welcome back" subtitle="Log in to create and schedule your Shorts."
      footer={<>New here? <Link to={`/signup${params.get('next') ? `?next=${encodeURIComponent(params.get('next'))}` : ''}`} className="link">Create a free account</Link></>}>
      <form className="auth-form" onSubmit={submit}>
        <label className="stack">
          <span className="label">Email</span>
          <input type="email" value={form.email} autoComplete="email" required autoFocus
            onChange={(e) => setForm({ ...form, email: e.target.value })} />
        </label>
        <label className="stack">
          <span className="label">Password</span>
          <PasswordInput value={form.password} autoComplete="current-password"
            onChange={(e) => setForm({ ...form, password: e.target.value })} />
        </label>
        {error && <p className="form-error" role="alert">{error}</p>}
        <button className="btn primary block lg" disabled={busy}>{busy && <Loader2 className="spin" size={16} />} Log in</button>
      </form>
    </AuthShell>
  );
}

export function Signup() {
  const { account, setAccount } = useStore();
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: '', email: '', password: '', confirm: '', agree: false });
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  if (account) return <Navigate to={safeNext(params)} replace />;
  const set = (patch) => setForm((f) => ({ ...f, ...patch }));

  const submit = async (e) => {
    e.preventDefault();
    setError('');
    if (form.password.length < 8) return setError('Password must be at least 8 characters');
    if (form.password !== form.confirm) return setError("Passwords don't match");
    if (!form.agree) return setError('Please accept the terms to continue');
    setBusy(true);
    try {
      setAccount(await api.signup({ name: form.name, email: form.email, password: form.password }));
      navigate(safeNext(params), { replace: true });
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  };

  return (
    <AuthShell title="Create your free account" subtitle="Registration is free. Try one Short on us, then pick a plan to upload and schedule."
      footer={<>Already have an account? <Link to="/login" className="link">Log in</Link></>}>
      <form className="auth-form" onSubmit={submit}>
        <label className="stack">
          <span className="label">Full name</span>
          <input value={form.name} autoComplete="name" required autoFocus maxLength={80} onChange={(e) => set({ name: e.target.value })} />
        </label>
        <label className="stack">
          <span className="label">Email</span>
          <input type="email" value={form.email} autoComplete="email" required onChange={(e) => set({ email: e.target.value })} />
        </label>
        <label className="stack">
          <span className="label">Password</span>
          <PasswordInput value={form.password} autoComplete="new-password" placeholder="At least 8 characters"
            onChange={(e) => set({ password: e.target.value })} />
        </label>
        <label className="stack">
          <span className="label">Confirm password</span>
          <PasswordInput value={form.confirm} autoComplete="new-password" onChange={(e) => set({ confirm: e.target.value })} />
        </label>
        <label className="toggle">
          <input type="checkbox" checked={form.agree} onChange={(e) => set({ agree: e.target.checked })} />
          <span>I agree to the Terms of Service and Privacy Policy</span>
        </label>
        {error && <p className="form-error" role="alert">{error}</p>}
        <button className="btn primary block lg" disabled={busy}>{busy && <Loader2 className="spin" size={16} />} Create free account</button>
      </form>
    </AuthShell>
  );
}
