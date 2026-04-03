import type { ColumnMapping, ColumnPreview } from "../../../services/api/clientApi";

export interface SystemFieldDef {
  value: string;
  label: string;
  required: boolean;
}

export const SYSTEM_FIELDS: SystemFieldDef[] = [
  { value: "full_name", label: "ПІБ", required: true },
  { value: "phone1", label: "Телефон 1", required: true },
  { value: "phone2", label: "Телефон 2", required: false },
  { value: "addr1_street", label: "Вулиця 1", required: true },
  { value: "addr1_house", label: "Будинок 1", required: true },
  { value: "addr1_apartment", label: "Квартира 1", required: false },
  { value: "addr1_entrance", label: "Під'їзд 1", required: false },
  { value: "addr1_floor", label: "Поверх 1", required: false },
  { value: "addr1_intercom", label: "Домофон 1", required: false },
  { value: "addr1_district", label: "Район 1", required: false },
  { value: "addr1_comment", label: "Коментар 1", required: false },
  { value: "addr2_street", label: "Вулиця 2", required: false },
  { value: "addr2_house", label: "Будинок 2", required: false },
  { value: "addr2_apartment", label: "Квартира 2", required: false },
  { value: "addr2_entrance", label: "Під'їзд 2", required: false },
  { value: "addr2_floor", label: "Поверх 2", required: false },
  { value: "addr2_intercom", label: "Домофон 2", required: false },
  { value: "addr2_district", label: "Район 2", required: false },
  { value: "addr2_comment", label: "Коментар 2", required: false },
];

export const REQUIRED_SYSTEM_FIELDS = SYSTEM_FIELDS.filter((f) => f.required).map((f) => f.value);

const FIELD_KEYWORDS: Record<string, string[]> = {
  "піб": ["full_name"],
  "прізвище": ["full_name"],
  "ім'я": ["full_name"],
  "имя": ["full_name"],
  "фио": ["full_name"],
  "фамилия": ["full_name"],
  "клієнт": ["full_name"],
  "клиент": ["full_name"],
  "name": ["full_name"],
  "телефон": ["phone1", "phone2"],
  "phone": ["phone1", "phone2"],
  "тел": ["phone1", "phone2"],
  "номер": ["phone1", "phone2"],
  "вулиця": ["addr1_street", "addr2_street"],
  "улица": ["addr1_street", "addr2_street"],
  "street": ["addr1_street", "addr2_street"],
  "будинок": ["addr1_house", "addr2_house"],
  "дом": ["addr1_house", "addr2_house"],
  "house": ["addr1_house", "addr2_house"],
  "квартира": ["addr1_apartment", "addr2_apartment"],
  "кв": ["addr1_apartment", "addr2_apartment"],
  "під'їзд": ["addr1_entrance", "addr2_entrance"],
  "подъезд": ["addr1_entrance", "addr2_entrance"],
  "поверх": ["addr1_floor", "addr2_floor"],
  "этаж": ["addr1_floor", "addr2_floor"],
  "домофон": ["addr1_intercom", "addr2_intercom"],
  "район": ["addr1_district", "addr2_district"],
  "коментар": ["addr1_comment", "addr2_comment"],
  "комментарий": ["addr1_comment", "addr2_comment"],
  "примітка": ["addr1_comment", "addr2_comment"],
};

export function autoMatchColumns(columns: ColumnPreview[]): ColumnMapping {
  const mapping: ColumnMapping = {};
  const usedFields = new Set<string>();

  for (const col of columns) {
    if (!col.header) continue;
    const headerLower = col.header.toLowerCase().trim();

    for (const [keyword, candidates] of Object.entries(FIELD_KEYWORDS)) {
      if (!headerLower.includes(keyword)) continue;

      const field = candidates.find((f) => !usedFields.has(f));
      if (field) {
        mapping[col.index] = field;
        usedFields.add(field);
        break;
      }
    }
  }

  return mapping;
}

export function getColumnLetter(index: number): string {
  let result = "";
  let n = index;
  while (n > 0) {
    n--;
    result = String.fromCharCode(65 + (n % 26)) + result;
    n = Math.floor(n / 26);
  }
  return result;
}
