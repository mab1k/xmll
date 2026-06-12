import { useEffect, useState } from 'react'
import { createAdminUser, deleteAdminUser, fetchAdminUsers, updateAdminUser } from '../api'
import type { AdminUser } from '../types'
import { Button } from './ui'

interface AdminPageProps {
  currentUserId: string
  onBack: () => void
}

export function AdminPage({ currentUserId, onBack }: AdminPageProps) {
  const [users, setUsers] = useState<AdminUser[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [newUsername, setNewUsername] = useState('')
  const [newPassword, setNewPassword] = useState('')

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      setUsers(await fetchAdminUsers())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [])

  const handleCreate = async () => {
    setError('')
    setSuccess('')
    try {
      const user = await createAdminUser(newUsername, newPassword)
      setUsers((prev) => [...prev, user])
      setNewUsername('')
      setNewPassword('')
      setSuccess('Пользователь создан')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка создания')
    }
  }

  return (
    <div className="attempts-page">
      <div className="attempts-header">
        <div>
          <h2>Администрирование</h2>
          <p>Управление пользователями системы</p>
        </div>
        <Button variant="secondary" onClick={onBack}>
          Назад
        </Button>
      </div>

      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      <section className="section-card admin-create">
        <h3>Новый пользователь</h3>
        <div className="admin-form-row">
          <input
            className="input"
            placeholder="Логин"
            value={newUsername}
            onChange={(e) => setNewUsername(e.target.value)}
          />
          <input
            className="input"
            type="password"
            placeholder="Пароль"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
          />
          <Button onClick={() => void handleCreate()}>Добавить</Button>
        </div>
      </section>

      {loading ? (
        <div className="attempts-empty">Загрузка…</div>
      ) : (
        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Логин</th>
                <th>Роль</th>
                <th>Статус</th>
                <th>Создан</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <AdminUserRow
                  key={user.id}
                  user={user}
                  isSelf={user.id === currentUserId}
                  onUpdated={(updated) =>
                    setUsers((prev) => prev.map((item) => (item.id === updated.id ? updated : item)))
                  }
                  onDeleted={() => setUsers((prev) => prev.filter((item) => item.id !== user.id))}
                  onError={setError}
                />
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

function AdminUserRow({
  user,
  isSelf,
  onUpdated,
  onDeleted,
  onError,
}: {
  user: AdminUser
  isSelf: boolean
  onUpdated: (user: AdminUser) => void
  onDeleted: () => void
  onError: (message: string) => void
}) {
  const [username, setUsername] = useState(user.username)
  const [password, setPassword] = useState('')
  const [isActive, setIsActive] = useState(user.isActive)

  useEffect(() => {
    setUsername(user.username)
    setIsActive(user.isActive)
  }, [user])

  const handleSave = async () => {
    onError('')
    try {
      const updated = await updateAdminUser(user.id, {
        username: username !== user.username ? username : undefined,
        password: password || undefined,
        isActive: isActive !== user.isActive ? isActive : undefined,
      })
      onUpdated(updated)
      setPassword('')
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Ошибка сохранения')
    }
  }

  const handleDelete = async () => {
    if (!window.confirm(`Удалить пользователя «${user.username}»?`)) {
      return
    }
    onError('')
    try {
      await deleteAdminUser(user.id)
      onDeleted()
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Ошибка удаления')
    }
  }

  return (
    <tr>
      <td>
        <input
          className="input"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          disabled={user.isAdmin}
        />
      </td>
      <td>{user.isAdmin ? 'Администратор' : 'Пользователь'}</td>
      <td>{user.isActive ? 'Активен' : 'Отключён'}</td>
      <td>{new Date(user.createdAt).toLocaleString('ru-RU')}</td>
      <td className="admin-actions">
        <input
          className="input"
          type="password"
          placeholder="Новый пароль"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        {!user.isAdmin && (
          <label className="admin-active">
            <input
              type="checkbox"
              checked={isActive}
              onChange={(e) => setIsActive(e.target.checked)}
            />
            Активен
          </label>
        )}
        <Button variant="secondary" onClick={() => void handleSave()}>
          Сохранить
        </Button>
        {!isSelf && !user.isAdmin && (
          <Button variant="danger" onClick={() => void handleDelete()}>
            Удалить
          </Button>
        )}
      </td>
    </tr>
  )
}
