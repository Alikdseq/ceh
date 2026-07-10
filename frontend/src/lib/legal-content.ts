import { readFileSync } from "fs";
import { join } from "path";

import type { ContentPage } from "@/lib/types";

function readLegalHtml(filename: string): string {
  const path = join(process.cwd(), "src/content/legal", filename);
  return readFileSync(path, "utf-8");
}

export function getPrivacyPage(): ContentPage {
  return {
    title: "Политика конфиденциальности",
    slug: "privacy",
    h1: "Политика конфиденциальности",
    meta_title: "Политика конфиденциальности",
    meta_description:
      "Политика обработки персональных данных АО «Владикавказский завод «Электроконтактор» в соответствии с 152-ФЗ.",
    body: readLegalHtml("privacy.html"),
    updated_at: "2026-07-03T12:00:00Z",
  };
}

export function getTermsPage(): ContentPage {
  return {
    title: "Пользовательское соглашение",
    slug: "terms",
    h1: "Пользовательское соглашение",
    meta_title: "Пользовательское соглашение",
    meta_description:
      "Условия использования сайта АО «Владикавказский завод «Электроконтактор».",
    body: readLegalHtml("terms.html"),
    updated_at: "2026-07-03T12:00:00Z",
  };
}

export function getCookiesPage(): ContentPage {
  return {
    title: "Политика cookie",
    slug: "cookies",
    h1: "Политика cookie",
    meta_title: "Политика cookie",
    meta_description:
      "Информация о файлах cookie и настройках аналитики на сайте АО «Владикавказский завод «Электроконтактор».",
    body: readLegalHtml("cookies.html"),
    updated_at: "2026-07-07T12:00:00Z",
  };
}
