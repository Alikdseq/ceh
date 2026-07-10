/** Yandex Maps — карточка завода АО «Электроконтактор» */
export const YANDEX_FACTORY_MAP_URL =
  "https://yandex.ru/maps/org/elektrokontaktor/1023671276/?ll=44.690012%2C43.018442&mode=search&sctx=ZAAAAAgBEAAaKAoSCcu6fyxEV0ZAEXv2XKYmg0VAEhIJDJQUWABT1j8RV7WkoxzMwj8iBgABAgMEBSgKOABAwYgGSAFqAnJ1nQHNzMw9oAEAqAEAvQGAS06KwgEF7PeP6AOCAiDRjdC70LXQutGC0YDQvtC60L7QvdGC0LDQutGC0L7RgIoCAJICAJoCDGRlc2t0b3AtbWFwcw%3D%3D&sll=44.690012%2C43.018442&sspn=0.126792%2C0.053386&text=%D1%8D%D0%BB%D0%B5%D0%BA%D1%82%D1%80%D0%BE%D0%BA%D0%BE%D0%BD%D1%82%D0%B0%D0%BA%D1%82%D0%BE%D1%80&z=13.46";

export function phoneToTelHref(phone: string): string {
  const digits = phone.replace(/\D/g, "");
  if (!digits) return "";
  if (digits.length === 11 && digits.startsWith("8")) return `tel:+7${digits.slice(1)}`;
  if (digits.length === 11 && digits.startsWith("7")) return `tel:+${digits}`;
  if (digits.length === 10) return `tel:+7${digits}`;
  return `tel:+${digits}`;
}
