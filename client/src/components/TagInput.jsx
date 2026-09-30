import { useState } from 'react';
import { X } from 'lucide-react';

export default function TagInput({ tags, onChange, placeholder }) {
  const [draft, setDraft] = useState('');

  const add = (raw) => {
    const next = raw
      .split(',')
      .map((t) => t.replace(/^#/, '').trim())
      .filter((t) => t && !tags.some((x) => x.toLowerCase() === t.toLowerCase()));
    if (next.length) onChange([...tags, ...next]);
    setDraft('');
  };

  return (
    <div className="tag-input">
      {tags.map((tag) => (
        <span key={tag} className="chip">
          #{tag}
          <button type="button" aria-label={`Remove ${tag}`} onClick={() => onChange(tags.filter((t) => t !== tag))}>
            <X size={12} />
          </button>
        </span>
      ))}
      <input
        value={draft}
        placeholder={tags.length ? '' : placeholder}
        onChange={(e) => (e.target.value.endsWith(',') ? add(e.target.value) : setDraft(e.target.value))}
        onKeyDown={(e) => {
          if (e.key === 'Enter') {
            e.preventDefault();
            add(draft);
          } else if (e.key === 'Backspace' && !draft && tags.length) {
            onChange(tags.slice(0, -1));
          }
        }}
        onBlur={() => draft && add(draft)}
      />
    </div>
  );
}
