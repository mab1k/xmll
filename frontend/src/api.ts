import { clearAuth, getToken } from './auth'
import { collectNewUploads } from './formStorage'
import type {
  AdminUser,
  AttemptDetail,
  AttemptsPageResult,
  AuthUser,
  FileUploadRef,
  FormState,
  Mismatch,
  MismatchExtended,
  OptionsMap,
  SerializableFormState,
} from './types'

type ApiFetchOptions = RequestInit & { skipAuth?: boolean }

let onUnauthorized: (() => void) | null = null

export function setUnauthorizedHandler(handler: () => void): void {
  onUnauthorized = handler
}

async function parseError(response: Response, fallback: string): Promise<string> {
  const data = await response.json().catch(() => null)
  return data?.detail || fallback
}

export async function apiFetch(input: string, init: ApiFetchOptions = {}): Promise<Response> {
  const { skipAuth, headers, ...rest } = init
  const requestHeaders = new Headers(headers)
  if (!skipAuth) {
    const token = getToken()
    if (token) {
      requestHeaders.set('Authorization', `Bearer ${token}`)
    }
  }
  const response = await fetch(input, { ...rest, headers: requestHeaders })
  if (response.status === 401 && !skipAuth) {
    clearAuth()
    onUnauthorized?.()
  }
  return response
}

export async function login(username: string, password: string): Promise<{ token: string; user: AuthUser }> {
  const response = await apiFetch('/api/auth/login', {
    method: 'POST',
    skipAuth: true,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
  if (!response.ok) {
    throw new Error(await parseError(response, 'Неверный логин или пароль'))
  }
  return response.json()
}

export async function fetchMe(): Promise<AuthUser> {
  const response = await apiFetch('/api/auth/me')
  if (!response.ok) {
    throw new Error('Сессия истекла')
  }
  return response.json()
}

export async function fetchAdminUsers(): Promise<AdminUser[]> {
  const response = await apiFetch('/api/admin/users')
  if (!response.ok) {
    throw new Error(await parseError(response, 'Не удалось загрузить пользователей'))
  }
  return response.json()
}

export async function createAdminUser(username: string, password: string): Promise<AdminUser> {
  const response = await apiFetch('/api/admin/users', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
  if (!response.ok) {
    throw new Error(await parseError(response, 'Не удалось создать пользователя'))
  }
  return response.json()
}

export async function updateAdminUser(
  userId: string,
  data: { username?: string; password?: string; isActive?: boolean },
): Promise<AdminUser> {
  const response = await apiFetch(`/api/admin/users/${userId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: data.username,
      password: data.password,
      isActive: data.isActive,
    }),
  })
  if (!response.ok) {
    throw new Error(await parseError(response, 'Не удалось обновить пользователя'))
  }
  return response.json()
}

export async function deleteAdminUser(userId: string): Promise<void> {
  const response = await apiFetch(`/api/admin/users/${userId}`, { method: 'DELETE' })
  if (!response.ok) {
    throw new Error(await parseError(response, 'Не удалось удалить пользователя'))
  }
}

export function storedFileUrl(fileId: string): string {
  return `/api/files/${fileId}`
}

export async function downloadStoredFile(fileId: string, filename: string): Promise<void> {
  const response = await apiFetch(storedFileUrl(fileId))
  if (!response.ok) {
    throw new Error('Не удалось скачать файл')
  }
  const blob = await response.blob()
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  URL.revokeObjectURL(url)
}

export async function fetchDemoForm(): Promise<Record<string, unknown>> {
  const response = await apiFetch('/api/demo/form')
  if (!response.ok) {
    throw new Error('Не удалось загрузить демо-данные')
  }
  return response.json()
}

export async function fetchDemoFile(fileName: string): Promise<Blob> {
  const response = await apiFetch(`/api/demo/files/${encodeURIComponent(fileName)}`)
  if (!response.ok) {
    throw new Error(`Не удалось загрузить файл ${fileName}`)
  }
  return response.blob()
}

export async function generateDemoXml(): Promise<Blob> {
  const response = await apiFetch('/api/demo/generate', { method: 'POST' })
  if (!response.ok) {
    const data = await response.json().catch(() => null)
    throw new Error(data?.detail || 'Ошибка генерации примера')
  }
  return response.blob()
}

export async function fetchOptions(): Promise<OptionsMap> {
  const response = await apiFetch('/api/options')
  if (!response.ok) {
    throw new Error('Не удалось загрузить справочники')
  }
  return response.json()
}

function stripMismatch(item: Mismatch) {
  return {
    summary: item.summary,
    part: item.part,
    link: item.link,
  }
}

function stripMismatchExtended(item: MismatchExtended) {
  return {
    ...stripMismatch(item),
    expertType: item.expertType,
  }
}

function buildPayload(form: FormState) {
  return {
    expertOrganization: form.expertOrganization,
    approver: form.approver,
    examinationObject: form.examinationObject,
    documents: form.documents.map((doc) => ({
      docType: doc.docType,
      docName: doc.docName,
      docNumber: doc.docNumber,
      docDate: doc.docDate,
      docChanges: doc.docChanges,
      docAuthor: doc.docAuthor,
      fileName: doc.fileName,
      signFileNames: doc.signFileNames,
    })),
    previousConclusions: form.previousConclusions.map((item) => ({
      date: item.date,
      number: item.number,
      numberFormat: item.numberFormat,
      objectType: item.objectType,
      name: item.name,
      result: item.result,
    })),
    previousSimpleConclusions: form.previousSimpleConclusions.map((item) => ({
      date: item.date,
      number: item.number,
      objectType: item.objectType,
      result: item.result,
    })),
    capitalObject: form.capitalObject,
    ecology: form.ecology,
    cadastralNumbers: form.cadastralNumbers.filter((n) => n.trim()),
    declarant: form.declarant,
    projectDocumentsParties: form.projectDocumentsParties.map((party) => ({
      partyType: party.partyType,
      entity: party.entity,
    })),
    finance: form.finance.map((item) => ({
      financeType: item.financeType,
      budgetType: item.budgetType,
      financeSize: item.financeSize,
      owner: item.owner,
    })),
    financeComment: form.financeComment,
    estimatedCost: form.estimatedCost,
    climateConditions: form.climateConditions,
    designers: form.designers.map((designer) => {
      const { id: _id, ...rest } = designer
      return rest
    }),
    eepdUse: form.eepdUse.map((item) => ({
      note: item.note,
      number: item.number,
      numberFormat: item.numberFormat,
      date: item.date,
    })),
    engineeringSurveyAddresses: form.engineeringSurveyAddresses.map((item) => ({
      region: item.region,
      district: item.district,
    })),
    engineeringSurveyParties: form.engineeringSurveyParties.map((party) => ({
      partyType: party.partyType,
      entity: party.entity,
    })),
    expertEngineeringSurveys: form.expertEngineeringSurveys.map((block) => ({
      surveyType: block.surveyType,
      normsMismatches: block.normsMismatches.map(stripMismatch),
    })),
    expertProjectDocuments: form.expertProjectDocuments.map((block) => ({
      expertType: block.expertType,
      dangerSolutions: block.dangerSolutions,
      engineeringSurveyMismatches: block.engineeringSurveyMismatches.map(stripMismatch),
      projectTaskMismatches: block.projectTaskMismatches.map(stripMismatch),
      normsMismatches: block.normsMismatches.map(stripMismatch),
      dangerMismatch: block.dangerMismatch,
    })),
    expertEstimate: {
      estimateNorms: form.expertEstimate.estimateNorms,
      commonMismatches: form.expertEstimate.commonMismatches.map(stripMismatch),
      fullCalculationMismatches: form.expertEstimate.fullCalculationMismatches.map(stripMismatch),
      localCalculationMismatches: form.expertEstimate.localCalculationMismatches.map(stripMismatch),
      projectDocumentsMismatches: form.expertEstimate.projectDocumentsMismatches.map(
        stripMismatchExtended,
      ),
      basicMismatches: form.expertEstimate.basicMismatches.map(stripMismatch),
    },
    summary: form.summary,
    experts: form.experts.map((e) => ({
      familyName: e.familyName,
      firstName: e.firstName,
      secondName: e.secondName,
      expertType: e.expertType,
      expertCertificate: e.expertCertificate,
      certificateBeginDate: e.certificateBeginDate,
      certificateEndDate: e.certificateEndDate,
    })),
  }
}

async function saveAttemptRequest(
  url: string,
  method: 'POST' | 'PUT',
  title: string,
  payload: SerializableFormState,
  files: File[],
  refs: FileUploadRef[],
): Promise<AttemptDetail> {
  const body = new FormData()
  body.append('title', title)
  body.append('payload', JSON.stringify(payload))
  body.append('file_refs', JSON.stringify(refs))
  for (const file of files) {
    body.append('files', file, file.name)
  }

  const response = await apiFetch(url, { method, body })
  if (!response.ok) {
    const data = await response.json().catch(() => null)
    throw new Error(data?.detail || 'Не удалось сохранить проект')
  }
  return response.json()
}

export async function fetchAttempts(params: {
  page?: number
  pageSize?: number
  search?: string
} = {}): Promise<AttemptsPageResult> {
  const query = new URLSearchParams()
  if (params.page) {
    query.set('page', String(params.page))
  }
  if (params.pageSize) {
    query.set('pageSize', String(params.pageSize))
  }
  if (params.search?.trim()) {
    query.set('search', params.search.trim())
  }
  const suffix = query.toString() ? `?${query.toString()}` : ''
  const response = await apiFetch(`/api/attempts${suffix}`)
  if (!response.ok) {
    throw new Error('Не удалось загрузить список проектов')
  }
  return response.json()
}

export async function fetchAttempt(attemptId: string): Promise<AttemptDetail> {
  const response = await apiFetch(`/api/attempts/${attemptId}`)
  if (!response.ok) {
    throw new Error('Проект не найден')
  }
  return response.json()
}

export async function createAttempt(title: string, form: FormState): Promise<AttemptDetail> {
  const { payload, files, refs } = collectNewUploads(form)
  return saveAttemptRequest('/api/attempts', 'POST', title, payload, files, refs)
}

export async function updateAttempt(
  attemptId: string,
  title: string,
  form: FormState,
): Promise<AttemptDetail> {
  const { payload, files, refs } = collectNewUploads(form)
  return saveAttemptRequest(`/api/attempts/${attemptId}`, 'PUT', title, payload, files, refs)
}

export async function deleteAttempt(attemptId: string): Promise<void> {
  const response = await apiFetch(`/api/attempts/${attemptId}`, { method: 'DELETE' })
  if (!response.ok) {
    const data = await response.json().catch(() => null)
    throw new Error(data?.detail || 'Не удалось удалить проект')
  }
}

export async function generateSavedAttempt(attemptId: string): Promise<Blob> {
  const response = await apiFetch(`/api/attempts/${attemptId}/generate`, { method: 'POST' })
  if (!response.ok) {
    const data = await response.json().catch(() => null)
    throw new Error(data?.detail || 'Ошибка генерации XML')
  }
  return response.blob()
}

export async function downloadAttemptArchive(attemptId: string): Promise<Blob> {
  const response = await apiFetch(`/api/attempts/${attemptId}/archive`)
  if (!response.ok) {
    const data = await response.json().catch(() => null)
    throw new Error(data?.detail || 'Архив не найден')
  }
  return response.blob()
}

export async function generateConclusion(form: FormState): Promise<Blob> {
  const body = new FormData()
  body.append('payload', JSON.stringify(buildPayload(form)))

  for (const doc of form.documents) {
    if (doc.file) {
      body.append('files', doc.file, doc.fileName || doc.file.name)
    }
    for (const sign of doc.signFiles) {
      body.append('files', sign, sign.name)
    }
  }

  const response = await apiFetch('/api/generate', {
    method: 'POST',
    body,
  })

  if (!response.ok) {
    const data = await response.json().catch(() => null)
    throw new Error(data?.detail || 'Ошибка генерации XML')
  }

  return response.blob()
}
