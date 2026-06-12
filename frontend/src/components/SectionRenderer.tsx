import { downloadStoredFile } from '../api'
import { ATTACHMENT_SECTIONS } from '../formConfig'
import { newId } from '../id'
import { emptyAddress, emptyEntity } from '../defaultForm'
import { ProjectAttachmentsSection } from './ProjectAttachmentsSection'
import type {
  DocumentItem,
  Expert,
  FormState,
  OptionsMap,
  PartyItem,
  PreviousConclusion,
  PreviousSimpleConclusion,
} from '../types'
import {
  AddressFields,
  ClimateValueList,
  ComplexCostForm,
  EntityForm,
  MismatchBlock,
  MismatchExtendedBlock,
  NumberFormatRadios,
  ObjectPartEditor,
  PartyBlock,
  TeiEditor,
  TechnicalCustomerForm,
} from './forms/common'
import { Button, Field, SectionCard, SelectInput, TextInput } from './ui'

interface SectionRendererProps {
  sectionId: string
  form: FormState
  options: OptionsMap
  update: <K extends keyof FormState>(key: K, value: FormState[K]) => void
}

export function SectionRenderer({ sectionId, form, options, update }: SectionRendererProps) {
  switch (sectionId) {
    case 'org':
      return (
        <SectionCard title="Сведения об организации по проведению экспертизы">
          <div className="grid">
            <Field label="Полное наименование" required>
              <TextInput
                value={form.expertOrganization.orgFullName}
                onChange={(v) =>
                  update('expertOrganization', { ...form.expertOrganization, orgFullName: v })
                }
              />
            </Field>
            <Field label="ОГРН" required>
              <TextInput
                value={form.expertOrganization.orgOgrn}
                onChange={(v) => update('expertOrganization', { ...form.expertOrganization, orgOgrn: v })}
              />
            </Field>
            <Field label="ИНН" required>
              <TextInput
                value={form.expertOrganization.orgInn}
                onChange={(v) => update('expertOrganization', { ...form.expertOrganization, orgInn: v })}
              />
            </Field>
            <Field label="КПП" required>
              <TextInput
                value={form.expertOrganization.orgKpp}
                onChange={(v) => update('expertOrganization', { ...form.expertOrganization, orgKpp: v })}
              />
            </Field>
          </div>
          <AddressFields
            value={form.expertOrganization.address}
            onChange={(address) =>
              update('expertOrganization', { ...form.expertOrganization, address })
            }
            options={options}
            title="Адрес организации"
          />
        </SectionCard>
      )

    case 'approver':
      return (
        <SectionCard title="Сведения о лице, утвердившем заключение">
          <div className="grid">
            <Field label="Фамилия" required>
              <TextInput
                value={form.approver.familyName}
                onChange={(v) => update('approver', { ...form.approver, familyName: v })}
              />
            </Field>
            <Field label="Имя" required>
              <TextInput
                value={form.approver.firstName}
                onChange={(v) => update('approver', { ...form.approver, firstName: v })}
              />
            </Field>
            <Field label="Отчество" optional>
              <TextInput
                value={form.approver.secondName}
                onChange={(v) => update('approver', { ...form.approver, secondName: v })}
              />
            </Field>
            <Field label="Должность" required>
              <TextInput
                value={form.approver.position}
                onChange={(v) => update('approver', { ...form.approver, position: v })}
              />
            </Field>
          </div>
        </SectionCard>
      )

    case 'object':
      return (
        <SectionCard title="Сведения об объекте экспертизы">
          <div className="grid">
            <Field label="Форма экспертизы" required>
              <SelectInput
                value={form.examinationObject.examinationForm}
                onChange={(v) =>
                  update('examinationObject', { ...form.examinationObject, examinationForm: v })
                }
                options={options.examinationForm}
              />
            </Field>
            <Field label="Результат экспертизы" required>
              <SelectInput
                value={form.examinationObject.examinationResult}
                onChange={(v) =>
                  update('examinationObject', { ...form.examinationObject, examinationResult: v })
                }
                options={options.examinationResult}
              />
            </Field>
            <Field label="Вид объекта экспертизы" required>
              <SelectInput
                value={form.examinationObject.examinationObjectType}
                onChange={(v) =>
                  update('examinationObject', { ...form.examinationObject, examinationObjectType: v })
                }
                options={options.examinationObjectType}
              />
            </Field>
            <Field label="Вид работ" optional>
              <SelectInput
                value={form.examinationObject.constructionType}
                onChange={(v) =>
                  update('examinationObject', { ...form.examinationObject, constructionType: v })
                }
                options={options.constructionType}
              />
            </Field>
            <Field label="Вид экспертизы" optional>
              <SelectInput
                value={form.examinationObject.examinationStage}
                onChange={(v) =>
                  update('examinationObject', { ...form.examinationObject, examinationStage: v })
                }
                options={options.examinationStage}
              />
            </Field>
            <Field label="Сведения о подготовке проектной документации в форме информационной модели" optional>
              <SelectInput
                value={form.examinationObject.projectDocumentationIM}
                onChange={(v) =>
                  update('examinationObject', { ...form.examinationObject, projectDocumentationIM: v })
                }
                options={options.im}
              />
            </Field>
            <Field label="Сведения о подготовке инженерных изысканий в форме информационной модели" optional>
              <SelectInput
                value={form.examinationObject.engineeringSurveysIM}
                onChange={(v) =>
                  update('examinationObject', { ...form.examinationObject, engineeringSurveysIM: v })
                }
                options={options.im}
              />
            </Field>
          </div>
          <Field label="Предмет экспертизы" required>
            <div className="checkbox-list">
              {options.examinationType.map((opt) => (
                <label key={opt.value} className="checkbox-item">
                  <input
                    type="checkbox"
                    checked={form.examinationObject.examinationTypes.includes(opt.value)}
                    onChange={(e) => {
                      const types = e.target.checked
                        ? [...form.examinationObject.examinationTypes, opt.value]
                        : form.examinationObject.examinationTypes.filter((t) => t !== opt.value)
                      update('examinationObject', { ...form.examinationObject, examinationTypes: types })
                    }}
                  />
                  <span>{opt.label}</span>
                </label>
              ))}
            </div>
          </Field>
          <Field label="Дополнительные сведения о виде экспертизы" optional>
            <TextInput
              multiline
              value={form.examinationObject.examinationStageNote}
              onChange={(v) =>
                update('examinationObject', { ...form.examinationObject, examinationStageNote: v })
              }
            />
          </Field>
          <Field label="Наименование объекта экспертизы" required>
            <TextInput
              multiline
              value={form.examinationObject.name}
              onChange={(v) => update('examinationObject', { ...form.examinationObject, name: v })}
            />
          </Field>
        </SectionCard>
      )

    case 'documents':
      return (
        <SectionCard title="Документы, рассмотренные в рамках экспертизы">
          {form.documents.length === 0 && (
            <p className="hint">Добавьте хотя бы один документ с файлом PDF.</p>
          )}
          {form.documents.map((doc, index) => (
            <DocumentBlock
              key={doc.id}
              doc={doc}
              index={index}
              options={options}
              onChange={(updated) =>
                update(
                  'documents',
                  form.documents.map((d) => (d.id === doc.id ? updated : d)),
                )
              }
              onRemove={() => update('documents', form.documents.filter((d) => d.id !== doc.id))}
            />
          ))}
          <Button
            variant="secondary"
            onClick={() => {
              const item: DocumentItem = {
                id: newId(),
                docType: '07.01',
                docName: '',
                docNumber: '',
                docDate: '',
                docChanges: '',
                docAuthor: '',
                file: null,
                fileName: '',
                signFiles: [],
                signFileNames: [],
              }
              update('documents', [...form.documents, item])
            }}
          >
            + Добавить документ
          </Button>
        </SectionCard>
      )

    case 'previousConclusions':
      return (
        <SectionCard title="Сведения о ранее выданных заключениях экспертизы (необяз.)">
          {form.previousConclusions.map((item, index) => (
            <PreviousConclusionBlock
              key={item.id}
              item={item}
              index={index}
              options={options}
              onChange={(updated) =>
                update(
                  'previousConclusions',
                  form.previousConclusions.map((p) => (p.id === item.id ? updated : p)),
                )
              }
              onRemove={() =>
                update('previousConclusions', form.previousConclusions.filter((p) => p.id !== item.id))
              }
            />
          ))}
          <Button
            variant="secondary"
            onClick={() => {
              const item: PreviousConclusion = {
                id: newId(),
                date: '',
                number: '',
                numberFormat: 'egrz',
                objectType: '',
                name: '',
                result: '',
              }
              update('previousConclusions', [...form.previousConclusions, item])
            }}
          >
            + Добавить заключение
          </Button>
        </SectionCard>
      )

    case 'previousSimpleConclusions':
      return (
        <SectionCard title="Заключения по экспертному сопровождению (необяз.)">
          {form.previousSimpleConclusions.map((item, index) => (
            <PreviousSimpleConclusionBlock
              key={item.id}
              item={item}
              index={index}
              options={options}
              onChange={(updated) =>
                update(
                  'previousSimpleConclusions',
                  form.previousSimpleConclusions.map((p) => (p.id === item.id ? updated : p)),
                )
              }
              onRemove={() =>
                update(
                  'previousSimpleConclusions',
                  form.previousSimpleConclusions.filter((p) => p.id !== item.id),
                )
              }
            />
          ))}
          <Button
            variant="secondary"
            onClick={() => {
              const item: PreviousSimpleConclusion = {
                id: newId(),
                date: '',
                number: '',
                objectType: '',
                result: '',
              }
              update('previousSimpleConclusions', [...form.previousSimpleConclusions, item])
            }}
          >
            + Добавить заключение
          </Button>
        </SectionCard>
      )

    case 'capitalObject':
      return (
        <SectionCard title="Сведения об объекте капитального строительства (необяз.)">
          <Field label="Наименование объекта">
            <TextInput
              value={form.capitalObject.name}
              onChange={(v) => update('capitalObject', { ...form.capitalObject, name: v })}
            />
          </Field>
          {form.capitalObject.addresses.map((addr, idx) => (
            <div key={idx} className="repeat-block">
              <AddressFields
                value={addr}
                onChange={(address) => {
                  const addresses = [...form.capitalObject.addresses]
                  addresses[idx] = address
                  update('capitalObject', { ...form.capitalObject, addresses })
                }}
                options={options}
                title={`Адрес ${idx + 1}`}
              />
            </div>
          ))}
          <Button
            variant="secondary"
            onClick={() =>
              update('capitalObject', {
                ...form.capitalObject,
                addresses: [...form.capitalObject.addresses, emptyAddress()],
              })
            }
          >
            + Добавить адрес
          </Button>
          <Field label="Вид объекта">
            <SelectInput
              value={form.capitalObject.type}
              onChange={(v) => update('capitalObject', { ...form.capitalObject, type: v })}
              options={options.capitalObjectType}
              placeholder="— не выбрано —"
            />
          </Field>
          <Field label="Код классификатора объектов капитального строительства">
            <TextInput
              value={form.capitalObject.functionsClass}
              onChange={(v) =>
                update('capitalObject', { ...form.capitalObject, functionsClass: v })
              }
            />
          </Field>
          <h3>Технико-экономические показатели</h3>
          <TeiEditor
            items={form.capitalObject.tei}
            onChange={(tei) => update('capitalObject', { ...form.capitalObject, tei })}
          />
          <h3>Описание составной части сложного объекта</h3>
          <ObjectPartEditor
            parts={form.capitalObject.parts}
            onChange={(parts) => update('capitalObject', { ...form.capitalObject, parts })}
            options={options}
          />
        </SectionCard>
      )

    case 'ecology':
      return (
        <SectionCard title="Сведения о необходимости проведения экологической экспертизы">
          <div className="grid">
            <Field label="Отметка о необходимости проведения экологической экспертизы" required>
              <SelectInput
                value={form.ecology.needExpertise}
                onChange={(v) => update('ecology', { ...form.ecology, needExpertise: v })}
                options={options.im}
              />
            </Field>
            <Field
              label="Обоснование необходимости (отсутствия необходимости) проведения экологической экспертизы"
              optional
            >
              <TextInput
                multiline
                value={form.ecology.comment}
                onChange={(v) => update('ecology', { ...form.ecology, comment: v })}
              />
            </Field>
          </div>
        </SectionCard>
      )

    case 'cadastral':
      return (
        <SectionCard title="Кадастровый номер земельного участка (необяз.)">
          {form.cadastralNumbers.map((num, index) => (
            <div key={index} className="inline-row">
              <Field label={`Кадастровый номер ${index + 1}`}>
                <TextInput
                  value={num}
                  onChange={(v) => {
                    const numbers = [...form.cadastralNumbers]
                    numbers[index] = v
                    update('cadastralNumbers', numbers)
                  }}
                  placeholder="77:01:0002401:107"
                />
              </Field>
              {form.cadastralNumbers.length > 1 && (
                <Button
                  variant="danger"
                  onClick={() =>
                    update(
                      'cadastralNumbers',
                      form.cadastralNumbers.filter((_, i) => i !== index),
                    )
                  }
                >
                  ✕
                </Button>
              )}
            </div>
          ))}
          <Button
            variant="secondary"
            onClick={() => update('cadastralNumbers', [...form.cadastralNumbers, ''])}
          >
            + Добавить
          </Button>
        </SectionCard>
      )

    case 'declarant':
      return (
        <SectionCard title="Сведения о заявителе">
          <EntityForm
            value={form.declarant}
            onChange={(declarant) => update('declarant', declarant)}
            options={options}
            typeOptions={options.declarantType}
          />
        </SectionCard>
      )

    case 'projectDocumentsParties':
      return (
        <SectionCard title="Застройщик / техзаказчик проектной документации (необяз.)">
          {form.projectDocumentsParties.map((party, index) => (
            <PartyItemBlock
              key={party.id}
              party={party}
              index={index}
              blockLabel="Подготовка проектной документации"
              developerLabel="Застройщик, обеспечивший подготовку проектной документации (внесение изменений в проектную документацию)"
              technicalCustomerLabel="Технический заказчик, обеспечивший подготовку проектной документации (внесение изменений в проектную документацию)"
              options={options}
              onChange={(updated) =>
                update(
                  'projectDocumentsParties',
                  form.projectDocumentsParties.map((p) => (p.id === party.id ? updated : p)),
                )
              }
              onRemove={() =>
                update(
                  'projectDocumentsParties',
                  form.projectDocumentsParties.filter((p) => p.id !== party.id),
                )
              }
            />
          ))}
          <Button
            variant="secondary"
            onClick={() => {
              const party: PartyItem = {
                id: newId(),
                partyType: 'developer',
                entity: emptyEntity('organization'),
              }
              update('projectDocumentsParties', [...form.projectDocumentsParties, party])
            }}
          >
            + Добавить
          </Button>
        </SectionCard>
      )

    case 'finance':
      return (
        <SectionCard title="Сведения об источнике финансирования">
          {form.finance.map((item, index) => (
            <div key={item.id} className="repeat-block">
              <h3>Источник финансирования {index + 1}</h3>
              <div className="grid">
                <Field label="Вид источника" required>
                  <SelectInput
                    value={item.financeType}
                    onChange={(v) => {
                      const finance = form.finance.map((f) =>
                        f.id === item.id ? { ...f, financeType: v } : f,
                      )
                      update('finance', finance)
                    }}
                    options={options.financeType}
                    placeholder="— не выбрано —"
                  />
                </Field>
                {item.financeType === '1' && (
                  <Field label="Уровень бюджета" required>
                    <SelectInput
                      value={item.budgetType}
                      onChange={(v) => {
                        const finance = form.finance.map((f) =>
                          f.id === item.id ? { ...f, budgetType: v } : f,
                        )
                        update('finance', finance)
                      }}
                      options={options.budgetType}
                      placeholder="— не выбрано —"
                    />
                  </Field>
                )}
                {item.financeType !== '3' && (
                  <Field label="Размер финансирования" required>
                    <TextInput
                      value={item.financeSize}
                      onChange={(v) => {
                        const finance = form.finance.map((f) =>
                          f.id === item.id ? { ...f, financeSize: v } : f,
                        )
                        update('finance', finance)
                      }}
                    />
                  </Field>
                )}
              </div>
              {item.financeType === '2' && (
                <>
                  <h4>Сведения о собственнике средств</h4>
                  <TechnicalCustomerForm
                    value={item.owner}
                    onChange={(owner) => {
                      const finance = form.finance.map((f) =>
                        f.id === item.id ? { ...f, owner } : f,
                      )
                      update('finance', finance)
                    }}
                    options={options}
                  />
                </>
              )}
            </div>
          ))}
          <Button
            variant="secondary"
            onClick={() =>
              update('finance', [
                ...form.finance,
                {
                  id: newId(),
                  financeType: '',
                  budgetType: '',
                  financeSize: '',
                  owner: emptyEntity('organization'),
                },
              ])
            }
          >
            + Добавить источник финансирования
          </Button>
          <Field label="Дополнительные сведения об источнике финансирования" optional>
            <TextInput
              multiline
              value={form.financeComment}
              onChange={(v) => update('financeComment', v)}
            />
          </Field>
        </SectionCard>
      )

    case 'estimatedCost':
      return (
        <SectionCard title="Сведения о сметной стоимости (необяз.)">
          <Field label="Валюта, в которой производится расчёт сметной стоимости" optional>
            <TextInput
              value={form.estimatedCost.currency}
              onChange={(v) => update('estimatedCost', { ...form.estimatedCost, currency: v })}
            />
          </Field>
          <Field label="Способ указания сметной стоимости">
            <div className="radio-list">
              {options.estimatedCostMode.map((opt) => (
                <label key={opt.value} className="radio-item">
                  <input
                    type="radio"
                    checked={form.estimatedCost.mode === opt.value}
                    onChange={() =>
                      update('estimatedCost', {
                        ...form.estimatedCost,
                        mode: opt.value as 'complete' | 'complex',
                      })
                    }
                  />
                  <span>{opt.label}</span>
                </label>
              ))}
            </div>
          </Field>
          {form.estimatedCost.mode === 'complete' ? (
            <div className="grid">
              <Field label="Сметная стоимость на дату представления документации для проведения экспертизы">
                <TextInput
                  value={form.estimatedCost.completeBefore}
                  onChange={(v) =>
                    update('estimatedCost', { ...form.estimatedCost, completeBefore: v })
                  }
                />
              </Field>
              <Field label="Сметная стоимость на дату утверждения заключения экспертизы">
                <TextInput
                  value={form.estimatedCost.completePost}
                  onChange={(v) =>
                    update('estimatedCost', { ...form.estimatedCost, completePost: v })
                  }
                />
              </Field>
            </div>
          ) : (
            <>
              <ComplexCostForm
                title="На дату представления документации для проведения экспертизы"
                value={form.estimatedCost.complexBefore}
                onChange={(complexBefore) =>
                  update('estimatedCost', { ...form.estimatedCost, complexBefore })
                }
                options={options}
              />
              <ComplexCostForm
                title="По результатам проверки достоверности определения сметной стоимости"
                value={form.estimatedCost.complexPost}
                onChange={(complexPost) =>
                  update('estimatedCost', { ...form.estimatedCost, complexPost })
                }
                options={options}
              />
            </>
          )}
        </SectionCard>
      )

    case 'climateConditions':
      return (
        <SectionCard title="Сведения о природных и техногенных условиях (необяз.)">
          <ClimateValueList
            title="Климатический район, подрайон"
            values={form.climateConditions.climateDistricts}
            onChange={(climateDistricts) =>
              update('climateConditions', { ...form.climateConditions, climateDistricts })
            }
            options={options.climateDistrict}
          />
          <ClimateValueList
            title="Категория сложности инженерно-геологических (геокриологических) условий"
            values={form.climateConditions.geologicalConditions}
            onChange={(geologicalConditions) =>
              update('climateConditions', { ...form.climateConditions, geologicalConditions })
            }
            options={options.geologicalConditions}
          />
          <ClimateValueList
            title="Ветровой район"
            values={form.climateConditions.windDistricts}
            onChange={(windDistricts) =>
              update('climateConditions', { ...form.climateConditions, windDistricts })
            }
            options={options.windDistrict}
          />
          <ClimateValueList
            title="Снеговой район"
            values={form.climateConditions.snowDistricts}
            onChange={(snowDistricts) =>
              update('climateConditions', { ...form.climateConditions, snowDistricts })
            }
            options={options.snowDistrict}
          />
          <ClimateValueList
            title="Интенсивность сейсмических воздействий"
            values={form.climateConditions.seismicActivities}
            onChange={(seismicActivities) =>
              update('climateConditions', { ...form.climateConditions, seismicActivities })
            }
            options={options.seismicActivity}
          />
          <div className="sub-frame">
            <h4>Расчётное значение интенсивности сейсмических воздействий</h4>
            <label className="checkbox-item">
              <input
                type="checkbox"
                checked={form.climateConditions.seismicCalculated.enabled}
                onChange={(e) =>
                  update('climateConditions', {
                    ...form.climateConditions,
                    seismicCalculated: {
                      ...form.climateConditions.seismicCalculated,
                      enabled: e.target.checked,
                    },
                  })
                }
              />
              <span>Указать расчётное значение</span>
            </label>
            {form.climateConditions.seismicCalculated.enabled && (
              <div className="grid">
                <Field label="Минимальное значение">
                  <TextInput
                    value={form.climateConditions.seismicCalculated.min}
                    onChange={(v) =>
                      update('climateConditions', {
                        ...form.climateConditions,
                        seismicCalculated: {
                          ...form.climateConditions.seismicCalculated,
                          min: v,
                        },
                      })
                    }
                  />
                </Field>
                <Field label="Максимальное значение" optional>
                  <TextInput
                    value={form.climateConditions.seismicCalculated.max}
                    onChange={(v) =>
                      update('climateConditions', {
                        ...form.climateConditions,
                        seismicCalculated: {
                          ...form.climateConditions.seismicCalculated,
                          max: v,
                        },
                      })
                    }
                  />
                </Field>
              </div>
            )}
          </div>
          <Field label="Дополнительные сведения о природных и техногенных условиях" optional>
            <TextInput
              multiline
              value={form.climateConditions.note}
              onChange={(v) => update('climateConditions', { ...form.climateConditions, note: v })}
            />
          </Field>
        </SectionCard>
      )

    case 'designers':
      return (
        <SectionCard title="Сведения о проектировщике (необяз.)">
          {form.designers.map((designer, index) => (
            <div key={designer.id} className="repeat-block">
              <div className="repeat-header">
                <h3>Проектировщик {index + 1}</h3>
                <Button
                  variant="danger"
                  onClick={() =>
                    update('designers', form.designers.filter((d) => d.id !== designer.id))
                  }
                >
                  Удалить
                </Button>
              </div>
              <EntityForm
                value={designer}
                onChange={(entity) => {
                  update(
                    'designers',
                    form.designers.map((d) =>
                      d.id === designer.id ? { ...d, ...entity, id: designer.id, general: designer.general } : d,
                    ),
                  )
                }}
                options={options}
                typeOptions={options.designerType}
              />
              <Field label="Отметка о роли генерального проектировщика">
                <SelectInput
                  value={designer.general}
                  onChange={(v) =>
                    update(
                      'designers',
                      form.designers.map((d) => (d.id === designer.id ? { ...d, general: v } : d)),
                    )
                  }
                  options={options.im}
                  placeholder="— не выбрано —"
                />
              </Field>
            </div>
          ))}
          <Button
            variant="secondary"
            onClick={() =>
              update('designers', [
                ...form.designers,
                { ...emptyEntity('organization'), id: newId(), general: '' },
              ])
            }
          >
            + Добавить проектировщика
          </Button>
        </SectionCard>
      )

    case 'eepdUse':
      return (
        <SectionCard title="Использование типовой / ЭПД (необяз.)">
          {form.eepdUse.map((item, index) => (
            <div key={item.id} className="repeat-block">
              <div className="repeat-header">
                <h3>Использование типовой проектной документации {index + 1}</h3>
                <Button
                  variant="danger"
                  onClick={() => update('eepdUse', form.eepdUse.filter((e) => e.id !== item.id))}
                >
                  Удалить
                </Button>
              </div>
              <Field label="Сведения о разделах, которые не подвергались изменению и полностью соответствуют ЭПД повторного использования">
                <TextInput
                  value={item.note}
                  onChange={(v) =>
                    update(
                      'eepdUse',
                      form.eepdUse.map((e) => (e.id === item.id ? { ...e, note: v } : e)),
                    )
                  }
                />
              </Field>
              <h4>Номер заключения экспертизы в отношении использованной ЭПД</h4>
              <NumberFormatRadios
                value={item.numberFormat}
                onChange={(numberFormat) =>
                  update(
                    'eepdUse',
                    form.eepdUse.map((e) => (e.id === item.id ? { ...e, numberFormat } : e)),
                  )
                }
                egrzLabel="Номер заключения экспертизы в формате ЕГРЗ"
                noegrzLabel="Номер заключения экспертизы в произвольном формате"
              />
              <Field label="Номер заключения">
                <TextInput
                  value={item.number}
                  onChange={(v) =>
                    update(
                      'eepdUse',
                      form.eepdUse.map((e) => (e.id === item.id ? { ...e, number: v } : e)),
                    )
                  }
                />
              </Field>
              <Field label="Дата утверждения заключения экспертизы (ДД.ММ.ГГГГ)">
                <TextInput
                  value={item.date}
                  onChange={(v) =>
                    update(
                      'eepdUse',
                      form.eepdUse.map((e) => (e.id === item.id ? { ...e, date: v } : e)),
                    )
                  }
                />
              </Field>
            </div>
          ))}
          <Button
            variant="secondary"
            onClick={() =>
              update('eepdUse', [
                ...form.eepdUse,
                {
                  id: newId(),
                  note: '',
                  number: '',
                  numberFormat: 'egrz',
                  date: '',
                },
              ])
            }
          >
            + Добавить сведения об использовании ЭПД
          </Button>
        </SectionCard>
      )

    case 'engineeringSurveyAddresses':
      return (
        <SectionCard title="Местоположение района инженерных изысканий (необяз.)">
          {form.engineeringSurveyAddresses.map((item, index) => (
            <div key={item.id} className="repeat-block">
              <div className="repeat-header">
                <h3>Местоположение района изысканий {index + 1}</h3>
                <Button
                  variant="danger"
                  onClick={() =>
                    update(
                      'engineeringSurveyAddresses',
                      form.engineeringSurveyAddresses.filter((e) => e.id !== item.id),
                    )
                  }
                >
                  Удалить
                </Button>
              </div>
              <Field label="Код субъекта Российской Федерации">
                <SelectInput
                  value={item.region}
                  onChange={(v) =>
                    update(
                      'engineeringSurveyAddresses',
                      form.engineeringSurveyAddresses.map((e) =>
                        e.id === item.id ? { ...e, region: v } : e,
                      ),
                    )
                  }
                  options={options.regionRf}
                  placeholder="— не выбрано —"
                />
              </Field>
              <Field label="Описание района изысканий (наименование муниципального района)">
                <TextInput
                  multiline
                  value={item.district}
                  onChange={(v) =>
                    update(
                      'engineeringSurveyAddresses',
                      form.engineeringSurveyAddresses.map((e) =>
                        e.id === item.id ? { ...e, district: v } : e,
                      ),
                    )
                  }
                />
              </Field>
            </div>
          ))}
          <Button
            variant="secondary"
            onClick={() =>
              update('engineeringSurveyAddresses', [
                ...form.engineeringSurveyAddresses,
                { id: newId(), region: '', district: '' },
              ])
            }
          >
            + Добавить местоположение района изысканий
          </Button>
        </SectionCard>
      )

    case 'engineeringSurveyParties':
      return (
        <SectionCard title="Застройщик / техзаказчик инженерных изысканий (необяз.)">
          {form.engineeringSurveyParties.map((party, index) => (
            <PartyItemBlock
              key={party.id}
              party={party}
              index={index}
              blockLabel="Проведение инженерных изысканий"
              developerLabel="Застройщик, обеспечивший проведение инженерных изысканий"
              technicalCustomerLabel="Технический заказчик, обеспечивший проведение инженерных изысканий"
              options={options}
              onChange={(updated) =>
                update(
                  'engineeringSurveyParties',
                  form.engineeringSurveyParties.map((p) => (p.id === party.id ? updated : p)),
                )
              }
              onRemove={() =>
                update(
                  'engineeringSurveyParties',
                  form.engineeringSurveyParties.filter((p) => p.id !== party.id),
                )
              }
            />
          ))}
          <Button
            variant="secondary"
            onClick={() => {
              const party: PartyItem = {
                id: newId(),
                partyType: 'developer',
                entity: emptyEntity('organization'),
              }
              update('engineeringSurveyParties', [...form.engineeringSurveyParties, party])
            }}
          >
            + Добавить
          </Button>
        </SectionCard>
      )

    case 'expertEngineeringSurveys':
      return (
        <SectionCard title="Экспертиза результатов инженерных изысканий (необяз.)">
          {form.expertEngineeringSurveys.map((block, index) => (
            <div key={block.id} className="repeat-block">
              <div className="repeat-header">
                <h3>Экспертиза инженерных изысканий {index + 1}</h3>
                <Button
                  variant="danger"
                  onClick={() =>
                    update(
                      'expertEngineeringSurveys',
                      form.expertEngineeringSurveys.filter((e) => e.id !== block.id),
                    )
                  }
                >
                  Удалить блок
                </Button>
              </div>
              <MismatchBlock
                title="Несоответствие требованиям техрегламентов"
                items={block.normsMismatches}
                onChange={(normsMismatches) =>
                  update(
                    'expertEngineeringSurveys',
                    form.expertEngineeringSurveys.map((e) =>
                      e.id === block.id ? { ...e, normsMismatches } : e,
                    ),
                  )
                }
              />
              <Field label="Вид инженерных изысканий">
                <SelectInput
                  value={block.surveyType}
                  onChange={(v) =>
                    update(
                      'expertEngineeringSurveys',
                      form.expertEngineeringSurveys.map((e) =>
                        e.id === block.id ? { ...e, surveyType: v } : e,
                      ),
                    )
                  }
                  options={options.engineeringSurveyType}
                  placeholder="— не выбрано —"
                />
              </Field>
            </div>
          ))}
          <Button
            variant="secondary"
            onClick={() =>
              update('expertEngineeringSurveys', [
                ...form.expertEngineeringSurveys,
                { id: newId(), surveyType: '', normsMismatches: [] },
              ])
            }
          >
            + Добавить сведения экспертизы инженерных изысканий
          </Button>
        </SectionCard>
      )

    case 'expertProjectDocuments':
      return (
        <SectionCard title="Экспертиза проектной документации (необяз.)">
          {form.expertProjectDocuments.map((block, index) => (
            <div key={block.id} className="repeat-block">
              <div className="repeat-header">
                <h3>Экспертиза проектной документации {index + 1}</h3>
                <Button
                  variant="danger"
                  onClick={() =>
                    update(
                      'expertProjectDocuments',
                      form.expertProjectDocuments.filter((e) => e.id !== block.id),
                    )
                  }
                >
                  Удалить блок
                </Button>
              </div>
              <Field label="Сведения о решениях, приведённых в соответствие в ходе экспертизы">
                <TextInput
                  value={block.dangerSolutions}
                  onChange={(v) =>
                    update(
                      'expertProjectDocuments',
                      form.expertProjectDocuments.map((e) =>
                        e.id === block.id ? { ...e, dangerSolutions: v } : e,
                      ),
                    )
                  }
                />
              </Field>
              <div className="sub-frame">
                <h4>Сведения о несоответствии проектной документации установленным требованиям</h4>
                <MismatchBlock
                  title="Несоответствие результату инженерных изысканий"
                  items={block.engineeringSurveyMismatches}
                  onChange={(engineeringSurveyMismatches) =>
                    update(
                      'expertProjectDocuments',
                      form.expertProjectDocuments.map((e) =>
                        e.id === block.id ? { ...e, engineeringSurveyMismatches } : e,
                      ),
                    )
                  }
                />
                <MismatchBlock
                  title="Несоответствие заданию на проектирование"
                  items={block.projectTaskMismatches}
                  onChange={(projectTaskMismatches) =>
                    update(
                      'expertProjectDocuments',
                      form.expertProjectDocuments.map((e) =>
                        e.id === block.id ? { ...e, projectTaskMismatches } : e,
                      ),
                    )
                  }
                />
                <MismatchBlock
                  title="Несоответствие требованиям технических регламентов"
                  items={block.normsMismatches}
                  onChange={(normsMismatches) =>
                    update(
                      'expertProjectDocuments',
                      form.expertProjectDocuments.map((e) =>
                        e.id === block.id ? { ...e, normsMismatches } : e,
                      ),
                    )
                  }
                />
                <Field label="Описание опасного решения (DangerMismatch)">
                  <TextInput
                    value={block.dangerMismatch}
                    onChange={(v) =>
                      update(
                        'expertProjectDocuments',
                        form.expertProjectDocuments.map((e) =>
                          e.id === block.id ? { ...e, dangerMismatch: v } : e,
                        ),
                      )
                    }
                  />
                </Field>
              </div>
              <Field label="Направление деятельности в области экспертизы проектной документации">
                <SelectInput
                  value={block.expertType}
                  onChange={(v) =>
                    update(
                      'expertProjectDocuments',
                      form.expertProjectDocuments.map((e) =>
                        e.id === block.id ? { ...e, expertType: v } : e,
                      ),
                    )
                  }
                  options={options.expertType}
                  placeholder="— не выбрано —"
                />
              </Field>
            </div>
          ))}
          <Button
            variant="secondary"
            onClick={() =>
              update('expertProjectDocuments', [
                ...form.expertProjectDocuments,
                {
                  id: newId(),
                  expertType: '',
                  dangerSolutions: '',
                  engineeringSurveyMismatches: [],
                  projectTaskMismatches: [],
                  normsMismatches: [],
                  dangerMismatch: '',
                },
              ])
            }
          >
            + Добавить сведения экспертизы проектной документации
          </Button>
        </SectionCard>
      )

    case 'expertEstimate':
      return (
        <SectionCard title="Проверка сметной стоимости — сведения эксперта (необяз.)">
          <Field label="Информация об использовании сметных нормативов">
            <TextInput
              multiline
              value={form.expertEstimate.estimateNorms}
              onChange={(v) =>
                update('expertEstimate', { ...form.expertEstimate, estimateNorms: v })
              }
            />
          </Field>
          <div className="sub-frame">
            <h4>Сведения о несоответствии сметной части проектной документации</h4>
            <MismatchBlock
              title="Общее замечание"
              items={form.expertEstimate.commonMismatches}
              onChange={(commonMismatches) =>
                update('expertEstimate', { ...form.expertEstimate, commonMismatches })
              }
            />
            <MismatchBlock
              title="Замечание по сводному сметному расчету"
              items={form.expertEstimate.fullCalculationMismatches}
              onChange={(fullCalculationMismatches) =>
                update('expertEstimate', { ...form.expertEstimate, fullCalculationMismatches })
              }
            />
            <MismatchBlock
              title="Замечание по объектным или локальным сметным расчетам"
              items={form.expertEstimate.localCalculationMismatches}
              onChange={(localCalculationMismatches) =>
                update('expertEstimate', { ...form.expertEstimate, localCalculationMismatches })
              }
            />
            <MismatchExtendedBlock
              title="Замечание по соответствию расчетов проектной документации"
              items={form.expertEstimate.projectDocumentsMismatches}
              onChange={(projectDocumentsMismatches) =>
                update('expertEstimate', { ...form.expertEstimate, projectDocumentsMismatches })
              }
              options={options}
            />
            <MismatchBlock
              title="Замечание по пересчету из базисного уровня цен"
              items={form.expertEstimate.basicMismatches}
              onChange={(basicMismatches) =>
                update('expertEstimate', { ...form.expertEstimate, basicMismatches })
              }
            />
          </div>
        </SectionCard>
      )

    case 'summary':
      return (
        <SectionCard title="Выводы по результатам проведения экспертизы">
          <Field label="Вывод о соответствии результатов инженерных изысканий требованиям технических регламентов">
            <SelectInput
              value={form.summary.engineeringSurveySummary}
              onChange={(v) => update('summary', { ...form.summary, engineeringSurveySummary: v })}
              options={options.engineeringSurveySummary}
              placeholder="— не выбрано —"
            />
          </Field>
          <Field label="Сведения о дате требований (экспертиза результатов инженерных изысканий)">
            <TextInput
              value={form.summary.engineeringSurveySummaryDate}
              onChange={(v) =>
                update('summary', { ...form.summary, engineeringSurveySummaryDate: v })
              }
            />
          </Field>
          <div className="sub-frame">
            <h4>
              Вид инженерных изысканий, на соответствие которым проводилась экспертиза проектной
              документации
            </h4>
            {form.summary.engineeringSurveyTypes.map((surveyType, index) => (
              <div key={index} className="inline-row">
                <SelectInput
                  value={surveyType}
                  onChange={(v) => {
                    const types = [...form.summary.engineeringSurveyTypes]
                    types[index] = v
                    update('summary', { ...form.summary, engineeringSurveyTypes: types })
                  }}
                  options={options.engineeringSurveyType}
                  placeholder="— не выбрано —"
                />
                <Button
                  variant="danger"
                  onClick={() =>
                    update('summary', {
                      ...form.summary,
                      engineeringSurveyTypes: form.summary.engineeringSurveyTypes.filter(
                        (_, i) => i !== index,
                      ),
                    })
                  }
                >
                  ✕
                </Button>
              </div>
            ))}
            <Button
              variant="secondary"
              onClick={() =>
                update('summary', {
                  ...form.summary,
                  engineeringSurveyTypes: [...form.summary.engineeringSurveyTypes, ''],
                })
              }
            >
              + Добавить
            </Button>
          </div>
          <Field label="Вывод о соответствии технической части проектной документации">
            <SelectInput
              value={form.summary.projectDocumentsSummary}
              onChange={(v) => update('summary', { ...form.summary, projectDocumentsSummary: v })}
              options={options.projectDocumentsSummary}
              placeholder="— не выбрано —"
            />
          </Field>
          <Field label="Сведения о дате требований (экспертиза проектной документации)">
            <TextInput
              value={form.summary.projectDocumentsSummaryDate}
              onChange={(v) =>
                update('summary', { ...form.summary, projectDocumentsSummaryDate: v })
              }
            />
          </Field>
          <div className="sub-frame">
            <h4>Выводы по проверке достоверности определения сметной стоимости</h4>
            <div className="radio-list">
              <label className="radio-item">
                <input
                  type="radio"
                  checked={form.summary.estimateVariant === 'standard'}
                  onChange={() => update('summary', { ...form.summary, estimateVariant: 'standard' })}
                />
                <span>Стандартные выводы</span>
              </label>
              <label className="radio-item">
                <input
                  type="radio"
                  checked={form.summary.estimateVariant === '1315'}
                  onChange={() => update('summary', { ...form.summary, estimateVariant: '1315' })}
                />
                <span>Выводы по постановлению Правительства РФ от 09.08.2021 №1315</span>
              </label>
            </div>
            {form.summary.estimateVariant === 'standard' ? (
              <>
                <Field label="Вывод о соответствии расчетов сметной документации">
                  <SelectInput
                    value={form.summary.estimateNormsAndWorksSummary}
                    onChange={(v) =>
                      update('summary', { ...form.summary, estimateNormsAndWorksSummary: v })
                    }
                    options={options.estimateNormsAndWorksSummary}
                    placeholder="— не выбрано —"
                  />
                </Field>
                <Field label="Вывод о достоверности определения сметной стоимости">
                  <SelectInput
                    value={form.summary.estimateSummary}
                    onChange={(v) => update('summary', { ...form.summary, estimateSummary: v })}
                    options={options.estimateValidationSummary}
                    placeholder="— не выбрано —"
                  />
                </Field>
              </>
            ) : (
              <>
                <Field label="Вывод о соответствии расчетов (№1315)">
                  <TextInput
                    value={form.summary.estimateNormsAndWorksSummary1315}
                    onChange={(v) =>
                      update('summary', { ...form.summary, estimateNormsAndWorksSummary1315: v })
                    }
                  />
                </Field>
                <Field label="Вывод о достоверности определения сметной стоимости (№1315)">
                  <TextInput
                    value={form.summary.estimateSummary1315}
                    onChange={(v) => update('summary', { ...form.summary, estimateSummary1315: v })}
                  />
                </Field>
              </>
            )}
          </div>
          <div className="sub-frame">
            <h4>Общие выводы (итоговые выводы по результатам проведенной экспертизы)</h4>
            <Field label="Вывод о соответствии результатов инженерных изысканий">
              <SelectInput
                value={form.summary.examinationEngineeringSurveysResultsSummary}
                onChange={(v) =>
                  update('summary', {
                    ...form.summary,
                    examinationEngineeringSurveysResultsSummary: v,
                  })
                }
                options={options.engineeringSurveysResultsSummary}
                placeholder="— не выбрано —"
              />
            </Field>
            <div className="sub-frame">
              <h4>Выводы в отношении проектной документации</h4>
              <Field label="Соответствие результатам инженерных изысканий">
                <SelectInput
                  value={form.summary.examinationProjectDocumentsSummary.engineeringSurveysResults}
                  onChange={(v) =>
                    update('summary', {
                      ...form.summary,
                      examinationProjectDocumentsSummary: {
                        ...form.summary.examinationProjectDocumentsSummary,
                        engineeringSurveysResults: v,
                      },
                    })
                  }
                  options={options.projectDocsEngineeringSurveysResults}
                  placeholder="— не выбрано —"
                />
              </Field>
              <Field label="Соответствие заданию на проектирование">
                <SelectInput
                  value={form.summary.examinationProjectDocumentsSummary.designAssignment}
                  onChange={(v) =>
                    update('summary', {
                      ...form.summary,
                      examinationProjectDocumentsSummary: {
                        ...form.summary.examinationProjectDocumentsSummary,
                        designAssignment: v,
                      },
                    })
                  }
                  options={options.projectDocsDesignAssignment}
                  placeholder="— не выбрано —"
                />
              </Field>
              <Field label="Соответствие требованиям технических регламентов">
                <SelectInput
                  value={form.summary.examinationProjectDocumentsSummary.technicalRequirements}
                  onChange={(v) =>
                    update('summary', {
                      ...form.summary,
                      examinationProjectDocumentsSummary: {
                        ...form.summary.examinationProjectDocumentsSummary,
                        technicalRequirements: v,
                      },
                    })
                  }
                  options={options.projectDocsTechnicalRequirements}
                  placeholder="— не выбрано —"
                />
              </Field>
            </div>
            <Field label="Вывод об оценке достоверности определения сметной стоимости">
              <div className="radio-list">
                <label className="radio-item">
                  <input
                    type="radio"
                    checked={form.summary.examinationEstimateVariant === 'standard'}
                    onChange={() =>
                      update('summary', { ...form.summary, examinationEstimateVariant: 'standard' })
                    }
                  />
                  <span>Стандартный вывод</span>
                </label>
                <label className="radio-item">
                  <input
                    type="radio"
                    checked={form.summary.examinationEstimateVariant === '1315'}
                    onChange={() =>
                      update('summary', { ...form.summary, examinationEstimateVariant: '1315' })
                    }
                  />
                  <span>Вывод по постановлению №1315</span>
                </label>
              </div>
            </Field>
            {form.summary.examinationEstimateVariant === 'standard' ? (
              <SelectInput
                value={form.summary.examinationEstimateSummary}
                onChange={(v) =>
                  update('summary', { ...form.summary, examinationEstimateSummary: v })
                }
                options={options.estimateValidationSummary}
                placeholder="— не выбрано —"
              />
            ) : (
              <TextInput
                value={form.summary.examinationEstimateSummary1315}
                onChange={(v) =>
                  update('summary', { ...form.summary, examinationEstimateSummary1315: v })
                }
              />
            )}
          </div>
        </SectionCard>
      )

    case 'experts':
      return (
        <SectionCard title="Эксперты, подписавшие заключение">
          {form.experts.map((expert, index) => (
            <ExpertBlock
              key={expert.id}
              expert={expert}
              index={index}
              options={options}
              onChange={(updated) =>
                update('experts', form.experts.map((e) => (e.id === expert.id ? updated : e)))
              }
              onRemove={() => update('experts', form.experts.filter((e) => e.id !== expert.id))}
            />
          ))}
          <Button
            variant="secondary"
            onClick={() => {
              const item: Expert = {
                id: newId(),
                familyName: '',
                firstName: '',
                secondName: '',
                expertType: '',
                expertCertificate: '',
                certificateBeginDate: '',
                certificateEndDate: '',
              }
              update('experts', [...form.experts, item])
            }}
          >
            + Добавить эксперта
          </Button>
        </SectionCard>
      )

    case 'attachLocalConclusion':
    case 'attachRegistryCrypto':
    case 'attachContract':
    case 'attachWorkActs': {
      const attachmentConfig = ATTACHMENT_SECTIONS[sectionId]
      const category = attachmentConfig.category
      return (
        <ProjectAttachmentsSection
          title={attachmentConfig.title}
          hint={attachmentConfig.hint}
          accept={attachmentConfig.accept}
          items={form.projectAttachments[category]}
          onChange={(items) =>
            update('projectAttachments', {
              ...form.projectAttachments,
              [category]: items,
            })
          }
        />
      )
    }

    default:
      return null
  }
}

function StoredFileRow({
  fileId,
  fileName,
  label,
}: {
  fileId: string
  fileName: string
  label: string
}) {
  const handleDownload = async () => {
    try {
      await downloadStoredFile(fileId, fileName)
    } catch (err) {
      window.alert(err instanceof Error ? err.message : 'Не удалось скачать файл')
    }
  }

  return (
    <div className="stored-file-row">
      <span className="stored-file-label">{label}:</span>
      <button type="button" className="stored-file-link" onClick={() => void handleDownload()}>
        {fileName}
      </button>
    </div>
  )
}

function DocumentBlock({
  doc,
  index,
  options,
  onChange,
  onRemove,
}: {
  doc: DocumentItem
  index: number
  options: OptionsMap
  onChange: (doc: DocumentItem) => void
  onRemove: () => void
}) {
  return (
    <div className="repeat-block">
      <div className="repeat-header">
        <h3>Документ {index + 1}</h3>
        <Button variant="danger" onClick={onRemove}>
          Удалить
        </Button>
      </div>
      <div className="grid">
        <Field label="Код типа документа" required>
          <SelectInput
            value={doc.docType}
            onChange={(v) => onChange({ ...doc, docType: v })}
            options={options.docType}
          />
        </Field>
        <Field label="Наименование" required>
          <TextInput multiline value={doc.docName} onChange={(v) => onChange({ ...doc, docName: v })} />
        </Field>
        <Field label="Номер" optional>
          <TextInput value={doc.docNumber} onChange={(v) => onChange({ ...doc, docNumber: v })} />
        </Field>
        <Field label="Дата (ДД.ММ.ГГГГ)" required>
          <TextInput value={doc.docDate} onChange={(v) => onChange({ ...doc, docDate: v })} />
        </Field>
        <Field label="Сведения об изменениях" optional>
          <TextInput value={doc.docChanges} onChange={(v) => onChange({ ...doc, docChanges: v })} />
        </Field>
        <Field label="Автор документа" optional>
          <TextInput value={doc.docAuthor} onChange={(v) => onChange({ ...doc, docAuthor: v })} />
        </Field>
        <Field label="Файл PDF" required>
          {doc.fileStorageId && (
            <StoredFileRow
              fileId={doc.fileStorageId}
              fileName={doc.fileName || 'document.pdf'}
              label="Сохранённый файл"
            />
          )}
          <input
            className="input"
            type="file"
            accept=".pdf,.doc,.docx"
            onChange={(e) => {
              const file = e.target.files?.[0] || null
              onChange({ ...doc, file, fileName: file?.name || doc.fileName })
            }}
          />
        </Field>
        <Field label="Файлы подписи (.sig)" optional>
          {(doc.signStorageIds || [])
            .map((fileId, index) =>
              fileId ? (
                <StoredFileRow
                  key={fileId}
                  fileId={fileId}
                  fileName={doc.signFileNames?.[index] || `signature-${index + 1}.sig`}
                  label="Сохранённая подпись"
                />
              ) : null,
            )
            .filter(Boolean)}
          <input
            className="input"
            type="file"
            accept=".sig"
            multiple
            onChange={(e) => {
              const files = Array.from(e.target.files || [])
              onChange({
                ...doc,
                signFiles: files,
                signFileNames: files.map((f) => f.name),
              })
            }}
          />
        </Field>
      </div>
    </div>
  )
}

function PreviousConclusionBlock({
  item,
  index,
  options,
  onChange,
  onRemove,
}: {
  item: PreviousConclusion
  index: number
  options: OptionsMap
  onChange: (item: PreviousConclusion) => void
  onRemove: () => void
}) {
  return (
    <div className="repeat-block">
      <div className="repeat-header">
        <h3>Ранее выданное заключение {index + 1}</h3>
        <Button variant="danger" onClick={onRemove}>
          Удалить
        </Button>
      </div>
      <Field label="Дата заключения экспертизы (ДД.ММ.ГГГГ)">
        <TextInput value={item.date} onChange={(v) => onChange({ ...item, date: v })} />
      </Field>
      <Field label="Номер заключения экспертизы">
        <NumberFormatRadios
          value={item.numberFormat}
          onChange={(numberFormat) => onChange({ ...item, numberFormat })}
        />
        <TextInput value={item.number} onChange={(v) => onChange({ ...item, number: v })} />
      </Field>
      <Field label="Вид объекта экспертизы">
        <SelectInput
          value={item.objectType}
          onChange={(v) => onChange({ ...item, objectType: v })}
          options={options.examinationObjectType}
          placeholder="— не выбрано —"
        />
      </Field>
      <Field label="Наименование объекта экспертизы">
        <TextInput value={item.name} onChange={(v) => onChange({ ...item, name: v })} />
      </Field>
      <Field label="Результат экспертизы">
        <SelectInput
          value={item.result}
          onChange={(v) => onChange({ ...item, result: v })}
          options={options.examinationResult}
          placeholder="— не выбрано —"
        />
      </Field>
    </div>
  )
}

function PreviousSimpleConclusionBlock({
  item,
  index,
  options,
  onChange,
  onRemove,
}: {
  item: PreviousSimpleConclusion
  index: number
  options: OptionsMap
  onChange: (item: PreviousSimpleConclusion) => void
  onRemove: () => void
}) {
  return (
    <div className="repeat-block">
      <div className="repeat-header">
        <h3>Заключение по экспертному сопровождению {index + 1}</h3>
        <Button variant="danger" onClick={onRemove}>
          Удалить
        </Button>
      </div>
      <Field label="Дата заключения по результатам оценки в рамках экспертного сопровождения (ДД.ММ.ГГГГ)">
        <TextInput value={item.date} onChange={(v) => onChange({ ...item, date: v })} />
      </Field>
      <Field label="Номер заключения по результатам оценки в рамках экспертного сопровождения">
        <TextInput value={item.number} onChange={(v) => onChange({ ...item, number: v })} />
      </Field>
      <Field label="Вид объекта экспертизы">
        <SelectInput
          value={item.objectType}
          onChange={(v) => onChange({ ...item, objectType: v })}
          options={options.examinationObjectType}
          placeholder="— не выбрано —"
        />
      </Field>
      <Field label="Результат оценки соответствия в рамках экспертного сопровождения">
        <SelectInput
          value={item.result}
          onChange={(v) => onChange({ ...item, result: v })}
          options={options.examinationResult}
          placeholder="— не выбрано —"
        />
      </Field>
    </div>
  )
}

function PartyItemBlock({
  party,
  index,
  blockLabel,
  developerLabel,
  technicalCustomerLabel,
  options,
  onChange,
  onRemove,
}: {
  party: PartyItem
  index: number
  blockLabel: string
  developerLabel: string
  technicalCustomerLabel: string
  options: OptionsMap
  onChange: (party: PartyItem) => void
  onRemove: () => void
}) {
  return (
    <div className="repeat-block">
      <div className="repeat-header">
        <h3>
          {blockLabel} {index + 1}
        </h3>
        <Button variant="danger" onClick={onRemove}>
          Удалить
        </Button>
      </div>
      <PartyBlock
        value={party}
        onChange={onChange}
        options={options}
        developerLabel={developerLabel}
        technicalCustomerLabel={technicalCustomerLabel}
      />
    </div>
  )
}

function ExpertBlock({
  expert,
  index,
  options,
  onChange,
  onRemove,
}: {
  expert: Expert
  index: number
  options: OptionsMap
  onChange: (expert: Expert) => void
  onRemove: () => void
}) {
  return (
    <div className="repeat-block">
      <div className="repeat-header">
        <h3>Эксперт {index + 1}</h3>
        <Button variant="danger" onClick={onRemove}>
          Удалить
        </Button>
      </div>
      <div className="grid">
        <Field label="Фамилия" required>
          <TextInput value={expert.familyName} onChange={(v) => onChange({ ...expert, familyName: v })} />
        </Field>
        <Field label="Имя" required>
          <TextInput value={expert.firstName} onChange={(v) => onChange({ ...expert, firstName: v })} />
        </Field>
        <Field label="Отчество" optional>
          <TextInput value={expert.secondName} onChange={(v) => onChange({ ...expert, secondName: v })} />
        </Field>
        <Field label="Направление деятельности" required>
          <SelectInput
            value={expert.expertType}
            onChange={(v) => onChange({ ...expert, expertType: v })}
            options={options.expertType}
            placeholder="— не выбрано —"
          />
        </Field>
        <Field label="Номер аттестата" required>
          <TextInput
            value={expert.expertCertificate}
            onChange={(v) => onChange({ ...expert, expertCertificate: v })}
          />
        </Field>
        <Field label="Дата выдачи (ДД.ММ.ГГГГ)" required>
          <TextInput
            value={expert.certificateBeginDate}
            onChange={(v) => onChange({ ...expert, certificateBeginDate: v })}
          />
        </Field>
        <Field label="Дата окончания (ДД.ММ.ГГГГ)" required>
          <TextInput
            value={expert.certificateEndDate}
            onChange={(v) => onChange({ ...expert, certificateEndDate: v })}
          />
        </Field>
      </div>
    </div>
  )
}
