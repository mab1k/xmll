import { emptyAddress, emptyEntity, emptyMismatch, emptyMismatchExtended, emptyTei } from '../../defaultForm'
import { newId } from '../../id'
import type {
  Address,
  ComplexCostRecord,
  EntityData,
  Mismatch,
  MismatchExtended,
  ObjectPart,
  OptionItem,
  OptionsMap,
  PartyItem,
  PostAddress,
  TeiItem,
} from '../../types'
import { Button, Field, SelectInput, TextInput } from '../ui'

const REQUIRED_ADDRESS_KEYS: (keyof Address)[] = ['region', 'city', 'street', 'building', 'room']

interface AddressFieldsProps {
  value: Address
  onChange: (value: Address) => void
  options: OptionsMap
  title?: string
}

export function AddressFields({ value, onChange, options, title }: AddressFieldsProps) {
  return (
    <>
      {title && <h3>{title}</h3>}
      <div className="grid">
        {options.addressFields.map((field) => (
          <Field
            key={field.key}
            label={field.label}
            required={REQUIRED_ADDRESS_KEYS.includes(field.key)}
            optional={!REQUIRED_ADDRESS_KEYS.includes(field.key) && field.key !== 'country'}
          >
            <TextInput
              value={value[field.key] || ''}
              onChange={(v) => onChange({ ...value, [field.key]: v })}
            />
          </Field>
        ))}
      </div>
    </>
  )
}

interface PostAddressFieldsProps {
  value: PostAddress
  onChange: (value: PostAddress) => void
  options: OptionsMap
  title?: string
}

export function PostAddressFields({ value, onChange, options, title }: PostAddressFieldsProps) {
  return (
    <>
      {title && <h3>{title}</h3>}
      <div className="grid">
        {options.postAddressFields.map((field) => (
          <Field
            key={field.key}
            label={field.label}
            required={field.key === 'region' || field.key === 'post_index'}
            optional={!['region', 'post_index'].includes(field.key)}
          >
            <TextInput
              value={value[field.key] || ''}
              onChange={(v) => onChange({ ...value, [field.key]: v })}
            />
          </Field>
        ))}
      </div>
    </>
  )
}

interface EntityFormProps {
  value: EntityData
  onChange: (value: EntityData) => void
  options: OptionsMap
  typeOptions: OptionItem[]
}

export function EntityForm({ value, onChange, options, typeOptions }: EntityFormProps) {
  const setType = (type: EntityData['type']) => {
    onChange({ ...emptyEntity(type), email: value.email })
  }

  return (
    <>
      <Field label="Тип" required>
        <div className="radio-list">
          {typeOptions.map((opt) => (
            <label key={opt.value} className="radio-item">
              <input
                type="radio"
                name={`entity-type-${value.type}`}
                checked={value.type === opt.value}
                onChange={() => setType(opt.value as EntityData['type'])}
              />
              <span>{opt.label}</span>
            </label>
          ))}
        </div>
      </Field>

      {value.type === 'organization' && (
        <div className="grid">
          <Field label="Полное наименование юридического лица" required>
            <TextInput value={value.orgFullName} onChange={(v) => onChange({ ...value, orgFullName: v })} />
          </Field>
          <Field label="ОГРН" required>
            <TextInput value={value.orgOgrn} onChange={(v) => onChange({ ...value, orgOgrn: v })} />
          </Field>
          <Field label="ИНН" required>
            <TextInput value={value.orgInn} onChange={(v) => onChange({ ...value, orgInn: v })} />
          </Field>
          <Field label="КПП" required>
            <TextInput value={value.orgKpp} onChange={(v) => onChange({ ...value, orgKpp: v })} />
          </Field>
          <Field label="Адрес электронной почты" optional>
            <TextInput value={value.email} onChange={(v) => onChange({ ...value, email: v })} />
          </Field>
        </div>
      )}

      {value.type === 'organization' && (
        <AddressFields
          value={value.address}
          onChange={(address) => onChange({ ...value, address })}
          options={options}
          title="Адрес (местонахождение) юридического лица"
        />
      )}

      {value.type === 'foreign_organization' && (
        <>
          <div className="grid">
            <Field label="Полное наименование" required>
              <TextInput value={value.orgFullName} onChange={(v) => onChange({ ...value, orgFullName: v })} />
            </Field>
            <Field label="ИНН" required>
              <TextInput value={value.orgInn} onChange={(v) => onChange({ ...value, orgInn: v })} />
            </Field>
            <Field label="КПП" required>
              <TextInput value={value.orgKpp} onChange={(v) => onChange({ ...value, orgKpp: v })} />
            </Field>
            <Field label="Адрес электронной почты" optional>
              <TextInput value={value.email} onChange={(v) => onChange({ ...value, email: v })} />
            </Field>
          </div>
          <AddressFields
            value={value.address}
            onChange={(address) => onChange({ ...value, address })}
            options={options}
            title="Адрес (местонахождение) филиала или представительства"
          />
        </>
      )}

      {value.type === 'ip' && (
        <>
          <div className="grid">
            <Field label="Фамилия" required>
              <TextInput value={value.familyName} onChange={(v) => onChange({ ...value, familyName: v })} />
            </Field>
            <Field label="Имя" required>
              <TextInput value={value.firstName} onChange={(v) => onChange({ ...value, firstName: v })} />
            </Field>
            <Field label="Отчество" optional>
              <TextInput value={value.secondName} onChange={(v) => onChange({ ...value, secondName: v })} />
            </Field>
            <Field label="ОГРНИП" required>
              <TextInput value={value.ogrnip} onChange={(v) => onChange({ ...value, ogrnip: v })} />
            </Field>
            <Field label="Адрес электронной почты" optional>
              <TextInput value={value.email} onChange={(v) => onChange({ ...value, email: v })} />
            </Field>
          </div>
          <PostAddressFields
            value={value.postAddress}
            onChange={(postAddress) => onChange({ ...value, postAddress })}
            options={options}
            title="Почтовый адрес индивидуального предпринимателя"
          />
        </>
      )}

      {value.type === 'person' && (
        <>
          <div className="grid">
            <Field label="Фамилия" required>
              <TextInput value={value.familyName} onChange={(v) => onChange({ ...value, familyName: v })} />
            </Field>
            <Field label="Имя" required>
              <TextInput value={value.firstName} onChange={(v) => onChange({ ...value, firstName: v })} />
            </Field>
            <Field label="Отчество" optional>
              <TextInput value={value.secondName} onChange={(v) => onChange({ ...value, secondName: v })} />
            </Field>
            <Field label="СНИЛС" required>
              <TextInput value={value.snils} onChange={(v) => onChange({ ...value, snils: v })} />
            </Field>
            <Field label="Адрес электронной почты" optional>
              <TextInput value={value.email} onChange={(v) => onChange({ ...value, email: v })} />
            </Field>
          </div>
          <PostAddressFields
            value={value.postAddress}
            onChange={(postAddress) => onChange({ ...value, postAddress })}
            options={options}
            title="Почтовый адрес физического лица"
          />
        </>
      )}
    </>
  )
}

interface TechnicalCustomerFormProps {
  value: EntityData
  onChange: (value: EntityData) => void
  options: OptionsMap
}

export function TechnicalCustomerForm({ value, onChange, options }: TechnicalCustomerFormProps) {
  return (
    <EntityForm
      value={value}
      onChange={onChange}
      options={options}
      typeOptions={options.technicalCustomerType}
    />
  )
}

interface MismatchBlockProps {
  title: string
  items: Mismatch[]
  onChange: (items: Mismatch[]) => void
}

export function MismatchBlock({ title, items, onChange }: MismatchBlockProps) {
  const updateItem = (id: string, patch: Partial<Mismatch>) => {
    onChange(items.map((item) => (item.id === id ? { ...item, ...patch } : item)))
  }

  const addItem = () => onChange([...items, emptyMismatch()])
  const removeItem = (id: string) => onChange(items.filter((item) => item.id !== id))

  return (
    <div className="sub-frame">
      <h4>{title}</h4>
      {items.map((item, index) => (
        <div key={item.id} className="repeat-block">
          <div className="repeat-header">
            <h3>
              {title} {index + 1}
            </h3>
            <Button variant="danger" onClick={() => removeItem(item.id)}>
              Удалить
            </Button>
          </div>
          <Field label="Вывод о несоответствии">
            <TextInput multiline value={item.summary} onChange={(v) => updateItem(item.id, { summary: v })} />
          </Field>
          <Field label="Ссылка на материалы">
            <TextInput multiline value={item.part} onChange={(v) => updateItem(item.id, { part: v })} />
          </Field>
          <Field label="Ссылка на конкретное требование">
            <TextInput multiline value={item.link} onChange={(v) => updateItem(item.id, { link: v })} />
          </Field>
        </div>
      ))}
      <Button variant="secondary" onClick={addItem}>
        + Добавить
      </Button>
    </div>
  )
}

interface MismatchExtendedBlockProps {
  title: string
  items: MismatchExtended[]
  onChange: (items: MismatchExtended[]) => void
  options: OptionsMap
}

export function MismatchExtendedBlock({ title, items, onChange, options }: MismatchExtendedBlockProps) {
  const updateItem = (id: string, patch: Partial<MismatchExtended>) => {
    onChange(items.map((item) => (item.id === id ? { ...item, ...patch } : item)))
  }

  const addItem = () => onChange([...items, emptyMismatchExtended()])
  const removeItem = (id: string) => onChange(items.filter((item) => item.id !== id))

  return (
    <div className="sub-frame">
      <h4>{title}</h4>
      {items.map((item, index) => (
        <div key={item.id} className="repeat-block">
          <div className="repeat-header">
            <h3>
              {title} {index + 1}
            </h3>
            <Button variant="danger" onClick={() => removeItem(item.id)}>
              Удалить
            </Button>
          </div>
          <Field label="Вывод о несоответствии">
            <TextInput multiline value={item.summary} onChange={(v) => updateItem(item.id, { summary: v })} />
          </Field>
          <Field label="Ссылка на материалы">
            <TextInput multiline value={item.part} onChange={(v) => updateItem(item.id, { part: v })} />
          </Field>
          <Field label="Ссылка на конкретное требование">
            <TextInput multiline value={item.link} onChange={(v) => updateItem(item.id, { link: v })} />
          </Field>
          <Field label="Направление деятельности, в части которого сформулированы сведения">
            <SelectInput
              value={item.expertType}
              onChange={(v) => updateItem(item.id, { expertType: v })}
              options={options.expertType}
              placeholder="— не выбрано —"
            />
          </Field>
        </div>
      ))}
      <Button variant="secondary" onClick={addItem}>
        + Добавить
      </Button>
    </div>
  )
}

interface TeiEditorProps {
  items: TeiItem[]
  onChange: (items: TeiItem[]) => void
  minRows?: number
}

export function TeiEditor({ items, onChange, minRows = 1 }: TeiEditorProps) {
  const updateItem = (id: string, patch: Partial<TeiItem>) => {
    onChange(items.map((item) => (item.id === id ? { ...item, ...patch } : item)))
  }

  const addItem = () => onChange([...items, emptyTei()])
  const removeItem = (id: string) => {
    if (items.length <= minRows) return
    onChange(items.filter((item) => item.id !== id))
  }

  return (
    <>
      {items.map((item, index) => (
        <div key={item.id} className="repeat-block">
          <div className="repeat-header">
            <h3>Показатель {index + 1}</h3>
            {items.length > minRows && (
              <Button variant="danger" onClick={() => removeItem(item.id)}>
                Удалить
              </Button>
            )}
          </div>
          <div className="grid">
            <Field label="Наименование показателя">
              <TextInput value={item.name} onChange={(v) => updateItem(item.id, { name: v })} />
            </Field>
            <Field label="Единица измерения">
              <TextInput value={item.measure} onChange={(v) => updateItem(item.id, { measure: v })} />
            </Field>
            <Field label="Значение показателя">
              <TextInput value={item.value} onChange={(v) => updateItem(item.id, { value: v })} />
            </Field>
          </div>
        </div>
      ))}
      <Button variant="secondary" onClick={addItem}>
        + Добавить показатель
      </Button>
    </>
  )
}

interface ObjectPartEditorProps {
  parts: ObjectPart[]
  onChange: (parts: ObjectPart[]) => void
  options: OptionsMap
}

export function ObjectPartEditor({ parts, onChange, options }: ObjectPartEditorProps) {
  const updatePart = (id: string, patch: Partial<ObjectPart>) => {
    onChange(parts.map((part) => (part.id === id ? { ...part, ...patch } : part)))
  }

  const addPart = () =>
    onChange([
      ...parts,
      {
        id: newId(),
        name: '',
        addresses: [emptyAddress()],
        functionsClass: '',
        tei: [emptyTei()],
      },
    ])

  const removePart = (id: string) => onChange(parts.filter((part) => part.id !== id))

  return (
    <>
      {parts.map((part, index) => (
        <div key={part.id} className="repeat-block">
          <div className="repeat-header">
            <h3>Составная часть сложного объекта {index + 1}</h3>
            <Button variant="danger" onClick={() => removePart(part.id)}>
              Удалить
            </Button>
          </div>
          <Field label="Наименование объекта">
            <TextInput value={part.name} onChange={(v) => updatePart(part.id, { name: v })} />
          </Field>
          {part.addresses.map((addr, addrIdx) => (
            <div key={addrIdx} className="repeat-block">
              <AddressFields
                value={addr}
                onChange={(address) => {
                  const addresses = [...part.addresses]
                  addresses[addrIdx] = address
                  updatePart(part.id, { addresses })
                }}
                options={options}
                title={`Адрес ${addrIdx + 1}`}
              />
            </div>
          ))}
          <Button
            variant="secondary"
            onClick={() =>
              updatePart(part.id, { addresses: [...part.addresses, emptyAddress()] })
            }
          >
            + Добавить адрес
          </Button>
          <Field label="Код классификатора">
            <TextInput
              value={part.functionsClass}
              onChange={(v) => updatePart(part.id, { functionsClass: v })}
            />
          </Field>
          <h4>Технико-экономические показатели</h4>
          <TeiEditor
            items={part.tei}
            onChange={(tei) => updatePart(part.id, { tei })}
          />
        </div>
      ))}
      <Button variant="secondary" onClick={addPart}>
        + Добавить составную часть
      </Button>
    </>
  )
}

interface PartyBlockProps {
  value: PartyItem
  onChange: (value: PartyItem) => void
  options: OptionsMap
  developerLabel: string
  technicalCustomerLabel: string
}

export function PartyBlock({
  value,
  onChange,
  options,
  developerLabel,
  technicalCustomerLabel,
}: PartyBlockProps) {
  return (
    <>
      <Field label="Выберите один из вариантов">
        <div className="radio-list">
          <label className="radio-item">
            <input
              type="radio"
              checked={value.partyType === 'developer'}
              onChange={() => onChange({ ...value, partyType: 'developer', entity: emptyEntity('organization') })}
            />
            <span>{developerLabel}</span>
          </label>
          <label className="radio-item">
            <input
              type="radio"
              checked={value.partyType === 'technical_customer'}
              onChange={() =>
                onChange({ ...value, partyType: 'technical_customer', entity: emptyEntity('organization') })
              }
            />
            <span>{technicalCustomerLabel}</span>
          </label>
        </div>
      </Field>

      {value.partyType === 'developer' ? (
        <EntityForm
          value={value.entity}
          onChange={(entity) => onChange({ ...value, entity })}
          options={options}
          typeOptions={options.declarantType}
        />
      ) : (
        <TechnicalCustomerForm
          value={value.entity}
          onChange={(entity) => onChange({ ...value, entity })}
          options={options}
        />
      )}
    </>
  )
}

interface ClimateValueListProps {
  title: string
  values: string[]
  onChange: (values: string[]) => void
  options: OptionItem[]
}

export function ClimateValueList({ title, values, onChange, options }: ClimateValueListProps) {
  const updateRow = (index: number, val: string) => {
    const next = [...values]
    next[index] = val
    onChange(next)
  }

  const addRow = () => onChange([...values, ''])
  const removeRow = (index: number) => {
    if (values.length <= 1) return
    onChange(values.filter((_, i) => i !== index))
  }

  return (
    <div className="sub-frame">
      <h4>{title}</h4>
      {values.map((val, index) => (
        <div key={index} className="inline-row">
          <SelectInput
            value={val}
            onChange={(v) => updateRow(index, v)}
            options={options}
            placeholder="— не выбрано —"
          />
          {values.length > 1 && (
            <Button variant="danger" onClick={() => removeRow(index)}>
              ✕
            </Button>
          )}
        </div>
      ))}
      <Button variant="secondary" onClick={addRow}>
        + Добавить
      </Button>
    </div>
  )
}

interface ComplexCostFormProps {
  title: string
  value: ComplexCostRecord
  onChange: (value: ComplexCostRecord) => void
  options: OptionsMap
}

export function ComplexCostForm({ title, value, onChange, options }: ComplexCostFormProps) {
  const updateField = (key: string, fieldValue: string) => {
    onChange({ ...value, [key]: fieldValue })
  }

  return (
    <div className="sub-frame">
      <h4>{title}</h4>
      <div className="grid">
        {options.complexCostFields.map((field) => (
          <Field key={field.key} label={field.label}>
            <TextInput value={value[field.key] || ''} onChange={(v) => updateField(field.key, v)} />
          </Field>
        ))}
        {options.complexCostCommentFields.map((field) => (
          <Field key={field.key} label={field.label} optional>
            <TextInput value={value[field.key] || ''} onChange={(v) => updateField(field.key, v)} />
          </Field>
        ))}
      </div>
    </div>
  )
}

export function NumberFormatRadios({
  value,
  onChange,
  egrzLabel = 'В формате ЕГРЗ',
  noegrzLabel = 'В произвольном формате',
}: {
  value: 'egrz' | 'noegrz'
  onChange: (v: 'egrz' | 'noegrz') => void
  egrzLabel?: string
  noegrzLabel?: string
}) {
  return (
    <div className="radio-list">
      <label className="radio-item">
        <input type="radio" checked={value === 'egrz'} onChange={() => onChange('egrz')} />
        <span>{egrzLabel}</span>
      </label>
      <label className="radio-item">
        <input type="radio" checked={value === 'noegrz'} onChange={() => onChange('noegrz')} />
        <span>{noegrzLabel}</span>
      </label>
    </div>
  )
}
