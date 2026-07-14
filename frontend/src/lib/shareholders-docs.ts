export interface PriceListItem {
  id: number;
  name: string;
  price: string;
  price_without_vat: string;
  nominal_current_a: number | null;
  product_type: string;
  notes: string;
  sort_order: number;
}

export interface PriceListSection {
  id: number;
  name: string;
  sort_order: number;
  items: PriceListItem[];
}

export interface ShareholderDocument {
  label: string;
  file: string;
  sizeKb?: number;
}

export const CHARTER_DOCUMENTS: ShareholderDocument[] = [
  { label: "Устав", file: "ustav.doc" },
  { label: "Устав — новая редакция", file: "Устав_новая_редакция.doc" },
];

export const AFFILIATED_DOCUMENTS: ShareholderDocument[] = [
  { label: "Список аффилированных лиц на 30.06.2017", file: "Аффилированные_лица_на_30.06.2017.docx", sizeKb: 1079 },
  { label: "Список аффилированных лиц на 30.04.2017", file: "Аффилированные_лица_на_30.04.2017.docx", sizeKb: 1273 },
  { label: "Аффилированные лица на 31.03.2017", file: "Аффилированные_лица_на_30.03.2017.docx", sizeKb: 1154 },
  { label: "Аффилированные лица на 31.12.2016", file: "Аффилированные_лица_на_31.12.2016.docx", sizeKb: 1063 },
  { label: "Аффилированные лица на 30.09.2016", file: "1______________________________30.09.2016.docx", sizeKb: 1122 },
  { label: "Аффилированные лица на 30.06.2016", file: "_____________________________30.06.2016.docx", sizeKb: 1092 },
  { label: "Аффилированные лица на 29.04.2016", file: "_____________________________29.04.2016.docx", sizeKb: 2689 },
  { label: "Список аффилированных лиц на 31.03.2016", file: "____________.________31.03.2016.docx", sizeKb: 1045 },
  { label: "Аффилированные лица на 31.12.2015", file: "____________.________31.12.2015.docx", sizeKb: 1064 },
  { label: "Аффилированные лица на 30.09.2015", file: "____________.________30.09.2015.docx", sizeKb: 1081 },
  { label: "Аффилированные лица на 30.06.2015", file: "1_____________.________30.06.2015.docx", sizeKb: 1300 },
  { label: "Аффилированные лица на 30.04.2015", file: "____________.________30.04.2015.docx", sizeKb: 1344 },
  { label: "Аффилированные лица на 31.03.2015", file: "_____________________________21.03.2015.docx", sizeKb: 1330 },
  { label: "Аффилированные лица на 31.12.2014", file: "____________.________31.12.2014.docx", sizeKb: 1220 },
  { label: "Аффилированные лица на 30.09.2014", file: "____________.________30.09.2014.docx", sizeKb: 1350 },
  { label: "Аффилированные лица на 30.06.2014", file: "_____________________30.06.2014__..docx", sizeKb: 1331 },
  { label: "Аффилированные лица на 30.04.2014", file: "_____.______30.04.2014_..doc", sizeKb: 117 },
  { label: "Аффилированные лица на 31.03.2014", file: "_____________________31.03.2014__..docx", sizeKb: 1627 },
  { label: "Аффилированные лица на 31.12.2013", file: "____________________________31.12.2013__..docx", sizeKb: 1360 },
];

export const DISCLOSURE_DOCUMENTS: ShareholderDocument[] = [
  { label: "Отчёт АО «Электроконтактор» за 2025 г.", file: "Отчет_АО_Электроконтактор_за_2025г..docx", sizeKb: 7830 },
  { label: "Отчёт АО за 2024 г.", file: "Отчет_АО_за_2024.docx", sizeKb: 8983 },
  { label: "Отчёт за 2023 г.", file: "Отчет_за_2023г..docx", sizeKb: 11002 },
  { label: "Отчёт за 2022 г.", file: "Отчет_за_2022г..docx", sizeKb: 10591 },
  { label: "Отчёт акционерного общества за 2020 г.", file: "отчет_акционерного_общества_2020.docx", sizeKb: 9526 },
  { label: "Отчёт собрания за 2019 г.", file: "отчет_собрания_за_2019г..docx", sizeKb: 7751 },
  { label: "Отчёт собрания за 2016 г.", file: "Отчет_собрания_за_2016_г..doc", sizeKb: 214 },
  { label: "Отчёт АО", file: "Отчет_АО.doc", sizeKb: 19363 },
  { label: "Отчёт об итогах голосования", file: "отчет_об_итогах_голосования.docx", sizeKb: 1975 },
  {
    label: "Протокол общего собрания акционеров за 2021 г.",
    file: "Протокол_общего_собрания_акционеров_за_2021г..doc",
    sizeKb: 7688,
  },
  { label: "Протокол общего собрания акционеров", file: "Протокол_общего_собрания_акционеров.docx", sizeKb: 2985 },
  { label: "Протокол годового собрания за 2016 г.", file: "Протокол_годового_собрания_за_2016_г..doc", sizeKb: 116 },
  { label: "Протокол заседания № 11", file: "Протокоол_заседания___11.docx", sizeKb: 2717 },
  { label: "Протокол счётной комиссии", file: "Протокол_счетной_комисии_170329_195141.rtf", sizeKb: 358 },
  { label: "Приложение к раскрытию информации", file: "Doc3.docx", sizeKb: 2173 },
];

export function corporateDocDownloadUrl(category: "affilr" | "raskrinfo" | "charter", file: string): string {
  return `/api/v1/corporate-docs/download/?category=${encodeURIComponent(category)}&file=${encodeURIComponent(file)}`;
}
