export interface Partner {
  id: string;
  name: string;
  /** Дополнительная строка под названием (филиал, торговая марка) */
  subtitle?: string;
  inn: string;
}

/** Официальные партнёры и дилеры завода */
export const PARTNERS: Partner[] = [
  {
    id: "keaz",
    name: "АО «КЭАЗ»",
    subtitle: "АО «Курский электроаппаратный завод»",
    inn: "4629003691",
  },
  {
    id: "elektrotekhnik",
    name: "ПО «Электротехник»",
    inn: "7721249325",
  },
  {
    id: "techenergo",
    name: "ООО «МФК Техэнерго»",
    inn: "7715215141",
  },
  {
    id: "etk-spektr",
    name: "ООО «ЭТК Спектр»",
    inn: "9702004884",
  },
  {
    id: "tpo-ril",
    name: "ООО «ТПО РИЛ»",
    inn: "7839504428",
  },
  {
    id: "trk",
    name: "ООО «ТРК»",
    subtitle: "Трансрейл",
    inn: "7705553913",
  },
  {
    id: "vesta",
    name: "ООО «Веста»",
    inn: "7805326544",
  },
];
