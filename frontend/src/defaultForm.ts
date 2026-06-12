import { newId } from './id'
import type {
  Address,
  ComplexCostRecord,
  EntityData,
  FormState,
  Mismatch,
  MismatchExtended,
  PostAddress,
  TeiItem,
} from './types'

export const emptyAddress = (): Address => ({
  country: 'Россия',
  region: '',
  district: '',
  city: '',
  settlement: '',
  street: '',
  building: '',
  room: '',
  note: '',
})

export const emptyPostAddress = (): PostAddress => ({
  ...emptyAddress(),
  post_index: '',
})

export const emptyEntity = (type: EntityData['type'] = 'organization'): EntityData => ({
  type,
  orgFullName: '',
  orgOgrn: '',
  orgInn: '',
  orgKpp: '',
  familyName: '',
  firstName: '',
  secondName: '',
  ogrnip: '',
  snils: '',
  email: '',
  address: emptyAddress(),
  postAddress: emptyPostAddress(),
})

export const emptyTei = (): TeiItem => ({
  id: newId(),
  name: '',
  measure: '',
  value: '',
})

export const emptyMismatch = (): Mismatch => ({
  id: newId(),
  summary: '',
  part: '',
  link: '',
})

export const emptyMismatchExtended = (): MismatchExtended => ({
  ...emptyMismatch(),
  expertType: '',
})

const COMPLEX_COST_KEYS = [
  'CostBasic',
  'WorksCostBasic',
  'HardwareCostBasic',
  'OtherCostBasic',
  'ProjectWorksCostBasic',
  'BackSumCostBasic',
  'Cost',
  'WorksCost',
  'HardwareCost',
  'OtherCost',
  'ProjectWorksCost',
  'NDSCost',
  'BackSumCost',
  'CostBasicComment',
  'CostComment',
]

export const emptyComplexCost = (): ComplexCostRecord =>
  Object.fromEntries(COMPLEX_COST_KEYS.map((key) => [key, '']))

export const createDefaultForm = (): FormState => ({
  expertOrganization: {
    orgFullName: '',
    orgOgrn: '',
    orgInn: '',
    orgKpp: '',
    address: emptyAddress(),
  },
  approver: {
    familyName: '',
    firstName: '',
    secondName: '',
    position: '',
  },
  examinationObject: {
    examinationForm: '2',
    examinationResult: '1',
    examinationObjectType: '3',
    examinationTypes: ['1', '2'],
    constructionType: '1',
    examinationStage: '1',
    examinationStageNote: '',
    name: '',
    projectDocumentationIM: 'нет',
    engineeringSurveysIM: 'нет',
  },
  documents: [],
  previousConclusions: [],
  previousSimpleConclusions: [],
  capitalObject: {
    name: '',
    addresses: [emptyAddress()],
    type: '',
    functionsClass: '',
    tei: [emptyTei()],
    parts: [],
  },
  ecology: {
    needExpertise: 'нет',
    comment: '',
  },
  cadastralNumbers: [''],
  declarant: emptyEntity('organization'),
  projectDocumentsParties: [],
  finance: [
    {
      id: newId(),
      financeType: '3',
      budgetType: '',
      financeSize: '',
      owner: emptyEntity('organization'),
    },
  ],
  financeComment: '',
  estimatedCost: {
    currency: '',
    mode: 'complete',
    completeBefore: '',
    completePost: '',
    complexBefore: emptyComplexCost(),
    complexPost: emptyComplexCost(),
  },
  climateConditions: {
    climateDistricts: [''],
    geologicalConditions: [''],
    windDistricts: [''],
    snowDistricts: [''],
    seismicActivities: [''],
    seismicCalculated: { enabled: false, min: '', max: '' },
    note: '',
  },
  designers: [],
  eepdUse: [],
  engineeringSurveyAddresses: [],
  engineeringSurveyParties: [],
  expertEngineeringSurveys: [],
  expertProjectDocuments: [],
  expertEstimate: {
    estimateNorms: '',
    commonMismatches: [],
    fullCalculationMismatches: [],
    localCalculationMismatches: [],
    projectDocumentsMismatches: [],
    basicMismatches: [],
  },
  summary: {
    engineeringSurveySummary: '',
    engineeringSurveySummaryDate: '',
    engineeringSurveyTypes: [],
    projectDocumentsSummary: '',
    projectDocumentsSummaryDate: '',
    estimateVariant: 'standard',
    estimateNormsAndWorksSummary: '',
    estimateSummary: '',
    estimateNormsAndWorksSummary1315: '',
    estimateSummary1315: '',
    examinationEngineeringSurveysResultsSummary: '',
    examinationProjectDocumentsSummary: {
      engineeringSurveysResults: '',
      designAssignment: '',
      technicalRequirements: '',
    },
    examinationEstimateVariant: 'standard',
    examinationEstimateSummary: '',
    examinationEstimateSummary1315: '',
  },
  experts: [],
  projectAttachments: {
    localConclusion: [],
    registryCrypto: [],
    contract: [],
    workActs: [],
  },
})
