import { useCallback, useEffect, useRef, useState } from 'react'
import {
  createAttempt,
  downloadAttemptArchive,
  fetchAttempt,
  fetchMe,
  fetchOptions,
  generateConclusion,
  generateDemoXml,
  generateSavedAttempt,
  setUnauthorizedHandler,
  updateAttempt,
} from './api'
import { AdminPage } from './components/AdminPage'
import { AttemptsPage } from './components/AttemptsPage'
import { LoginPage } from './components/LoginPage'
import { SectionRenderer } from './components/SectionRenderer'
import { Button } from './components/ui'
import { clearAuth, getStoredUser, getToken, saveAuth } from './auth'
import { createDefaultForm } from './defaultForm'
import { createDemoProjectTitle, loadDemoForm } from './demoForm'
import { hydrateForm } from './formStorage'
import { SECTIONS } from './formConfig'
import type { AuthUser, FormState, OptionsMap } from './types'
import './App.css'

type ViewMode = 'list' | 'editor' | 'admin'
type SaveStatus = 'idle' | 'saving' | 'saved' | 'error'

const AUTOSAVE_DELAY_MS = 500

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  URL.revokeObjectURL(url)
}

function App() {
  const [user, setUser] = useState<AuthUser | null>(getStoredUser())
  const [authReady, setAuthReady] = useState(false)
  const [view, setView] = useState<ViewMode>('list')
  const [form, setForm] = useState<FormState>(createDefaultForm)
  const [options, setOptions] = useState<OptionsMap | null>(null)
  const [activeSection, setActiveSection] = useState<string>('org')
  const [attemptId, setAttemptId] = useState<string | null>(null)
  const [hasArchive, setHasArchive] = useState(false)
  const [lastGeneratedAt, setLastGeneratedAt] = useState<string | null>(null)
  const [projectTitle, setProjectTitle] = useState('Без названия')
  const [loading, setLoading] = useState(false)
  const [saveStatus, setSaveStatus] = useState<SaveStatus>('idle')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const skipAutosaveRef = useRef(false)
  const saveInFlightRef = useRef(false)
  const pendingSaveRef = useRef(false)

  const logout = () => {
    clearAuth()
    setUser(null)
    setOptions(null)
    setView('list')
    setAuthReady(true)
  }

  useEffect(() => {
    setUnauthorizedHandler(() => {
      setUser(null)
      setOptions(null)
    })
  }, [])

  useEffect(() => {
    const init = async () => {
      if (!getToken()) {
        setAuthReady(true)
        return
      }
      try {
        const me = await fetchMe()
        setUser(me)
        saveAuth(getToken()!, me)
        const opts = await fetchOptions()
        setOptions(opts)
      } catch {
        clearAuth()
        setUser(null)
      } finally {
        setAuthReady(true)
      }
    }
    void init()
  }, [])

  const handleLogin = async (authUser: AuthUser) => {
    setUser(authUser)
    setError('')
    const opts = await fetchOptions()
    setOptions(opts)
    setView('list')
  }

  const handleLogout = () => {
    logout()
  }

  const update = <K extends keyof FormState>(key: K, value: FormState[K]) => {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  const applyAttemptMeta = (detail: {
    hasArchive: boolean
    lastGeneratedAt: string | null
  }) => {
    setHasArchive(detail.hasArchive)
    setLastGeneratedAt(detail.lastGeneratedAt)
  }

  const markEditorContentLoaded = () => {
    skipAutosaveRef.current = true
  }

  const openNewProject = () => {
    markEditorContentLoaded()
    setAttemptId(null)
    setHasArchive(false)
    setLastGeneratedAt(null)
    setProjectTitle('Без названия')
    setForm(createDefaultForm())
    setActiveSection('org')
    setError('')
    setSuccess('')
    setSaveStatus('idle')
    setView('editor')
  }

  const loadExample = async () => {
    setError('')
    setSuccess('')
    setLoading(true)
    try {
      const demoForm = await loadDemoForm()
      markEditorContentLoaded()
      setAttemptId(null)
      setProjectTitle(createDemoProjectTitle(demoForm))
      setForm(demoForm)
      setSaveStatus('idle')
      setActiveSection('org')
      setView('editor')
      setSuccess('Форма заполнена примером. Нажмите «Создать XML».')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось загрузить пример')
    } finally {
      setLoading(false)
    }
  }

  const handleDemoGenerate = async () => {
    setError('')
    setSuccess('')
    setLoading(true)
    try {
      const blob = await generateDemoXml()
      downloadBlob(blob, 'conclusion-demo.zip')
      setSuccess('Пример conclusion-demo.zip скачан')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка генерации примера')
    } finally {
      setLoading(false)
    }
  }

  const openProject = async (id: string) => {
    setLoading(true)
    setError('')
    try {
      const detail = await fetchAttempt(id)
      markEditorContentLoaded()
      setAttemptId(detail.id)
      setProjectTitle(detail.title)
      setForm(hydrateForm(detail.form))
      setSaveStatus('saved')
      applyAttemptMeta(detail)
      setActiveSection('org')
      setSuccess('')
      setView('editor')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось открыть проект')
    } finally {
      setLoading(false)
    }
  }

  const persistProject = useCallback(
    async (options: { showSuccess?: boolean; useLoading?: boolean } = {}) => {
      const { showSuccess = false, useLoading = false } = options

      if (saveInFlightRef.current) {
        pendingSaveRef.current = true
        return
      }

      saveInFlightRef.current = true
      setSaveStatus('saving')
      if (useLoading) {
        setLoading(true)
      }

      try {
        const title =
          projectTitle.trim() ||
          form.examinationObject.name.trim() ||
          'Без названия'
        const detail = attemptId
          ? await updateAttempt(attemptId, title, form)
          : await createAttempt(title, form)
        setAttemptId(detail.id)
        setProjectTitle(detail.title)
        skipAutosaveRef.current = true
        setForm(hydrateForm(detail.form))
        applyAttemptMeta(detail)
        setSaveStatus('saved')
        setError('')
        if (showSuccess) {
          setSuccess('Проект сохранён')
        }
      } catch (err) {
        setSaveStatus('error')
        setError(err instanceof Error ? err.message : 'Ошибка сохранения')
      } finally {
        saveInFlightRef.current = false
        if (useLoading) {
          setLoading(false)
        }
        if (pendingSaveRef.current) {
          pendingSaveRef.current = false
          void persistProject(options)
        }
      }
    },
    [attemptId, form, projectTitle],
  )

  useEffect(() => {
    if (view !== 'editor') {
      return
    }

    if (skipAutosaveRef.current) {
      skipAutosaveRef.current = false
      return
    }

    const timer = window.setTimeout(() => {
      void persistProject()
    }, AUTOSAVE_DELAY_MS)

    return () => window.clearTimeout(timer)
  }, [form, projectTitle, view, persistProject])

  const handleSave = async () => {
    setSuccess('')
    await persistProject({ showSuccess: true, useLoading: true })
  }

  const handleDownloadArchive = async () => {
    if (!attemptId) {
      return
    }
    setError('')
    setSuccess('')
    setLoading(true)
    try {
      const blob = await downloadAttemptArchive(attemptId)
      downloadBlob(blob, 'conclusion.zip')
      setSuccess('Архив conclusion.zip скачан')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось скачать архив')
    } finally {
      setLoading(false)
    }
  }

  const handleGenerate = async () => {
    setError('')
    setSuccess('')
    setLoading(true)
    try {
      const title =
        projectTitle.trim() ||
        form.examinationObject.name.trim() ||
        'Без названия'
      let currentAttemptId = attemptId
      if (currentAttemptId) {
        const detail = await updateAttempt(currentAttemptId, title, form)
        currentAttemptId = detail.id
        setAttemptId(detail.id)
        setProjectTitle(detail.title)
        setForm(hydrateForm(detail.form))
      }
      const blob = currentAttemptId
        ? await generateSavedAttempt(currentAttemptId)
        : await generateConclusion(form)
      downloadBlob(blob, 'conclusion.zip')
      if (currentAttemptId) {
        const detail = await fetchAttempt(currentAttemptId)
        applyAttemptMeta(detail)
      }
      setSuccess('Архив conclusion.zip скачан и сохранён в проекте')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка генерации')
    } finally {
      setLoading(false)
    }
  }

  if (!authReady) {
    return <div className="app loading">Загрузка…</div>
  }

  if (!user) {
    return <LoginPage onSuccess={(authUser) => void handleLogin(authUser)} />
  }

  if (!options) {
    return <div className="app loading">Загрузка справочников…</div>
  }

  if (view === 'admin') {
    return (
      <div className="app app-single">
        <main className="content content-wide">
          <AdminPage currentUserId={user.id} onBack={() => setView('list')} />
        </main>
      </div>
    )
  }

  if (view === 'list') {
    return (
      <div className="app app-single">
        <header className="top-bar">
          <span className="top-bar-user">{user.username}</span>
          {user.isAdmin && (
            <Button variant="secondary" onClick={() => setView('admin')}>
              Админка
            </Button>
          )}
          <Button variant="secondary" onClick={handleLogout}>
            Выйти
          </Button>
        </header>
        <main className="content content-wide">
          <AttemptsPage
            onOpen={(id) => void openProject(id)}
            onCreate={openNewProject}
            onLoadExample={() => void loadExample()}
            onDemoGenerate={() => void handleDemoGenerate()}
            busy={loading}
          />
        </main>
      </div>
    )
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <h1>Генератор заключения</h1>
          <p>XML для ЕГРЗ (схема 01.03)</p>
          <p className="brand-user">{user.username}</p>
        </div>
        <label className="project-title-field">
          <span>Название проекта</span>
          <input
            className="input"
            value={projectTitle}
            onChange={(e) => setProjectTitle(e.target.value)}
          />
          <span className={`save-status save-status-${saveStatus}`}>
            {saveStatus === 'saving' && 'Сохранение…'}
            {saveStatus === 'saved' && 'Сохранено'}
            {saveStatus === 'error' && 'Ошибка сохранения'}
          </span>
        </label>
        <nav className="sidebar-nav">
          {SECTIONS.map((section) => (
            <button
              key={section.id}
              type="button"
              className={activeSection === section.id ? 'nav-item active' : 'nav-item'}
              onClick={() => setActiveSection(section.id)}
            >
              {section.title}
              {section.optional && <span className="nav-optional"> (необяз.)</span>}
            </button>
          ))}
        </nav>
        <div className="sidebar-footer sidebar-actions">
          {user.isAdmin && (
            <Button variant="secondary" onClick={() => setView('admin')}>
              Админка
            </Button>
          )}
          <Button variant="secondary" onClick={() => setView('list')}>
            К проектам
          </Button>
          <Button variant="secondary" onClick={handleLogout}>
            Выйти
          </Button>
          <Button variant="secondary" onClick={() => void loadExample()} disabled={loading}>
            Заполнить примером
          </Button>
          <Button onClick={() => void handleSave()} disabled={loading}>
            {loading ? 'Сохранение…' : 'Сохранить'}
          </Button>
          <Button onClick={() => void handleGenerate()} disabled={loading}>
            {loading ? 'Генерация…' : 'Создать XML'}
          </Button>
          {hasArchive && (
            <Button variant="secondary" onClick={() => void handleDownloadArchive()} disabled={loading}>
              Скачать XML
            </Button>
          )}
        </div>
      </aside>

      <main className="content">
        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}
        {hasArchive && lastGeneratedAt && (
          <div className="alert alert-info">
            Последняя генерация: {new Date(lastGeneratedAt).toLocaleString('ru-RU')}. Можно скачать архив
            повторно кнопкой «Скачать XML».
          </div>
        )}
        {!attemptId && saveStatus === 'idle' && (
          <div className="alert alert-info">
            Изменения сохраняются автоматически.
          </div>
        )}
        <SectionRenderer
          sectionId={activeSection}
          form={form}
          options={options}
          update={update}
        />
      </main>
    </div>
  )
}

export default App
