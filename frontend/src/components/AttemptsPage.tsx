import { useEffect, useState } from 'react'
import { deleteAttempt, downloadAttemptArchive, fetchAttempts } from '../api'
import type { AttemptSummary } from '../types'
import { Button } from './ui'

const PAGE_SIZE = 10

interface AttemptsPageProps {
  onOpen: (attemptId: string) => void
  onCreate: () => void
  onLoadExample: () => void
  onDemoGenerate: () => void
  busy?: boolean
}

function formatDate(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return value
  }
  return date.toLocaleString('ru-RU')
}

export function AttemptsPage({
  onOpen,
  onCreate,
  onLoadExample,
  onDemoGenerate,
  busy = false,
}: AttemptsPageProps) {
  const [items, setItems] = useState<AttemptSummary[]>([])
  const [search, setSearch] = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [totalPages, setTotalPages] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setDebouncedSearch(search)
      setPage(1)
    }, 300)
    return () => window.clearTimeout(timer)
  }, [search])

  const load = async (targetPage = page) => {
    setLoading(true)
    setError('')
    try {
      const result = await fetchAttempts({
        page: targetPage,
        pageSize: PAGE_SIZE,
        search: debouncedSearch,
      })
      setItems(result.items)
      setTotal(result.total)
      setTotalPages(result.totalPages)
      setPage(result.page)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось загрузить список')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load(page)
  }, [debouncedSearch, page])

  const handleDownload = async (attempt: AttemptSummary) => {
    setError('')
    try {
      const blob = await downloadAttemptArchive(attempt.id)
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = 'conclusion.zip'
      link.click()
      URL.revokeObjectURL(url)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось скачать архив')
    }
  }

  const handleDelete = async (attempt: AttemptSummary) => {
    if (!window.confirm(`Удалить «${attempt.title}»?`)) {
      return
    }
    try {
      await deleteAttempt(attempt.id)
      const nextPage = items.length === 1 && page > 1 ? page - 1 : page
      if (nextPage !== page) {
        setPage(nextPage)
      } else {
        await load(nextPage)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось удалить')
    }
  }

  const emptyMessage = debouncedSearch
    ? 'По вашему запросу ничего не найдено.'
    : 'Пока нет сохранённых проектов.'

  return (
    <div className="attempts-page">
      <div className="attempts-header">
        <div>
          <h2>Проекты</h2>
          <p>Общие сохранённые попытки генерации заключения</p>
        </div>
        <div className="attempts-header-actions">
          <Button variant="secondary" onClick={onLoadExample} disabled={busy}>
            Заполнить примером
          </Button>
          <Button onClick={onDemoGenerate} disabled={busy}>
            {busy ? 'Генерация…' : 'Создать пример XML'}
          </Button>
          <Button variant="secondary" onClick={onCreate}>
            Новый проект
          </Button>
        </div>
      </div>

      <div className="attempts-toolbar">
        <input
          className="input attempts-search"
          placeholder="Поиск по названию проекта…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        {total > 0 && (
          <span className="attempts-count">
            Найдено: {total}
          </span>
        )}
      </div>

      <div className="alert alert-info attempts-hint">
        «Создать пример XML» — сразу скачает архив с conclusion.xml на тестовых данных.
        «Заполнить примером» — откроет форму с данными, можно посмотреть и отредактировать.
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {loading ? (
        <div className="attempts-empty">Загрузка…</div>
      ) : items.length === 0 ? (
        <div className="attempts-empty">
          <p>{emptyMessage}</p>
          {!debouncedSearch && <Button onClick={onCreate}>Создать первый проект</Button>}
        </div>
      ) : (
        <>
          <div className="attempts-list">
            {items.map((item) => (
              <article key={item.id} className="attempt-card">
                <div className="attempt-card-body">
                  <h3>{item.title}</h3>
                  {item.examinationObjectName && (
                    <p className="attempt-meta">Объект: {item.examinationObjectName}</p>
                  )}
                  <p className="attempt-meta">Изменён: {formatDate(item.updatedAt)}</p>
                  {item.hasArchive && item.lastGeneratedAt && (
                    <p className="attempt-meta">
                      XML создан: {formatDate(item.lastGeneratedAt)}
                    </p>
                  )}
                </div>
                <div className="attempt-card-actions">
                  {item.hasArchive && (
                    <Button variant="secondary" onClick={() => void handleDownload(item)}>
                      Скачать XML
                    </Button>
                  )}
                  <Button onClick={() => onOpen(item.id)}>Открыть</Button>
                  <Button variant="danger" onClick={() => void handleDelete(item)}>
                    Удалить
                  </Button>
                </div>
              </article>
            ))}
          </div>

          {totalPages > 1 && (
            <div className="pagination">
              <Button
                variant="secondary"
                disabled={page <= 1 || loading}
                onClick={() => setPage((prev) => Math.max(prev - 1, 1))}
              >
                Назад
              </Button>
              <span className="pagination-info">
                Страница {page} из {totalPages}
              </span>
              <Button
                variant="secondary"
                disabled={page >= totalPages || loading}
                onClick={() => setPage((prev) => Math.min(prev + 1, totalPages))}
              >
                Вперёд
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
