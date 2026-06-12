import { downloadStoredFile } from '../api'
import type { ProjectAttachmentItem } from '../types'
import { Button, Field, SectionCard, TextInput } from './ui'

interface ProjectAttachmentsSectionProps {
  title: string
  hint: string
  accept: string
  items: ProjectAttachmentItem[]
  onChange: (items: ProjectAttachmentItem[]) => void
}

function StoredFileRow({
  fileId,
  fileName,
}: {
  fileId: string
  fileName: string
}) {
  const handleDownload = async () => {
    try {
      await downloadStoredFile(fileId, fileName)
    } catch {
      window.alert('Не удалось скачать файл')
    }
  }

  return (
    <div className="stored-file-row">
      <span className="stored-file-label">Сохранённый файл:</span>
      <button type="button" className="stored-file-link" onClick={() => void handleDownload()}>
        {fileName}
      </button>
    </div>
  )
}

export function ProjectAttachmentsSection({
  title,
  hint,
  accept,
  items,
  onChange,
}: ProjectAttachmentsSectionProps) {
  const updateItem = (id: string, updated: ProjectAttachmentItem) => {
    onChange(items.map((item) => (item.id === id ? updated : item)))
  }

  const removeItem = (id: string) => {
    onChange(items.filter((item) => item.id !== id))
  }

  const addItem = () => {
    onChange([
      ...items,
      {
        id: crypto.randomUUID(),
        file: null,
        fileName: '',
        comment: '',
      },
    ])
  }

  return (
    <SectionCard title={title}>
      <p className="hint">{hint}</p>
      {items.length === 0 && <p className="hint">Файлы ещё не добавлены.</p>}
      {items.map((item, index) => (
        <div key={item.id} className="repeat-block">
          <div className="repeat-header">
            <h3>Файл {index + 1}</h3>
            <Button variant="danger" onClick={() => removeItem(item.id)}>
              Удалить
            </Button>
          </div>
          <div className="grid">
            <Field label="Комментарий" optional>
              <TextInput
                value={item.comment}
                onChange={(value) => updateItem(item.id, { ...item, comment: value })}
                placeholder="Например: номер, дата, примечание"
              />
            </Field>
            <Field label="Файл" optional>
              {item.fileStorageId && (
                <StoredFileRow
                  fileId={item.fileStorageId}
                  fileName={item.fileName || 'file'}
                />
              )}
              <input
                className="input"
                type="file"
                accept={accept}
                onChange={(e) => {
                  const file = e.target.files?.[0] || null
                  updateItem(item.id, {
                    ...item,
                    file,
                    fileName: file?.name || item.fileName,
                  })
                }}
              />
            </Field>
          </div>
        </div>
      ))}
      <Button variant="secondary" onClick={addItem}>
        + Добавить файл
      </Button>
    </SectionCard>
  )
}
