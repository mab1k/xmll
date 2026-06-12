/** UUID, работает и по HTTP (не только в secure context). */
export function newId(): string {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    try {
      return crypto.randomUUID()
    } catch {
      // HTTP без TLS — randomUUID недоступен
    }
  }
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 11)}`
}
