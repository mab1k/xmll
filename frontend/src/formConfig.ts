import type { AttachmentCategory } from './types'

export interface FormSection {
  id: string
  title: string
  optional?: boolean
}

export const SECTIONS: FormSection[] = [
  { id: 'org', title: 'Сведения об организации по проведению экспертизы' },
  { id: 'approver', title: 'Сведения о лице, утвердившем заключение' },
  { id: 'object', title: 'Сведения об объекте экспертизы' },
  { id: 'documents', title: 'Документы, рассмотренные в рамках экспертизы' },
  {
    id: 'previousConclusions',
    title: 'Сведения о ранее выданных заключениях экспертизы',
    optional: true,
  },
  {
    id: 'previousSimpleConclusions',
    title: 'Заключения по экспертному сопровождению',
    optional: true,
  },
  {
    id: 'capitalObject',
    title: 'Сведения об объекте капитального строительства',
    optional: true,
  },
  { id: 'ecology', title: 'Сведения о необходимости проведения экологической экспертизы' },
  { id: 'cadastral', title: 'Кадастровый номер земельного участка', optional: true },
  { id: 'declarant', title: 'Сведения о заявителе' },
  {
    id: 'projectDocumentsParties',
    title: 'Застройщик / техзаказчик проектной документации',
    optional: true,
  },
  { id: 'finance', title: 'Сведения об источнике финансирования' },
  { id: 'estimatedCost', title: 'Сведения о сметной стоимости', optional: true },
  {
    id: 'climateConditions',
    title: 'Сведения о природных и техногенных условиях',
    optional: true,
  },
  { id: 'designers', title: 'Сведения о проектировщике', optional: true },
  { id: 'eepdUse', title: 'Использование типовой / ЭПД', optional: true },
  {
    id: 'engineeringSurveyAddresses',
    title: 'Местоположение района инженерных изысканий',
    optional: true,
  },
  {
    id: 'engineeringSurveyParties',
    title: 'Застройщик / техзаказчик инженерных изысканий',
    optional: true,
  },
  {
    id: 'expertEngineeringSurveys',
    title: 'Экспертиза результатов инженерных изысканий',
    optional: true,
  },
  {
    id: 'expertProjectDocuments',
    title: 'Экспертиза проектной документации',
    optional: true,
  },
  {
    id: 'expertEstimate',
    title: 'Проверка сметной стоимости — сведения эксперта',
    optional: true,
  },
  { id: 'summary', title: 'Выводы по результатам проведения экспертизы' },
  { id: 'experts', title: 'Эксперты, подписавшие заключение' },
  { id: 'attachLocalConclusion', title: 'Локальное заключение', optional: true },
  { id: 'attachRegistryCrypto', title: 'Криптоконтейнер от реестра', optional: true },
  { id: 'attachContract', title: 'Договор', optional: true },
  { id: 'attachWorkActs', title: 'Акты выполненных работ', optional: true },
]

export const ATTACHMENT_SECTIONS = {
  attachLocalConclusion: {
    category: 'localConclusion' as const,
    title: 'Локальное заключение',
    hint: 'Файлы локального заключения. Не участвуют в генерации XML.',
    accept: '.pdf,.doc,.docx,.xml,.zip,.sig',
  },
  attachRegistryCrypto: {
    category: 'registryCrypto' as const,
    title: 'Криптоконтейнер от реестра',
    hint: 'Криптоконтейнер, полученный из реестра. Не участвует в генерации XML.',
    accept: '.zip,.sig,.pdf,.xml',
  },
  attachContract: {
    category: 'contract' as const,
    title: 'Договор',
    hint: 'Договорные документы. Не участвуют в генерации XML.',
    accept: '.pdf,.doc,.docx,.zip,.sig',
  },
  attachWorkActs: {
    category: 'workActs' as const,
    title: 'Акты выполненных работ',
    hint: 'Акты выполненных работ. Не участвуют в генерации XML.',
    accept: '.pdf,.doc,.docx,.zip,.sig',
  },
} satisfies Record<
  string,
  {
    category: AttachmentCategory
    title: string
    hint: string
    accept: string
  }
>
