export interface Partner {
  id: string;
  name: string;
  /** Дополнительная строка под названием (филиал, торговая марка, страна) */
  subtitle?: string;
  inn?: string;
  address?: string;
  phone?: string;
  email?: string;
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
  {
    id: "transkomplekt",
    name: "ЗАО «Транскомплект»",
    subtitle: "Республика Беларусь, г. Минск",
    address: "ул. Ботаническая, 7, к. 101",
    phone: "+375 (17) 245-22-43",
    email: "transkomplektm@yandex.ru",
  },
  {
    id: "akep",
    name: "ТОО «АКЭП»",
    subtitle: "Республика Казахстан, г. Усть-Каменогорск",
    address: "ул. Белинского, 18",
    phone: "(7232) 22-55-45, 22-56-05",
    email: "akep@akep.net",
  },
];
