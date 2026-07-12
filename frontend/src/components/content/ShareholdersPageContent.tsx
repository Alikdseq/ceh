"use client";

import Link from "next/link";
import { Download, FileText } from "lucide-react";

import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { Button } from "@/components/ui/button";
import {
  AFFILIATED_DOCUMENTS,
  CHARTER_DOCUMENTS,
  DISCLOSURE_DOCUMENTS,
  corporateDocDownloadUrl,
  type ShareholderDocument,
} from "@/lib/shareholders-docs";

const SECTIONS = [
  { id: "overview", label: "Акционерам" },
  { id: "charter", label: "Устав" },
  { id: "affiliated", label: "Аффилированные лица" },
  { id: "disclosure", label: "Раскрытие информации" },
] as const;

function DocumentList({
  documents,
  category,
}: {
  documents: ShareholderDocument[];
  category: "affilr" | "raskrinfo" | "charter";
}) {
  if (!documents.length) {
    return (
      <p className="rounded-lg border border-dashed bg-muted/30 p-6 text-sm text-muted-foreground">
        Документы будут опубликованы в ближайшее время.
      </p>
    );
  }

  return (
    <ul className="divide-y rounded-xl border bg-card">
      {documents.map((doc) => (
        <li key={`${category}-${doc.file}`}>
          <a
            href={corporateDocDownloadUrl(category, doc.file)}
            className="flex items-center justify-between gap-4 px-4 py-3 transition hover:bg-[var(--color-brand-blue-light)]/40"
          >
            <span className="flex items-start gap-3 text-sm font-medium text-primary">
              <FileText className="mt-0.5 h-4 w-4 shrink-0" />
              {doc.label}
            </span>
            {doc.sizeKb ? (
              <span className="shrink-0 text-xs text-muted-foreground">{doc.sizeKb} кб</span>
            ) : null}
          </a>
        </li>
      ))}
    </ul>
  );
}

export function ShareholdersPageContent() {
  return (
    <div className="section-py">
      <div className="container-page">
        <Breadcrumbs
          items={[
            { label: "Главная", href: "/" },
            { label: "Акционерам", href: "/shareholders" },
          ]}
          className="mb-6"
        />
        <h1 className="font-display text-3xl font-bold md:text-4xl">Акционерам</h1>
        <p className="mt-3 max-w-3xl text-muted-foreground">
          Информация для акционеров АО «Владикавказский завод «Электроконтактор».
        </p>

        <nav className="mt-8 flex flex-wrap gap-2" aria-label="Разделы для акционеров">
          {SECTIONS.map((section) => (
            <a
              key={section.id}
              href={`#${section.id}`}
              className="rounded-full border bg-card px-4 py-2 text-sm font-medium transition hover:border-primary hover:text-primary"
            >
              {section.label}
            </a>
          ))}
        </nav>

        <section id="overview" className="mt-10 scroll-mt-28">
          <h2 className="font-display text-2xl font-semibold">АО «Владикавказский завод «Электроконтактор»</h2>
          <div className="mt-6 grid gap-6 lg:grid-cols-2">
            <div className="rounded-xl border bg-card p-6 shadow-sm">
              <h3 className="font-semibold">Полное наименование</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                Акционерное общество «Владикавказский завод «Электроконтактор»
              </p>
              <h3 className="mt-5 font-semibold">Юридический адрес</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                362003, Россия, Республика Северная Осетия-Алания, г. Владикавказ, ул. Кабардинская, 8 а/я 1034
              </p>
              <p className="mt-4 text-sm leading-relaxed">
                ИНН 1502013069 · КПП 151301001 · ОКПО 00213693 · ОКВЭД 31.20.1 · ОКОНХ 14171
                <br />
                ОГРН 1021500574336 · ОКАТО 904364000 · ОКТМО 90701000 · ОКОГУ 49008 · ОКФС 16 · ОКОПФ 47
              </p>
            </div>

            <div className="space-y-6">
              <div className="rounded-xl border bg-card p-6 shadow-sm">
                <h3 className="font-semibold">Платёжные реквизиты</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                  Р/сч. 40702810100220000142
                  <br />
                  К/сч. 30101810145250000411
                  <br />
                  Филиал «Центральный» Банк ВТБ (ПАО) г. Москва
                  <br />
                  ИНН 7702070139 · КПП 263443001 · БИК 044525411
                </p>
              </div>
              <div className="rounded-xl border bg-card p-6 shadow-sm">
                <h3 className="font-semibold">Отгрузочные реквизиты</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                  <strong className="text-foreground">Контейнерная отгрузка:</strong> станция Владикавказ
                  Северо-Кавказской ж.д., код станции 538708, код предприятия 1340
                  <br />
                  <br />
                  <strong className="text-foreground">Багаж:</strong> станция Владикавказ Сев.Кав.ж.д., код 538708,
                  код плательщика (ЕЛС) 1000143668
                </p>
              </div>
            </div>
          </div>

          <div className="mt-6 grid gap-6 lg:grid-cols-2">
            <div className="rounded-xl border bg-card p-6 shadow-sm">
              <h3 className="font-semibold">Связь</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                Тел. (8672) 53-33-44, 54-75-40, т/ф. 53-49-61 — секретарь
                <br />
                т/ф. 54-01-03, 53-82-55 — отдел сбыта
                <br />
                53-52-15 — отдел маркетинга
                <br />
                53-38-13 — отдел снабжения
                <br />
                Сайт:{" "}
                <Link href="https://www.ekontaktor.ru" className="text-primary hover:underline">
                  www.ekontaktor.ru
                </Link>
                <br />
                e-mail:{" "}
                <a href="mailto:info@ekontaktor.ru" className="text-primary hover:underline">
                  info@ekontaktor.ru
                </a>
                ,{" "}
                <a href="mailto:elkonreal@yandex.ru" className="text-primary hover:underline">
                  elkonreal@yandex.ru
                </a>
              </p>
            </div>
            <div className="rounded-xl border bg-card p-6 shadow-sm">
              <h3 className="font-semibold">Руководство завода</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                Генеральный директор: Цхурбаев Сослан Муратович — 53-33-44
                <br />
                Главный бухгалтер: Плиева Светлана Саукудзовна — 53-62-79
              </p>
            </div>
          </div>
        </section>

        <section id="charter" className="mt-14 scroll-mt-28">
          <h2 className="font-display text-2xl font-semibold">Устав</h2>
          <div className="prose prose-slate mt-6 max-w-none">
            <h3>1. Общие положения</h3>
            <p>
              1.1. Акционерное Общество «Владикавказский завод «Электроконтактор», в дальнейшем именуемое
              «обществом», является открытым акционерным обществом. Общество является юридическим лицом,
              действует на основании устава и законодательства Российской Федерации.
            </p>
            <p>1.2. Общество создано без ограничения срока его деятельности.</p>
            <h3>2. Фирменное наименование и место нахождения общества</h3>
            <p>
              2.1. Фирменное наименование: Открытое Акционерное Общество «Владикавказский завод
              «Электроконтактор». На английском языке: «Vladikavkazian Joint Stock Company
              «Electrocontactor». Сокращённое наименование: ОАО «Электроконтактор».
            </p>
            <p>
              2.2. Место нахождения общества: Россия, Республика Северная Осетия – Алания, г. Владикавказ,
              ул. Кабардинская, 8. Почтовый адрес: 362003, Республика Северная Осетия – Алания, ул.
              Кабардинская, 8.
            </p>
          </div>
          <div className="mt-6 flex flex-wrap gap-3">
            {CHARTER_DOCUMENTS.map((doc) => (
              <Button key={doc.file} asChild variant="outline" className="gap-2">
                <a href={corporateDocDownloadUrl("charter", doc.file)}>
                  <Download className="h-4 w-4" />
                  {doc.label}
                </a>
              </Button>
            ))}
          </div>
        </section>

        <section id="affiliated" className="mt-14 scroll-mt-28">
          <h2 className="font-display text-2xl font-semibold">Аффилированные лица</h2>
          <p className="mt-2 text-sm text-muted-foreground">
            Архивные списки аффилированных лиц общества. Нажмите на документ для скачивания.
          </p>
          <div className="mt-6">
            <DocumentList documents={AFFILIATED_DOCUMENTS} category="affilr" />
          </div>
        </section>

        <section id="disclosure" className="mt-14 scroll-mt-28">
          <h2 className="font-display text-2xl font-semibold">Раскрытие информации</h2>
          <p className="mt-2 text-sm text-muted-foreground">
            Документы по раскрытию информации для акционеров и инвесторов.
          </p>
          <div className="mt-6">
            <DocumentList documents={DISCLOSURE_DOCUMENTS} category="raskrinfo" />
          </div>
        </section>
      </div>
    </div>
  );
}
