export interface AuthUser {
  id: string
  username: string
  isAdmin: boolean
  isActive: boolean
  createdAt: string
}

export interface AdminUser extends AuthUser {}

export interface OptionItem {
  label: string
  value: string
}

export interface Address {
  country: string
  region: string
  district: string
  city: string
  settlement: string
  street: string
  building: string
  room: string
  note: string
}

export interface PostAddress extends Address {
  post_index: string
}

export interface Mismatch {
  id: string
  summary: string
  part: string
  link: string
}

export interface MismatchExtended extends Mismatch {
  expertType: string
}

export interface TeiItem {
  id: string
  name: string
  measure: string
  value: string
}

export type EntityType = 'organization' | 'foreign_organization' | 'ip' | 'person'

export interface EntityData {
  type: EntityType
  orgFullName: string
  orgOgrn: string
  orgInn: string
  orgKpp: string
  familyName: string
  firstName: string
  secondName: string
  ogrnip: string
  snils: string
  email: string
  address: Address
  postAddress: PostAddress
}

export type ComplexCostRecord = Record<string, string>

export interface ObjectPart {
  id: string
  name: string
  addresses: Address[]
  functionsClass: string
  tei: TeiItem[]
}

export interface CapitalObject {
  name: string
  addresses: Address[]
  type: string
  functionsClass: string
  tei: TeiItem[]
  parts: ObjectPart[]
}

export interface PreviousConclusion {
  id: string
  date: string
  number: string
  numberFormat: 'egrz' | 'noegrz'
  objectType: string
  name: string
  result: string
}

export interface PreviousSimpleConclusion {
  id: string
  date: string
  number: string
  objectType: string
  result: string
}

export type PartyType = 'developer' | 'technical_customer'

export interface PartyItem {
  id: string
  partyType: PartyType
  entity: EntityData
}

export interface EstimatedCost {
  currency: string
  mode: 'complete' | 'complex'
  completeBefore: string
  completePost: string
  complexBefore: ComplexCostRecord
  complexPost: ComplexCostRecord
}

export interface SeismicCalculated {
  enabled: boolean
  min: string
  max: string
}

export interface ClimateConditions {
  climateDistricts: string[]
  geologicalConditions: string[]
  windDistricts: string[]
  snowDistricts: string[]
  seismicActivities: string[]
  seismicCalculated: SeismicCalculated
  note: string
}

export interface Designer extends EntityData {
  id: string
  general: string
}

export interface EepdUseItem {
  id: string
  note: string
  number: string
  numberFormat: 'egrz' | 'noegrz'
  date: string
}

export interface EngineeringSurveyAddress {
  id: string
  region: string
  district: string
}

export interface ExpertEngineeringSurvey {
  id: string
  surveyType: string
  normsMismatches: Mismatch[]
}

export interface ExpertProjectDocument {
  id: string
  expertType: string
  dangerSolutions: string
  engineeringSurveyMismatches: Mismatch[]
  projectTaskMismatches: Mismatch[]
  normsMismatches: Mismatch[]
  dangerMismatch: string
}

export interface ExpertEstimate {
  estimateNorms: string
  commonMismatches: Mismatch[]
  fullCalculationMismatches: Mismatch[]
  localCalculationMismatches: Mismatch[]
  projectDocumentsMismatches: MismatchExtended[]
  basicMismatches: Mismatch[]
}

export interface ExpertOrganization {
  orgFullName: string
  orgOgrn: string
  orgInn: string
  orgKpp: string
  address: Address
}

export interface Approver {
  familyName: string
  firstName: string
  secondName: string
  position: string
}

export interface ExaminationObject {
  examinationForm: string
  examinationResult: string
  examinationObjectType: string
  examinationTypes: string[]
  constructionType: string
  examinationStage: string
  examinationStageNote: string
  name: string
  projectDocumentationIM: string
  engineeringSurveysIM: string
}

export interface DocumentItem {
  id: string
  docType: string
  docName: string
  docNumber: string
  docDate: string
  docChanges: string
  docAuthor: string
  file: File | null
  fileName: string
  fileStorageId?: string
  signFiles: File[]
  signFileNames: string[]
  signStorageIds?: string[]
}

export interface StoredDocumentItem extends Omit<DocumentItem, 'file' | 'signFiles'> {}

export interface Ecology {
  needExpertise: string
  comment: string
}

export interface Declarant extends EntityData {}

export interface FinanceOwner extends EntityData {}

export interface FinanceItem {
  id: string
  financeType: string
  budgetType: string
  financeSize: string
  owner: FinanceOwner
}

export interface ExaminationPdSummary {
  engineeringSurveysResults: string
  designAssignment: string
  technicalRequirements: string
}

export interface Summary {
  engineeringSurveySummary: string
  engineeringSurveySummaryDate: string
  engineeringSurveyTypes: string[]
  projectDocumentsSummary: string
  projectDocumentsSummaryDate: string
  estimateVariant: 'standard' | '1315'
  estimateNormsAndWorksSummary: string
  estimateSummary: string
  estimateNormsAndWorksSummary1315: string
  estimateSummary1315: string
  examinationEngineeringSurveysResultsSummary: string
  examinationProjectDocumentsSummary: ExaminationPdSummary
  examinationEstimateVariant: 'standard' | '1315'
  examinationEstimateSummary: string
  examinationEstimateSummary1315: string
}

export interface Expert {
  id: string
  familyName: string
  firstName: string
  secondName: string
  expertType: string
  expertCertificate: string
  certificateBeginDate: string
  certificateEndDate: string
}

export type AttachmentCategory =
  | 'localConclusion'
  | 'registryCrypto'
  | 'contract'
  | 'workActs'

export interface ProjectAttachmentItem {
  id: string
  file: File | null
  fileName: string
  fileStorageId?: string
  comment: string
}

export type StoredProjectAttachmentItem = Omit<ProjectAttachmentItem, 'file'>

export interface ProjectAttachments {
  localConclusion: ProjectAttachmentItem[]
  registryCrypto: ProjectAttachmentItem[]
  contract: ProjectAttachmentItem[]
  workActs: ProjectAttachmentItem[]
}

export type StoredProjectAttachments = {
  [K in AttachmentCategory]: StoredProjectAttachmentItem[]
}

export interface FormState {
  expertOrganization: ExpertOrganization
  approver: Approver
  examinationObject: ExaminationObject
  documents: DocumentItem[]
  previousConclusions: PreviousConclusion[]
  previousSimpleConclusions: PreviousSimpleConclusion[]
  capitalObject: CapitalObject
  ecology: Ecology
  cadastralNumbers: string[]
  declarant: Declarant
  projectDocumentsParties: PartyItem[]
  finance: FinanceItem[]
  financeComment: string
  estimatedCost: EstimatedCost
  climateConditions: ClimateConditions
  designers: Designer[]
  eepdUse: EepdUseItem[]
  engineeringSurveyAddresses: EngineeringSurveyAddress[]
  engineeringSurveyParties: PartyItem[]
  expertEngineeringSurveys: ExpertEngineeringSurvey[]
  expertProjectDocuments: ExpertProjectDocument[]
  expertEstimate: ExpertEstimate
  summary: Summary
  experts: Expert[]
  projectAttachments: ProjectAttachments
}

export interface SerializableFormState extends Omit<FormState, 'documents' | 'projectAttachments'> {
  documents: StoredDocumentItem[]
  projectAttachments: StoredProjectAttachments
}

export interface AttemptSummary {
  id: string
  title: string
  examinationObjectName: string
  cadastralNumbers: string[]
  egrzNumbers: string[]
  createdAt: string
  updatedAt: string
  hasArchive: boolean
  lastGeneratedAt: string | null
}

export interface AttemptsPageResult {
  items: AttemptSummary[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}

export interface AttemptDetail {
  id: string
  title: string
  form: SerializableFormState
  createdAt: string
  updatedAt: string
  hasArchive: boolean
  lastGeneratedAt: string | null
}

export interface FileUploadRef {
  docId?: string
  attachmentId?: string
  attachmentCategory?: AttachmentCategory
  kind: 'file' | 'sign' | 'attachment'
  index?: number
}

export interface FieldMeta {
  label: string
  key: string
}

export interface OptionsMap {
  examinationForm: OptionItem[]
  examinationResult: OptionItem[]
  examinationObjectType: OptionItem[]
  examinationType: OptionItem[]
  constructionType: OptionItem[]
  examinationStage: OptionItem[]
  im: OptionItem[]
  capitalObjectType: OptionItem[]
  docType: OptionItem[]
  declarantType: OptionItem[]
  technicalCustomerType: OptionItem[]
  designerType: OptionItem[]
  financeType: OptionItem[]
  budgetType: OptionItem[]
  climateDistrict: OptionItem[]
  geologicalConditions: OptionItem[]
  windDistrict: OptionItem[]
  snowDistrict: OptionItem[]
  seismicActivity: OptionItem[]
  engineeringSurveyType: OptionItem[]
  expertType: OptionItem[]
  regionRf: OptionItem[]
  engineeringSurveySummary: OptionItem[]
  projectDocumentsSummary: OptionItem[]
  engineeringSurveysResultsSummary: OptionItem[]
  projectDocsEngineeringSurveysResults: OptionItem[]
  projectDocsDesignAssignment: OptionItem[]
  projectDocsTechnicalRequirements: OptionItem[]
  estimateNormsAndWorksSummary: OptionItem[]
  estimateValidationSummary: OptionItem[]
  estimatedCostMode: OptionItem[]
  complexCostFields: FieldMeta[]
  complexCostCommentFields: FieldMeta[]
  addressFields: { label: string; key: keyof Address }[]
  postAddressFields: { label: string; key: keyof PostAddress }[]
}
