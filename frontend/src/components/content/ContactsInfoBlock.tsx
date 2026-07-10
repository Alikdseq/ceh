import { Mail, MapPin, Phone } from "lucide-react";

import type { SiteSettings } from "@/lib/types";
import { phoneToTelHref, YANDEX_FACTORY_MAP_URL } from "@/lib/site-links";

interface ContactsInfoBlockProps {
  settings: SiteSettings | null;
}

const DEFAULTS = {
  address: "362003, г. Владикавказ, ул. Кабардинская, 8",
  phone: "(8672) 53-33-44",
  email: "info@ekontaktor.ru",
  salesEmail: "elkonreal@yandex.ru",
};

export function ContactsInfoBlock({ settings }: ContactsInfoBlockProps) {
  const address = settings?.address || DEFAULTS.address;
  const phone = settings?.phone_main || DEFAULTS.phone;
  const email = settings?.email_main || DEFAULTS.email;
  const salesEmail =
    settings?.order_emails_list?.find((e) => e !== email) ??
    settings?.order_emails_list?.[1] ??
    DEFAULTS.salesEmail;
  const telHref = phoneToTelHref(phone);

  return (
    <address className="space-y-3 rounded-lg border p-4 not-italic lg:p-5">
      <p className="font-display text-sm font-semibold text-foreground">Контакты завода</p>
      <ul className="space-y-3 text-sm">
        <li className="flex gap-2.5">
          <MapPin className="mt-0.5 h-4 w-4 shrink-0 text-primary" aria-hidden />
          <span>
            <span className="text-muted-foreground">Адрес: </span>
            <a
              href={YANDEX_FACTORY_MAP_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="font-medium text-primary underline-offset-2 hover:underline"
            >
              {address}
            </a>
          </span>
        </li>
        <li className="flex gap-2.5">
          <Phone className="mt-0.5 h-4 w-4 shrink-0 text-primary" aria-hidden />
          <span>
            <span className="text-muted-foreground">Телефон: </span>
            {telHref ? (
              <a href={telHref} className="font-medium text-primary underline-offset-2 hover:underline">
                {phone}
              </a>
            ) : (
              phone
            )}
          </span>
        </li>
        <li className="flex gap-2.5">
          <Mail className="mt-0.5 h-4 w-4 shrink-0 text-primary" aria-hidden />
          <span>
            <span className="text-muted-foreground">Email: </span>
            <a
              href={`mailto:${email}`}
              className="font-medium text-primary underline-offset-2 hover:underline"
            >
              {email}
            </a>
          </span>
        </li>
        <li className="flex gap-2.5">
          <Mail className="mt-0.5 h-4 w-4 shrink-0 text-primary" aria-hidden />
          <span>
            <span className="text-muted-foreground">Отдел сбыта: </span>
            <a
              href={`mailto:${salesEmail}`}
              className="font-medium text-primary underline-offset-2 hover:underline"
            >
              {salesEmail}
            </a>
          </span>
        </li>
      </ul>
    </address>
  );
}
