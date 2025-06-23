import tkinter as tk
from tkinter import messagebox
import xml.etree.ElementTree as ET
from xml.dom import minidom


def prettify(elem):
    """Возвращает pretty-print XML элемента как строку."""
    rough_string = ET.tostring(elem, encoding='utf-8', method='xml')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def generate_xml():
    # Считываем данные из полей
    org_full_name = entry_org_full_name.get()
    org_ogrn = entry_org_ogrn.get()
    org_inn = entry_org_inn.get()
    org_kpp = entry_org_kpp.get()

    country = entry_country.get()
    region = entry_region.get()
    city = entry_city.get()
    street = entry_street.get()
    building = entry_building.get()
    room = entry_room.get()

    family_name = entry_family_name.get()
    first_name = entry_first_name.get()
    second_name = entry_middle_name.get()
    position = entry_position.get()

    selected_subjects = listbox_subjects.curselection()
    subjects = [listbox_subjects.get(i) for i in selected_subjects]

    if not subjects:
        messagebox.showwarning("Ошибка", "Выберите хотя бы один предмет экспертизы!")
        return



    if not all([family_name, first_name, position]):
        messagebox.showwarning("Ошибка", "Заполните обязательные поля лица, утвердившего заключение")
        return

    # Проверка на заполненность обязательных полей
    if not all([org_full_name, org_ogrn, org_inn, org_kpp, country, region, city, street, building, room]):
        messagebox.showwarning("Ошибка", "Заполните все поля организации по проведению экспертизы!")
        return

    # Создаем корневой элемент <Conclusion>
    conclusion = ET.Element('Conclusion', {
        'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xsi:noNamespaceSchemaLocation': 'conclusion-01-02.xsd',
        'ConclusionGUID': '508889FE-84C3-DC36-91D1-CD3CD513F689',
        'SchemaVersion': '01.02'
    })

    # Добавляем <ExpertOrganization>
    expert_organization = ET.SubElement(conclusion, 'ExpertOrganization')
    ET.SubElement(expert_organization, 'OrgFullName').text = org_full_name
    ET.SubElement(expert_organization, 'OrgOGRN').text = org_ogrn
    ET.SubElement(expert_organization, 'OrgINN').text = org_inn
    ET.SubElement(expert_organization, 'OrgKPP').text = org_kpp

    # Адрес
    address = ET.SubElement(expert_organization, 'Address')
    ET.SubElement(address, 'Country').text = country
    ET.SubElement(address, 'Region').text = region
    ET.SubElement(address, 'City').text = city
    ET.SubElement(address, 'Street').text = street
    ET.SubElement(address, 'Building').text = building
    ET.SubElement(address, 'Room').text = room

    # approver
    approver = ET.SubElement(conclusion, 'Approver')
    ET.SubElement(approver, 'FamilyName').text = family_name
    ET.SubElement(approver, 'FirstName').text = first_name
    ET.SubElement(approver, 'SecondName').text = second_name
    ET.SubElement(approver, 'Position').text = position


    # Документы
    documents = ET.SubElement(conclusion, 'Documents')
    ET.SubElement(documents, 'Document')  # Пустой тег

    # Декларант
    declarant = ET.SubElement(conclusion, 'Declarant')  # Пустой тег

    # Форматируем и сохраняем в файл
    xml_pretty_str = prettify(conclusion)

    lines = xml_pretty_str.splitlines()



    full_xml_str = (
                       '<?xml version="1.0" encoding="UTF-8"?>\n'
                       '<?xml-stylesheet type="text/xsl" href="conclusion-01-02.xsl" ?>\n'
                   ) + xml_pretty_str

    lines = full_xml_str.splitlines()

    del lines[2]


    with open("conclusion.xml", "w", encoding="utf-8") as f:
        f.write('\n'.join(lines))

    messagebox.showinfo("Готово", "XML файл успешно создан как 'conclusion.xml'")


# Создание главного окна
root = tk.Tk()
root.title("Генератор XML")
root.geometry("500x600")

# Заголовки и поля ввода
fields_org = [
    ("Полное наименование юрлица:", "org_full_name"),
    ("ОГРН:", "org_ogrn"),
    ("ИНН:", "org_inn"),
    ("КПП:", "org_kpp"),
    ("Страна:", "country"),
    ("Код региона (например: 77):", "region"),
    ("Город:", "city"),
    ("Улица:", "street"),
    ("Здание/сооружение:", "building"),
    ("Номер помещения:", "room"),
]

fields_glin = [
    ("Фамилия:", "family_name"),
    ("Имя:", "first_name"),
    ("Отчество:", "middle_name"),
    ("Должность:", "position"),
]


entries_org = {}
entries_glin = {}



label = tk.Label(root, text="Сведения об организации по проведению экспертизы", font=("Arial", 10), fg="black")
label.grid(row=0, column=0, sticky="w", padx=10, pady=5)

for idx, (label_text, field_name) in enumerate(fields_org):
    tk.Label(root, text=label_text).grid(row=idx + 1, column=0, sticky="w", padx=10, pady=5)
    entry = tk.Entry(root, width=50)
    entry.grid(row=idx + 1, column=1, padx=10, pady=5)
    entries_org[field_name] = entry

# Привязка к переменным
entry_org_full_name = entries_org["org_full_name"]
entry_org_ogrn = entries_org["org_ogrn"]
entry_org_inn = entries_org["org_inn"]
entry_org_kpp = entries_org["org_kpp"]
entry_country = entries_org["country"]
entry_region = entries_org["region"]
entry_city = entries_org["city"]
entry_street = entries_org["street"]
entry_building = entries_org["building"]
entry_room = entries_org["room"]

# Размещаем заголовок для данных эксперта
label_glin = tk.Label(root, text="Сведения о лице, утвердившем заключение", font=("Arial", 10), fg="black")
label_glin.grid(row=len(fields_org)+1, column=0, sticky="w", padx=10, pady=10)

# Размещаем поля из fields_glin ниже полей организации
for idx, (label_text, field_name) in enumerate(fields_glin):
    tk.Label(root, text=label_text).grid(
        row=len(fields_org) + 2 + idx, column=0, sticky="w", padx=10, pady=5
    )
    entry = tk.Entry(root, width=50)
    entry.grid(row=len(fields_org) + 2 + idx, column=1, padx=10, pady=5)
    entries_glin[field_name] = entry


entry_family_name = entries_glin["family_name"]
entry_first_name = entries_glin["first_name"]
entry_middle_name = entries_glin["middle_name"]
entry_position = entries_glin["position"]

label_glin = tk.Label(root, text="Сведения об объекте экспертизы", font=("Arial", 10), fg="black")
label_glin.grid(row=len(fields_org) + len(fields_glin) + 2, column=0, sticky="w", padx=10, pady=10)

label_subjects = tk.Label(root, text="Предметы экспертизы:", font=("Arial", 10), fg="black")
label_subjects.grid(row=len(fields_org) + len(fields_glin) + 2, column=0, sticky="w", padx=10, pady=5)

listbox_subjects = tk.Listbox(root, selectmode=tk.MULTIPLE, height=3)
listbox_subjects.grid(row=len(fields_org) + len(fields_glin) + 2, column=1, padx=10, pady=5)

for subject in ["1", "2", "3"]:
    listbox_subjects.insert(tk.END, subject)

# Кнопка для создания XML
btn_generate = tk.Button(root, text="Создать XML", command=generate_xml, width=20)
btn_generate.grid(row=len(fields_org) + len(fields_glin) + 3, column=0, columnspan=2, pady=20)



# Запуск главного цикла
root.mainloop()