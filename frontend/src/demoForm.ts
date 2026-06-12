import { fetchDemoFile, fetchDemoForm } from './api'
import { emptyTei } from './defaultForm'
import { hydrateForm } from './formStorage'
import type { FormState, SerializableFormState } from './types'

function withId<T extends { id?: string }>(item: T): T & { id: string } {
  return { ...item, id: item.id || crypto.randomUUID() }
}

export function ensureFormIds(form: FormState): FormState {
  return {
    ...form,
    documents: form.documents.map((doc) => withId(doc)),
    experts: form.experts.map((expert) => withId(expert)),
    finance: form.finance.map((item) => withId(item)),
    designers: form.designers.map((designer) => withId(designer)),
    previousConclusions: form.previousConclusions.map((item) => withId(item)),
    previousSimpleConclusions: form.previousSimpleConclusions.map((item) => withId(item)),
    eepdUse: form.eepdUse.map((item) => withId(item)),
    engineeringSurveyAddresses: form.engineeringSurveyAddresses.map((item) => withId(item)),
    projectDocumentsParties: form.projectDocumentsParties.map((item) => withId(item)),
    engineeringSurveyParties: form.engineeringSurveyParties.map((item) => withId(item)),
    expertEngineeringSurveys: form.expertEngineeringSurveys.map((item) => withId(item)),
    expertProjectDocuments: form.expertProjectDocuments.map((item) => withId(item)),
    capitalObject: {
      ...form.capitalObject,
      tei: form.capitalObject.tei.map((item) => withId(item)),
      parts: form.capitalObject.parts.map((part) => ({
        ...withId(part),
        addresses: part.addresses,
        tei: part.tei.map((tei) => withId(tei)),
      })),
    },
    expertEstimate: {
      ...form.expertEstimate,
      commonMismatches: form.expertEstimate.commonMismatches.map((item) => withId(item)),
      fullCalculationMismatches: form.expertEstimate.fullCalculationMismatches.map((item) =>
        withId(item),
      ),
      localCalculationMismatches: form.expertEstimate.localCalculationMismatches.map((item) =>
        withId(item),
      ),
      projectDocumentsMismatches: form.expertEstimate.projectDocumentsMismatches.map((item) =>
        withId(item),
      ),
      basicMismatches: form.expertEstimate.basicMismatches.map((item) => withId(item)),
    },
  }
}

async function attachDemoFiles(form: FormState): Promise<FormState> {
  const fileNames = [...new Set(form.documents.map((doc) => doc.fileName).filter(Boolean))]
  const fileMap = new Map<string, File>()

  await Promise.all(
    fileNames.map(async (name) => {
      const blob = await fetchDemoFile(name)
      fileMap.set(name, new File([blob], name, { type: blob.type || 'application/pdf' }))
    }),
  )

  return {
    ...form,
    documents: form.documents.map((doc) => ({
      ...doc,
      file: doc.fileName ? fileMap.get(doc.fileName) || null : null,
    })),
  }
}

export async function loadDemoForm(): Promise<FormState> {
  const payload = (await fetchDemoForm()) as unknown as SerializableFormState
  const hydrated = hydrateForm(payload)
  const withIds = ensureFormIds(hydrated)
  if (!withIds.capitalObject.tei.length) {
    withIds.capitalObject.tei = [emptyTei()]
  }
  return attachDemoFiles(withIds)
}

export function createDemoProjectTitle(form: FormState): string {
  return form.examinationObject.name.trim() || 'Пример заключения'
}
