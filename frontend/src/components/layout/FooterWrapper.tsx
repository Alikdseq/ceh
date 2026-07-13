import { getSiteSettings } from "@/lib/api";
import { FACTORY_PHONE } from "@/lib/site-links";

import { Footer as FooterClient } from "./Footer";

export async function Footer() {
  const settings = await getSiteSettings();

  return (
    <FooterClient
      companyName={settings?.company_name ?? 'АО «Электроконтактор»'}
      address={settings?.address ?? "362003, г. Владикавказ, ул. Кабардинская, 8"}
      email={settings?.email_main ?? "info@ekontaktor.ru"}
      phone={settings?.phone_main ?? FACTORY_PHONE}
      requisites={settings?.requisites}
    />
  );
}
