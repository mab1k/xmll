import type { OptionItem } from '../types'

interface FieldProps {
  label: string
  required?: boolean
  optional?: boolean
  children: React.ReactNode
}

export function Field({ label, required, optional, children }: FieldProps) {
  return (
    <label className="field">
      <span className="field-label">
        {label}
        {required && <span className="required"> *</span>}
        {optional && <span className="optional"> (необяз.)</span>}
      </span>
      {children}
    </label>
  )
}

interface TextInputProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  multiline?: boolean
}

export function TextInput({ value, onChange, placeholder, multiline }: TextInputProps) {
  if (multiline) {
    return (
      <textarea
        className="input"
        rows={3}
        value={value}
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value)}
      />
    )
  }
  return (
    <input
      className="input"
      type="text"
      value={value}
      placeholder={placeholder}
      onChange={(e) => onChange(e.target.value)}
    />
  )
}

interface SelectInputProps {
  value: string
  onChange: (value: string) => void
  options: OptionItem[]
  placeholder?: string
}

export function SelectInput({ value, onChange, options, placeholder }: SelectInputProps) {
  return (
    <select className="input" value={value} onChange={(e) => onChange(e.target.value)}>
      {placeholder && <option value="">{placeholder}</option>}
      {options.map((opt) => (
        <option key={opt.value} value={opt.value}>
          {opt.label}
        </option>
      ))}
    </select>
  )
}

export function SectionCard({
  title,
  children,
}: {
  title: string
  children: React.ReactNode
}) {
  return (
    <section className="section-card">
      <h2>{title}</h2>
      <div className="section-body">{children}</div>
    </section>
  )
}

export function Button({
  children,
  onClick,
  variant = 'primary',
  disabled,
  type = 'button',
}: {
  children: React.ReactNode
  onClick?: () => void
  variant?: 'primary' | 'secondary' | 'danger'
  disabled?: boolean
  type?: 'button' | 'submit'
}) {
  return (
    <button
      type={type}
      className={`btn btn-${variant}`}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  )
}
