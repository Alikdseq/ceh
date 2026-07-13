/** Официальные логотипы «Честный знак» из /public/photos */
export const HONEST_SIGN_LOGO_COMPACT = "/photos/01.png";
export const HONEST_SIGN_LOGO_HORIZONTAL = "/photos/04.png";
export const HONEST_SIGN_LOGO_PARTNER = "/photos/07.png";

const MARKED_PRODUCT_TYPES = new Set(["KT", "KTP", "KTE"]);

/** Показывать маркировку на карточке (поле БД или тип контактора). */
export function showHonestSignMarking(product: {
  honest_sign?: boolean;
  product_type?: string;
}): boolean {
  if (product.honest_sign) return true;
  return MARKED_PRODUCT_TYPES.has(product.product_type ?? "");
}

export const HONEST_SIGN_DESCRIPTION =
  "Контакторы электромагнитные внесены в систему обязательной маркировки «Честный знак». Каждая единица продукции получает уникальный код Data Matrix для прослеживаемости и защиты от контрафакта.";
