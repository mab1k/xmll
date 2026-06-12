import { useState } from 'react'
import { login } from '../api'
import { saveAuth } from '../auth'
import type { AuthUser } from '../types'
import { Button } from './ui'

interface LoginPageProps {
  onSuccess: (user: AuthUser) => void
}

export function LoginPage({ onSuccess }: LoginPageProps) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setError('')
    setLoading(true)
    try {
      const result = await login(username, password)
      saveAuth(result.token, result.user)
      onSuccess(result.user)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка входа')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <form className="login-card" onSubmit={(e) => void handleSubmit(e)}>
        <h1>Генератор заключения</h1>
        <p className="login-subtitle">Вход в систему</p>
        {error && <div className="alert alert-error">{error}</div>}
        <label className="field">
          <span className="field-label">Логин</span>
          <input
            className="input"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="username"
            required
          />
        </label>
        <label className="field">
          <span className="field-label">Пароль</span>
          <input
            className="input"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            required
          />
        </label>
        <Button type="submit" disabled={loading}>
          {loading ? 'Вход…' : 'Войти'}
        </Button>
      </form>
    </div>
  )
}
