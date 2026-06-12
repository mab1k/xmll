import os
import re
import shutil
import zlib
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import xml.etree.ElementTree as ET
from xml.dom import minidom
import uuid

from climate_options import (
    CLIMATE_DISTRICT_OPTIONS,
    GEOLOGICAL_CONDITIONS_OPTIONS,
    SEISMIC_ACTIVITY_OPTIONS,
    SNOW_DISTRICT_OPTIONS,
    WIND_DISTRICT_OPTIONS,
)
from doc_types import DOC_TYPE_LABELS, DOC_TYPE_OPTIONS, DEFAULT_DOC_TYPE_LABEL, NOT_SPECIFIED
from engineering_survey_options import ENGINEERING_SURVEY_TYPE_OPTIONS
from expert_type_options import EXPERT_TYPE_OPTIONS
from region_options import REGION_RF_OPTIONS
from summary_options import (
    ENGINEERING_SURVEY_SUMMARY_OPTIONS,
    ENGINEERING_SURVEYS_RESULTS_SUMMARY_OPTIONS,
    ESTIMATE_NORMS_AND_WORKS_SUMMARY_OPTIONS,
    ESTIMATE_VALIDATION_SUMMARY_OPTIONS,
    PROJECT_DOCS_DESIGN_ASSIGNMENT_OPTIONS,
    PROJECT_DOCS_ENGINEERING_SURVEYS_RESULTS_OPTIONS,
    PROJECT_DOCS_TECHNICAL_REQUIREMENTS_OPTIONS,
    PROJECT_DOCUMENTS_SUMMARY_OPTIONS,
)


def prettify(elem):
    """Возвращает pretty-print XML элемента как строку."""
    rough_string = ET.tostring(elem, encoding='utf-8', method='xml')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


EXAMINATION_FORM_OPTIONS = {
    NOT_SPECIFIED: "",
    "Государственная": "1",
    "Негосударственная": "2",
}

EXAMINATION_RESULT_OPTIONS = {
    NOT_SPECIFIED: "",
    "Положительный": "1",
    "Отрицательный": "2",
}

EXAMINATION_OBJECT_TYPE_OPTIONS = {
    NOT_SPECIFIED: "",
    "Результаты инженерных изысканий": "1",
    "Проектная документация": "2",
    "Проектная документация и результаты инженерных изысканий": "3",
}

EXAMINATION_TYPE_OPTIONS = {
    NOT_SPECIFIED: "",
    "Оценка соответствия результатов инженерных изысканий требованиям технических регламентов "
    "(абзац 1 пункта 5 статьи 49 Градостроительного кодекса Российской Федерации)": "1",
    "Оценка соответствия проектной документации установленным требованиям "
    "(подпункт 1 пункт 5 статьи 49 Градостроительного кодекса Российской Федерации)": "2",
    "Проверка достоверности определения сметной стоимости "
    "(подпункт 2 пункт 5 статьи 49 Градостроительного кодекса Российской Федерации)": "3",
}

CONSTRUCTION_TYPE_OPTIONS = {
    NOT_SPECIFIED: "",
    "Строительство": "1",
    "Реконструкция": "2",
    "Капитальный ремонт": "3",
    "Снос": "4",
    "Сохранение объекта культурного наследия": "5",
}

EXAMINATION_STAGE_OPTIONS = {
    NOT_SPECIFIED: "",
    "Первичная": "1",
    "Повторная": "2",
    "По результатам экспертного сопровождения": "3",
}

IM_OPTIONS = {
    NOT_SPECIFIED: "",
    "Да": "да",
    "Нет": "нет",
}

CAPITAL_OBJECT_TYPE_OPTIONS = {
    NOT_SPECIFIED: "",
    "Объект производственного назначения": "1",
    "Объект непроизводственного назначения": "2",
    "Линейный объект": "3",
}

CADASTRAL_NUMBER_RE = re.compile(r"^\d+:\d+:\d+:\d+$")
ORG_OGRN_RE = re.compile(r"^\d{13}$")
ORG_INN_RE = re.compile(r"^\d{10}$")
ORG_KPP_RE = re.compile(r"^\d{9}$")
OGRNIP_RE = re.compile(r"^\d{15}$")
SNILS_RE = re.compile(r"^[0-9]{3}-[0-9]{3}-[0-9]{3} [0-9]{2}$")
POST_INDEX_RE = re.compile(r"^\d{6}$")
EMAIL_RE = re.compile(
    r"^[a-zA-Zа-яА-Я0-9_.\-]{1,}@[a-zA-Zа-яА-Я0-9_.\-]{1,}\.[a-zA-Zа-яА-Я]{2,}$"
)

DECLARANT_TYPE_OPTIONS = [
    ("organization", "Юридическое лицо"),
    ("foreign_organization", "Иностранное юридическое лицо (представительство, филиал)"),
    ("ip", "Индивидуальный предприниматель"),
    ("person", "Физическое лицо"),
]

TECHNICAL_CUSTOMER_TYPE_OPTIONS = [
    ("organization", "Юридическое лицо"),
    ("foreign_organization", "Иностранное юридическое лицо (представительство, филиал)"),
]

DESIGNER_TYPE_OPTIONS = [
    ("organization", "Проектная организация — организация"),
    ("foreign_organization", "Иностранная организация (представительство, филиал)"),
    ("ip", "Проектная организация — индивидуальный предприниматель"),
]

FINANCE_TYPE_OPTIONS = {
    NOT_SPECIFIED: "",
    "Бюджетные средства": "1",
    "Средства юридических лиц, перечисленных в части 2 статьи 8.3 "
    "Градостроительного кодекса Российской Федерации": "2",
    "Средства, не входящие в перечень, указанный в части 2 статьи 8.3 "
    "Градостроительного кодекса Российской Федерации": "3",
}

ESTIMATED_SUM_RE = re.compile(r"^(Не требуется|Отсутствует|-?\d*\.?\d*)$")

ESTIMATED_COST_MODE_OPTIONS = [
    (
        "complete",
        "Сметная стоимость на дату представления документации и на дату утверждения заключения",
    ),
    (
        "complex",
        "Составная сметная стоимость (проверка достоверности определения сметной стоимости)",
    ),
]

COMPLEX_ESTIMATED_COST_FIELDS = [
    ("Сметная стоимость в базисном уровне цен (тыс. руб.):", "CostBasic"),
    ("СМР в базисном уровне цен (тыс. руб.):", "WorksCostBasic"),
    ("Оборудование в базисном уровне цен (тыс. руб.):", "HardwareCostBasic"),
    ("Прочие затраты в базисном уровне цен (тыс. руб.):", "OtherCostBasic"),
    ("ПИР в базисном уровне цен (тыс. руб.):", "ProjectWorksCostBasic"),
    ("Возвратные суммы в базисном уровне цен (тыс. руб.):", "BackSumCostBasic"),
    ("Сметная стоимость в текущем уровне цен (тыс. руб.):", "Cost"),
    ("СМР в текущем уровне цен (тыс. руб.):", "WorksCost"),
    ("Оборудование в текущем уровне цен (тыс. руб.):", "HardwareCost"),
    ("Прочие затраты в текущем уровне цен (тыс. руб.):", "OtherCost"),
    ("ПИР в текущем уровне цен (тыс. руб.):", "ProjectWorksCost"),
    ("НДС (тыс. руб.):", "NDSCost"),
    ("Возвратные суммы в текущем уровне цен (тыс. руб.):", "BackSumCost"),
]

OPTIONAL_COMPLEX_COST_COMMENT_FIELDS = [
    ("Комментарий к сметной стоимости в базисном уровне цен:", "CostBasicComment"),
    ("Комментарий к сметной стоимости в текущем уровне цен:", "CostComment"),
]

BUDGET_TYPE_OPTIONS = {
    NOT_SPECIFIED: "",
    "Федеральный бюджет": "1",
    "Бюджет субъекта Российской Федерации": "2",
    "Местный бюджет": "3",
    "Бюджет государственного внебюджетного фонда Российской Федерации": "4",
    "Бюджет территориального государственного внебюджетного фонда": "5",
}

CAPITAL_OBJECT_ADDRESS_FIELDS = [
    ("Страна:", "country"),
    ("Код субъекта РФ:", "region"),
    ("Наименование района:", "district"),
    ("Город:", "city"),
    ("Населённый пункт:", "settlement"),
    ("Улица:", "street"),
    ("Номер здания/сооружения:", "building"),
    ("Номер помещения:", "room"),
    ("Неформализованное описание адреса:", "note"),
]

POST_ADDRESS_FIELDS = [
    ("Страна:", "country"),
    ("Код субъекта РФ:", "region"),
    ("Почтовый индекс:", "post_index"),
    ("Наименование района:", "district"),
    ("Город:", "city"),
    ("Населённый пункт:", "settlement"),
    ("Улица:", "street"),
    ("Номер здания/сооружения:", "building"),
    ("Номер помещения:", "room"),
    ("Неформализованное описание адреса:", "note"),
]

UI_FONT = ("Segoe UI", 10)
UI_FONT_BOLD = ("Segoe UI", 10, "bold")
UI_FONT_SECTION = ("Segoe UI", 11, "bold")
UI_FONT_HINT = ("Segoe UI", 9)
UI_COLOR_TEXT = "#1f2937"
UI_COLOR_OPTIONAL = "#6b7280"
UI_COLOR_HINT = "#9ca3af"
UI_COLOR_REQUIRED = "#b45309"
UI_PAD_X = 12
UI_PAD_Y = 4

ADDRESS_FIELD_META = {
    "country": {"optional": True},
    "region": {"required": True},
    "district": {"optional": True},
    "city": {"optional": True},
    "settlement": {"optional": True},
    "street": {"optional": True},
    "building": {"optional": True},
    "room": {"optional": True},
    "note": {"optional": True},
    "post_index": {"required": True},
}


def setup_app_theme(root):
    root.configure(bg="#f3f4f6")
    style = ttk.Style(root)
    if "vista" in style.theme_names():
        style.theme_use("vista")
    elif "clam" in style.theme_names():
        style.theme_use("clam")
    style.configure("TCombobox", padding=2)
    style.configure("Section.TLabelframe", padding=(10, 6))
    style.configure("Section.TLabelframe.Label", font=UI_FONT_BOLD, foreground=UI_COLOR_TEXT)
    style.configure("Primary.TButton", font=UI_FONT_BOLD, padding=(12, 6))
    style.configure("Secondary.TButton", padding=(8, 4))


def format_field_label(text, *, required=False, optional=False):
    base = text.rstrip(":")
    if required:
        return f"{base} *:"
    if optional:
        return f"{base} (необяз.):"
    return f"{base}:"


def _parent_bg(parent):
    try:
        return parent.cget("bg")
    except tk.TclError:
        return "#f3f4f6"


def create_field_label(
    parent,
    text,
    row,
    *,
    column=0,
    required=False,
    optional=False,
    sticky="w",
    pady=UI_PAD_Y,
    padx=UI_PAD_X,
):
    label = tk.Label(
        parent,
        text=format_field_label(text, required=required, optional=optional),
        font=UI_FONT,
        fg=UI_COLOR_REQUIRED if required else (UI_COLOR_OPTIONAL if optional else UI_COLOR_TEXT),
        bg=_parent_bg(parent),
        justify="left",
    )
    label.grid(row=row, column=column, sticky=sticky, padx=padx, pady=pady)
    return label


def create_section_title(parent, text, row, *, colspan=2, pady=(14, 6)):
    label = tk.Label(
        parent,
        text=text,
        font=UI_FONT_SECTION,
        fg=UI_COLOR_TEXT,
        bg="#f3f4f6",
        anchor="w",
        justify="left",
    )
    label.grid(row=row, column=0, columnspan=colspan, sticky="w", padx=UI_PAD_X, pady=pady)
    separator = ttk.Separator(parent, orient="horizontal")
    separator.grid(row=row + 1, column=0, columnspan=colspan, sticky="ew", padx=UI_PAD_X, pady=(0, 4))
    return row + 2


def create_form_legend(parent, row, *, colspan=2):
    legend = tk.Label(
        parent,
        text="* — обязательное поле     (необяз.) — заполняется при необходимости",
        font=UI_FONT_HINT,
        fg=UI_COLOR_HINT,
        bg="#f3f4f6",
        anchor="w",
    )
    legend.grid(row=row, column=0, columnspan=colspan, sticky="w", padx=UI_PAD_X, pady=(0, 8))
    return row + 1


def create_primary_button(parent, text, command, **grid_options):
    button = ttk.Button(parent, text=text, command=command, style="Primary.TButton")
    button.grid(**grid_options)
    return button


def create_secondary_button(parent, text, command, **grid_options):
    button = ttk.Button(parent, text=text, command=command, style="Secondary.TButton")
    button.grid(**grid_options)
    return button


def create_packed_caption(parent, text, *, optional=False, bold=False, pady=(8, 0)):
    suffix = " (необяз.)" if optional else ""
    label = tk.Label(
        parent,
        text=f"{text}{suffix}:",
        font=UI_FONT_BOLD if bold else UI_FONT,
        fg=UI_COLOR_OPTIONAL if optional else UI_COLOR_TEXT,
        bg=_parent_bg(parent),
        anchor="w",
        justify="left",
    )
    label.pack(anchor="w", pady=pady)
    return label


def _parse_field_spec(field):
    if len(field) == 2:
        return field[0], field[1], {}
    return field[0], field[1], field[2]


def create_combobox(parent, options, default=None):
    var = tk.StringVar(value=default or NOT_SPECIFIED)
    combo = ttk.Combobox(
        parent,
        textvariable=var,
        values=list(options.keys()),
        state="readonly",
        width=58,
    )
    return combo, var


def add_examination_type_row(parent, row_frame, rows_list):
    var = tk.StringVar(value=NOT_SPECIFIED)
    combo = ttk.Combobox(
        row_frame,
        textvariable=var,
        values=list(EXAMINATION_TYPE_OPTIONS.keys()),
        state="readonly",
        width=50,
    )
    combo.grid(row=0, column=0, padx=(0, 5), sticky="ew")

    def remove_row():
        if len(rows_list) <= 1:
            messagebox.showwarning("Ошибка", "Должен остаться хотя бы один предмет экспертизы!")
            return
        rows_list.remove(row_data)
        row_frame.destroy()

    btn_remove = tk.Button(row_frame, text="✕", command=remove_row, width=3)
    btn_remove.grid(row=0, column=1)

    row_data = {"frame": row_frame, "var": var, "combo": combo}
    rows_list.append(row_data)


def get_option_value(options, var):
    return options.get(var.get(), "")


def compute_file_checksum(file_path, uppercase=False):
    with open(file_path, "rb") as f:
        value = f"{zlib.crc32(f.read()) & 0xFFFFFFFF:08x}"
        return value.upper() if uppercase else value


def get_file_metadata(file_path, checksum_upper=False):
    file_name = os.path.basename(file_path)
    return {
        "file_path": file_path,
        "file_name": file_name,
        "file_format": os.path.splitext(file_name)[1].lstrip(".").lower(),
        "file_checksum": compute_file_checksum(file_path, uppercase=checksum_upper),
    }


def format_doc_date(value):
    value = value.strip()
    if not value:
        return ""
    match = re.fullmatch(r"(\d{2})\.(\d{2})\.(\d{4})", value)
    if match:
        day, month, year = match.groups()
        return f"{year}-{month}-{day}"
    match = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", value)
    if match:
        return value
    return ""


def create_doc_type_combobox(parent):
    frame = tk.Frame(parent)
    var = tk.StringVar(value=DEFAULT_DOC_TYPE_LABEL)
    values = [NOT_SPECIFIED] + DOC_TYPE_LABELS
    combo = ttk.Combobox(frame, textvariable=var, values=values, width=70)

    def filter_doc_types(event=None):
        typed = var.get().lower()
        if not typed or typed == NOT_SPECIFIED.lower():
            combo["values"] = values
            return
        combo["values"] = [NOT_SPECIFIED] + [label for label in DOC_TYPE_LABELS if typed in label.lower()]

    combo.bind("<KeyRelease>", filter_doc_types)
    combo.pack(fill="x")
    return frame, var, combo


def collect_document_data(row):
    doc_type = get_option_value(DOC_TYPE_OPTIONS, row["var_doc_type"])
    doc_name = row["text_doc_name"].get("1.0", tk.END).strip()
    doc_number = row["entry_doc_number"].get().strip()
    doc_date = format_doc_date(row["entry_doc_date"].get())
    doc_changes = row["entry_doc_changes"].get().strip()
    doc_author = row["entry_doc_author"].get().strip()
    file_path = row["file_path"]

    file_meta = get_file_metadata(file_path) if file_path else {}
    sign_files = [
        get_file_metadata(path, checksum_upper=True)
        for path in row.get("sign_files", [])
    ]

    return {
        "doc_type": doc_type,
        "doc_name": doc_name,
        "doc_number": doc_number,
        "doc_date": doc_date,
        "doc_changes": doc_changes,
        "doc_author": doc_author,
        "file_path": file_path,
        "file_name": file_meta.get("file_name", ""),
        "file_format": file_meta.get("file_format", ""),
        "file_checksum": file_meta.get("file_checksum", ""),
        "sign_files": sign_files,
    }


def add_document_block(container, rows_list, default_values=None):
    default_values = default_values or {}
    index = len(rows_list) + 1
    block = ttk.LabelFrame(container, text=f"Документ {index}", style="Section.TLabelframe")
    block.pack(fill="x", pady=8, padx=4)

    row = 0
    create_field_label(block, "Код типа документа", row, required=True, padx=8)
    type_frame, var_doc_type, combo_doc_type = create_doc_type_combobox(block)
    type_frame.grid(row=row, column=1, sticky="w", pady=4, padx=(0, 8))
    if default_values.get("doc_type_label"):
        var_doc_type.set(default_values["doc_type_label"])
    row += 1

    create_field_label(block, "Наименование документа", row, required=True, padx=8)
    text_doc_name = tk.Text(block, width=60, height=2, font=UI_FONT)
    text_doc_name.grid(row=row, column=1, sticky="w", pady=4, padx=(0, 8))
    if default_values.get("doc_name"):
        text_doc_name.insert("1.0", default_values["doc_name"])
    row += 1

    create_field_label(block, "Номер (обозначение, шифр) документа", row, optional=True, padx=8)
    entry_doc_number = tk.Entry(block, width=60, font=UI_FONT)
    entry_doc_number.grid(row=row, column=1, sticky="w", pady=4, padx=(0, 8))
    if default_values.get("doc_number"):
        entry_doc_number.insert(0, default_values["doc_number"])
    row += 1

    create_field_label(block, "Дата документа (ДД.ММ.ГГГГ)", row, required=True, padx=8)
    entry_doc_date = tk.Entry(block, width=20, font=UI_FONT)
    entry_doc_date.grid(row=row, column=1, sticky="w", pady=4, padx=(0, 8))
    if default_values.get("doc_date"):
        entry_doc_date.insert(0, default_values["doc_date"])
    row += 1

    create_field_label(block, "Примечание об изменении документа", row, optional=True, padx=8)
    entry_doc_changes = tk.Entry(block, width=60, font=UI_FONT)
    entry_doc_changes.grid(row=row, column=1, sticky="w", pady=4, padx=(0, 8))
    if default_values.get("doc_changes"):
        entry_doc_changes.insert(0, default_values["doc_changes"])
    row += 1

    create_field_label(
        block,
        "Автор документа (организация, ИП или физ. лицо)",
        row,
        optional=True,
        padx=8,
    )
    entry_doc_author = tk.Entry(block, width=60, font=UI_FONT)
    entry_doc_author.grid(row=row, column=1, sticky="w", pady=4, padx=(0, 8))
    if default_values.get("doc_author"):
        entry_doc_author.insert(0, default_values["doc_author"])
    row += 1

    create_field_label(block, "Файл документа", row, required=True, padx=8)
    file_frame = tk.Frame(block)
    file_frame.grid(row=row, column=1, sticky="w", pady=4)

    row_data = {
        "frame": block,
        "var_doc_type": var_doc_type,
        "text_doc_name": text_doc_name,
        "entry_doc_number": entry_doc_number,
        "entry_doc_date": entry_doc_date,
        "entry_doc_changes": entry_doc_changes,
        "entry_doc_author": entry_doc_author,
        "file_path": default_values.get("file_path"),
        "sign_files": list(default_values.get("sign_files", [])),
    }

    label_file = tk.Label(file_frame, text="Файл не выбран", fg="gray", anchor="w", justify="left")
    label_file.pack(anchor="w")

    def update_file_label():
        path = row_data["file_path"]
        if not path:
            label_file.config(text="Файл не выбран", fg="gray")
            return
        meta = get_file_metadata(path)
        label_file.config(
            text=(
                f"{meta['file_name']}\n"
                f"Формат: {meta['file_format']}  |  Контрольная сумма: {meta['file_checksum']}"
            ),
            fg="black",
        )

    def select_file():
        path = filedialog.askopenfilename(title="Выберите файл документа")
        if not path:
            return
        row_data["file_path"] = path
        update_file_label()

    update_file_label()
    row_data["label_file"] = label_file

    btn_file = tk.Button(file_frame, text="Загрузить файл", command=select_file)
    btn_file.pack(anchor="w", pady=(4, 0))

    signs_container = tk.Frame(file_frame)
    signs_container.pack(anchor="w", fill="x", pady=(8, 0))

    def refresh_signs_list():
        for widget in signs_container.winfo_children():
            widget.destroy()
        if not row_data["sign_files"]:
            return
        tk.Label(signs_container, text="Эл. подписи:", anchor="w").pack(anchor="w")
        for index, path in enumerate(row_data["sign_files"]):
            sign_frame = tk.Frame(signs_container)
            sign_frame.pack(fill="x", pady=2)
            meta = get_file_metadata(path, checksum_upper=True)

            def remove_sign(idx=index):
                row_data["sign_files"].pop(idx)
                refresh_signs_list()

            tk.Label(
                sign_frame,
                text=f"• {meta['file_name']}  |  {meta['file_format']}  |  {meta['file_checksum']}",
                anchor="w",
            ).pack(side="left")
            tk.Button(sign_frame, text="✕", command=remove_sign, width=3).pack(side="right")

    def add_sign_file():
        path = filedialog.askopenfilename(
            title="Выберите файл эл. подписи",
            filetypes=[("Файлы подписи", "*.sig *.sgn"), ("Все файлы", "*.*")],
        )
        if not path:
            return
        row_data["sign_files"].append(path)
        refresh_signs_list()

    btn_sign = tk.Button(file_frame, text="Добавить эл. подпись", command=add_sign_file)
    btn_sign.pack(anchor="w", pady=(4, 0))
    refresh_signs_list()

    def remove_document():
        if len(rows_list) <= 1:
            messagebox.showwarning("Ошибка", "Должен остаться хотя бы один документ!")
            return
        rows_list.remove(row_data)
        block.destroy()
        for idx, doc_row in enumerate(rows_list, start=1):
            doc_row["frame"].config(text=f"Документ {idx}")

    btn_remove = tk.Button(block, text="Удалить документ", command=remove_document)
    btn_remove.grid(row=row + 1, column=1, sticky="w", pady=8)

    rows_list.append(row_data)


def collect_previous_conclusion_data(row):
    return {
        "date": format_doc_date(row["entry_date"].get()),
        "number": row["entry_number"].get().strip(),
        "number_format": row["var_number_format"].get(),
        "object_type": get_option_value(EXAMINATION_OBJECT_TYPE_OPTIONS, row["var_object_type"]),
        "name": row["entry_name"].get().strip(),
        "result": get_option_value(EXAMINATION_RESULT_OPTIONS, row["var_result"]),
    }


def is_previous_conclusion_filled(data):
    return any([
        data["date"],
        data["number"],
        data["object_type"],
        data["name"],
        data["result"],
    ])


def add_previous_conclusion_block(container, rows_list, default_values=None):
    default_values = default_values or {}
    index = len(rows_list) + 1
    block = tk.LabelFrame(
        container,
        text=f"Ранее выданное заключение {index}",
        padx=8,
        pady=8,
    )
    block.pack(fill="x", pady=8, padx=4)

    row = 0
    tk.Label(block, text="Дата заключения экспертизы (ДД.ММ.ГГГГ):").grid(
        row=row, column=0, sticky="w", pady=4
    )
    entry_date = tk.Entry(block, width=20)
    entry_date.grid(row=row, column=1, sticky="w", pady=4)
    if default_values.get("date"):
        entry_date.insert(0, default_values["date"])
    row += 1

    tk.Label(block, text="Номер заключения экспертизы:").grid(row=row, column=0, sticky="nw", pady=4)
    number_frame = tk.Frame(block)
    number_frame.grid(row=row, column=1, sticky="w", pady=4)

    var_number_format = tk.StringVar(value=default_values.get("number_format", "egrz"))
    tk.Radiobutton(
        number_frame,
        text="В формате ЕГРЗ",
        variable=var_number_format,
        value="egrz",
    ).pack(anchor="w")
    tk.Radiobutton(
        number_frame,
        text="В произвольном формате",
        variable=var_number_format,
        value="noegrz",
    ).pack(anchor="w")

    entry_number = tk.Entry(number_frame, width=60)
    entry_number.pack(anchor="w", pady=(4, 0))
    if default_values.get("number"):
        entry_number.insert(0, default_values["number"])
    row += 1

    combo_object_type, var_object_type = create_combobox(
        block,
        EXAMINATION_OBJECT_TYPE_OPTIONS,
        default_values.get("object_type_label", NOT_SPECIFIED),
    )
    tk.Label(block, text="Вид объекта экспертизы:").grid(row=row, column=0, sticky="w", pady=4)
    combo_object_type.grid(row=row, column=1, sticky="w", pady=4)
    row += 1

    tk.Label(block, text="Наименование объекта экспертизы:").grid(row=row, column=0, sticky="w", pady=4)
    entry_name = tk.Entry(block, width=60)
    entry_name.grid(row=row, column=1, sticky="w", pady=4)
    if default_values.get("name"):
        entry_name.insert(0, default_values["name"])
    row += 1

    combo_result, var_result = create_combobox(
        block,
        EXAMINATION_RESULT_OPTIONS,
        default_values.get("result_label", NOT_SPECIFIED),
    )
    tk.Label(block, text="Результат экспертизы:").grid(row=row, column=0, sticky="w", pady=4)
    combo_result.grid(row=row, column=1, sticky="w", pady=4)

    row_data = {
        "frame": block,
        "entry_date": entry_date,
        "entry_number": entry_number,
        "var_number_format": var_number_format,
        "var_object_type": var_object_type,
        "entry_name": entry_name,
        "var_result": var_result,
    }

    def remove_block():
        rows_list.remove(row_data)
        block.destroy()
        for idx, item in enumerate(rows_list, start=1):
            item["frame"].config(text=f"Ранее выданное заключение {idx}")

    btn_remove = tk.Button(block, text="Удалить", command=remove_block)
    btn_remove.grid(row=row + 1, column=1, sticky="w", pady=8)

    rows_list.append(row_data)


def collect_previous_simple_conclusion_data(row):
    return {
        "date": format_doc_date(row["entry_date"].get()),
        "number": row["entry_number"].get().strip(),
        "object_type": get_option_value(EXAMINATION_OBJECT_TYPE_OPTIONS, row["var_object_type"]),
        "result": get_option_value(EXAMINATION_RESULT_OPTIONS, row["var_result"]),
    }


def is_previous_simple_conclusion_filled(data):
    return any([
        data["date"],
        data["number"],
        data["object_type"],
        data["result"],
    ])


def add_previous_simple_conclusion_block(container, rows_list, default_values=None):
    default_values = default_values or {}
    index = len(rows_list) + 1
    block = tk.LabelFrame(
        container,
        text=f"Заключение по экспертному сопровождению {index}",
        padx=8,
        pady=8,
    )
    block.pack(fill="x", pady=8, padx=4)

    row = 0
    tk.Label(
        block,
        text="Дата заключения по результатам оценки\nв рамках экспертного сопровождения (ДД.ММ.ГГГГ):",
    ).grid(row=row, column=0, sticky="nw", pady=4)
    entry_date = tk.Entry(block, width=20)
    entry_date.grid(row=row, column=1, sticky="w", pady=4)
    if default_values.get("date"):
        entry_date.insert(0, default_values["date"])
    row += 1

    tk.Label(
        block,
        text="Номер заключения по результатам оценки\nв рамках экспертного сопровождения:",
    ).grid(row=row, column=0, sticky="nw", pady=4)
    entry_number = tk.Entry(block, width=60)
    entry_number.grid(row=row, column=1, sticky="w", pady=4)
    if default_values.get("number"):
        entry_number.insert(0, default_values["number"])
    row += 1

    combo_object_type, var_object_type = create_combobox(
        block,
        EXAMINATION_OBJECT_TYPE_OPTIONS,
        default_values.get("object_type_label", NOT_SPECIFIED),
    )
    tk.Label(block, text="Вид объекта экспертизы:").grid(row=row, column=0, sticky="w", pady=4)
    combo_object_type.grid(row=row, column=1, sticky="w", pady=4)
    row += 1

    combo_result, var_result = create_combobox(
        block,
        EXAMINATION_RESULT_OPTIONS,
        default_values.get("result_label", NOT_SPECIFIED),
    )
    tk.Label(
        block,
        text="Результат оценки соответствия\nв рамках экспертного сопровождения:",
    ).grid(row=row, column=0, sticky="nw", pady=4)
    combo_result.grid(row=row, column=1, sticky="w", pady=4)

    row_data = {
        "frame": block,
        "entry_date": entry_date,
        "entry_number": entry_number,
        "var_object_type": var_object_type,
        "var_result": var_result,
    }

    def remove_block():
        rows_list.remove(row_data)
        block.destroy()
        for idx, item in enumerate(rows_list, start=1):
            item["frame"].config(text=f"Заключение по экспертному сопровождению {idx}")

    btn_remove = tk.Button(block, text="Удалить", command=remove_block)
    btn_remove.grid(row=row + 1, column=1, sticky="w", pady=8)

    rows_list.append(row_data)


def append_previous_conclusions_xml(conclusion, items):
    if not items:
        return
    previous_conclusions = ET.SubElement(conclusion, 'PreviousConclusions')
    for prev in items:
        prev_elem = ET.SubElement(previous_conclusions, 'PreviousConclusion')
        ET.SubElement(prev_elem, 'Date').text = prev["date"]
        number_elem = ET.SubElement(prev_elem, 'Number')
        if prev["number_format"] == "egrz":
            ET.SubElement(number_elem, 'EGRZ').text = prev["number"]
        else:
            ET.SubElement(number_elem, 'noEGRZ').text = prev["number"]
        ET.SubElement(prev_elem, 'ExaminationObjectType').text = prev["object_type"]
        ET.SubElement(prev_elem, 'Name').text = prev["name"]
        ET.SubElement(prev_elem, 'Result').text = prev["result"]


def append_previous_simple_conclusions(conclusion, items):
    if not items:
        return
    previous_simple = ET.SubElement(conclusion, 'PreviousSimpleConclusions')
    for item in items:
        elem = ET.SubElement(previous_simple, 'PreviousSimpleConclusion')
        ET.SubElement(elem, 'Date').text = item["date"]
        ET.SubElement(elem, 'Number').text = item["number"]
        ET.SubElement(elem, 'ExaminationObjectType').text = item["object_type"]
        ET.SubElement(elem, 'Result').text = item["result"]


def address_block_title(index, total):
    title = "Почтовый (строительный) адрес (местоположение)"
    if total > 1:
        return f"{title} {index}"
    return title


def refresh_address_titles(rows_list):
    total = len(rows_list)
    for index, row in enumerate(rows_list, start=1):
        row["frame"].config(text=address_block_title(index, total))


def add_address_block(container, rows_list, defaults=None):
    defaults = defaults or {}
    index = len(rows_list) + 1
    frame = tk.LabelFrame(
        container,
        text=address_block_title(index, index),
        padx=6,
        pady=6,
    )
    frame.pack(fill="x", pady=4)

    entries = {}
    for row_idx, (label_text, key) in enumerate(CAPITAL_OBJECT_ADDRESS_FIELDS):
        meta = ADDRESS_FIELD_META.get(key, {})
        create_field_label(
            frame,
            label_text.rstrip(":"),
            row_idx,
            required=meta.get("required", False),
            optional=meta.get("optional", False),
            padx=6,
            pady=2,
        )
        entry = tk.Entry(frame, width=55, font=UI_FONT)
        entry.grid(row=row_idx, column=1, sticky="w", pady=2, padx=(4, 0))
        if defaults.get(key):
            entry.insert(0, defaults[key])
        entries[key] = entry

    row_data = {"frame": frame, "entries": entries}

    def remove_block():
        if len(rows_list) <= 1:
            messagebox.showwarning("Ошибка", "Должен остаться хотя бы один адрес!")
            return
        rows_list.remove(row_data)
        frame.destroy()
        refresh_address_titles(rows_list)

    tk.Button(frame, text="Удалить адрес", command=remove_block).grid(
        row=len(CAPITAL_OBJECT_ADDRESS_FIELDS),
        column=1,
        sticky="w",
        pady=4,
    )
    rows_list.append(row_data)
    refresh_address_titles(rows_list)


def collect_address_data(entries):
    return {key: entries[key].get().strip() for _, key in CAPITAL_OBJECT_ADDRESS_FIELDS}


def collect_address_rows(rows_list):
    addresses = []
    for row in rows_list:
        data = collect_address_data(row["entries"])
        if any(data.values()):
            addresses.append(data)
    return addresses


def append_address_xml(parent_elem, address_data):
    address = ET.SubElement(parent_elem, 'Address')
    tag_map = [
        ("country", "Country"),
        ("region", "Region"),
        ("district", "District"),
        ("city", "City"),
        ("settlement", "Settlement"),
        ("street", "Street"),
        ("building", "Building"),
        ("room", "Room"),
        ("note", "Note"),
    ]
    for key, tag in tag_map:
        value = address_data.get(key, "")
        if value:
            ET.SubElement(address, tag).text = value


def append_addresses_xml(parent_elem, addresses):
    for address_data in addresses:
        append_address_xml(parent_elem, address_data)


def create_inline_form(parent, fields, title=None):
    if title:
        frame = ttk.LabelFrame(parent, text=title, style="Section.TLabelframe")
    else:
        frame = tk.Frame(parent)
    frame.pack(fill="x", pady=4)
    entries = {}
    for row_idx, field in enumerate(fields):
        label_text, key, meta = _parse_field_spec(field)
        create_field_label(
            frame,
            label_text.rstrip(":"),
            row_idx,
            required=meta.get("required", False),
            optional=meta.get("optional", False),
            padx=6,
            pady=2,
        )
        entry = tk.Entry(frame, width=55, font=UI_FONT)
        entry.grid(row=row_idx, column=1, sticky="w", pady=2, padx=(4, 6))
        entries[key] = entry
    return frame, entries


def collect_inline_form(entries, field_keys):
    return {key: entries[key].get().strip() for key in field_keys}


def validate_address_data(address_data, label):
    region = address_data.get("region", "")
    if not region:
        return f"Укажите код субъекта РФ в адресе ({label})!"
    detail_fields = ("district", "city", "settlement", "street", "building", "room")
    if not address_data.get("note") and not any(address_data.get(key) for key in detail_fields):
        return (
            f"Заполните адрес ({label}): укажите неформализованное описание "
            f"или хотя бы одно из полей района, города, населённого пункта, улицы, здания, помещения!"
        )
    return None


def validate_post_address_data(address_data, label):
    region = address_data.get("region", "")
    post_index = address_data.get("post_index", "")
    if not region:
        return f"Укажите код субъекта РФ в почтовом адресе ({label})!"
    if not post_index:
        return f"Укажите почтовый индекс ({label})!"
    if not POST_INDEX_RE.match(post_index):
        return f"Некорректный почтовый индекс ({label})! Формат: 123456"
    return None


def append_post_address_xml(parent_elem, address_data):
    post_address = ET.SubElement(parent_elem, 'PostAddress')
    tag_map = [
        ("country", "Country"),
        ("region", "Region"),
        ("post_index", "PostIndex"),
        ("district", "District"),
        ("city", "City"),
        ("settlement", "Settlement"),
        ("street", "Street"),
        ("building", "Building"),
        ("room", "Room"),
        ("note", "Note"),
    ]
    for key, tag in tag_map:
        value = address_data.get(key, "")
        if value:
            ET.SubElement(post_address, tag).text = value


def append_organization_xml(parent_elem, tag_name, data):
    org = ET.SubElement(parent_elem, tag_name)
    ET.SubElement(org, 'OrgFullName').text = data["org_full_name"]
    if data.get("org_ogrn"):
        ET.SubElement(org, 'OrgOGRN').text = data["org_ogrn"]
    ET.SubElement(org, 'OrgINN').text = data["org_inn"]
    ET.SubElement(org, 'OrgKPP').text = data["org_kpp"]
    append_address_xml(org, data["address"])
    if data.get("email"):
        ET.SubElement(org, 'Email').text = data["email"]


def append_ip_xml(parent_elem, data):
    ip = ET.SubElement(parent_elem, 'IP')
    ET.SubElement(ip, 'FamilyName').text = data["family_name"]
    ET.SubElement(ip, 'FirstName').text = data["first_name"]
    if data.get("second_name"):
        ET.SubElement(ip, 'SecondName').text = data["second_name"]
    ET.SubElement(ip, 'OGRNIP').text = data["ogrnip"]
    append_post_address_xml(ip, data["post_address"])
    if data.get("email"):
        ET.SubElement(ip, 'Email').text = data["email"]


def append_person_xml(parent_elem, data):
    person = ET.SubElement(parent_elem, 'Person')
    ET.SubElement(person, 'FamilyName').text = data["family_name"]
    ET.SubElement(person, 'FirstName').text = data["first_name"]
    if data.get("second_name"):
        ET.SubElement(person, 'SecondName').text = data["second_name"]
    ET.SubElement(person, 'SNILS').text = data["snils"]
    append_post_address_xml(person, data["post_address"])
    if data.get("email"):
        ET.SubElement(person, 'Email').text = data["email"]


def append_declarant_entity_xml(parent_elem, data):
    declarant_type = data["type"]
    if declarant_type == "organization":
        append_organization_xml(parent_elem, 'Organization', data)
    elif declarant_type == "foreign_organization":
        append_organization_xml(parent_elem, 'ForeignOrganization', data)
    elif declarant_type == "ip":
        append_ip_xml(parent_elem, data)
    else:
        append_person_xml(parent_elem, data)


def append_declarant_xml(conclusion, data):
    declarant = ET.SubElement(conclusion, 'Declarant')
    append_declarant_entity_xml(declarant, data)


def collect_declarant_data():
    declarant_type = var_declarant_type.get()
    address_keys = [key for _, key in CAPITAL_OBJECT_ADDRESS_FIELDS]
    post_address_keys = [key for _, key in POST_ADDRESS_FIELDS]

    if declarant_type == "organization":
        data = collect_inline_form(declarant_org_entries, [
            "org_full_name", "org_ogrn", "org_inn", "org_kpp",
        ])
        data["address"] = collect_inline_form(declarant_org_address_entries, address_keys)
        data["email"] = declarant_org_email.get().strip()
        data["type"] = declarant_type
        return data

    if declarant_type == "foreign_organization":
        data = collect_inline_form(declarant_foreign_entries, [
            "org_full_name", "org_inn", "org_kpp",
        ])
        data["address"] = collect_inline_form(declarant_foreign_address_entries, address_keys)
        data["email"] = declarant_foreign_email.get().strip()
        data["type"] = declarant_type
        return data

    if declarant_type == "ip":
        data = collect_inline_form(declarant_ip_entries, [
            "family_name", "first_name", "second_name", "ogrnip",
        ])
        data["post_address"] = collect_inline_form(declarant_ip_post_address_entries, post_address_keys)
        data["email"] = declarant_ip_email.get().strip()
        data["type"] = declarant_type
        return data

    data = collect_inline_form(declarant_person_entries, [
        "family_name", "first_name", "second_name", "snils",
    ])
    data["post_address"] = collect_inline_form(declarant_person_post_address_entries, post_address_keys)
    data["email"] = declarant_person_email.get().strip()
    data["type"] = declarant_type
    return data


def create_declarant_ui(parent):
    container = tk.Frame(parent)
    container.pack(fill="x", pady=4)

    var_type = tk.StringVar(value="organization")
    type_frame = tk.Frame(container)
    type_frame.pack(fill="x", pady=(0, 4))
    panels = {}

    def switch_panel():
        selected = var_type.get()
        for key, panel in panels.items():
            if key == selected:
                panel.pack(fill="x", pady=4)
            else:
                panel.pack_forget()

    for value, label in DECLARANT_TYPE_OPTIONS:
        tk.Radiobutton(
            type_frame,
            text=label,
            variable=var_type,
            value=value,
            command=switch_panel,
            anchor="w",
        ).pack(fill="x", pady=1)

    details_frame = tk.Frame(container)
    details_frame.pack(fill="x")

    org_panel = tk.Frame(details_frame)
    _, org_entries = create_inline_form(
        org_panel,
        [
            ("Полное наименование юридического лица:", "org_full_name"),
            ("ОГРН:", "org_ogrn"),
            ("ИНН:", "org_inn"),
            ("КПП:", "org_kpp"),
        ],
    )
    _, org_address_entries = create_inline_form(
        org_panel,
        CAPITAL_OBJECT_ADDRESS_FIELDS,
        title="Адрес (местонахождение) юридического лица",
    )
    tk.Label(org_panel, text="Адрес электронной почты:").pack(anchor="w", pady=(4, 0))
    org_email = tk.Entry(org_panel, width=60)
    org_email.pack(anchor="w", pady=(2, 4))
    panels["organization"] = org_panel

    foreign_panel = tk.Frame(details_frame)
    _, foreign_entries = create_inline_form(
        foreign_panel,
        [
            ("Полное наименование:", "org_full_name"),
            ("ИНН:", "org_inn"),
            ("КПП:", "org_kpp"),
        ],
    )
    _, foreign_address_entries = create_inline_form(
        foreign_panel,
        CAPITAL_OBJECT_ADDRESS_FIELDS,
        title="Адрес (местонахождение) филиала или представительства",
    )
    tk.Label(foreign_panel, text="Адрес электронной почты:").pack(anchor="w", pady=(4, 0))
    foreign_email = tk.Entry(foreign_panel, width=60)
    foreign_email.pack(anchor="w", pady=(2, 4))
    panels["foreign_organization"] = foreign_panel

    ip_panel = tk.Frame(details_frame)
    _, ip_entries = create_inline_form(
        ip_panel,
        [
            ("Фамилия:", "family_name"),
            ("Имя:", "first_name"),
            ("Отчество:", "second_name"),
            ("ОГРНИП:", "ogrnip"),
        ],
    )
    _, ip_post_address_entries = create_inline_form(
        ip_panel,
        POST_ADDRESS_FIELDS,
        title="Почтовый адрес индивидуального предпринимателя",
    )
    tk.Label(ip_panel, text="Адрес электронной почты:").pack(anchor="w", pady=(4, 0))
    ip_email = tk.Entry(ip_panel, width=60)
    ip_email.pack(anchor="w", pady=(2, 4))
    panels["ip"] = ip_panel

    person_panel = tk.Frame(details_frame)
    _, person_entries = create_inline_form(
        person_panel,
        [
            ("Фамилия:", "family_name"),
            ("Имя:", "first_name"),
            ("Отчество:", "second_name"),
            ("СНИЛС:", "snils"),
        ],
    )
    _, person_post_address_entries = create_inline_form(
        person_panel,
        POST_ADDRESS_FIELDS,
        title="Почтовый адрес физического лица",
    )
    tk.Label(person_panel, text="Адрес электронной почты:").pack(anchor="w", pady=(4, 0))
    person_email = tk.Entry(person_panel, width=60)
    person_email.pack(anchor="w", pady=(2, 4))
    panels["person"] = person_panel

    switch_panel()

    return {
        "container": container,
        "var_type": var_type,
        "organization": {
            "entries": org_entries,
            "address": org_address_entries,
            "email": org_email,
        },
        "foreign_organization": {
            "entries": foreign_entries,
            "address": foreign_address_entries,
            "email": foreign_email,
        },
        "ip": {
            "entries": ip_entries,
            "post_address": ip_post_address_entries,
            "email": ip_email,
        },
        "person": {
            "entries": person_entries,
            "post_address": person_post_address_entries,
            "email": person_email,
        },
    }


def collect_declarant_ui_data(ui):
    declarant_type = ui["var_type"].get()
    address_keys = [key for _, key in CAPITAL_OBJECT_ADDRESS_FIELDS]
    post_address_keys = [key for _, key in POST_ADDRESS_FIELDS]

    if declarant_type == "organization":
        data = collect_inline_form(ui["organization"]["entries"], [
            "org_full_name", "org_ogrn", "org_inn", "org_kpp",
        ])
        data["address"] = collect_inline_form(ui["organization"]["address"], address_keys)
        data["email"] = ui["organization"]["email"].get().strip()
        data["type"] = declarant_type
        return data

    if declarant_type == "foreign_organization":
        data = collect_inline_form(ui["foreign_organization"]["entries"], [
            "org_full_name", "org_inn", "org_kpp",
        ])
        data["address"] = collect_inline_form(
            ui["foreign_organization"]["address"],
            address_keys,
        )
        data["email"] = ui["foreign_organization"]["email"].get().strip()
        data["type"] = declarant_type
        return data

    if declarant_type == "ip":
        data = collect_inline_form(ui["ip"]["entries"], [
            "family_name", "first_name", "second_name", "ogrnip",
        ])
        data["post_address"] = collect_inline_form(ui["ip"]["post_address"], post_address_keys)
        data["email"] = ui["ip"]["email"].get().strip()
        data["type"] = declarant_type
        return data

    data = collect_inline_form(ui["person"]["entries"], [
        "family_name", "first_name", "second_name", "snils",
    ])
    data["post_address"] = collect_inline_form(ui["person"]["post_address"], post_address_keys)
    data["email"] = ui["person"]["email"].get().strip()
    data["type"] = declarant_type
    return data


def is_declarant_data_filled(data):
    if data["type"] == "organization":
        org_keys = ("org_full_name", "org_ogrn", "org_inn", "org_kpp", "email")
    elif data["type"] == "foreign_organization":
        org_keys = ("org_full_name", "org_inn", "org_kpp", "email")
    elif data["type"] == "ip":
        if any(data.get(key) for key in ("family_name", "first_name", "second_name", "ogrnip", "email")):
            return True
        return any(data.get("post_address", {}).values())
    else:
        if any(data.get(key) for key in ("family_name", "first_name", "second_name", "snils", "email")):
            return True
        return any(data.get("post_address", {}).values())
    if any(data.get(key) for key in org_keys):
        return True
    return any(data.get("address", {}).values())


def create_technical_customer_ui(parent):
    container = tk.Frame(parent)
    container.pack(fill="x", pady=4)

    var_type = tk.StringVar(value="organization")
    type_frame = tk.Frame(container)
    type_frame.pack(fill="x", pady=(0, 4))
    panels = {}

    def switch_panel():
        selected = var_type.get()
        for key, panel in panels.items():
            if key == selected:
                panel.pack(fill="x", pady=4)
            else:
                panel.pack_forget()

    for value, label in TECHNICAL_CUSTOMER_TYPE_OPTIONS:
        tk.Radiobutton(
            type_frame,
            text=label,
            variable=var_type,
            value=value,
            command=switch_panel,
            anchor="w",
        ).pack(fill="x", pady=1)

    details_frame = tk.Frame(container)
    details_frame.pack(fill="x")

    org_panel = tk.Frame(details_frame)
    _, org_entries = create_inline_form(
        org_panel,
        [
            ("Полное наименование юридического лица:", "org_full_name"),
            ("ОГРН:", "org_ogrn"),
            ("ИНН:", "org_inn"),
            ("КПП:", "org_kpp"),
        ],
    )
    _, org_address_entries = create_inline_form(
        org_panel,
        CAPITAL_OBJECT_ADDRESS_FIELDS,
        title="Адрес (местонахождение) юридического лица",
    )
    tk.Label(org_panel, text="Адрес электронной почты:").pack(anchor="w", pady=(4, 0))
    org_email = tk.Entry(org_panel, width=60)
    org_email.pack(anchor="w", pady=(2, 4))
    panels["organization"] = org_panel

    foreign_panel = tk.Frame(details_frame)
    _, foreign_entries = create_inline_form(
        foreign_panel,
        [
            ("Полное наименование:", "org_full_name"),
            ("ИНН:", "org_inn"),
            ("КПП:", "org_kpp"),
        ],
    )
    _, foreign_address_entries = create_inline_form(
        foreign_panel,
        CAPITAL_OBJECT_ADDRESS_FIELDS,
        title="Адрес (местонахождение) филиала или представительства",
    )
    tk.Label(foreign_panel, text="Адрес электронной почты:").pack(anchor="w", pady=(4, 0))
    foreign_email = tk.Entry(foreign_panel, width=60)
    foreign_email.pack(anchor="w", pady=(2, 4))
    panels["foreign_organization"] = foreign_panel

    switch_panel()

    return {
        "container": container,
        "var_type": var_type,
        "organization": {
            "entries": org_entries,
            "address": org_address_entries,
            "email": org_email,
        },
        "foreign_organization": {
            "entries": foreign_entries,
            "address": foreign_address_entries,
            "email": foreign_email,
        },
    }


def is_technical_customer_filled(data):
    if data["type"] == "organization":
        org_keys = ("org_full_name", "org_ogrn", "org_inn", "org_kpp", "email")
    else:
        org_keys = ("org_full_name", "org_inn", "org_kpp", "email")
    if any(data.get(key) for key in org_keys):
        return True
    return any(data.get("address", {}).values())


def collect_technical_customer_data(ui):
    customer_type = ui["var_type"].get()
    address_keys = [key for _, key in CAPITAL_OBJECT_ADDRESS_FIELDS]
    if customer_type == "organization":
        data = collect_inline_form(ui["organization"]["entries"], [
            "org_full_name", "org_ogrn", "org_inn", "org_kpp",
        ])
        data["address"] = collect_inline_form(ui["organization"]["address"], address_keys)
        data["email"] = ui["organization"]["email"].get().strip()
        data["type"] = customer_type
        return data

    data = collect_inline_form(ui["foreign_organization"]["entries"], [
        "org_full_name", "org_inn", "org_kpp",
    ])
    data["address"] = collect_inline_form(ui["foreign_organization"]["address"], address_keys)
    data["email"] = ui["foreign_organization"]["email"].get().strip()
    data["type"] = customer_type
    return data


def validate_technical_customer_data(data, label):
    email = data.get("email", "")
    if email and not EMAIL_RE.match(email):
        return f"Некорректный адрес электронной почты ({label})!"

    if data["type"] == "organization":
        if not data["org_full_name"]:
            return f"Укажите полное наименование юридического лица ({label})!"
        if not data["org_ogrn"]:
            return f"Укажите ОГРН ({label})!"
        if not ORG_OGRN_RE.match(data["org_ogrn"]):
            return f"Некорректный ОГРН ({label})! Должно быть 13 цифр."
        if not data["org_inn"]:
            return f"Укажите ИНН ({label})!"
        if not ORG_INN_RE.match(data["org_inn"]):
            return f"Некорректный ИНН ({label})! Должно быть 10 цифр."
        if not data["org_kpp"]:
            return f"Укажите КПП ({label})!"
        if not ORG_KPP_RE.match(data["org_kpp"]):
            return f"Некорректный КПП ({label})! Должно быть 9 цифр."
        return validate_address_data(data["address"], label)

    if not data["org_full_name"]:
        return f"Укажите полное наименование иностранного юридического лица ({label})!"
    if not data["org_inn"]:
        return f"Укажите ИНН ({label})!"
    if not ORG_INN_RE.match(data["org_inn"]):
        return f"Некорректный ИНН ({label})! Должно быть 10 цифр."
    if not data["org_kpp"]:
        return f"Укажите КПП ({label})!"
    if not ORG_KPP_RE.match(data["org_kpp"]):
        return f"Некорректный КПП ({label})! Должно быть 9 цифр."
    return validate_address_data(data["address"], label)


def append_technical_customer_xml(parent_elem, data):
    if data["type"] == "organization":
        append_organization_xml(parent_elem, 'Organization', data)
    else:
        append_organization_xml(parent_elem, 'ForeignOrganization', data)


def add_project_documents_party_block(container, rows_list):
    index = len(rows_list) + 1
    block = tk.LabelFrame(
        container,
        text=f"Подготовка проектной документации {index}",
        padx=8,
        pady=8,
    )
    block.pack(fill="x", pady=8, padx=4)

    var_party = tk.StringVar(value="developer")
    tk.Label(block, text="Выберите один из вариантов:").pack(anchor="w", pady=(0, 4))
    tk.Radiobutton(
        block,
        text="Застройщик, обеспечивший подготовку проектной документации "
        "(внесение изменений в проектную документацию)",
        variable=var_party,
        value="developer",
        command=lambda: switch_party(),
        anchor="w",
        justify="left",
    ).pack(fill="x")
    tk.Radiobutton(
        block,
        text="Технический заказчик, обеспечивший подготовку проектной документации "
        "(внесение изменений в проектную документацию)",
        variable=var_party,
        value="technical_customer",
        command=lambda: switch_party(),
        anchor="w",
        justify="left",
    ).pack(fill="x")

    developer_frame = tk.LabelFrame(
        block,
        text="Застройщик, обеспечивший подготовку проектной документации",
        padx=8,
        pady=8,
    )
    technical_frame = tk.LabelFrame(
        block,
        text="Технический заказчик, обеспечивший подготовку проектной документации",
        padx=8,
        pady=8,
    )
    declarant_ui = create_declarant_ui(developer_frame)
    technical_ui = create_technical_customer_ui(technical_frame)

    def switch_party():
        if var_party.get() == "developer":
            developer_frame.pack(fill="x", pady=4)
            technical_frame.pack_forget()
        else:
            developer_frame.pack_forget()
            technical_frame.pack(fill="x", pady=4)

    switch_party()

    row_data = {
        "frame": block,
        "var_party": var_party,
        "declarant_ui": declarant_ui,
        "technical_ui": technical_ui,
    }

    def remove_block():
        rows_list.remove(row_data)
        block.destroy()
        for idx, item in enumerate(rows_list, start=1):
            item["frame"].config(text=f"Подготовка проектной документации {idx}")

    tk.Button(block, text="Удалить", command=remove_block).pack(anchor="w", pady=8)
    rows_list.append(row_data)


def collect_project_documents_party_data(row):
    if row["var_party"].get() == "developer":
        entity = collect_declarant_ui_data(row["declarant_ui"])
        return {"party_type": "developer", "entity": entity}
    entity = collect_technical_customer_data(row["technical_ui"])
    return {"party_type": "technical_customer", "entity": entity}


def is_project_documents_party_filled(item):
    if item["party_type"] == "developer":
        return is_declarant_data_filled(item["entity"])
    return is_technical_customer_filled(item["entity"])


def collect_project_documents_parties_data(rows_list):
    parties = []
    for row in rows_list:
        item = collect_project_documents_party_data(row)
        if is_project_documents_party_filled(item):
            parties.append(item)
    return parties


def validate_project_documents_parties_rows(rows_list):
    for idx, row in enumerate(rows_list, start=1):
        item = collect_project_documents_party_data(row)
        if not is_project_documents_party_filled(item):
            continue
        if item["party_type"] == "developer":
            error = validate_declarant_entity_data(
                item["entity"],
                f"застройщик проектной документации {idx}",
            )
        else:
            error = validate_technical_customer_data(
                item["entity"],
                f"технический заказчик проектной документации {idx}",
            )
        if error:
            return error
    return ""


def append_project_documents_parties_xml(conclusion, parties):
    for item in parties:
        if item["party_type"] == "developer":
            elem = ET.SubElement(conclusion, 'ProjectDocumentsDeveloper')
            append_declarant_entity_xml(elem, item["entity"])
        else:
            elem = ET.SubElement(conclusion, 'ProjectDocumentsTechnicalCustomer')
            append_technical_customer_xml(elem, item["entity"])


def add_engineering_survey_party_block(container, rows_list):
    index = len(rows_list) + 1
    block = tk.LabelFrame(
        container,
        text=f"Проведение инженерных изысканий {index}",
        padx=8,
        pady=8,
    )
    block.pack(fill="x", pady=8, padx=4)

    var_party = tk.StringVar(value="developer")
    tk.Label(block, text="Выберите один из вариантов:").pack(anchor="w", pady=(0, 4))
    tk.Radiobutton(
        block,
        text="Застройщик, обеспечивший проведение инженерных изысканий",
        variable=var_party,
        value="developer",
        command=lambda: switch_party(),
        anchor="w",
        justify="left",
    ).pack(fill="x")
    tk.Radiobutton(
        block,
        text="Технический заказчик, обеспечивший проведение инженерных изысканий",
        variable=var_party,
        value="technical_customer",
        command=lambda: switch_party(),
        anchor="w",
        justify="left",
    ).pack(fill="x")

    developer_frame = tk.LabelFrame(
        block,
        text="Застройщик, обеспечивший проведение инженерных изысканий",
        padx=8,
        pady=8,
    )
    technical_frame = tk.LabelFrame(
        block,
        text="Технический заказчик, обеспечивший проведение инженерных изысканий",
        padx=8,
        pady=8,
    )
    declarant_ui = create_declarant_ui(developer_frame)
    technical_ui = create_technical_customer_ui(technical_frame)

    def switch_party():
        if var_party.get() == "developer":
            developer_frame.pack(fill="x", pady=4)
            technical_frame.pack_forget()
        else:
            developer_frame.pack_forget()
            technical_frame.pack(fill="x", pady=4)

    switch_party()

    row_data = {
        "frame": block,
        "var_party": var_party,
        "declarant_ui": declarant_ui,
        "technical_ui": technical_ui,
    }

    def remove_block():
        rows_list.remove(row_data)
        block.destroy()
        for idx, item in enumerate(rows_list, start=1):
            item["frame"].config(text=f"Проведение инженерных изысканий {idx}")

    tk.Button(block, text="Удалить", command=remove_block).pack(anchor="w", pady=8)
    rows_list.append(row_data)


def collect_engineering_survey_party_data(row):
    if row["var_party"].get() == "developer":
        entity = collect_declarant_ui_data(row["declarant_ui"])
        return {"party_type": "developer", "entity": entity}
    entity = collect_technical_customer_data(row["technical_ui"])
    return {"party_type": "technical_customer", "entity": entity}


def is_engineering_survey_party_filled(item):
    if item["party_type"] == "developer":
        return is_declarant_data_filled(item["entity"])
    return is_technical_customer_filled(item["entity"])


def collect_engineering_survey_parties_data(rows_list):
    parties = []
    for row in rows_list:
        item = collect_engineering_survey_party_data(row)
        if is_engineering_survey_party_filled(item):
            parties.append(item)
    return parties


def validate_engineering_survey_parties_rows(rows_list):
    for idx, row in enumerate(rows_list, start=1):
        item = collect_engineering_survey_party_data(row)
        if not is_engineering_survey_party_filled(item):
            continue
        if item["party_type"] == "developer":
            error = validate_declarant_entity_data(
                item["entity"],
                f"застройщик инженерных изысканий {idx}",
            )
        else:
            error = validate_technical_customer_data(
                item["entity"],
                f"технический заказчик инженерных изысканий {idx}",
            )
        if error:
            return error
    return ""


def append_engineering_survey_parties_xml(conclusion, parties):
    for item in parties:
        if item["party_type"] == "developer":
            elem = ET.SubElement(conclusion, 'EngineeringSurveyDeveloper')
            append_declarant_entity_xml(elem, item["entity"])
        else:
            elem = ET.SubElement(conclusion, 'EngineeringSurveyTechnicalCustomer')
            append_technical_customer_xml(elem, item["entity"])


def add_finance_block(container, rows_list):
    index = len(rows_list) + 1
    block = tk.LabelFrame(
        container,
        text=f"Источник финансирования {index}",
        padx=8,
        pady=8,
    )
    block.pack(fill="x", pady=8, padx=4)

    tk.Label(block, text="Вид источника финансирования:").grid(row=0, column=0, sticky="w", pady=4)
    combo_finance_type, var_finance_type = create_combobox(block, FINANCE_TYPE_OPTIONS)
    combo_finance_type.grid(row=0, column=1, sticky="w", pady=4)

    tk.Label(block, text="Уровень бюджета\n(в случае бюджетного финансирования):").grid(
        row=1, column=0, sticky="nw", pady=4
    )
    combo_budget_type, var_budget_type = create_combobox(block, BUDGET_TYPE_OPTIONS)
    combo_budget_type.grid(row=1, column=1, sticky="w", pady=4)

    tk.Label(block, text="Размер финансирования\n(в % от общей суммы):").grid(
        row=2, column=0, sticky="nw", pady=4
    )
    entry_finance_size = tk.Entry(block, width=20)
    entry_finance_size.grid(row=2, column=1, sticky="w", pady=4)

    owner_wrapper = tk.Frame(block)
    owner_wrapper.grid(row=3, column=0, columnspan=2, sticky="ew", pady=4)
    owner_label = tk.Label(
        owner_wrapper,
        text="Сведения о юридическом лице – источнике финансирования:",
        font=("Arial", 9, "bold"),
    )
    owner_label.pack(anchor="w")
    owner_ui = create_technical_customer_ui(owner_wrapper)

    row_data = {
        "frame": block,
        "var_finance_type": var_finance_type,
        "var_budget_type": var_budget_type,
        "entry_finance_size": entry_finance_size,
        "owner_wrapper": owner_wrapper,
        "owner_ui": owner_ui,
        "combo_budget_type": combo_budget_type,
    }

    def update_finance_fields(*_args):
        finance_type = get_option_value(FINANCE_TYPE_OPTIONS, var_finance_type)
        if finance_type == "1":
            combo_budget_type.config(state="readonly")
            owner_wrapper.grid()
        elif finance_type == "2":
            combo_budget_type.set(NOT_SPECIFIED)
            combo_budget_type.config(state="disabled")
            owner_wrapper.grid()
        else:
            combo_budget_type.set(NOT_SPECIFIED)
            combo_budget_type.config(state="disabled")
            owner_wrapper.grid_remove()

    var_finance_type.trace_add("write", update_finance_fields)
    update_finance_fields()

    def remove_block():
        if len(rows_list) <= 1:
            messagebox.showwarning("Ошибка", "Должен остаться хотя бы один источник финансирования!")
            return
        rows_list.remove(row_data)
        block.destroy()
        for idx, item in enumerate(rows_list, start=1):
            item["frame"].config(text=f"Источник финансирования {idx}")

    tk.Button(block, text="Удалить", command=remove_block).grid(
        row=4, column=1, sticky="w", pady=8
    )
    rows_list.append(row_data)


def collect_finance_data(row):
    finance_type = get_option_value(FINANCE_TYPE_OPTIONS, row["var_finance_type"])
    budget_type = get_option_value(BUDGET_TYPE_OPTIONS, row["var_budget_type"])
    finance_size = row["entry_finance_size"].get().strip()
    owner = None
    if finance_type in ("1", "2"):
        owner_data = collect_technical_customer_data(row["owner_ui"])
        if is_technical_customer_filled(owner_data):
            owner = owner_data
    return {
        "finance_type": finance_type,
        "budget_type": budget_type,
        "finance_size": finance_size,
        "owner": owner,
    }


def validate_finance_data(data, index):
    if not data["finance_type"]:
        return f"Укажите вид источника финансирования {index}!"

    finance_type = data["finance_type"]
    if finance_type in ("1", "2"):
        if not data["finance_size"]:
            return f"Укажите размер финансирования для источника {index}!"
        try:
            float(data["finance_size"].replace(",", "."))
        except ValueError:
            return f"Некорректный размер финансирования для источника {index}!"

    if finance_type == "1":
        if not data["budget_type"]:
            return f"Укажите уровень бюджета для источника {index}!"
        if data.get("owner"):
            return validate_technical_customer_data(
                data["owner"],
                f"источник финансирования {index}",
            )
        return None

    if finance_type == "2":
        if not data.get("owner"):
            return f"Укажите сведения о юридическом лице – источнике финансирования {index}!"
        return validate_technical_customer_data(
            data["owner"],
            f"источник финансирования {index}",
        )

    return None


def append_finance_xml(conclusion, items):
    for item in items:
        finance = ET.SubElement(conclusion, 'Finance')
        ET.SubElement(finance, 'FinanceType').text = item["finance_type"]
        if item.get("budget_type"):
            ET.SubElement(finance, 'BudgetType').text = item["budget_type"]
        if item.get("finance_size"):
            ET.SubElement(finance, 'FinanceSize').text = item["finance_size"].replace(",", ".")
        if item.get("owner"):
            owner_elem = ET.SubElement(finance, 'FinanceOwner')
            append_technical_customer_xml(owner_elem, item["owner"])


def validate_estimated_sum(value, label):
    if not value:
        return f"Укажите значение: {label}!"
    if not ESTIMATED_SUM_RE.match(value):
        return (
            f"Некорректное значение ({label})! "
            f"Допустимо: число, «Не требуется» или «Отсутствует»."
        )
    return None


def create_complex_cost_form(parent, title):
    frame = tk.LabelFrame(parent, text=title, padx=6, pady=6)
    frame.pack(fill="x", pady=4)
    entries = {}
    row_idx = 0
    for label_text, key in COMPLEX_ESTIMATED_COST_FIELDS:
        tk.Label(frame, text=label_text).grid(row=row_idx, column=0, sticky="w", pady=2)
        entry = tk.Entry(frame, width=30)
        entry.grid(row=row_idx, column=1, sticky="w", pady=2, padx=(4, 0))
        entries[key] = entry
        row_idx += 1
    for label_text, key in OPTIONAL_COMPLEX_COST_COMMENT_FIELDS:
        tk.Label(frame, text=label_text).grid(row=row_idx, column=0, sticky="w", pady=2)
        entry = tk.Entry(frame, width=55)
        entry.grid(row=row_idx, column=1, sticky="w", pady=2, padx=(4, 0))
        entries[key] = entry
        row_idx += 1
    return frame, entries


def collect_complex_cost_data(entries):
    data = {}
    for _, key in COMPLEX_ESTIMATED_COST_FIELDS:
        data[key] = entries[key].get().strip()
    for _, key in OPTIONAL_COMPLEX_COST_COMMENT_FIELDS:
        data[key] = entries[key].get().strip()
    return data


def is_complex_cost_filled(data):
    required_keys = [key for _, key in COMPLEX_ESTIMATED_COST_FIELDS]
    return any(data.get(key) for key in required_keys) or any(
        data.get(key) for _, key in OPTIONAL_COMPLEX_COST_COMMENT_FIELDS
    )


def validate_complex_cost_data(data, label):
    for field_label, key in COMPLEX_ESTIMATED_COST_FIELDS:
        error = validate_estimated_sum(data.get(key, ""), f"{label} — {field_label}")
        if error:
            return error
    return None


def append_complex_cost_xml(parent_elem, data):
    for _, key in COMPLEX_ESTIMATED_COST_FIELDS:
        ET.SubElement(parent_elem, key).text = data[key]
    for _, key in OPTIONAL_COMPLEX_COST_COMMENT_FIELDS:
        if data.get(key):
            ET.SubElement(parent_elem, key).text = data[key]


def collect_estimated_cost_data():
    currency = entry_estimated_currency.get().strip()
    mode = var_estimated_cost_mode.get()
    complete_before = entry_complete_cost_before.get().strip()
    complete_post = entry_complete_cost_post.get().strip()
    complex_before = collect_complex_cost_data(complex_cost_before_entries)
    complex_post = collect_complex_cost_data(complex_cost_post_entries)
    return {
        "currency": currency,
        "mode": mode,
        "complete_before": complete_before,
        "complete_post": complete_post,
        "complex_before": complex_before,
        "complex_post": complex_post,
    }


def is_estimated_cost_filled(data):
    if data["currency"]:
        return True
    if data["mode"] == "complete":
        return bool(data["complete_before"] or data["complete_post"])
    return is_complex_cost_filled(data["complex_before"]) or is_complex_cost_filled(
        data["complex_post"]
    )


def validate_estimated_cost_data(data):
    if not is_estimated_cost_filled(data):
        return None

    if data["mode"] == "complete":
        error = validate_estimated_sum(
            data["complete_before"],
            "Сметная стоимость на дату представления документации",
        )
        if error:
            return error
        return validate_estimated_sum(
            data["complete_post"],
            "Сметная стоимость на дату утверждения заключения",
        )

    if not is_complex_cost_filled(data["complex_before"]):
        return (
            "Заполните сведения о сметной стоимости на дату представления документации "
            "(составное значение)!"
        )
    if not is_complex_cost_filled(data["complex_post"]):
        return (
            "Заполните сведения о сметной стоимости по результатам проверки "
            "достоверности (составное значение)!"
        )
    error = validate_complex_cost_data(
        data["complex_before"],
        "на дату представления документации",
    )
    if error:
        return error
    return validate_complex_cost_data(
        data["complex_post"],
        "по результатам проверки достоверности",
    )


def create_designer_entity_ui(parent):
    container = tk.Frame(parent)
    container.pack(fill="x", pady=4)

    var_type = tk.StringVar(value="organization")
    type_frame = tk.Frame(container)
    type_frame.pack(fill="x", pady=(0, 4))
    panels = {}

    def switch_panel():
        selected = var_type.get()
        for key, panel in panels.items():
            if key == selected:
                panel.pack(fill="x", pady=4)
            else:
                panel.pack_forget()

    for value, label in DESIGNER_TYPE_OPTIONS:
        tk.Radiobutton(
            type_frame,
            text=label,
            variable=var_type,
            value=value,
            command=switch_panel,
            anchor="w",
            wraplength=650,
            justify="left",
        ).pack(fill="x", pady=1)

    details_frame = tk.Frame(container)
    details_frame.pack(fill="x")

    org_panel = tk.Frame(details_frame)
    _, org_entries = create_inline_form(
        org_panel,
        [
            ("Полное наименование юридического лица:", "org_full_name"),
            ("ОГРН:", "org_ogrn"),
            ("ИНН:", "org_inn"),
            ("КПП:", "org_kpp"),
        ],
    )
    _, org_address_entries = create_inline_form(
        org_panel,
        CAPITAL_OBJECT_ADDRESS_FIELDS,
        title="Адрес (местонахождение) юридического лица",
    )
    tk.Label(org_panel, text="Адрес электронной почты:").pack(anchor="w", pady=(4, 0))
    org_email = tk.Entry(org_panel, width=60)
    org_email.pack(anchor="w", pady=(2, 4))
    panels["organization"] = org_panel

    foreign_panel = tk.Frame(details_frame)
    _, foreign_entries = create_inline_form(
        foreign_panel,
        [
            ("Полное наименование:", "org_full_name"),
            ("ИНН:", "org_inn"),
            ("КПП:", "org_kpp"),
        ],
    )
    _, foreign_address_entries = create_inline_form(
        foreign_panel,
        CAPITAL_OBJECT_ADDRESS_FIELDS,
        title="Адрес (местонахождение) филиала или представительства",
    )
    tk.Label(foreign_panel, text="Адрес электронной почты:").pack(anchor="w", pady=(4, 0))
    foreign_email = tk.Entry(foreign_panel, width=60)
    foreign_email.pack(anchor="w", pady=(2, 4))
    panels["foreign_organization"] = foreign_panel

    ip_panel = tk.Frame(details_frame)
    _, ip_entries = create_inline_form(
        ip_panel,
        [
            ("Фамилия:", "family_name"),
            ("Имя:", "first_name"),
            ("Отчество:", "second_name"),
            ("ОГРНИП:", "ogrnip"),
        ],
    )
    _, ip_post_address_entries = create_inline_form(
        ip_panel,
        POST_ADDRESS_FIELDS,
        title="Почтовый адрес индивидуального предпринимателя",
    )
    tk.Label(ip_panel, text="Адрес электронной почты:").pack(anchor="w", pady=(4, 0))
    ip_email = tk.Entry(ip_panel, width=60)
    ip_email.pack(anchor="w", pady=(2, 4))
    panels["ip"] = ip_panel

    switch_panel()

    return {
        "var_type": var_type,
        "organization": {
            "entries": org_entries,
            "address": org_address_entries,
            "email": org_email,
        },
        "foreign_organization": {
            "entries": foreign_entries,
            "address": foreign_address_entries,
            "email": foreign_email,
        },
        "ip": {
            "entries": ip_entries,
            "post_address": ip_post_address_entries,
            "email": ip_email,
        },
    }


def collect_designer_entity_data(ui):
    entity_type = ui["var_type"].get()
    address_keys = [key for _, key in CAPITAL_OBJECT_ADDRESS_FIELDS]
    post_address_keys = [key for _, key in POST_ADDRESS_FIELDS]

    if entity_type == "organization":
        data = collect_inline_form(ui["organization"]["entries"], [
            "org_full_name", "org_ogrn", "org_inn", "org_kpp",
        ])
        data["address"] = collect_inline_form(ui["organization"]["address"], address_keys)
        data["email"] = ui["organization"]["email"].get().strip()
        data["type"] = entity_type
        return data

    if entity_type == "foreign_organization":
        data = collect_inline_form(ui["foreign_organization"]["entries"], [
            "org_full_name", "org_inn", "org_kpp",
        ])
        data["address"] = collect_inline_form(
            ui["foreign_organization"]["address"], address_keys
        )
        data["email"] = ui["foreign_organization"]["email"].get().strip()
        data["type"] = entity_type
        return data

    data = collect_inline_form(ui["ip"]["entries"], [
        "family_name", "first_name", "second_name", "ogrnip",
    ])
    data["post_address"] = collect_inline_form(ui["ip"]["post_address"], post_address_keys)
    data["email"] = ui["ip"]["email"].get().strip()
    data["type"] = entity_type
    return data


def is_designer_entity_filled(data):
    if data["type"] == "organization":
        keys = ("org_full_name", "org_ogrn", "org_inn", "org_kpp", "email")
    elif data["type"] == "foreign_organization":
        keys = ("org_full_name", "org_inn", "org_kpp", "email")
    else:
        keys = ("family_name", "first_name", "ogrnip", "email")
    if any(data.get(key) for key in keys):
        return True
    if data["type"] == "ip":
        return any(data.get("post_address", {}).values())
    return any(data.get("address", {}).values())


def validate_designer_entity_data(data, index):
    label = f"проектировщик {index}"
    email = data.get("email", "")
    if email and not EMAIL_RE.match(email):
        return f"Некорректный адрес электронной почты ({label})!"

    if data["type"] == "organization":
        if not data["org_full_name"]:
            return f"Укажите полное наименование юридического лица ({label})!"
        if not data["org_ogrn"]:
            return f"Укажите ОГРН ({label})!"
        if not ORG_OGRN_RE.match(data["org_ogrn"]):
            return f"Некорректный ОГРН ({label})! Должно быть 13 цифр."
        if not data["org_inn"]:
            return f"Укажите ИНН ({label})!"
        if not ORG_INN_RE.match(data["org_inn"]):
            return f"Некорректный ИНН ({label})! Должно быть 10 цифр."
        if not data["org_kpp"]:
            return f"Укажите КПП ({label})!"
        if not ORG_KPP_RE.match(data["org_kpp"]):
            return f"Некорректный КПП ({label})! Должно быть 9 цифр."
        return validate_address_data(data["address"], label)

    if data["type"] == "foreign_organization":
        if not data["org_full_name"]:
            return f"Укажите полное наименование иностранного юридического лица ({label})!"
        if not data["org_inn"]:
            return f"Укажите ИНН ({label})!"
        if not ORG_INN_RE.match(data["org_inn"]):
            return f"Некорректный ИНН ({label})! Должно быть 10 цифр."
        if not data["org_kpp"]:
            return f"Укажите КПП ({label})!"
        if not ORG_KPP_RE.match(data["org_kpp"]):
            return f"Некорректный КПП ({label})! Должно быть 9 цифр."
        return validate_address_data(data["address"], label)

    if not data["family_name"]:
        return f"Укажите фамилию индивидуального предпринимателя ({label})!"
    if not data["first_name"]:
        return f"Укажите имя индивидуального предпринимателя ({label})!"
    if not data["ogrnip"]:
        return f"Укажите ОГРНИП ({label})!"
    if not OGRNIP_RE.match(data["ogrnip"]):
        return "Некорректный ОГРНИП! Должно быть 15 цифр."
    return validate_post_address_data(data["post_address"], label)


def append_designer_entity_xml(parent_elem, data):
    if data["type"] == "organization":
        append_organization_xml(parent_elem, 'Organization', data)
    elif data["type"] == "foreign_organization":
        append_organization_xml(parent_elem, 'ForeignOrganization', data)
    else:
        append_ip_xml(parent_elem, data)


def add_designer_block(container, rows_list):
    index = len(rows_list) + 1
    block = tk.LabelFrame(
        container,
        text=f"Проектировщик {index}",
        padx=8,
        pady=8,
    )
    block.pack(fill="x", pady=8, padx=4)

    entity_ui = create_designer_entity_ui(block)

    tk.Label(
        block,
        text="Отметка о роли генерального проектировщика:",
    ).pack(anchor="w", pady=(8, 0))
    combo_general, var_general = create_combobox(block, IM_OPTIONS)
    combo_general.pack(anchor="w", pady=(2, 4))

    row_data = {
        "frame": block,
        "entity_ui": entity_ui,
        "var_general": var_general,
    }

    def remove_block():
        rows_list.remove(row_data)
        block.destroy()
        for idx, item in enumerate(rows_list, start=1):
            item["frame"].config(text=f"Проектировщик {idx}")

    tk.Button(block, text="Удалить", command=remove_block).pack(anchor="w", pady=8)
    rows_list.append(row_data)


def collect_designer_row_data(row):
    data = collect_designer_entity_data(row["entity_ui"])
    data["general"] = get_option_value(IM_OPTIONS, row["var_general"])
    return data


def append_designers_xml(conclusion, items):
    for item in items:
        designer = ET.SubElement(conclusion, 'Designer')
        if item.get("general"):
            designer.set('General', item["general"])
        append_designer_entity_xml(designer, item)


EGRZ_NUMBER_PATTERN = re.compile(
    r'^[0-9]{2}-[1-2]{1}-[1-2]{1}-[1-3]{1}-[0-9]{6}-[0-9]{4}$'
)


def add_eepd_use_block(container, rows_list, default_values=None):
    default_values = default_values or {}
    index = len(rows_list) + 1
    block = tk.LabelFrame(
        container,
        text=f"Использование типовой проектной документации {index}",
        padx=8,
        pady=8,
    )
    block.pack(fill="x", pady=8, padx=4)

    tk.Label(
        block,
        text="Сведения о разделах, которые не подвергались изменению\n"
        "и полностью соответствуют ЭПД повторного использования:",
        justify="left",
    ).pack(anchor="w", pady=(0, 4))
    entry_note = tk.Entry(block, width=80)
    entry_note.pack(anchor="w", pady=(0, 8))
    if default_values.get("note"):
        entry_note.insert(0, default_values["note"])

    number_frame = tk.LabelFrame(
        block,
        text="Номер заключения экспертизы в отношении использованной ЭПД",
        padx=8,
        pady=8,
    )
    number_frame.pack(fill="x", pady=4)

    var_number_format = tk.StringVar(value=default_values.get("number_format", "egrz"))
    tk.Radiobutton(
        number_frame,
        text="Номер заключения экспертизы в формате ЕГРЗ",
        variable=var_number_format,
        value="egrz",
    ).pack(anchor="w")
    tk.Radiobutton(
        number_frame,
        text="Номер заключения экспертизы в произвольном формате",
        variable=var_number_format,
        value="noegrz",
    ).pack(anchor="w")

    entry_number = tk.Entry(number_frame, width=60)
    entry_number.pack(anchor="w", pady=(4, 0))
    if default_values.get("number"):
        entry_number.insert(0, default_values["number"])

    date_frame = tk.Frame(block)
    date_frame.pack(fill="x", pady=8)
    tk.Label(
        date_frame,
        text="Дата утверждения заключения экспертизы (ДД.ММ.ГГГГ):",
    ).pack(side="left")
    entry_date = tk.Entry(date_frame, width=20)
    entry_date.pack(side="left", padx=(8, 0))
    if default_values.get("date"):
        entry_date.insert(0, default_values["date"])

    row_data = {
        "frame": block,
        "entry_note": entry_note,
        "entry_number": entry_number,
        "var_number_format": var_number_format,
        "entry_date": entry_date,
    }

    def remove_block():
        rows_list.remove(row_data)
        block.destroy()
        for idx, item in enumerate(rows_list, start=1):
            item["frame"].config(
                text=f"Использование типовой проектной документации {idx}"
            )

    tk.Button(block, text="Удалить", command=remove_block).pack(anchor="w", pady=8)
    rows_list.append(row_data)


def collect_eepd_use_data(row):
    return {
        "note": row["entry_note"].get().strip(),
        "number": row["entry_number"].get().strip(),
        "number_format": row["var_number_format"].get(),
        "date": format_doc_date(row["entry_date"].get()),
    }


def is_eepd_use_filled(data):
    return any([data["note"], data["number"], data["date"]])


def validate_eepd_use_data(data, index):
    if not data["note"]:
        return f"Укажите сведения о разделах для блока ЭПД повторного использования {index}!"
    if not data["number"]:
        return (
            f"Укажите номер заключения экспертизы для блока ЭПД повторного использования {index}!"
        )
    if data["number_format"] == "egrz" and not EGRZ_NUMBER_PATTERN.fullmatch(data["number"]):
        return (
            f"Номер ЕГРЗ для блока ЭПД повторного использования {index} "
            "должен быть в формате XX-X-X-X-XXXXXX-XXXX!"
        )
    if data["number_format"] == "noegrz" and len(data["number"]) > 50:
        return (
            f"Номер в произвольном формате для блока ЭПД повторного использования {index} "
            "не должен превышать 50 символов!"
        )
    if not data["date"]:
        return (
            f"Укажите дату утверждения заключения для блока ЭПД повторного использования {index}!"
        )
    return ""


def append_eepd_use_xml(conclusion, items):
    for item in items:
        eepd_use = ET.SubElement(conclusion, 'EEPDUse')
        ET.SubElement(eepd_use, 'EEPDNote').text = item["note"]
        number_elem = ET.SubElement(eepd_use, 'EEPDNumber')
        if item["number_format"] == "egrz":
            ET.SubElement(number_elem, 'EGRZ').text = item["number"]
        else:
            ET.SubElement(number_elem, 'noEGRZ').text = item["number"]
        ET.SubElement(eepd_use, 'EEPDDate').text = item["date"]


def add_engineering_survey_address_block(container, rows_list, default_values=None):
    default_values = default_values or {}
    index = len(rows_list) + 1
    block = tk.LabelFrame(
        container,
        text=f"Местоположение района изысканий {index}",
        padx=8,
        pady=8,
    )
    block.pack(fill="x", pady=8, padx=4)

    tk.Label(block, text="Код субъекта Российской Федерации:").pack(anchor="w", pady=(0, 4))
    combo_region, var_region = create_combobox(
        block,
        REGION_RF_OPTIONS,
        default_values.get("region_label", NOT_SPECIFIED),
    )
    combo_region.pack(anchor="w", pady=(0, 8))

    tk.Label(
        block,
        text="Описание района изысканий (наименование муниципального района):",
        justify="left",
    ).pack(anchor="w", pady=(0, 4))
    text_district = tk.Text(block, width=80, height=3)
    text_district.pack(anchor="w", pady=(0, 8))
    if default_values.get("district"):
        text_district.insert("1.0", default_values["district"])

    row_data = {
        "frame": block,
        "var_region": var_region,
        "text_district": text_district,
    }

    def remove_block():
        rows_list.remove(row_data)
        block.destroy()
        for idx, item in enumerate(rows_list, start=1):
            item["frame"].config(text=f"Местоположение района изысканий {idx}")

    tk.Button(block, text="Удалить", command=remove_block).pack(anchor="w", pady=8)
    rows_list.append(row_data)


def collect_engineering_survey_address_data(row):
    return {
        "region": get_option_value(REGION_RF_OPTIONS, row["var_region"]),
        "district": row["text_district"].get("1.0", "end").strip(),
    }


def is_engineering_survey_address_filled(data):
    return any([data["region"], data["district"]])


def validate_engineering_survey_address_data(data, index):
    if not data["region"]:
        return f"Укажите код субъекта РФ для местоположения района изысканий {index}!"
    if not data["district"]:
        return f"Укажите описание района изысканий {index}!"
    if len(data["district"]) > 1000:
        return f"Описание района изысканий {index} не должно превышать 1000 символов!"
    return ""


def append_engineering_survey_addresses_xml(conclusion, items):
    for item in items:
        address = ET.SubElement(conclusion, 'EngineeringSurveyAddress')
        ET.SubElement(address, 'EngineeringSurveyRegion').text = item["region"]
        ET.SubElement(address, 'EngineeringSurveyDistrict').text = item["district"]


def add_mismatch_block(parent, rows_list, block_title, default_values=None):
    default_values = default_values or {}
    index = len(rows_list) + 1
    block = tk.LabelFrame(
        parent,
        text=f"{block_title} {index}",
        padx=8,
        pady=8,
    )
    block.pack(fill="x", pady=6, padx=4)

    fields = [
        ("summary", "Вывод о несоответствии:"),
        ("part", "Ссылка на материалы:"),
        ("link", "Ссылка на конкретное требование:"),
    ]
    text_widgets = {}
    for key, label in fields:
        tk.Label(block, text=label, justify="left").pack(anchor="w", pady=(4, 2))
        text_widget = tk.Text(block, width=80, height=2)
        text_widget.pack(anchor="w", pady=(0, 4))
        if default_values.get(key):
            text_widget.insert("1.0", default_values[key])
        text_widgets[key] = text_widget

    row_data = {"frame": block, "text_widgets": text_widgets, "block_title": block_title}

    def remove_block():
        rows_list.remove(row_data)
        block.destroy()
        for idx, item in enumerate(rows_list, start=1):
            item["frame"].config(text=f"{block_title} {idx}")

    tk.Button(block, text="Удалить", command=remove_block).pack(anchor="w", pady=4)
    rows_list.append(row_data)


def collect_mismatch_data(row):
    return {
        key: row["text_widgets"][key].get("1.0", "end").strip()
        for key in ("summary", "part", "link")
    }


def is_mismatch_filled(data):
    return any(data.values())


def is_mismatch_complete(data):
    return all(data.values())


def collect_filled_mismatches(rows_list):
    mismatches = []
    for row in rows_list:
        mismatch_data = collect_mismatch_data(row)
        if is_mismatch_filled(mismatch_data):
            mismatches.append(mismatch_data)
    return mismatches


def validate_mismatch_rows(rows_list, section_label, block_index, block_label):
    for mismatch_idx, mismatch_row in enumerate(rows_list, start=1):
        mismatch_data = collect_mismatch_data(mismatch_row)
        if is_mismatch_filled(mismatch_data) and not is_mismatch_complete(mismatch_data):
            return (
                f"Заполните все поля несоответствия {mismatch_idx} "
                f"({section_label}) в блоке экспертизы {block_label} {block_index}!"
            )
    return ""


def append_mismatch_xml(parent_elem, tag_name, mismatch):
    elem = ET.SubElement(parent_elem, tag_name)
    ET.SubElement(elem, 'Summary').text = mismatch["summary"]
    ET.SubElement(elem, 'Part').text = mismatch["part"]
    ET.SubElement(elem, 'Link').text = mismatch["link"]


def add_expert_engineering_surveys_block(container, rows_list, default_values=None):
    default_values = default_values or {}
    index = len(rows_list) + 1
    block = tk.LabelFrame(
        container,
        text=f"Экспертиза инженерных изысканий {index}",
        padx=8,
        pady=8,
    )
    block.pack(fill="x", pady=8, padx=4)

    mismatches_frame = tk.LabelFrame(
        block,
        text="Сведения о несоответствии результатов инженерных изысканий\n"
        "требованиям технических регламентов",
        padx=8,
        pady=8,
    )
    mismatches_frame.pack(fill="x", pady=4)

    norms_rows = []
    norms_container = tk.Frame(mismatches_frame)
    norms_container.pack(fill="x")

    def add_norms_mismatch():
        mismatch_defaults = {}
        if len(norms_rows) == 0 and default_values.get("norms_mismatch"):
            mismatch_defaults = default_values["norms_mismatch"]
        add_mismatch_block(
            norms_container,
            norms_rows,
            "Несоответствие требованиям техрегламентов",
            mismatch_defaults,
        )

    tk.Button(
        mismatches_frame,
        text="+ Добавить несоответствие",
        command=add_norms_mismatch,
    ).pack(anchor="w", pady=4)

    if default_values.get("norms_mismatch"):
        add_norms_mismatch()

    tk.Label(block, text="Вид инженерных изысканий:").pack(anchor="w", pady=(8, 4))
    combo_type, var_type = create_combobox(
        block,
        ENGINEERING_SURVEY_TYPE_OPTIONS,
        default_values.get("survey_type_label", NOT_SPECIFIED),
    )
    combo_type.pack(anchor="w", pady=(0, 8))

    row_data = {
        "frame": block,
        "norms_rows": norms_rows,
        "var_type": var_type,
    }

    def remove_block():
        rows_list.remove(row_data)
        block.destroy()
        for idx, item in enumerate(rows_list, start=1):
            item["frame"].config(text=f"Экспертиза инженерных изысканий {idx}")

    tk.Button(block, text="Удалить блок", command=remove_block).pack(anchor="w", pady=8)
    rows_list.append(row_data)


def collect_expert_engineering_surveys_data(row):
    return {
        "survey_type": get_option_value(ENGINEERING_SURVEY_TYPE_OPTIONS, row["var_type"]),
        "norms_mismatches": collect_filled_mismatches(row["norms_rows"]),
    }


def is_expert_engineering_surveys_filled(data):
    return bool(data["survey_type"]) or bool(data["norms_mismatches"])


def validate_expert_engineering_surveys_row(row, index):
    data = collect_expert_engineering_surveys_data(row)
    if not data["survey_type"]:
        return f"Укажите вид инженерных изысканий для блока экспертизы {index}!"
    return validate_mismatch_rows(
        row["norms_rows"],
        "несоответствие требованиям техрегламентов",
        index,
        "инженерных изысканий",
    )


def append_expert_engineering_surveys_xml(conclusion, items):
    for item in items:
        expert_surveys = ET.SubElement(conclusion, 'ExpertEngineeringSurveys')
        expert_surveys.set('EngineeringSurveyType', item["survey_type"])
        if item["norms_mismatches"]:
            mismatches = ET.SubElement(expert_surveys, 'Mismatches')
            for mismatch in item["norms_mismatches"]:
                append_mismatch_xml(mismatches, 'NormsMismatch', mismatch)


def _add_project_mismatch_section(parent, title, rows_list, default_values=None):
    section = tk.LabelFrame(parent, text=title, padx=8, pady=8)
    section.pack(fill="x", pady=4)
    container = tk.Frame(section)
    container.pack(fill="x")

    def add_item():
        item_defaults = default_values if len(rows_list) == 0 and default_values else None
        add_mismatch_block(container, rows_list, title, item_defaults)

    tk.Button(section, text="+ Добавить", command=add_item).pack(anchor="w", pady=4)
    if default_values:
        add_item()
    return container


def add_expert_project_documents_block(container, rows_list, default_values=None):
    default_values = default_values or {}
    index = len(rows_list) + 1
    block = tk.LabelFrame(
        container,
        text=f"Экспертиза проектной документации {index}",
        padx=8,
        pady=8,
    )
    block.pack(fill="x", pady=8, padx=4)

    tk.Label(
        block,
        text="Сведения о решениях, приведённых в соответствие в ходе экспертизы:",
        justify="left",
    ).pack(anchor="w", pady=(0, 4))
    entry_danger_solutions = tk.Entry(block, width=80)
    entry_danger_solutions.pack(anchor="w", pady=(0, 8))
    if default_values.get("danger_solutions"):
        entry_danger_solutions.insert(0, default_values["danger_solutions"])

    mismatches_frame = tk.LabelFrame(
        block,
        text="Сведения о несоответствии проектной документации установленным требованиям",
        padx=8,
        pady=8,
    )
    mismatches_frame.pack(fill="x", pady=4)

    engineering_rows = []
    project_task_rows = []
    norms_rows = []
    _add_project_mismatch_section(
        mismatches_frame,
        "Несоответствие результату инженерных изысканий",
        engineering_rows,
        default_values.get("engineering_survey_mismatch"),
    )
    _add_project_mismatch_section(
        mismatches_frame,
        "Несоответствие заданию на проектирование",
        project_task_rows,
        default_values.get("project_task_mismatch"),
    )
    _add_project_mismatch_section(
        mismatches_frame,
        "Несоответствие требованиям технических регламентов",
        norms_rows,
        default_values.get("norms_mismatch"),
    )

    tk.Label(
        mismatches_frame,
        text="Описание опасного решения (DangerMismatch):",
        justify="left",
    ).pack(anchor="w", pady=(8, 4))
    entry_danger_mismatch = tk.Entry(mismatches_frame, width=80)
    entry_danger_mismatch.pack(anchor="w", pady=(0, 8))
    if default_values.get("danger_mismatch"):
        entry_danger_mismatch.insert(0, default_values["danger_mismatch"])

    tk.Label(
        block,
        text="Направление деятельности в области экспертизы проектной документации:",
    ).pack(anchor="w", pady=(8, 4))
    combo_expert_type, var_expert_type = create_combobox(
        block,
        EXPERT_TYPE_OPTIONS,
        default_values.get("expert_type_label", NOT_SPECIFIED),
    )
    combo_expert_type.pack(anchor="w", pady=(0, 8))

    row_data = {
        "frame": block,
        "entry_danger_solutions": entry_danger_solutions,
        "engineering_rows": engineering_rows,
        "project_task_rows": project_task_rows,
        "norms_rows": norms_rows,
        "entry_danger_mismatch": entry_danger_mismatch,
        "var_expert_type": var_expert_type,
    }

    def remove_block():
        rows_list.remove(row_data)
        block.destroy()
        for idx, item in enumerate(rows_list, start=1):
            item["frame"].config(text=f"Экспертиза проектной документации {idx}")

    tk.Button(block, text="Удалить блок", command=remove_block).pack(anchor="w", pady=8)
    rows_list.append(row_data)


def collect_expert_project_documents_data(row):
    engineering_mismatches = collect_filled_mismatches(row["engineering_rows"])
    project_task_mismatches = collect_filled_mismatches(row["project_task_rows"])
    norms_mismatches = collect_filled_mismatches(row["norms_rows"])
    danger_mismatch = row["entry_danger_mismatch"].get().strip()
    return {
        "expert_type": get_option_value(EXPERT_TYPE_OPTIONS, row["var_expert_type"]),
        "danger_solutions": row["entry_danger_solutions"].get().strip(),
        "engineering_survey_mismatches": engineering_mismatches,
        "project_task_mismatches": project_task_mismatches,
        "norms_mismatches": norms_mismatches,
        "danger_mismatch": danger_mismatch,
    }


def is_expert_project_documents_filled(data):
    return any([
        data["expert_type"],
        data["danger_solutions"],
        data["engineering_survey_mismatches"],
        data["project_task_mismatches"],
        data["norms_mismatches"],
        data["danger_mismatch"],
    ])


def has_project_documents_mismatches_content(data):
    return any([
        data["engineering_survey_mismatches"],
        data["project_task_mismatches"],
        data["norms_mismatches"],
        data["danger_mismatch"],
    ])


def validate_expert_project_documents_row(row, index):
    data = collect_expert_project_documents_data(row)
    if not data["expert_type"]:
        return f"Укажите направление деятельности для блока экспертизы проектной документации {index}!"
    for section_label, section_rows in [
        ("несоответствие результату инженерных изысканий", row["engineering_rows"]),
        ("несоответствие заданию на проектирование", row["project_task_rows"]),
        ("несоответствие требованиям технических регламентов", row["norms_rows"]),
    ]:
        section_error = validate_mismatch_rows(
            section_rows,
            section_label,
            index,
            "проектной документации",
        )
        if section_error:
            return section_error
    if has_project_documents_mismatches_content(data):
        if not any([
            data["engineering_survey_mismatches"],
            data["project_task_mismatches"],
            data["norms_mismatches"],
        ]):
            return (
                f"В блоке экспертизы проектной документации {index} укажите хотя бы одно "
                "несоответствие (изыскания, задание или техрегламенты)!"
            )
    return ""


def append_expert_project_documents_xml(conclusion, items):
    for item in items:
        expert_docs = ET.SubElement(conclusion, 'ExpertProjectDocuments')
        expert_docs.set('ExpertType', item["expert_type"])
        if item["danger_solutions"]:
            ET.SubElement(expert_docs, 'DangerSolutions').text = item["danger_solutions"]
        if has_project_documents_mismatches_content(item):
            mismatches = ET.SubElement(expert_docs, 'Mismatches')
            for mismatch in item["engineering_survey_mismatches"]:
                append_mismatch_xml(mismatches, 'EngineeringSurveyMismatch', mismatch)
            for mismatch in item["project_task_mismatches"]:
                append_mismatch_xml(mismatches, 'ProjectTaskMismatch', mismatch)
            for mismatch in item["norms_mismatches"]:
                append_mismatch_xml(mismatches, 'NormsMismatch', mismatch)
            if item["danger_mismatch"]:
                ET.SubElement(mismatches, 'DangerMismatch').text = item["danger_mismatch"]


def add_mismatch_extended_block(parent, rows_list, block_title, default_values=None):
    default_values = default_values or {}
    index = len(rows_list) + 1
    block = tk.LabelFrame(
        parent,
        text=f"{block_title} {index}",
        padx=8,
        pady=8,
    )
    block.pack(fill="x", pady=6, padx=4)

    fields = [
        ("summary", "Вывод о несоответствии:"),
        ("part", "Ссылка на материалы:"),
        ("link", "Ссылка на конкретное требование:"),
    ]
    text_widgets = {}
    for key, label in fields:
        tk.Label(block, text=label, justify="left").pack(anchor="w", pady=(4, 2))
        text_widget = tk.Text(block, width=80, height=2)
        text_widget.pack(anchor="w", pady=(0, 4))
        if default_values.get(key):
            text_widget.insert("1.0", default_values[key])
        text_widgets[key] = text_widget

    tk.Label(
        block,
        text="Направление деятельности, в части которого сформулированы сведения:",
        justify="left",
    ).pack(anchor="w", pady=(4, 2))
    combo_expert_type, var_expert_type = create_combobox(
        block,
        EXPERT_TYPE_OPTIONS,
        default_values.get("expert_type_label", NOT_SPECIFIED),
    )
    combo_expert_type.pack(anchor="w", pady=(0, 4))

    row_data = {
        "frame": block,
        "text_widgets": text_widgets,
        "var_expert_type": var_expert_type,
        "block_title": block_title,
    }

    def remove_block():
        rows_list.remove(row_data)
        block.destroy()
        for idx, item in enumerate(rows_list, start=1):
            item["frame"].config(text=f"{block_title} {idx}")

    tk.Button(block, text="Удалить", command=remove_block).pack(anchor="w", pady=4)
    rows_list.append(row_data)


def collect_mismatch_extended_data(row):
    data = collect_mismatch_data(row)
    data["expert_type"] = get_option_value(EXPERT_TYPE_OPTIONS, row["var_expert_type"])
    return data


def is_mismatch_extended_filled(data):
    return is_mismatch_filled(data) or bool(data.get("expert_type"))


def is_mismatch_extended_complete(data):
    return is_mismatch_complete(data) and bool(data.get("expert_type"))


def collect_filled_extended_mismatches(rows_list):
    mismatches = []
    for row in rows_list:
        mismatch_data = collect_mismatch_extended_data(row)
        if is_mismatch_extended_filled(mismatch_data):
            mismatches.append(mismatch_data)
    return mismatches


def validate_mismatch_extended_rows(rows_list, section_label, block_label):
    for mismatch_idx, mismatch_row in enumerate(rows_list, start=1):
        mismatch_data = collect_mismatch_extended_data(mismatch_row)
        if is_mismatch_extended_filled(mismatch_data) and not is_mismatch_extended_complete(mismatch_data):
            return (
                f"Заполните все поля несоответствия {mismatch_idx} "
                f"({section_label}) в блоке {block_label}, включая направление деятельности!"
            )
    return ""


def append_mismatch_extended_xml(parent_elem, tag_name, mismatch):
    elem = ET.SubElement(parent_elem, tag_name)
    elem.set('ExpertType', mismatch["expert_type"])
    ET.SubElement(elem, 'Summary').text = mismatch["summary"]
    ET.SubElement(elem, 'Part').text = mismatch["part"]
    ET.SubElement(elem, 'Link').text = mismatch["link"]


def _add_estimate_mismatch_section(parent, title, rows_list, extended=False, default_values=None):
    section = tk.LabelFrame(parent, text=title, padx=8, pady=8)
    section.pack(fill="x", pady=4)
    container = tk.Frame(section)
    container.pack(fill="x")

    def add_item():
        item_defaults = default_values if len(rows_list) == 0 and default_values else None
        if extended:
            add_mismatch_extended_block(container, rows_list, title, item_defaults)
        else:
            add_mismatch_block(container, rows_list, title, item_defaults)

    tk.Button(section, text="+ Добавить", command=add_item).pack(anchor="w", pady=4)
    if default_values:
        add_item()


def build_expert_estimate_ui(parent):
    ui = {}

    tk.Label(
        parent,
        text="Информация об использовании сметных нормативов:",
        justify="left",
    ).pack(anchor="w", pady=(0, 4))
    ui["text_estimate_norms"] = tk.Text(parent, width=80, height=3)
    ui["text_estimate_norms"].pack(anchor="w", pady=(0, 8))

    mismatches_frame = tk.LabelFrame(
        parent,
        text="Сведения о несоответствии сметной части проектной документации",
        padx=8,
        pady=8,
    )
    mismatches_frame.pack(fill="x", pady=4)

    ui["common_rows"] = []
    ui["full_calculation_rows"] = []
    ui["local_calculation_rows"] = []
    ui["project_documents_rows"] = []
    ui["basic_rows"] = []

    _add_estimate_mismatch_section(
        mismatches_frame,
        "Общее замечание",
        ui["common_rows"],
    )
    _add_estimate_mismatch_section(
        mismatches_frame,
        "Замечание по сводному сметному расчету",
        ui["full_calculation_rows"],
    )
    _add_estimate_mismatch_section(
        mismatches_frame,
        "Замечание по объектным или локальным сметным расчетам",
        ui["local_calculation_rows"],
    )
    _add_estimate_mismatch_section(
        mismatches_frame,
        "Замечание по соответствию расчетов проектной документации",
        ui["project_documents_rows"],
        extended=True,
    )
    _add_estimate_mismatch_section(
        mismatches_frame,
        "Замечание по пересчету из базисного уровня цен",
        ui["basic_rows"],
    )

    return ui


def collect_expert_estimate_data(ui):
    return {
        "estimate_norms": ui["text_estimate_norms"].get("1.0", "end").strip(),
        "common_mismatches": collect_filled_mismatches(ui["common_rows"]),
        "full_calculation_mismatches": collect_filled_mismatches(ui["full_calculation_rows"]),
        "local_calculation_mismatches": collect_filled_mismatches(ui["local_calculation_rows"]),
        "project_documents_mismatches": collect_filled_extended_mismatches(ui["project_documents_rows"]),
        "basic_mismatches": collect_filled_mismatches(ui["basic_rows"]),
    }


def has_expert_estimate_mismatches_content(data):
    return any([
        data["common_mismatches"],
        data["full_calculation_mismatches"],
        data["local_calculation_mismatches"],
        data["project_documents_mismatches"],
        data["basic_mismatches"],
    ])


def is_expert_estimate_filled(data):
    return bool(data["estimate_norms"]) or has_expert_estimate_mismatches_content(data)


def validate_expert_estimate_data(ui):
    data = collect_expert_estimate_data(ui)
    if not is_expert_estimate_filled(data):
        return ""
    if not data["estimate_norms"]:
        return "Укажите информацию об использовании сметных нормативов!"
    mismatch_sections = [
        ("общее замечание", ui["common_rows"], False),
        ("замечание по сводному сметному расчету", ui["full_calculation_rows"], False),
        ("замечание по локальным сметным расчетам", ui["local_calculation_rows"], False),
        ("замечание по соответствию расчетов проектной документации", ui["project_documents_rows"], True),
        ("замечание по пересчету из базисного уровня цен", ui["basic_rows"], False),
    ]
    for section_label, section_rows, extended in mismatch_sections:
        if extended:
            section_error = validate_mismatch_extended_rows(
                section_rows,
                section_label,
                "проверки сметной стоимости",
            )
        else:
            section_error = validate_mismatch_rows(
                section_rows,
                section_label,
                1,
                "проверки сметной стоимости",
            )
        if section_error:
            return section_error
    return ""


def append_expert_estimate_xml(conclusion, data):
    expert_estimate = ET.SubElement(conclusion, 'ExpertEstimate')
    ET.SubElement(expert_estimate, 'EstimateNorms').text = data["estimate_norms"]
    if has_expert_estimate_mismatches_content(data):
        mismatches = ET.SubElement(expert_estimate, 'Mismatches')
        for mismatch in data["common_mismatches"]:
            append_mismatch_xml(mismatches, 'CommonMismatch', mismatch)
        for mismatch in data["full_calculation_mismatches"]:
            append_mismatch_xml(mismatches, 'FullCalculationMismatch', mismatch)
        for mismatch in data["local_calculation_mismatches"]:
            append_mismatch_xml(mismatches, 'LocalCalculationMismatch', mismatch)
        for mismatch in data["project_documents_mismatches"]:
            append_mismatch_extended_xml(mismatches, 'ProjectDocumentsMismatch', mismatch)
        for mismatch in data["basic_mismatches"]:
            append_mismatch_xml(mismatches, 'BasicMismatch', mismatch)


def add_summary_engineering_survey_type_row(container, rows_list):
    row_frame = tk.Frame(container)
    row_frame.pack(fill="x", pady=2)

    combo, var = create_combobox(row_frame, ENGINEERING_SURVEY_TYPE_OPTIONS)
    combo.pack(side="left", fill="x", expand=True)

    row_data = {"frame": row_frame, "var": var}

    def remove_row():
        rows_list.remove(row_data)
        row_frame.destroy()

    tk.Button(row_frame, text="✕", command=remove_row, width=3).pack(side="left", padx=(4, 0))
    rows_list.append(row_data)


def build_summary_ui(parent):
    ui = {}

    tk.Label(
        parent,
        text="Вывод о соответствии результатов инженерных изысканий\n"
        "требованиям технических регламентов:",
        justify="left",
    ).pack(anchor="w", pady=(0, 4))
    combo_eng_summary, var_eng_summary = create_combobox(parent, ENGINEERING_SURVEY_SUMMARY_OPTIONS)
    combo_eng_summary.pack(anchor="w", pady=(0, 8))
    ui["var_engineering_survey_summary"] = var_eng_summary

    tk.Label(
        parent,
        text="Сведения о дате требований (экспертиза результатов инженерных изысканий):",
        justify="left",
    ).pack(anchor="w", pady=(0, 4))
    ui["entry_engineering_survey_summary_date"] = tk.Entry(parent, width=80)
    ui["entry_engineering_survey_summary_date"].pack(anchor="w", pady=(0, 8))

    survey_types_frame = tk.LabelFrame(
        parent,
        text="Вид инженерных изысканий, на соответствие которым проводилась экспертиза проектной документации",
        padx=8,
        pady=8,
    )
    survey_types_frame.pack(fill="x", pady=4)
    ui["engineering_survey_type_rows"] = []
    survey_types_container = tk.Frame(survey_types_frame)
    survey_types_container.pack(fill="x")

    def add_survey_type_row():
        add_summary_engineering_survey_type_row(
            survey_types_container,
            ui["engineering_survey_type_rows"],
        )

    tk.Button(survey_types_frame, text="+ Добавить", command=add_survey_type_row).pack(
        anchor="w", pady=4
    )

    tk.Label(
        parent,
        text="Вывод о соответствии технической части проектной документации:",
        justify="left",
    ).pack(anchor="w", pady=(8, 4))
    combo_proj_summary, var_proj_summary = create_combobox(parent, PROJECT_DOCUMENTS_SUMMARY_OPTIONS)
    combo_proj_summary.pack(anchor="w", pady=(0, 8))
    ui["var_project_documents_summary"] = var_proj_summary

    tk.Label(
        parent,
        text="Сведения о дате требований (экспертиза проектной документации):",
        justify="left",
    ).pack(anchor="w", pady=(0, 4))
    ui["entry_project_documents_summary_date"] = tk.Entry(parent, width=80)
    ui["entry_project_documents_summary_date"].pack(anchor="w", pady=(0, 8))

    estimate_frame = tk.LabelFrame(
        parent,
        text="Выводы по проверке достоверности определения сметной стоимости",
        padx=8,
        pady=8,
    )
    estimate_frame.pack(fill="x", pady=4)
    ui["var_estimate_variant"] = tk.StringVar(value="standard")

    def switch_estimate_variant():
        if ui["var_estimate_variant"].get() == "standard":
            standard_estimate_frame.pack(fill="x", pady=4)
            estimate_1315_frame.pack_forget()
        else:
            standard_estimate_frame.pack_forget()
            estimate_1315_frame.pack(fill="x", pady=4)

    tk.Radiobutton(
        estimate_frame,
        text="Стандартные выводы",
        variable=ui["var_estimate_variant"],
        value="standard",
        command=switch_estimate_variant,
        anchor="w",
    ).pack(fill="x")
    tk.Radiobutton(
        estimate_frame,
        text="Выводы по постановлению Правительства РФ от 09.08.2021 №1315",
        variable=ui["var_estimate_variant"],
        value="1315",
        command=switch_estimate_variant,
        anchor="w",
    ).pack(fill="x")

    standard_estimate_frame = tk.Frame(estimate_frame)
    tk.Label(
        standard_estimate_frame,
        text="Вывод о соответствии расчетов сметной документации:",
        justify="left",
    ).pack(anchor="w", pady=(4, 4))
    combo_norms_works, var_norms_works = create_combobox(
        standard_estimate_frame,
        ESTIMATE_NORMS_AND_WORKS_SUMMARY_OPTIONS,
    )
    combo_norms_works.pack(anchor="w", pady=(0, 8))
    ui["var_estimate_norms_and_works_summary"] = var_norms_works

    tk.Label(
        standard_estimate_frame,
        text="Вывод о достоверности определения сметной стоимости:",
        justify="left",
    ).pack(anchor="w", pady=(0, 4))
    combo_estimate_summary, var_estimate_summary = create_combobox(
        standard_estimate_frame,
        ESTIMATE_VALIDATION_SUMMARY_OPTIONS,
    )
    combo_estimate_summary.pack(anchor="w", pady=(0, 4))
    ui["var_estimate_summary"] = var_estimate_summary

    estimate_1315_frame = tk.Frame(estimate_frame)
    tk.Label(
        estimate_1315_frame,
        text="Вывод о соответствии расчетов (№1315):",
        justify="left",
    ).pack(anchor="w", pady=(4, 4))
    ui["entry_estimate_norms_and_works_summary_1315"] = tk.Entry(estimate_1315_frame, width=80)
    ui["entry_estimate_norms_and_works_summary_1315"].pack(anchor="w", pady=(0, 8))

    tk.Label(
        estimate_1315_frame,
        text="Вывод о достоверности определения сметной стоимости (№1315):",
        justify="left",
    ).pack(anchor="w", pady=(0, 4))
    ui["entry_estimate_summary_1315"] = tk.Entry(estimate_1315_frame, width=80)
    ui["entry_estimate_summary_1315"].pack(anchor="w", pady=(0, 4))

    switch_estimate_variant()

    exam_frame = tk.LabelFrame(
        parent,
        text="Общие выводы (итоговые выводы по результатам проведенной экспертизы)",
        padx=8,
        pady=8,
    )
    exam_frame.pack(fill="x", pady=4)

    tk.Label(
        exam_frame,
        text="Вывод о соответствии результатов инженерных изысканий:",
        justify="left",
    ).pack(anchor="w", pady=(0, 4))
    combo_exam_eng, var_exam_eng = create_combobox(
        exam_frame,
        ENGINEERING_SURVEYS_RESULTS_SUMMARY_OPTIONS,
    )
    combo_exam_eng.pack(anchor="w", pady=(0, 8))
    ui["var_examination_engineering_surveys_results_summary"] = var_exam_eng

    exam_pd_frame = tk.LabelFrame(
        exam_frame,
        text="Выводы в отношении проектной документации",
        padx=8,
        pady=8,
    )
    exam_pd_frame.pack(fill="x", pady=4)

    tk.Label(
        exam_pd_frame,
        text="Соответствие результатам инженерных изысканий:",
        justify="left",
    ).pack(anchor="w", pady=(0, 4))
    combo_exam_pd_eng, var_exam_pd_eng = create_combobox(
        exam_pd_frame,
        PROJECT_DOCS_ENGINEERING_SURVEYS_RESULTS_OPTIONS,
    )
    combo_exam_pd_eng.pack(anchor="w", pady=(0, 8))
    ui["var_examination_pd_engineering_surveys_results"] = var_exam_pd_eng

    tk.Label(
        exam_pd_frame,
        text="Соответствие заданию на проектирование:",
        justify="left",
    ).pack(anchor="w", pady=(0, 4))
    combo_exam_pd_design, var_exam_pd_design = create_combobox(
        exam_pd_frame,
        PROJECT_DOCS_DESIGN_ASSIGNMENT_OPTIONS,
    )
    combo_exam_pd_design.pack(anchor="w", pady=(0, 8))
    ui["var_examination_pd_design_assignment"] = var_exam_pd_design

    tk.Label(
        exam_pd_frame,
        text="Соответствие требованиям технических регламентов:",
        justify="left",
    ).pack(anchor="w", pady=(0, 4))
    combo_exam_pd_tech, var_exam_pd_tech = create_combobox(
        exam_pd_frame,
        PROJECT_DOCS_TECHNICAL_REQUIREMENTS_OPTIONS,
    )
    combo_exam_pd_tech.pack(anchor="w", pady=(0, 4))
    ui["var_examination_pd_technical_requirements"] = var_exam_pd_tech

    ui["var_examination_estimate_variant"] = tk.StringVar(value="standard")

    def switch_examination_estimate_variant():
        if ui["var_examination_estimate_variant"].get() == "standard":
            standard_exam_estimate_frame.pack(fill="x", pady=4)
            exam_estimate_1315_frame.pack_forget()
        else:
            standard_exam_estimate_frame.pack_forget()
            exam_estimate_1315_frame.pack(fill="x", pady=4)

    tk.Label(
        exam_frame,
        text="Вывод об оценке достоверности определения сметной стоимости:",
        justify="left",
    ).pack(anchor="w", pady=(8, 4))
    tk.Radiobutton(
        exam_frame,
        text="Стандартный вывод",
        variable=ui["var_examination_estimate_variant"],
        value="standard",
        command=switch_examination_estimate_variant,
        anchor="w",
    ).pack(fill="x")
    tk.Radiobutton(
        exam_frame,
        text="Вывод по постановлению №1315",
        variable=ui["var_examination_estimate_variant"],
        value="1315",
        command=switch_examination_estimate_variant,
        anchor="w",
    ).pack(fill="x")

    standard_exam_estimate_frame = tk.Frame(exam_frame)
    combo_exam_estimate, var_exam_estimate = create_combobox(
        standard_exam_estimate_frame,
        ESTIMATE_VALIDATION_SUMMARY_OPTIONS,
    )
    combo_exam_estimate.pack(anchor="w", pady=4)
    ui["var_examination_estimate_summary"] = var_exam_estimate

    exam_estimate_1315_frame = tk.Frame(exam_frame)
    ui["entry_examination_estimate_summary_1315"] = tk.Entry(exam_estimate_1315_frame, width=80)
    ui["entry_examination_estimate_summary_1315"].pack(anchor="w", pady=4)

    switch_examination_estimate_variant()

    return ui


def collect_summary_data(ui):
    engineering_survey_types = []
    for row in ui["engineering_survey_type_rows"]:
        value = get_option_value(ENGINEERING_SURVEY_TYPE_OPTIONS, row["var"])
        if value:
            engineering_survey_types.append(value)

    examination_pd = {
        "engineering_surveys_results": get_option_value(
            PROJECT_DOCS_ENGINEERING_SURVEYS_RESULTS_OPTIONS,
            ui["var_examination_pd_engineering_surveys_results"],
        ),
        "design_assignment": get_option_value(
            PROJECT_DOCS_DESIGN_ASSIGNMENT_OPTIONS,
            ui["var_examination_pd_design_assignment"],
        ),
        "technical_requirements": get_option_value(
            PROJECT_DOCS_TECHNICAL_REQUIREMENTS_OPTIONS,
            ui["var_examination_pd_technical_requirements"],
        ),
    }

    return {
        "engineering_survey_summary": get_option_value(
            ENGINEERING_SURVEY_SUMMARY_OPTIONS,
            ui["var_engineering_survey_summary"],
        ),
        "engineering_survey_summary_date": ui["entry_engineering_survey_summary_date"].get().strip(),
        "engineering_survey_types": engineering_survey_types,
        "project_documents_summary": get_option_value(
            PROJECT_DOCUMENTS_SUMMARY_OPTIONS,
            ui["var_project_documents_summary"],
        ),
        "project_documents_summary_date": ui["entry_project_documents_summary_date"].get().strip(),
        "estimate_variant": ui["var_estimate_variant"].get(),
        "estimate_norms_and_works_summary": get_option_value(
            ESTIMATE_NORMS_AND_WORKS_SUMMARY_OPTIONS,
            ui["var_estimate_norms_and_works_summary"],
        ),
        "estimate_summary": get_option_value(
            ESTIMATE_VALIDATION_SUMMARY_OPTIONS,
            ui["var_estimate_summary"],
        ),
        "estimate_norms_and_works_summary_1315": ui[
            "entry_estimate_norms_and_works_summary_1315"
        ].get().strip(),
        "estimate_summary_1315": ui["entry_estimate_summary_1315"].get().strip(),
        "examination_engineering_surveys_results_summary": get_option_value(
            ENGINEERING_SURVEYS_RESULTS_SUMMARY_OPTIONS,
            ui["var_examination_engineering_surveys_results_summary"],
        ),
        "examination_project_documents_summary": examination_pd,
        "examination_estimate_variant": ui["var_examination_estimate_variant"].get(),
        "examination_estimate_summary": get_option_value(
            ESTIMATE_VALIDATION_SUMMARY_OPTIONS,
            ui["var_examination_estimate_summary"],
        ),
        "examination_estimate_summary_1315": ui[
            "entry_examination_estimate_summary_1315"
        ].get().strip(),
    }


def validate_summary_data(ui):
    data = collect_summary_data(ui)
    pd_summary = data["examination_project_documents_summary"]
    pd_values = [
        pd_summary["engineering_surveys_results"],
        pd_summary["design_assignment"],
        pd_summary["technical_requirements"],
    ]
    if any(pd_values) and not all(pd_values):
        return (
            "В общих выводах по проектной документации укажите все три подпункта "
            "или оставьте их пустыми!"
        )
    return ""


def append_summary_xml(conclusion, data):
    summary = ET.SubElement(conclusion, 'Summary')

    if data["engineering_survey_summary"]:
        ET.SubElement(summary, 'EngineeringSurveySummary').text = data["engineering_survey_summary"]
    if data["engineering_survey_summary_date"]:
        ET.SubElement(
            summary,
            'EngineeringSurveySummaryDate',
        ).text = data["engineering_survey_summary_date"]
    for survey_type in data["engineering_survey_types"]:
        ET.SubElement(summary, 'EngineeringSurveyType').text = survey_type
    if data["project_documents_summary"]:
        ET.SubElement(summary, 'ProjectDocumentsSummary').text = data["project_documents_summary"]
    if data["project_documents_summary_date"]:
        ET.SubElement(
            summary,
            'ProjectDocumentsSummaryDate',
        ).text = data["project_documents_summary_date"]

    if data["estimate_variant"] == "standard":
        if data["estimate_norms_and_works_summary"]:
            ET.SubElement(
                summary,
                'EstimateNormsAndWorksSummary',
            ).text = data["estimate_norms_and_works_summary"]
        if data["estimate_summary"]:
            ET.SubElement(summary, 'EstimateSummary').text = data["estimate_summary"]
    else:
        if data["estimate_norms_and_works_summary_1315"]:
            ET.SubElement(
                summary,
                'EstimateNormsAndWorksSummary1315',
            ).text = data["estimate_norms_and_works_summary_1315"]
        if data["estimate_summary_1315"]:
            ET.SubElement(summary, 'EstimateSummary1315').text = data["estimate_summary_1315"]

    exam_summary = ET.SubElement(summary, 'ExaminationSummary')
    if data["examination_engineering_surveys_results_summary"]:
        ET.SubElement(
            exam_summary,
            'EngineeringSurveysResultsSummary',
        ).text = data["examination_engineering_surveys_results_summary"]

    pd_summary = data["examination_project_documents_summary"]
    if all(pd_summary.values()):
        project_docs_summary = ET.SubElement(exam_summary, 'ProjectDocumentsSummary')
        ET.SubElement(
            project_docs_summary,
            'ProjectDocumentationEngineeringSurveysResultsSummary',
        ).text = pd_summary["engineering_surveys_results"]
        ET.SubElement(
            project_docs_summary,
            'ProjectDocumentationDesignAssignmentSummary',
        ).text = pd_summary["design_assignment"]
        ET.SubElement(
            project_docs_summary,
            'ProjectDocumentationTechnicalRequirementsSummary',
        ).text = pd_summary["technical_requirements"]

    if data["examination_estimate_variant"] == "standard":
        if data["examination_estimate_summary"]:
            ET.SubElement(
                exam_summary,
                'EstimateSummary',
            ).text = data["examination_estimate_summary"]
    elif data["examination_estimate_summary_1315"]:
        ET.SubElement(
            exam_summary,
            'EstimateSummary1315',
        ).text = data["examination_estimate_summary_1315"]


EXPERT_CERTIFICATE_PATTERN = re.compile(
    r'^(МС-Э-[0-9]{1,3}-[0-9]{1,2}-[0-9]{4,5}|'
    r'ГС-Э-[0-9]{1,2}-[0-9]{1,2}-[0-9]{4,5}|'
    r'Т[0-9]{3}-[0-9]{5}-00/[0-9]{8})$'
)


def add_expert_block(container, rows_list, default_values=None):
    default_values = default_values or {}
    index = len(rows_list) + 1
    block = tk.LabelFrame(container, text=f"Эксперт {index}", padx=8, pady=8)
    block.pack(fill="x", pady=8, padx=4)

    fields = [
        ("Фамилия:", "family_name"),
        ("Имя:", "first_name"),
        ("Отчество:", "second_name"),
    ]
    entries = {}
    for row_idx, (label, key) in enumerate(fields):
        tk.Label(block, text=label).grid(row=row_idx, column=0, sticky="w", pady=4)
        entry = tk.Entry(block, width=60)
        entry.grid(row=row_idx, column=1, sticky="w", pady=4)
        if default_values.get(key):
            entry.insert(0, default_values[key])
        entries[key] = entry

    tk.Label(
        block,
        text="Направление деятельности эксперта:",
    ).grid(row=3, column=0, sticky="w", pady=4)
    combo_expert_type, var_expert_type = create_combobox(
        block,
        EXPERT_TYPE_OPTIONS,
        default_values.get("expert_type_label", NOT_SPECIFIED),
    )
    combo_expert_type.grid(row=3, column=1, sticky="w", pady=4)

    cert_fields = [
        ("Номер квалификационного аттестата:", "expert_certificate"),
        ("Дата выдачи аттестата (ДД.ММ.ГГГГ):", "certificate_begin_date"),
        ("Дата окончания действия аттестата (ДД.ММ.ГГГГ):", "certificate_end_date"),
    ]
    for row_idx, (label, key) in enumerate(cert_fields, start=4):
        tk.Label(block, text=label).grid(row=row_idx, column=0, sticky="w", pady=4)
        entry = tk.Entry(block, width=60)
        entry.grid(row=row_idx, column=1, sticky="w", pady=4)
        if default_values.get(key):
            entry.insert(0, default_values[key])
        entries[key] = entry

    row_data = {
        "frame": block,
        "entries": entries,
        "var_expert_type": var_expert_type,
    }

    def remove_block():
        rows_list.remove(row_data)
        block.destroy()
        for idx, item in enumerate(rows_list, start=1):
            item["frame"].config(text=f"Эксперт {idx}")

    tk.Button(block, text="Удалить эксперта", command=remove_block).grid(
        row=7, column=1, sticky="w", pady=8
    )
    rows_list.append(row_data)


def collect_expert_row_data(row):
    entries = row["entries"]
    return {
        "family_name": entries["family_name"].get().strip(),
        "first_name": entries["first_name"].get().strip(),
        "second_name": entries["second_name"].get().strip(),
        "expert_type": get_option_value(EXPERT_TYPE_OPTIONS, row["var_expert_type"]),
        "expert_certificate": entries["expert_certificate"].get().strip(),
        "certificate_begin_date": format_doc_date(entries["certificate_begin_date"].get()),
        "certificate_end_date": format_doc_date(entries["certificate_end_date"].get()),
    }


def is_expert_row_filled(data):
    return any([
        data["family_name"],
        data["first_name"],
        data["second_name"],
        data["expert_type"],
        data["expert_certificate"],
        data["certificate_begin_date"],
        data["certificate_end_date"],
    ])


def is_expert_row_complete(data):
    required = (
        data["family_name"],
        data["first_name"],
        data["expert_type"],
        data["expert_certificate"],
        data["certificate_begin_date"],
        data["certificate_end_date"],
    )
    return all(required)


def collect_experts_data(rows_list):
    experts = []
    for row in rows_list:
        data = collect_expert_row_data(row)
        if is_expert_row_filled(data):
            experts.append(data)
    return experts


def validate_experts_rows(rows_list):
    experts = collect_experts_data(rows_list)
    if not experts:
        return "Добавьте хотя бы одного эксперта!"

    for idx, row in enumerate(rows_list, start=1):
        data = collect_expert_row_data(row)
        if not is_expert_row_filled(data):
            continue
        if not is_expert_row_complete(data):
            return f"Заполните все обязательные поля для эксперта {idx}!"
        if not EXPERT_CERTIFICATE_PATTERN.fullmatch(data["expert_certificate"]):
            return (
                f"Некорректный номер аттестата у эксперта {idx}! "
                "Пример: МС-Э-49-5-12918"
            )
        if not data["certificate_begin_date"]:
            return f"Укажите дату выдачи аттестата для эксперта {idx} (ДД.ММ.ГГГГ)!"
        if not data["certificate_end_date"]:
            return f"Укажите дату окончания действия аттестата для эксперта {idx}!"
    return ""


def append_experts_xml(conclusion, experts):
    experts_elem = ET.SubElement(conclusion, 'Experts')
    for expert_data in experts:
        expert = ET.SubElement(experts_elem, 'Expert')
        ET.SubElement(expert, 'FamilyName').text = expert_data["family_name"]
        ET.SubElement(expert, 'FirstName').text = expert_data["first_name"]
        if expert_data["second_name"]:
            ET.SubElement(expert, 'SecondName').text = expert_data["second_name"]
        ET.SubElement(expert, 'ExpertType').text = expert_data["expert_type"]
        ET.SubElement(expert, 'ExpertCertificate').text = expert_data["expert_certificate"]
        ET.SubElement(
            expert,
            'ExpertCertificateBeginDate',
        ).text = expert_data["certificate_begin_date"]
        ET.SubElement(
            expert,
            'ExpertCertificateEndDate',
        ).text = expert_data["certificate_end_date"]


def add_climate_value_row(container, rows_list, options):
    row_frame = tk.Frame(container)
    row_frame.pack(fill="x", pady=2)

    var = tk.StringVar(value=NOT_SPECIFIED)
    combo = ttk.Combobox(
        row_frame,
        textvariable=var,
        values=list(options.keys()),
        state="readonly",
        width=55,
    )
    combo.pack(side="left", fill="x", expand=True)

    row_data = {"frame": row_frame, "var": var, "options": options}

    def remove_row():
        rows_list.remove(row_data)
        row_frame.destroy()

    tk.Button(row_frame, text="✕", command=remove_row, width=3).pack(side="left", padx=(4, 0))
    rows_list.append(row_data)


def collect_climate_values(rows_list):
    values = []
    for row in rows_list:
        value = get_option_value(row["options"], row["var"])
        if value:
            values.append(value)
    return values


def collect_climate_conditions_data():
    seismic_calculated = None
    if var_include_seismic_calc.get():
        seismic_calculated = {
            "min": entry_seismic_calc_min.get().strip(),
            "max": entry_seismic_calc_max.get().strip(),
        }
    return {
        "climate_districts": collect_climate_values(climate_district_rows),
        "geological_conditions": collect_climate_values(geological_conditions_rows),
        "wind_districts": collect_climate_values(wind_district_rows),
        "snow_districts": collect_climate_values(snow_district_rows),
        "seismic_activities": collect_climate_values(seismic_activity_rows),
        "seismic_calculated": seismic_calculated,
        "note": text_climate_conditions_note.get("1.0", tk.END).strip(),
    }


def is_climate_conditions_block_filled(data):
    lists = (
        data["climate_districts"],
        data["geological_conditions"],
        data["wind_districts"],
        data["snow_districts"],
        data["seismic_activities"],
    )
    if any(items for items in lists):
        return True
    if data.get("seismic_calculated"):
        return True
    return False


def validate_climate_conditions_data(data):
    if not is_climate_conditions_block_filled(data):
        return None

    required_lists = [
        ("climate_districts", "климатический район"),
        ("geological_conditions", "категорию сложности инженерно-геологических условий"),
        ("wind_districts", "ветровой район"),
        ("snow_districts", "снеговой район"),
        ("seismic_activities", "интенсивность сейсмических воздействий"),
    ]
    for key, label in required_lists:
        if not data[key]:
            return f"Добавьте хотя бы один элемент: {label}!"

    if data.get("seismic_calculated"):
        if not data["seismic_calculated"]["min"]:
            return "Укажите минимальное расчётное значение интенсивности сейсмических воздействий!"
    return None


def append_climate_conditions_xml(conclusion, data):
    climate = ET.SubElement(conclusion, 'ClimateConditions')
    for value in data["climate_districts"]:
        ET.SubElement(climate, 'ClimateDistrict').text = value
    for value in data["geological_conditions"]:
        ET.SubElement(climate, 'GeologicalConditions').text = value
    for value in data["wind_districts"]:
        ET.SubElement(climate, 'WindDistrict').text = value
    for value in data["snow_districts"]:
        ET.SubElement(climate, 'SnowDistrict').text = value
    for value in data["seismic_activities"]:
        ET.SubElement(climate, 'SeismicActivity').text = value
    if data.get("seismic_calculated") and data["seismic_calculated"]["min"]:
        calc_elem = ET.SubElement(climate, 'SeismicActivityCalculatedValue')
        ET.SubElement(calc_elem, 'MinValue').text = data["seismic_calculated"]["min"]
        if data["seismic_calculated"].get("max"):
            ET.SubElement(calc_elem, 'MaxValue').text = data["seismic_calculated"]["max"]


def append_estimated_cost_xml(conclusion, data):
    estimated_cost = ET.SubElement(conclusion, 'EstimatedCost')
    if data.get("currency"):
        ET.SubElement(estimated_cost, 'Currency').text = data["currency"]
    if data["mode"] == "complete":
        ET.SubElement(
            estimated_cost, 'EstimatedCompleteCostBefore'
        ).text = data["complete_before"]
        ET.SubElement(
            estimated_cost, 'EstimatedCompleteCostPost'
        ).text = data["complete_post"]
        return

    before_elem = ET.SubElement(estimated_cost, 'EstimatedComplexCostBefore')
    append_complex_cost_xml(before_elem, data["complex_before"])
    post_elem = ET.SubElement(estimated_cost, 'EstimatedComplexCostPost')
    append_complex_cost_xml(post_elem, data["complex_post"])


def validate_declarant_entity_data(data, label):
    email = data.get("email", "")
    if email and not EMAIL_RE.match(email):
        return f"Некорректный адрес электронной почты ({label})!"

    if data["type"] == "organization":
        if not data["org_full_name"]:
            return f"Укажите полное наименование юридического лица ({label})!"
        if not data["org_ogrn"]:
            return f"Укажите ОГРН юридического лица ({label})!"
        if not ORG_OGRN_RE.match(data["org_ogrn"]):
            return f"Некорректный ОГРН ({label})! Должно быть 13 цифр."
        if not data["org_inn"]:
            return f"Укажите ИНН юридического лица ({label})!"
        if not ORG_INN_RE.match(data["org_inn"]):
            return f"Некорректный ИНН ({label})! Должно быть 10 цифр."
        if not data["org_kpp"]:
            return f"Укажите КПП юридического лица ({label})!"
        if not ORG_KPP_RE.match(data["org_kpp"]):
            return f"Некорректный КПП ({label})! Должно быть 9 цифр."
        return validate_address_data(data["address"], label)

    if data["type"] == "foreign_organization":
        if not data["org_full_name"]:
            return f"Укажите полное наименование иностранного юридического лица ({label})!"
        if not data["org_inn"]:
            return f"Укажите ИНН филиала/представительства ({label})!"
        if not ORG_INN_RE.match(data["org_inn"]):
            return f"Некорректный ИНН ({label})! Должно быть 10 цифр."
        if not data["org_kpp"]:
            return f"Укажите КПП филиала/представительства ({label})!"
        if not ORG_KPP_RE.match(data["org_kpp"]):
            return f"Некорректный КПП ({label})! Должно быть 9 цифр."
        return validate_address_data(data["address"], label)

    if data["type"] == "ip":
        if not data["family_name"]:
            return f"Укажите фамилию индивидуального предпринимателя ({label})!"
        if not data["first_name"]:
            return f"Укажите имя индивидуального предпринимателя ({label})!"
        if not data["ogrnip"]:
            return f"Укажите ОГРНИП ({label})!"
        if not OGRNIP_RE.match(data["ogrnip"]):
            return "Некорректный ОГРНИП! Должно быть 15 цифр."
        return validate_post_address_data(data["post_address"], label)

    if not data["family_name"]:
        return f"Укажите фамилию физического лица ({label})!"
    if not data["first_name"]:
        return f"Укажите имя физического лица ({label})!"
    if not data["snils"]:
        return f"Укажите СНИЛС физического лица ({label})!"
    if not SNILS_RE.match(data["snils"]):
        return "Некорректный СНИЛС! Формат: 123-456-789 01"
    return validate_post_address_data(data["post_address"], label)


def validate_declarant_data(data):
    return validate_declarant_entity_data(data, "заявитель")


def add_tei_row(container, rows_list, defaults=None):
    defaults = defaults or {}
    row_frame = tk.Frame(container)
    row_frame.pack(fill="x", pady=4)

    entries = {}
    for label_text, key in [
        ("Наименование показателя:", "name"),
        ("Единица измерения:", "measure"),
        ("Значение показателя:", "value"),
    ]:
        line = tk.Frame(row_frame)
        line.pack(fill="x", pady=1)
        tk.Label(line, text=label_text, width=22, anchor="w").pack(side="left")
        entry = tk.Entry(line, width=45)
        entry.pack(side="left", fill="x", expand=True)
        if defaults.get(key):
            entry.insert(0, defaults[key])
        entries[key] = entry

    def remove_row():
        if len(rows_list) <= 1:
            messagebox.showwarning("Ошибка", "Должен остаться хотя бы один показатель!")
            return
        rows_list.remove(row_data)
        row_frame.destroy()

    tk.Button(row_frame, text="✕", command=remove_row, width=3).pack(anchor="e", pady=2)
    row_data = {"frame": row_frame, "entries": entries}
    rows_list.append(row_data)


def collect_tei_rows(rows_list):
    items = []
    for row in rows_list:
        item = {
            "name": row["entries"]["name"].get().strip(),
            "measure": row["entries"]["measure"].get().strip(),
            "value": row["entries"]["value"].get().strip(),
        }
        if any(item.values()):
            items.append(item)
    return items


def append_tei_xml(parent_elem, tei_items):
    for tei in tei_items:
        tei_elem = ET.SubElement(parent_elem, 'TEI')
        ET.SubElement(tei_elem, 'Name').text = tei["name"]
        ET.SubElement(tei_elem, 'Measure').text = tei["measure"]
        ET.SubElement(tei_elem, 'Value').text = tei["value"]


def add_object_part_block(container, rows_list, defaults=None):
    defaults = defaults or {}
    index = len(rows_list) + 1
    block = tk.LabelFrame(
        container,
        text=f"Составная часть сложного объекта {index}",
        padx=8,
        pady=8,
    )
    block.pack(fill="x", pady=8, padx=4)

    tk.Label(block, text="Наименование объекта:").grid(row=0, column=0, sticky="w", pady=4)
    entry_name = tk.Entry(block, width=60)
    entry_name.grid(row=0, column=1, sticky="w", pady=4)
    if defaults.get("name"):
        entry_name.insert(0, defaults["name"])

    address_wrapper = tk.Frame(block)
    address_wrapper.grid(row=1, column=0, columnspan=2, sticky="ew")
    address_list_frame = tk.Frame(address_wrapper)
    address_list_frame.pack(fill="x")
    address_rows = []

    def add_part_address():
        default_addresses = defaults.get("addresses", [])
        default = (
            default_addresses[len(address_rows)]
            if len(address_rows) < len(default_addresses)
            else None
        )
        add_address_block(address_list_frame, address_rows, default)

    add_part_address()
    tk.Button(address_wrapper, text="+ Добавить адрес", command=add_part_address).pack(
        anchor="w", pady=4
    )

    tk.Label(block, text="Код классификатора:").grid(row=2, column=0, sticky="w", pady=4)
    entry_functions_class = tk.Entry(block, width=60)
    entry_functions_class.grid(row=2, column=1, sticky="w", pady=4)
    if defaults.get("functions_class"):
        entry_functions_class.insert(0, defaults["functions_class"])

    tk.Label(block, text="Технико-экономические показатели:").grid(
        row=3, column=0, sticky="nw", pady=4
    )
    tei_container = tk.Frame(block)
    tei_container.grid(row=3, column=1, sticky="w", pady=4)
    tei_rows = []

    def add_part_tei():
        add_tei_row(tei_container, tei_rows, defaults.get("tei"))

    add_part_tei()

    btn_add_tei = tk.Button(block, text="+ Добавить показатель", command=add_part_tei)
    btn_add_tei.grid(row=4, column=1, sticky="w", pady=4)

    row_data = {
        "frame": block,
        "entry_name": entry_name,
        "address_rows": address_rows,
        "entry_functions_class": entry_functions_class,
        "tei_rows": tei_rows,
    }

    def remove_block():
        rows_list.remove(row_data)
        block.destroy()
        for idx, item in enumerate(rows_list, start=1):
            item["frame"].config(text=f"Составная часть сложного объекта {idx}")

    tk.Button(block, text="Удалить часть", command=remove_block).grid(
        row=5, column=1, sticky="w", pady=8
    )
    rows_list.append(row_data)


def collect_object_part_data(row):
    return {
        "name": row["entry_name"].get().strip(),
        "addresses": collect_address_rows(row["address_rows"]),
        "functions_class": row["entry_functions_class"].get().strip(),
        "tei": collect_tei_rows(row["tei_rows"]),
    }


def collect_capital_object_data():
    name = entry_capital_object_name.get().strip()
    addresses = collect_address_rows(capital_object_address_rows)
    object_type = get_option_value(CAPITAL_OBJECT_TYPE_OPTIONS, var_capital_object_type)
    functions_class = entry_capital_functions_class.get().strip()
    tei = collect_tei_rows(capital_object_tei_rows)
    parts = [collect_object_part_data(row) for row in capital_object_part_rows]
    return {
        "name": name,
        "addresses": addresses,
        "type": object_type,
        "functions_class": functions_class,
        "tei": tei,
        "parts": parts,
    }


def is_capital_object_filled(data):
    if data["name"]:
        return True
    if data["addresses"]:
        return True
    if data["type"] or data["functions_class"]:
        return True
    if data["tei"]:
        return True
    return any(
        part["name"] or part["functions_class"] or part["tei"] or part["addresses"]
        for part in data["parts"]
    )


def add_cadastral_number_row(container, rows_list, default_value=""):
    row_frame = tk.Frame(container)
    row_frame.pack(fill="x", pady=2)

    entry = tk.Entry(row_frame, width=60)
    entry.pack(side="left", fill="x", expand=True)
    if default_value:
        entry.insert(0, default_value)

    def remove_row():
        rows_list.remove(row_data)
        row_frame.destroy()

    tk.Button(row_frame, text="✕", command=remove_row, width=3).pack(side="left", padx=(4, 0))
    row_data = {"frame": row_frame, "entry": entry}
    rows_list.append(row_data)


def collect_and_validate_cadastral_numbers(rows_list):
    values = [row["entry"].get().strip() for row in rows_list]
    non_empty = [value for value in values if value]
    if not non_empty and len(values) <= 1:
        return [], None
    for idx, value in enumerate(values, start=1):
        if not value:
            return None, f"Укажите кадастровый номер в строке {idx}!"
        if not CADASTRAL_NUMBER_RE.match(value):
            return (
                None,
                f"Некорректный кадастровый номер в строке {idx} "
                f"(формат: 77:01:0002401:107)!",
            )
    return values, None


def append_capital_object(conclusion, data):
    obj = ET.SubElement(conclusion, 'Object')
    ET.SubElement(obj, 'Name').text = data["name"]
    append_addresses_xml(obj, data["addresses"])
    if data["type"]:
        ET.SubElement(obj, 'Type').text = data["type"]
    if data["functions_class"]:
        ET.SubElement(obj, 'FunctionsClass').text = data["functions_class"]
    append_tei_xml(obj, data["tei"])
    for part in data["parts"]:
        part_elem = ET.SubElement(obj, 'ObjectPart')
        ET.SubElement(part_elem, 'Name').text = part["name"]
        append_addresses_xml(part_elem, part["addresses"])
        if part["functions_class"]:
            ET.SubElement(part_elem, 'FunctionsClass').text = part["functions_class"]
        append_tei_xml(part_elem, part["tei"])


def generate_xml():
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

    examination_types = [
        get_option_value(EXAMINATION_TYPE_OPTIONS, row["var"])
        for row in examination_type_rows
        if get_option_value(EXAMINATION_TYPE_OPTIONS, row["var"])
    ]

    object_name = text_name.get("1.0", tk.END).strip()

    if not examination_types:
        messagebox.showwarning("Ошибка", "Выберите хотя бы один предмет экспертизы!")
        return

    if not object_name:
        messagebox.showwarning("Ошибка", "Укажите наименование объекта экспертизы!")
        return

    if not all([family_name, first_name, position]):
        messagebox.showwarning("Ошибка", "Заполните обязательные поля лица, утвердившего заключение")
        return

    if not all([org_full_name, org_ogrn, org_inn, org_kpp, country, region, city, street, building, room]):
        messagebox.showwarning("Ошибка", "Заполните все поля организации по проведению экспертизы!")
        return

    documents_data = [collect_document_data(row) for row in document_rows]
    if not documents_data:
        messagebox.showwarning("Ошибка", "Добавьте хотя бы один документ!")
        return

    for idx, doc in enumerate(documents_data, start=1):
        if not doc["doc_type"]:
            messagebox.showwarning("Ошибка", f"Укажите код типа документа для документа {idx}!")
            return
        if not doc["doc_name"]:
            messagebox.showwarning("Ошибка", f"Укажите наименование документа {idx}!")
            return
        if not doc["doc_date"]:
            messagebox.showwarning("Ошибка", f"Укажите корректную дату документа {idx} (ДД.ММ.ГГГГ)!")
            return
        if not doc["file_path"]:
            messagebox.showwarning("Ошибка", f"Загрузите файл для документа {idx}!")
            return

    conclusion = ET.Element('Conclusion', {
        'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xsi:noNamespaceSchemaLocation': 'conclusion-01-03.xsd',
        'ConclusionGUID': str(uuid.uuid4()).upper(),
        'SchemaVersion': '01.03',
    })

    expert_organization = ET.SubElement(conclusion, 'ExpertOrganization')
    ET.SubElement(expert_organization, 'OrgFullName').text = org_full_name
    ET.SubElement(expert_organization, 'OrgOGRN').text = org_ogrn
    ET.SubElement(expert_organization, 'OrgINN').text = org_inn
    ET.SubElement(expert_organization, 'OrgKPP').text = org_kpp

    address = ET.SubElement(expert_organization, 'Address')
    ET.SubElement(address, 'Country').text = country
    ET.SubElement(address, 'Region').text = region
    ET.SubElement(address, 'City').text = city
    ET.SubElement(address, 'Street').text = street
    ET.SubElement(address, 'Building').text = building
    ET.SubElement(address, 'Room').text = room

    approver = ET.SubElement(conclusion, 'Approver')
    ET.SubElement(approver, 'FamilyName').text = family_name
    ET.SubElement(approver, 'FirstName').text = first_name
    ET.SubElement(approver, 'SecondName').text = second_name
    ET.SubElement(approver, 'Position').text = position

    examination_object = ET.SubElement(conclusion, 'ExaminationObject')

    def add_if_set(parent, tag, value):
        if value:
            ET.SubElement(parent, tag).text = value

    add_if_set(examination_object, 'ExaminationForm', get_option_value(EXAMINATION_FORM_OPTIONS, var_examination_form))
    add_if_set(examination_object, 'ExaminationResult', get_option_value(EXAMINATION_RESULT_OPTIONS, var_examination_result))
    add_if_set(
        examination_object,
        'ExaminationObjectType',
        get_option_value(EXAMINATION_OBJECT_TYPE_OPTIONS, var_examination_object_type),
    )
    for exam_type in examination_types:
        ET.SubElement(examination_object, 'ExaminationType').text = exam_type
    add_if_set(
        examination_object,
        'ConstructionType',
        get_option_value(CONSTRUCTION_TYPE_OPTIONS, var_construction_type),
    )
    add_if_set(
        examination_object,
        'ExaminationStage',
        get_option_value(EXAMINATION_STAGE_OPTIONS, var_examination_stage),
    )

    stage_note = text_stage_note.get("1.0", tk.END).strip()
    if stage_note:
        ET.SubElement(examination_object, 'ExaminationStageNote').text = stage_note

    ET.SubElement(examination_object, 'Name').text = object_name
    add_if_set(
        examination_object,
        'ProjectDocumentationIM',
        get_option_value(IM_OPTIONS, var_project_documentation_im),
    )
    add_if_set(
        examination_object,
        'EngineeringSurveysIM',
        get_option_value(IM_OPTIONS, var_engineering_surveys_im),
    )

    documents = ET.SubElement(conclusion, 'Documents')
    output_dir = os.path.dirname(os.path.abspath("conclusion.xml")) or "."

    for doc in documents_data:
        document = ET.SubElement(documents, 'Document')
        ET.SubElement(document, 'DocType').text = doc["doc_type"]
        ET.SubElement(document, 'DocName').text = doc["doc_name"]
        if doc["doc_number"]:
            ET.SubElement(document, 'DocNumber').text = doc["doc_number"]
        ET.SubElement(document, 'DocDate').text = doc["doc_date"]
        if doc["doc_author"]:
            ET.SubElement(document, 'DocIssueAuthor').text = doc["doc_author"]
        if doc["doc_changes"]:
            ET.SubElement(document, 'DocChanges').text = doc["doc_changes"]

        file_elem = ET.SubElement(document, 'File')
        ET.SubElement(file_elem, 'FileName').text = doc["file_name"]
        ET.SubElement(file_elem, 'FileFormat').text = doc["file_format"]
        ET.SubElement(file_elem, 'FileChecksum').text = doc["file_checksum"]

        dest_path = os.path.join(output_dir, doc["file_name"])
        if os.path.abspath(doc["file_path"]) != os.path.abspath(dest_path):
            shutil.copy2(doc["file_path"], dest_path)

        for sign in doc["sign_files"]:
            sign_elem = ET.SubElement(file_elem, 'SignFile')
            ET.SubElement(sign_elem, 'FileName').text = sign["file_name"]
            ET.SubElement(sign_elem, 'FileFormat').text = sign["file_format"]
            ET.SubElement(sign_elem, 'FileChecksum').text = sign["file_checksum"]

            dest_sign_path = os.path.join(output_dir, sign["file_name"])
            if os.path.abspath(sign["file_path"]) != os.path.abspath(dest_sign_path):
                shutil.copy2(sign["file_path"], dest_sign_path)

    previous_conclusions_data = []
    for row in previous_conclusion_rows:
        prev_data = collect_previous_conclusion_data(row)
        if is_previous_conclusion_filled(prev_data):
            previous_conclusions_data.append(prev_data)

    for idx, prev in enumerate(previous_conclusions_data, start=1):
        if not prev["date"]:
            messagebox.showwarning("Ошибка", f"Укажите дату для ранее выданного заключения {idx}!")
            return
        if not prev["number"]:
            messagebox.showwarning("Ошибка", f"Укажите номер для ранее выданного заключения {idx}!")
            return
        if not prev["object_type"]:
            messagebox.showwarning("Ошибка", f"Укажите вид объекта для ранее выданного заключения {idx}!")
            return
        if not prev["name"]:
            messagebox.showwarning("Ошибка", f"Укажите наименование объекта для ранее выданного заключения {idx}!")
            return
        if not prev["result"]:
            messagebox.showwarning("Ошибка", f"Укажите результат для ранее выданного заключения {idx}!")
            return

    append_previous_conclusions_xml(conclusion, previous_conclusions_data)

    previous_simple_data = []
    for row in previous_simple_conclusion_rows:
        simple_data = collect_previous_simple_conclusion_data(row)
        if is_previous_simple_conclusion_filled(simple_data):
            previous_simple_data.append(simple_data)

    for idx, simple in enumerate(previous_simple_data, start=1):
        if not simple["date"]:
            messagebox.showwarning(
                "Ошибка",
                f"Укажите дату для заключения по экспертному сопровождению {idx}!",
            )
            return
        if not simple["number"]:
            messagebox.showwarning(
                "Ошибка",
                f"Укажите номер для заключения по экспертному сопровождению {idx}!",
            )
            return
        if not simple["object_type"]:
            messagebox.showwarning(
                "Ошибка",
                f"Укажите вид объекта для заключения по экспертному сопровождению {idx}!",
            )
            return
        if not simple["result"]:
            messagebox.showwarning(
                "Ошибка",
                f"Укажите результат для заключения по экспертному сопровождению {idx}!",
            )
            return

    append_previous_simple_conclusions(conclusion, previous_simple_data)

    capital_object_data = collect_capital_object_data()
    if is_capital_object_filled(capital_object_data):
        if not capital_object_data["name"]:
            messagebox.showwarning("Ошибка", "Укажите наименование объекта капитального строительства!")
            return
        if not capital_object_data["addresses"]:
            messagebox.showwarning("Ошибка", "Добавьте хотя бы один адрес объекта!")
            return
        if not capital_object_data["type"]:
            messagebox.showwarning("Ошибка", "Укажите вид объекта капитального строительства!")
            return
        if not capital_object_data["functions_class"]:
            messagebox.showwarning("Ошибка", "Укажите код классификатора объекта!")
            return
        if not capital_object_data["tei"]:
            messagebox.showwarning("Ошибка", "Добавьте хотя бы один технико-экономический показатель!")
            return
        for idx, tei in enumerate(capital_object_data["tei"], start=1):
            if not all([tei["name"], tei["measure"], tei["value"]]):
                messagebox.showwarning("Ошибка", f"Заполните все поля показателя {idx}!")
                return
        for idx, part in enumerate(capital_object_data["parts"], start=1):
            if not part["name"]:
                messagebox.showwarning("Ошибка", f"Укажите наименование составной части {idx}!")
                return
            if not part["addresses"]:
                messagebox.showwarning("Ошибка", f"Добавьте хотя бы один адрес для составной части {idx}!")
                return
            if not part["functions_class"]:
                messagebox.showwarning("Ошибка", f"Укажите код классификатора для составной части {idx}!")
                return
            if not part["tei"]:
                messagebox.showwarning("Ошибка", f"Добавьте показатель для составной части {idx}!")
                return
            for tei_idx, tei in enumerate(part["tei"], start=1):
                if not all([tei["name"], tei["measure"], tei["value"]]):
                    messagebox.showwarning(
                        "Ошибка",
                        f"Заполните все поля показателя {tei_idx} составной части {idx}!",
                    )
                    return
        append_capital_object(conclusion, capital_object_data)

    need_expertise = get_option_value(IM_OPTIONS, var_need_expertise)
    if not need_expertise:
        messagebox.showwarning(
            "Ошибка",
            "Укажите необходимость проведения экологической экспертизы!",
        )
        return
    ecology = ET.SubElement(conclusion, 'EcologyExpertise')
    ET.SubElement(ecology, 'NeedExpertise').text = need_expertise
    ecology_comment = text_ecology_comment.get("1.0", tk.END).strip()
    if ecology_comment:
        ET.SubElement(ecology, 'Comment').text = ecology_comment

    cadastral_numbers, cadastral_error = collect_and_validate_cadastral_numbers(
        cadastral_number_rows
    )
    if cadastral_error:
        messagebox.showwarning("Ошибка", cadastral_error)
        return
    for number in cadastral_numbers:
        ET.SubElement(conclusion, 'CadastralNumber').text = number

    declarant_data = collect_declarant_data()
    declarant_error = validate_declarant_data(declarant_data)
    if declarant_error:
        messagebox.showwarning("Ошибка", declarant_error)
        return
    append_declarant_xml(conclusion, declarant_data)

    project_docs_parties = collect_project_documents_parties_data(project_documents_party_rows)
    project_docs_parties_error = validate_project_documents_parties_rows(
        project_documents_party_rows,
    )
    if project_docs_parties_error:
        messagebox.showwarning("Ошибка", project_docs_parties_error)
        return
    if project_docs_parties:
        append_project_documents_parties_xml(conclusion, project_docs_parties)

    finance_items = [collect_finance_data(row) for row in finance_rows]
    finance_items = [item for item in finance_items if item["finance_type"]]
    if not finance_items:
        messagebox.showwarning("Ошибка", "Добавьте хотя бы один источник финансирования!")
        return
    for idx, finance_item in enumerate(finance_items, start=1):
        finance_error = validate_finance_data(finance_item, idx)
        if finance_error:
            messagebox.showwarning("Ошибка", finance_error)
            return
    append_finance_xml(conclusion, finance_items)

    finance_comment = text_finance_comment.get("1.0", tk.END).strip()
    if finance_comment:
        ET.SubElement(conclusion, 'FinanceComment').text = finance_comment

    estimated_cost_data = collect_estimated_cost_data()
    if is_estimated_cost_filled(estimated_cost_data):
        estimated_cost_error = validate_estimated_cost_data(estimated_cost_data)
        if estimated_cost_error:
            messagebox.showwarning("Ошибка", estimated_cost_error)
            return
        append_estimated_cost_xml(conclusion, estimated_cost_data)

    climate_data = collect_climate_conditions_data()
    if is_climate_conditions_block_filled(climate_data):
        climate_error = validate_climate_conditions_data(climate_data)
        if climate_error:
            messagebox.showwarning("Ошибка", climate_error)
            return
        append_climate_conditions_xml(conclusion, climate_data)
    if climate_data.get("note"):
        ET.SubElement(conclusion, 'ClimateConditionsNote').text = climate_data["note"]

    designer_items = []
    for row in designer_rows:
        designer_data = collect_designer_row_data(row)
        if is_designer_entity_filled(designer_data):
            designer_items.append(designer_data)
    for idx, designer_data in enumerate(designer_items, start=1):
        designer_error = validate_designer_entity_data(designer_data, idx)
        if designer_error:
            messagebox.showwarning("Ошибка", designer_error)
            return
    if designer_items:
        append_designers_xml(conclusion, designer_items)

    eepd_use_items = []
    for row in eepd_use_rows:
        eepd_data = collect_eepd_use_data(row)
        if is_eepd_use_filled(eepd_data):
            eepd_use_items.append(eepd_data)
    for idx, eepd_data in enumerate(eepd_use_items, start=1):
        eepd_error = validate_eepd_use_data(eepd_data, idx)
        if eepd_error:
            messagebox.showwarning("Ошибка", eepd_error)
            return
    if eepd_use_items:
        append_eepd_use_xml(conclusion, eepd_use_items)

    survey_address_items = []
    for row in engineering_survey_address_rows:
        survey_data = collect_engineering_survey_address_data(row)
        if is_engineering_survey_address_filled(survey_data):
            survey_address_items.append(survey_data)
    for idx, survey_data in enumerate(survey_address_items, start=1):
        survey_error = validate_engineering_survey_address_data(survey_data, idx)
        if survey_error:
            messagebox.showwarning("Ошибка", survey_error)
            return
    if survey_address_items:
        append_engineering_survey_addresses_xml(conclusion, survey_address_items)

    engineering_survey_parties = collect_engineering_survey_parties_data(
        engineering_survey_party_rows,
    )
    engineering_survey_parties_error = validate_engineering_survey_parties_rows(
        engineering_survey_party_rows,
    )
    if engineering_survey_parties_error:
        messagebox.showwarning("Ошибка", engineering_survey_parties_error)
        return
    if engineering_survey_parties:
        append_engineering_survey_parties_xml(conclusion, engineering_survey_parties)

    expert_surveys_items = []
    for row in expert_engineering_surveys_rows:
        expert_data = collect_expert_engineering_surveys_data(row)
        if is_expert_engineering_surveys_filled(expert_data):
            expert_surveys_items.append((row, expert_data))
    for idx, (expert_row, expert_data) in enumerate(expert_surveys_items, start=1):
        expert_error = validate_expert_engineering_surveys_row(expert_row, idx)
        if expert_error:
            messagebox.showwarning("Ошибка", expert_error)
            return
    if expert_surveys_items:
        append_expert_engineering_surveys_xml(
            conclusion,
            [expert_data for _, expert_data in expert_surveys_items],
        )

    expert_project_docs_items = []
    for row in expert_project_documents_rows:
        project_docs_data = collect_expert_project_documents_data(row)
        if is_expert_project_documents_filled(project_docs_data):
            expert_project_docs_items.append((row, project_docs_data))
    for idx, (project_row, _) in enumerate(expert_project_docs_items, start=1):
        project_error = validate_expert_project_documents_row(project_row, idx)
        if project_error:
            messagebox.showwarning("Ошибка", project_error)
            return
    if expert_project_docs_items:
        append_expert_project_documents_xml(
            conclusion,
            [project_data for _, project_data in expert_project_docs_items],
        )

    expert_estimate_data = collect_expert_estimate_data(expert_estimate_ui)
    if is_expert_estimate_filled(expert_estimate_data):
        expert_estimate_error = validate_expert_estimate_data(expert_estimate_ui)
        if expert_estimate_error:
            messagebox.showwarning("Ошибка", expert_estimate_error)
            return
        append_expert_estimate_xml(conclusion, expert_estimate_data)

    summary_error = validate_summary_data(summary_ui)
    if summary_error:
        messagebox.showwarning("Ошибка", summary_error)
        return
    append_summary_xml(conclusion, collect_summary_data(summary_ui))

    experts_error = validate_experts_rows(expert_rows)
    if experts_error:
        messagebox.showwarning("Ошибка", experts_error)
        return
    append_experts_xml(conclusion, collect_experts_data(expert_rows))

    write_conclusion_xml(conclusion)
    messagebox.showinfo("Готово", "XML файл успешно создан как 'conclusion.xml'")


def write_conclusion_xml(conclusion, output_path="conclusion.xml"):
    xml_pretty_str = prettify(conclusion)
    full_xml_str = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<?xml-stylesheet type="text/xsl" href="conclusion-01-03.xsl" ?>\n'
    ) + xml_pretty_str
    lines = full_xml_str.splitlines()
    del lines[2]
    with open(output_path, "w", encoding="utf-8") as f:
        f.write('\n'.join(lines))


def run_gui():
    root = tk.Tk()
    root.title("Генератор заключения экспертизы (XML)")
    root.geometry("940x820")
    root.minsize(860, 640)
    setup_app_theme(root)
    
    canvas = tk.Canvas(root, bg="#f3f4f6", highlightthickness=0)
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#f3f4f6")
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
    )
    scrollable_frame.grid_columnconfigure(1, weight=1)
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    root.bind_all("<MouseWheel>", _on_mousewheel)
    
    fields_org = [
        ("Полное наименование юрлица:", "org_full_name", {"required": True}),
        ("ОГРН:", "org_ogrn", {"required": True}),
        ("ИНН:", "org_inn", {"required": True}),
        ("КПП:", "org_kpp", {"required": True}),
        ("Страна:", "country", {"required": True}),
        ("Код региона (например: 77):", "region", {"required": True}),
        ("Город:", "city", {"required": True}),
        ("Улица:", "street", {"required": True}),
        ("Здание/сооружение:", "building", {"required": True}),
        ("Номер помещения:", "room", {"required": True}),
    ]
    
    fields_glin = [
        ("Фамилия:", "family_name", {"required": True}),
        ("Имя:", "first_name", {"required": True}),
        ("Отчество:", "middle_name", {"optional": True}),
        ("Должность:", "position", {"required": True}),
    ]
    
    entries_org = {}
    entries_glin = {}
    current_row = 0
    
    current_row = create_section_title(
        scrollable_frame,
        "Сведения об организации по проведению экспертизы",
        current_row,
    )
    current_row = create_form_legend(scrollable_frame, current_row)
    
    for field in fields_org:
        label_text, field_name, meta = _parse_field_spec(field)
        create_field_label(
            scrollable_frame,
            label_text.rstrip(":"),
            current_row,
            required=meta.get("required", False),
            optional=meta.get("optional", False),
        )
        entry = tk.Entry(scrollable_frame, width=60, font=UI_FONT)
        entry.grid(row=current_row, column=1, padx=UI_PAD_X, pady=UI_PAD_Y, sticky="w")
        entries_org[field_name] = entry
        current_row += 1
    
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
    
    current_row = create_section_title(
        scrollable_frame,
        "Сведения о лице, утвердившем заключение",
        current_row,
    )
    
    for field in fields_glin:
        label_text, field_name, meta = _parse_field_spec(field)
        create_field_label(
            scrollable_frame,
            label_text.rstrip(":"),
            current_row,
            required=meta.get("required", False),
            optional=meta.get("optional", False),
        )
        entry = tk.Entry(scrollable_frame, width=60, font=UI_FONT)
        entry.grid(row=current_row, column=1, padx=UI_PAD_X, pady=UI_PAD_Y, sticky="w")
        entries_glin[field_name] = entry
        current_row += 1
    
    entry_family_name = entries_glin["family_name"]
    entry_first_name = entries_glin["first_name"]
    entry_middle_name = entries_glin["middle_name"]
    entry_position = entries_glin["position"]
    
    current_row = create_section_title(
        scrollable_frame,
        "Сведения об объекте экспертизы",
        current_row,
    )
    
    examination_object_fields = [
        ("Форма экспертизы", EXAMINATION_FORM_OPTIONS, "Государственная", {"required": True}),
        ("Результат экспертизы", EXAMINATION_RESULT_OPTIONS, "Положительный", {"required": True}),
        ("Вид объекта экспертизы", EXAMINATION_OBJECT_TYPE_OPTIONS, "Проектная документация", {"required": True}),
        ("Вид работ", CONSTRUCTION_TYPE_OPTIONS, "Строительство", {"optional": True}),
        ("Вид экспертизы", EXAMINATION_STAGE_OPTIONS, "Первичная", {"optional": True}),
    ]
    
    combo_examination_form, var_examination_form = create_combobox(
        scrollable_frame, EXAMINATION_FORM_OPTIONS, "Государственная"
    )
    combo_examination_result, var_examination_result = create_combobox(
        scrollable_frame, EXAMINATION_RESULT_OPTIONS, "Положительный"
    )
    combo_examination_object_type, var_examination_object_type = create_combobox(
        scrollable_frame, EXAMINATION_OBJECT_TYPE_OPTIONS, "Проектная документация"
    )
    combo_construction_type, var_construction_type = create_combobox(
        scrollable_frame, CONSTRUCTION_TYPE_OPTIONS, "Строительство"
    )
    combo_examination_stage, var_examination_stage = create_combobox(
        scrollable_frame, EXAMINATION_STAGE_OPTIONS, "Первичная"
    )
    
    combos = [
        combo_examination_form,
        combo_examination_result,
        combo_examination_object_type,
        combo_construction_type,
        combo_examination_stage,
    ]
    
    for (label_text, _, _, meta), combo in zip(examination_object_fields, combos):
        create_field_label(
            scrollable_frame,
            label_text,
            current_row,
            required=meta.get("required", False),
            optional=meta.get("optional", False),
        )
        combo.grid(row=current_row, column=1, padx=UI_PAD_X, pady=UI_PAD_Y, sticky="w")
        current_row += 1
    
    create_field_label(scrollable_frame, "Предмет экспертизы", current_row, required=True)
    
    subjects_frame = tk.Frame(scrollable_frame)
    subjects_frame.grid(row=current_row, column=1, padx=10, pady=5, sticky="w")
    current_row += 1
    
    examination_type_rows = []
    
    def add_subject():
        row_frame = tk.Frame(subjects_frame)
        row_frame.pack(fill="x", pady=2)
        add_examination_type_row(scrollable_frame, row_frame, examination_type_rows)
        default_subject = (
            "Оценка соответствия результатов инженерных изысканий требованиям технических регламентов "
            "(абзац 1 пункта 5 статьи 49 Градостроительного кодекса Российской Федерации)"
        )
        examination_type_rows[-1]["var"].set(default_subject)
    
    add_subject()
    
    create_secondary_button(
        scrollable_frame,
        "+ Добавить предмет",
        add_subject,
        row=current_row,
        column=1,
        sticky="w",
        padx=UI_PAD_X,
        pady=UI_PAD_Y,
    )
    current_row += 1
    
    create_field_label(
        scrollable_frame,
        "Дополнительные сведения о виде экспертизы",
        current_row,
        optional=True,
    )
    text_stage_note = tk.Text(scrollable_frame, width=60, height=3, font=UI_FONT)
    text_stage_note.grid(row=current_row, column=1, padx=UI_PAD_X, pady=UI_PAD_Y, sticky="w")
    current_row += 1
    
    create_field_label(
        scrollable_frame,
        "Наименование объекта экспертизы",
        current_row,
        required=True,
    )
    text_name = tk.Text(scrollable_frame, width=60, height=3, font=UI_FONT)
    text_name.insert("1.0", "Стройка")
    text_name.grid(row=current_row, column=1, padx=10, pady=5, sticky="w")
    current_row += 1
    
    combo_project_im, var_project_documentation_im = create_combobox(scrollable_frame, IM_OPTIONS, "Да")
    combo_engineering_im, var_engineering_surveys_im = create_combobox(scrollable_frame, IM_OPTIONS, "Да")
    
    im_fields = [
        (
            "Сведения о подготовке проектной документации в форме информационной модели",
            combo_project_im,
        ),
        (
            "Сведения о подготовке отчётной документации об инженерных изысканиях в форме ИМ",
            combo_engineering_im,
        ),
    ]
    
    for label_text, combo in im_fields:
        create_field_label(scrollable_frame, label_text, current_row, optional=True)
        combo.grid(row=current_row, column=1, padx=UI_PAD_X, pady=UI_PAD_Y, sticky="w")
        current_row += 1
    
    current_row = create_section_title(
        scrollable_frame,
        "Документы, рассмотренные в рамках экспертизы",
        current_row,
    )
    
    documents_container = tk.Frame(scrollable_frame)
    documents_container.grid(row=current_row, column=0, columnspan=2, sticky="ew", padx=10)
    current_row += 1
    
    document_rows = []
    
    
    def add_document():
        add_document_block(documents_container, document_rows)
    
    
    add_document_block(
        documents_container,
        document_rows,
        {
            "doc_type_label": DEFAULT_DOC_TYPE_LABEL,
            "doc_name": "123",
            "doc_number": "123",
            "doc_date": "21.09.2004",
            "doc_changes": "123",
            "doc_author": "ппп",
        },
    )
    
    create_secondary_button(
        scrollable_frame,
        "+ Добавить документ",
        add_document,
        row=current_row,
        column=0,
        columnspan=2,
        sticky="w",
        padx=UI_PAD_X,
        pady=UI_PAD_Y,
    )
    current_row += 1
    
    current_row = create_section_title(
        scrollable_frame,
        "Сведения о ранее выданных заключениях экспертизы (необяз.)",
        current_row,
    )
    
    previous_conclusions_container = tk.Frame(scrollable_frame)
    previous_conclusions_container.grid(row=current_row, column=0, columnspan=2, sticky="ew", padx=10)
    current_row += 1
    
    previous_conclusion_rows = []
    previous_simple_conclusion_rows = []
    
    
    def add_previous_conclusion():
        add_previous_conclusion_block(previous_conclusions_container, previous_conclusion_rows)
    
    
    create_secondary_button(
        scrollable_frame,
        "+ Добавить заключение",
        add_previous_conclusion,
        row=current_row,
        column=0,
        columnspan=2,
        sticky="w",
        padx=UI_PAD_X,
        pady=UI_PAD_Y,
    )
    current_row += 1
    
    current_row = create_section_title(
        scrollable_frame,
        "Заключения по экспертному сопровождению (необяз.)",
        current_row,
    )
    
    previous_simple_conclusions_container = tk.Frame(scrollable_frame)
    previous_simple_conclusions_container.grid(row=current_row, column=0, columnspan=2, sticky="ew", padx=10)
    current_row += 1
    
    
    def add_previous_simple_conclusion():
        add_previous_simple_conclusion_block(
            previous_simple_conclusions_container,
            previous_simple_conclusion_rows,
        )
    
    
    create_secondary_button(
        scrollable_frame,
        "+ Добавить заключение",
        add_previous_simple_conclusion,
        row=current_row,
        column=0,
        columnspan=2,
        sticky="w",
        padx=UI_PAD_X,
        pady=UI_PAD_Y,
    )
    current_row += 1
    
    current_row = create_section_title(
        scrollable_frame,
        "Сведения об объекте капитального строительства (необяз.)",
        current_row,
    )
    
    capital_object_container = tk.Frame(scrollable_frame, bg="#f3f4f6")
    capital_object_container.grid(row=current_row, column=0, columnspan=2, sticky="ew", padx=10)
    current_row += 1
    
    create_packed_caption(capital_object_container, "Наименование объекта")
    entry_capital_object_name = tk.Entry(capital_object_container, width=70, font=UI_FONT)
    entry_capital_object_name.pack(anchor="w", pady=(2, 8))
    
    capital_object_addresses_frame = tk.Frame(capital_object_container)
    capital_object_addresses_frame.pack(fill="x", pady=(0, 8))
    capital_object_address_list_frame = tk.Frame(capital_object_addresses_frame)
    capital_object_address_list_frame.pack(fill="x")
    capital_object_address_rows = []
    
    
    def add_capital_object_address():
        add_address_block(capital_object_address_list_frame, capital_object_address_rows)
    
    
    add_capital_object_address()
    tk.Button(
        capital_object_addresses_frame,
        text="+ Добавить адрес",
        command=add_capital_object_address,
    ).pack(anchor="w", pady=(4, 0))
    
    create_packed_caption(capital_object_container, "Вид объекта", pady=(8, 0))
    combo_capital_object_type, var_capital_object_type = create_combobox(
        capital_object_container,
        CAPITAL_OBJECT_TYPE_OPTIONS,
        "Объект производственного назначения",
    )
    combo_capital_object_type.pack(anchor="w", pady=(2, 8))
    
    create_packed_caption(capital_object_container, "Код классификатора объектов капитального строительства")
    entry_capital_functions_class = tk.Entry(capital_object_container, width=70, font=UI_FONT)
    entry_capital_functions_class.pack(anchor="w", pady=(2, 8))
    
    tk.Label(
        capital_object_container,
        text="Технико-экономические показатели:",
        font=("Arial", 9, "bold"),
    ).pack(anchor="w", pady=(4, 0))
    capital_object_tei_container = tk.Frame(capital_object_container)
    capital_object_tei_container.pack(fill="x", pady=4)
    capital_object_tei_rows = []
    
    
    def add_capital_object_tei():
        add_tei_row(capital_object_tei_container, capital_object_tei_rows)
    
    
    add_tei_row(capital_object_tei_container, capital_object_tei_rows)
    
    btn_add_capital_tei = tk.Button(
        capital_object_container,
        text="+ Добавить показатель",
        command=add_capital_object_tei,
    )
    btn_add_capital_tei.pack(anchor="w", pady=(0, 8))
    
    tk.Label(
        capital_object_container,
        text="Описание составной части сложного объекта:",
        font=("Arial", 9, "bold"),
    ).pack(anchor="w", pady=(8, 0))
    capital_object_parts_container = tk.Frame(capital_object_container)
    capital_object_parts_container.pack(fill="x", pady=4)
    capital_object_part_rows = []
    
    
    def add_capital_object_part():
        add_object_part_block(capital_object_parts_container, capital_object_part_rows)
    
    
    btn_add_capital_part = tk.Button(
        capital_object_container,
        text="+ Добавить составную часть",
        command=add_capital_object_part,
    )
    btn_add_capital_part.pack(anchor="w", pady=(0, 8))
    
    current_row = create_section_title(
        scrollable_frame,
        "Сведения о необходимости проведения экологической экспертизы",
        current_row,
    )
    
    create_field_label(
        scrollable_frame,
        "Отметка о необходимости проведения экологической экспертизы",
        current_row,
        required=True,
    )
    combo_need_expertise, var_need_expertise = create_combobox(scrollable_frame, IM_OPTIONS, "Да")
    combo_need_expertise.grid(row=current_row, column=1, sticky="w", padx=UI_PAD_X, pady=UI_PAD_Y)
    current_row += 1
    
    create_field_label(
        scrollable_frame,
        "Обоснование необходимости (отсутствия необходимости) проведения экологической экспертизы",
        current_row,
        optional=True,
    )
    text_ecology_comment = tk.Text(scrollable_frame, width=60, height=3, font=UI_FONT)
    text_ecology_comment.grid(row=current_row, column=1, sticky="w", padx=UI_PAD_X, pady=UI_PAD_Y)
    current_row += 1
    
    current_row = create_section_title(
        scrollable_frame,
        "Кадастровый номер земельного участка (необяз.)",
        current_row,
    )
    
    cadastral_numbers_container = tk.Frame(scrollable_frame)
    cadastral_numbers_container.grid(row=current_row, column=0, columnspan=2, sticky="ew", padx=10)
    current_row += 1
    cadastral_number_rows = []
    
    
    def add_cadastral_number():
        add_cadastral_number_row(cadastral_numbers_container, cadastral_number_rows)
    
    
    add_cadastral_number_row(cadastral_numbers_container, cadastral_number_rows)
    tk.Button(
        scrollable_frame,
        text="+ Добавить",
        command=add_cadastral_number,
    ).grid(row=current_row, column=0, columnspan=2, sticky="w", padx=10, pady=5)
    current_row += 1
    
    current_row = create_section_title(
        scrollable_frame,
        "Сведения о заявителе",
        current_row,
    )
    
    declarant_type_frame = tk.Frame(scrollable_frame)
    declarant_type_frame.grid(row=current_row, column=0, columnspan=2, sticky="w", padx=10)
    current_row += 1
    
    var_declarant_type = tk.StringVar(value="organization")
    declarant_panels = {}
    
    
    def switch_declarant_panel():
        selected = var_declarant_type.get()
        for key, panel in declarant_panels.items():
            if key == selected:
                panel.pack(fill="x", pady=4)
            else:
                panel.pack_forget()
    
    
    for value, label in DECLARANT_TYPE_OPTIONS:
        tk.Radiobutton(
            declarant_type_frame,
            text=label,
            variable=var_declarant_type,
            value=value,
            command=switch_declarant_panel,
            anchor="w",
        ).pack(fill="x", pady=1)
    
    declarant_details_frame = tk.Frame(scrollable_frame)
    declarant_details_frame.grid(row=current_row, column=0, columnspan=2, sticky="ew", padx=10)
    current_row += 1
    
    declarant_org_panel = tk.Frame(declarant_details_frame)
    _, declarant_org_entries = create_inline_form(
        declarant_org_panel,
        [
            ("Полное наименование юридического лица", "org_full_name", {"required": True}),
            ("ОГРН", "org_ogrn", {"required": True}),
            ("ИНН", "org_inn", {"required": True}),
            ("КПП", "org_kpp", {"required": True}),
        ],
    )
    _, declarant_org_address_entries = create_inline_form(
        declarant_org_panel,
        CAPITAL_OBJECT_ADDRESS_FIELDS,
        title="Адрес (местонахождение) юридического лица",
    )
    create_packed_caption(declarant_org_panel, "Адрес электронной почты", optional=True, pady=(4, 0))
    declarant_org_email = tk.Entry(declarant_org_panel, width=60, font=UI_FONT)
    declarant_org_email.pack(anchor="w", pady=(2, 4))
    declarant_panels["organization"] = declarant_org_panel
    
    declarant_foreign_panel = tk.Frame(declarant_details_frame)
    _, declarant_foreign_entries = create_inline_form(
        declarant_foreign_panel,
        [
            ("Полное наименование:", "org_full_name"),
            ("ИНН:", "org_inn"),
            ("КПП:", "org_kpp"),
        ],
    )
    _, declarant_foreign_address_entries = create_inline_form(
        declarant_foreign_panel,
        CAPITAL_OBJECT_ADDRESS_FIELDS,
        title="Адрес (местонахождение) филиала или представительства",
    )
    tk.Label(declarant_foreign_panel, text="Адрес электронной почты:").pack(anchor="w", pady=(4, 0))
    declarant_foreign_email = tk.Entry(declarant_foreign_panel, width=60)
    declarant_foreign_email.pack(anchor="w", pady=(2, 4))
    declarant_panels["foreign_organization"] = declarant_foreign_panel
    
    declarant_ip_panel = tk.Frame(declarant_details_frame)
    _, declarant_ip_entries = create_inline_form(
        declarant_ip_panel,
        [
            ("Фамилия:", "family_name"),
            ("Имя:", "first_name"),
            ("Отчество:", "second_name"),
            ("ОГРНИП:", "ogrnip"),
        ],
    )
    _, declarant_ip_post_address_entries = create_inline_form(
        declarant_ip_panel,
        POST_ADDRESS_FIELDS,
        title="Почтовый адрес индивидуального предпринимателя",
    )
    tk.Label(declarant_ip_panel, text="Адрес электронной почты:").pack(anchor="w", pady=(4, 0))
    declarant_ip_email = tk.Entry(declarant_ip_panel, width=60)
    declarant_ip_email.pack(anchor="w", pady=(2, 4))
    declarant_panels["ip"] = declarant_ip_panel
    
    declarant_person_panel = tk.Frame(declarant_details_frame)
    _, declarant_person_entries = create_inline_form(
        declarant_person_panel,
        [
            ("Фамилия:", "family_name"),
            ("Имя:", "first_name"),
            ("Отчество:", "second_name"),
            ("СНИЛС:", "snils"),
        ],
    )
    _, declarant_person_post_address_entries = create_inline_form(
        declarant_person_panel,
        POST_ADDRESS_FIELDS,
        title="Почтовый адрес физического лица",
    )
    tk.Label(declarant_person_panel, text="Адрес электронной почты:").pack(anchor="w", pady=(4, 0))
    declarant_person_email = tk.Entry(declarant_person_panel, width=60)
    declarant_person_email.pack(anchor="w", pady=(2, 4))
    declarant_panels["person"] = declarant_person_panel
    
    switch_declarant_panel()
    
    current_row = create_section_title(
        scrollable_frame,
        "Застройщик / техзаказчик проектной документации (необяз.)",
        current_row,
    )
    
    project_documents_party_container = tk.Frame(scrollable_frame)
    project_documents_party_container.grid(row=current_row, column=0, columnspan=2, sticky="ew", padx=10)
    current_row += 1
    project_documents_party_rows = []
    
    
    def add_project_documents_party():
        add_project_documents_party_block(
            project_documents_party_container,
            project_documents_party_rows,
        )
    
    
    tk.Button(
        scrollable_frame,
        text="+ Добавить",
        command=add_project_documents_party,
    ).grid(row=current_row, column=0, columnspan=2, sticky="w", padx=10, pady=5)
    current_row += 1
    
    current_row = create_section_title(
        scrollable_frame,
        "Сведения об источнике финансирования",
        current_row,
    )
    
    finance_container = tk.Frame(scrollable_frame)
    finance_container.grid(row=current_row, column=0, columnspan=2, sticky="ew", padx=10)
    current_row += 1
    finance_rows = []
    
    
    def add_finance():
        add_finance_block(finance_container, finance_rows)
    
    
    add_finance_block(finance_container, finance_rows)
    tk.Button(
        scrollable_frame,
        text="+ Добавить источник финансирования",
        command=add_finance,
    ).grid(row=current_row, column=0, columnspan=2, sticky="w", padx=10, pady=5)
    current_row += 1
    
    create_field_label(
        scrollable_frame,
        "Дополнительные сведения об источнике финансирования",
        current_row,
        optional=True,
    )
    text_finance_comment = tk.Text(scrollable_frame, width=60, height=3, font=UI_FONT)
    text_finance_comment.grid(row=current_row, column=1, sticky="w", padx=UI_PAD_X, pady=UI_PAD_Y)
    current_row += 1
    
    current_row = create_section_title(
        scrollable_frame,
        "Сведения о сметной стоимости (необяз.)",
        current_row,
    )
    
    create_field_label(
        scrollable_frame,
        "Валюта, в которой производится расчёт сметной стоимости",
        current_row,
        optional=True,
    )
    entry_estimated_currency = tk.Entry(scrollable_frame, width=60, font=UI_FONT)
    entry_estimated_currency.grid(row=current_row, column=1, sticky="w", padx=10, pady=5)
    current_row += 1
    
    estimated_cost_mode_frame = tk.Frame(scrollable_frame)
    estimated_cost_mode_frame.grid(row=current_row, column=0, columnspan=2, sticky="w", padx=10)
    current_row += 1
    
    var_estimated_cost_mode = tk.StringVar(value="complete")
    estimated_cost_panels = {}
    
    estimated_cost_details_frame = tk.Frame(scrollable_frame)
    estimated_cost_details_frame.grid(row=current_row, column=0, columnspan=2, sticky="ew", padx=10)
    current_row += 1
    
    
    def switch_estimated_cost_panel():
        selected = var_estimated_cost_mode.get()
        for key, panel in estimated_cost_panels.items():
            if key == selected:
                panel.pack(fill="x", pady=4)
            else:
                panel.pack_forget()
    
    
    for value, label in ESTIMATED_COST_MODE_OPTIONS:
        tk.Radiobutton(
            estimated_cost_mode_frame,
            text=label,
            variable=var_estimated_cost_mode,
            value=value,
            command=switch_estimated_cost_panel,
            anchor="w",
            wraplength=700,
            justify="left",
        ).pack(fill="x", pady=2)
    
    complete_cost_panel = tk.Frame(estimated_cost_details_frame)
    tk.Label(
        complete_cost_panel,
        text="Сметная стоимость на дату представления документации для проведения экспертизы:",
    ).pack(anchor="w", pady=(4, 0))
    entry_complete_cost_before = tk.Entry(complete_cost_panel, width=30)
    entry_complete_cost_before.pack(anchor="w", pady=(2, 8))
    tk.Label(
        complete_cost_panel,
        text="Сметная стоимость на дату утверждения заключения экспертизы:",
    ).pack(anchor="w")
    entry_complete_cost_post = tk.Entry(complete_cost_panel, width=30)
    entry_complete_cost_post.pack(anchor="w", pady=(2, 4))
    estimated_cost_panels["complete"] = complete_cost_panel
    
    complex_cost_panel = tk.Frame(estimated_cost_details_frame)
    _, complex_cost_before_entries = create_complex_cost_form(
        complex_cost_panel,
        "На дату представления документации для проведения экспертизы",
    )
    _, complex_cost_post_entries = create_complex_cost_form(
        complex_cost_panel,
        "По результатам проверки достоверности определения сметной стоимости",
    )
    estimated_cost_panels["complex"] = complex_cost_panel
    
    switch_estimated_cost_panel()
    
    current_row = create_section_title(
        scrollable_frame,
        "Сведения о природных и техногенных условиях (необяз.)",
        current_row,
    )
    
    climate_container = tk.Frame(scrollable_frame)
    climate_container.grid(row=current_row, column=0, columnspan=2, sticky="ew", padx=10)
    current_row += 1
    
    climate_district_rows = []
    geological_conditions_rows = []
    wind_district_rows = []
    snow_district_rows = []
    seismic_activity_rows = []
    
    
    def add_climate_section(parent, title, rows_list, options):
        section = ttk.LabelFrame(parent, text=title, style="Section.TLabelframe")
        section.pack(fill="x", pady=6)
        list_frame = tk.Frame(section)
        list_frame.pack(fill="x")
    
        def add_row():
            add_climate_value_row(list_frame, rows_list, options)
    
        add_row()
        tk.Button(section, text="+ Добавить", command=add_row).pack(anchor="w", pady=(4, 0))
        return section
    
    
    add_climate_section(
        climate_container,
        "Климатический район, подрайон",
        climate_district_rows,
        CLIMATE_DISTRICT_OPTIONS,
    )
    add_climate_section(
        climate_container,
        "Категория сложности инженерно-геологических (геокриологических) условий",
        geological_conditions_rows,
        GEOLOGICAL_CONDITIONS_OPTIONS,
    )
    add_climate_section(
        climate_container,
        "Ветровой район",
        wind_district_rows,
        WIND_DISTRICT_OPTIONS,
    )
    add_climate_section(
        climate_container,
        "Снеговой район",
        snow_district_rows,
        SNOW_DISTRICT_OPTIONS,
    )
    add_climate_section(
        climate_container,
        "Интенсивность сейсмических воздействий",
        seismic_activity_rows,
        SEISMIC_ACTIVITY_OPTIONS,
    )
    
    seismic_calc_frame = tk.LabelFrame(
        climate_container,
        text="Расчётное значение интенсивности сейсмических воздействий",
        padx=6,
        pady=6,
    )
    seismic_calc_frame.pack(fill="x", pady=6)
    var_include_seismic_calc = tk.BooleanVar(value=False)
    
    
    def toggle_seismic_calc_fields():
        state = "normal" if var_include_seismic_calc.get() else "disabled"
        entry_seismic_calc_min.config(state=state)
        entry_seismic_calc_max.config(state=state)
    
    
    tk.Checkbutton(
        seismic_calc_frame,
        text="Указать расчётное значение",
        variable=var_include_seismic_calc,
        command=toggle_seismic_calc_fields,
    ).pack(anchor="w", pady=(0, 4))
    tk.Label(seismic_calc_frame, text="Минимальное значение:").pack(anchor="w")
    entry_seismic_calc_min = tk.Entry(seismic_calc_frame, width=30, state="disabled")
    entry_seismic_calc_min.pack(anchor="w", pady=(2, 6))
    tk.Label(seismic_calc_frame, text="Максимальное значение (необязательно):").pack(anchor="w")
    entry_seismic_calc_max = tk.Entry(seismic_calc_frame, width=30, state="disabled")
    entry_seismic_calc_max.pack(anchor="w", pady=(2, 4))
    
    create_field_label(
        scrollable_frame,
        "Дополнительные сведения о природных и техногенных условиях",
        current_row,
        optional=True,
    )
    text_climate_conditions_note = tk.Text(scrollable_frame, width=60, height=3, font=UI_FONT)
    text_climate_conditions_note.grid(row=current_row, column=1, sticky="w", padx=10, pady=5)
    current_row += 1
    
    current_row = create_section_title(
        scrollable_frame,
        "Сведения о проектировщике (необяз.)",
        current_row,
    )
    
    designers_container = tk.Frame(scrollable_frame)
    designers_container.grid(row=current_row, column=0, columnspan=2, sticky="ew", padx=10)
    current_row += 1
    designer_rows = []
    
    
    def add_designer():
        add_designer_block(designers_container, designer_rows)
    
    
    tk.Button(
        scrollable_frame,
        text="+ Добавить проектировщика",
        command=add_designer,
    ).grid(row=current_row, column=0, columnspan=2, sticky="w", padx=10, pady=5)
    current_row += 1
    
    current_row = create_section_title(
        scrollable_frame,
        "Использование типовой / ЭПД (необяз.)",
        current_row,
    )
    
    eepd_use_container = tk.Frame(scrollable_frame)
    eepd_use_container.grid(row=current_row, column=0, columnspan=2, sticky="ew", padx=10)
    current_row += 1
    eepd_use_rows = []
    
    
    def add_eepd_use():
        add_eepd_use_block(eepd_use_container, eepd_use_rows)
    
    
    tk.Button(
        scrollable_frame,
        text="+ Добавить сведения об использовании ЭПД",
        command=add_eepd_use,
    ).grid(row=current_row, column=0, columnspan=2, sticky="w", padx=10, pady=5)
    current_row += 1
    
    current_row = create_section_title(
        scrollable_frame,
        "Местоположение района инженерных изысканий (необяз.)",
        current_row,
    )
    
    engineering_survey_address_container = tk.Frame(scrollable_frame)
    engineering_survey_address_container.grid(row=current_row, column=0, columnspan=2, sticky="ew", padx=10)
    current_row += 1
    engineering_survey_address_rows = []
    
    
    def add_engineering_survey_address():
        add_engineering_survey_address_block(
            engineering_survey_address_container,
            engineering_survey_address_rows,
        )
    
    
    tk.Button(
        scrollable_frame,
        text="+ Добавить местоположение района изысканий",
        command=add_engineering_survey_address,
    ).grid(row=current_row, column=0, columnspan=2, sticky="w", padx=10, pady=5)
    current_row += 1
    
    current_row = create_section_title(
        scrollable_frame,
        "Застройщик / техзаказчик инженерных изысканий (необяз.)",
        current_row,
    )
    
    engineering_survey_party_container = tk.Frame(scrollable_frame)
    engineering_survey_party_container.grid(row=current_row, column=0, columnspan=2, sticky="ew", padx=10)
    current_row += 1
    engineering_survey_party_rows = []
    
    
    def add_engineering_survey_party():
        add_engineering_survey_party_block(
            engineering_survey_party_container,
            engineering_survey_party_rows,
        )
    
    
    tk.Button(
        scrollable_frame,
        text="+ Добавить",
        command=add_engineering_survey_party,
    ).grid(row=current_row, column=0, columnspan=2, sticky="w", padx=10, pady=5)
    current_row += 1
    
    current_row = create_section_title(
        scrollable_frame,
        "Экспертиза результатов инженерных изысканий (необяз.)",
        current_row,
    )
    
    expert_engineering_surveys_container = tk.Frame(scrollable_frame)
    expert_engineering_surveys_container.grid(row=current_row, column=0, columnspan=2, sticky="ew", padx=10)
    current_row += 1
    expert_engineering_surveys_rows = []
    
    
    def add_expert_engineering_surveys():
        add_expert_engineering_surveys_block(
            expert_engineering_surveys_container,
            expert_engineering_surveys_rows,
        )
    
    
    tk.Button(
        scrollable_frame,
        text="+ Добавить сведения экспертизы инженерных изысканий",
        command=add_expert_engineering_surveys,
    ).grid(row=current_row, column=0, columnspan=2, sticky="w", padx=10, pady=5)
    current_row += 1
    
    current_row = create_section_title(
        scrollable_frame,
        "Экспертиза проектной документации (необяз.)",
        current_row,
    )
    
    expert_project_documents_container = tk.Frame(scrollable_frame)
    expert_project_documents_container.grid(row=current_row, column=0, columnspan=2, sticky="ew", padx=10)
    current_row += 1
    expert_project_documents_rows = []
    
    
    def add_expert_project_documents():
        add_expert_project_documents_block(
            expert_project_documents_container,
            expert_project_documents_rows,
        )
    
    
    tk.Button(
        scrollable_frame,
        text="+ Добавить сведения экспертизы проектной документации",
        command=add_expert_project_documents,
    ).grid(row=current_row, column=0, columnspan=2, sticky="w", padx=10, pady=5)
    current_row += 1
    
    current_row = create_section_title(
        scrollable_frame,
        "Проверка сметной стоимости — сведения эксперта (необяз.)",
        current_row,
    )
    
    expert_estimate_frame = tk.Frame(scrollable_frame)
    expert_estimate_frame.grid(row=current_row, column=0, columnspan=2, sticky="ew", padx=10)
    current_row += 1
    expert_estimate_ui = build_expert_estimate_ui(expert_estimate_frame)
    
    current_row = create_section_title(
        scrollable_frame,
        "Выводы по результатам проведения экспертизы",
        current_row,
    )
    
    summary_frame = tk.Frame(scrollable_frame)
    summary_frame.grid(row=current_row, column=0, columnspan=2, sticky="ew", padx=10)
    current_row += 1
    summary_ui = build_summary_ui(summary_frame)
    
    current_row = create_section_title(
        scrollable_frame,
        "Эксперты, подписавшие заключение",
        current_row,
    )
    
    experts_container = tk.Frame(scrollable_frame)
    experts_container.grid(row=current_row, column=0, columnspan=2, sticky="ew", padx=10)
    current_row += 1
    expert_rows = []
    
    
    def add_expert():
        add_expert_block(experts_container, expert_rows)
    
    
    tk.Button(
        scrollable_frame,
        text="+ Добавить эксперта",
        command=add_expert,
    ).grid(row=current_row, column=0, columnspan=2, sticky="w", padx=10, pady=5)
    current_row += 1
    
    create_primary_button(
        scrollable_frame,
        "Создать XML",
        generate_xml,
        row=current_row,
        column=0,
        columnspan=2,
        pady=24,
        padx=UI_PAD_X,
        sticky="w",
    )
    
if __name__ == "__main__":
    run_gui()
    root.mainloop()
