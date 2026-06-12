import { createDefaultForm } from './defaultForm'
import { newId } from './id'
import type {
  AttachmentCategory,
  FileUploadRef,
  FormState,
  ProjectAttachments,
  SerializableFormState,
  StoredDocumentItem,
  StoredProjectAttachments,
} from './types'

const ATTACHMENT_CATEGORIES: AttachmentCategory[] = [
  'localConclusion',
  'registryCrypto',
  'contract',
  'workActs',
]

function serializeAttachments(attachments: ProjectAttachments): StoredProjectAttachments {
  return {
    localConclusion: attachments.localConclusion.map(({ file: _file, ...item }) => item),
    registryCrypto: attachments.registryCrypto.map(({ file: _file, ...item }) => item),
    contract: attachments.contract.map(({ file: _file, ...item }) => item),
    workActs: attachments.workActs.map(({ file: _file, ...item }) => item),
  }
}

function hydrateAttachments(data?: Partial<StoredProjectAttachments>): ProjectAttachments {
  const defaults = createDefaultForm().projectAttachments
  const result = { ...defaults }
  for (const category of ATTACHMENT_CATEGORIES) {
    result[category] = (data?.[category] || []).map((item) => ({
      ...item,
      id: item.id || newId(),
      file: null,
      comment: item.comment || '',
    }))
  }
  return result
}

export function serializeForm(form: FormState): SerializableFormState {
  return {
    ...form,
    documents: form.documents.map(({ file: _file, signFiles: _signFiles, ...doc }) => doc),
    projectAttachments: serializeAttachments(form.projectAttachments),
  }
}

export function hydrateForm(data: SerializableFormState): FormState {
  const defaults = createDefaultForm()
  return {
    ...defaults,
    ...data,
    documents: (data.documents || []).map((doc) => ({
      ...doc,
      id: doc.id || newId(),
      file: null,
      signFiles: [],
      signStorageIds: doc.signStorageIds || [],
    })),
    capitalObject: {
      ...defaults.capitalObject,
      ...data.capitalObject,
      addresses: data.capitalObject?.addresses?.length
        ? data.capitalObject.addresses
        : defaults.capitalObject.addresses,
      tei: data.capitalObject?.tei?.length ? data.capitalObject.tei : defaults.capitalObject.tei,
      parts: data.capitalObject?.parts || [],
    },
    climateConditions: {
      ...defaults.climateConditions,
      ...data.climateConditions,
      seismicCalculated: {
        ...defaults.climateConditions.seismicCalculated,
        ...(data.climateConditions?.seismicCalculated || {}),
      },
    },
    estimatedCost: {
      ...defaults.estimatedCost,
      ...data.estimatedCost,
      complexBefore: {
        ...defaults.estimatedCost.complexBefore,
        ...(data.estimatedCost?.complexBefore || {}),
      },
      complexPost: {
        ...defaults.estimatedCost.complexPost,
        ...(data.estimatedCost?.complexPost || {}),
      },
    },
    summary: {
      ...defaults.summary,
      ...data.summary,
      examinationProjectDocumentsSummary: {
        ...defaults.summary.examinationProjectDocumentsSummary,
        ...(data.summary?.examinationProjectDocumentsSummary || {}),
      },
    },
    expertEstimate: {
      ...defaults.expertEstimate,
      ...data.expertEstimate,
    },
    cadastralNumbers: data.cadastralNumbers?.length ? data.cadastralNumbers : [''],
    finance: data.finance?.length ? data.finance : defaults.finance,
    projectAttachments: hydrateAttachments(data.projectAttachments),
  }
}

export function collectNewUploads(form: FormState): {
  payload: SerializableFormState
  files: File[]
  refs: FileUploadRef[]
} {
  const payload = serializeForm(form)
  const files: File[] = []
  const refs: FileUploadRef[] = []

  for (const doc of form.documents) {
    if (doc.file) {
      files.push(doc.file)
      refs.push({ docId: doc.id, kind: 'file' })
    }
    doc.signFiles.forEach((sign, index) => {
      files.push(sign)
      refs.push({ docId: doc.id, kind: 'sign', index })
    })
  }

  for (const category of ATTACHMENT_CATEGORIES) {
    for (const item of form.projectAttachments[category]) {
      if (item.file) {
        files.push(item.file)
        refs.push({
          attachmentCategory: category,
          attachmentId: item.id,
          kind: 'attachment',
        })
      }
    }
  }

  return { payload, files, refs }
}

export function documentHasStoredFile(doc: StoredDocumentItem): boolean {
  return Boolean(doc.fileStorageId || (doc.signStorageIds && doc.signStorageIds.some(Boolean)))
}
