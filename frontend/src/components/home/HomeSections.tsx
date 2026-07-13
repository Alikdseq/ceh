import Link from "next/link";
import Image from "next/image";
import { Award, Factory } from "lucide-react";

import { AntiCounterfeitBlock } from "@/components/content/AntiCounterfeitBlock";
import { HonestSignSection } from "@/components/home/HonestSignSection";
import { PartnersCarousel } from "@/components/home/PartnersCarousel";

import { Button } from "@/components/ui/button";
import { HONEST_SIGN_LOGO_COMPACT } from "@/lib/honest-sign";
import { SERIES_BLOCKS } from "@/lib/catalog-meta";
import { PARTNERS } from "@/lib/partners";
import { publicAssetSrc } from "@/lib/utils";

const TRUST_BADGES = [
  {
    logo: HONEST_SIGN_LOGO_COMPACT,
    label: "Честный знак",
    desc: "Партнёр оператора маркировки, прослеживаемость продукции",
  },
  { icon: Factory, label: "100% РФ", desc: "Собственное производство во Владикавказе" },
  { icon: Award, label: "EAC", desc: "Сертификация продукции" },
] as const;

export function HeroSection() {
  return (
    <section className="hero-gradient relative overflow-hidden text-white">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_rgba(255,255,255,0.08)_0%,_transparent_55%)]" />
      <div className="container-page relative py-12 md:py-16 lg:py-20">
        <div className="grid items-center gap-10 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.15fr)] lg:gap-10 xl:gap-14">
          <div className="min-w-0">
            <p className="font-display text-4xl font-bold leading-none tracking-tight md:text-5xl lg:text-6xl xl:text-7xl">
              Электроконтактор
            </p>
            <h1 className="mt-4 font-display text-2xl font-semibold leading-snug text-white/95 md:text-3xl lg:text-4xl">
              Производитель контакторов с 1956 года
            </h1>
            <p className="mt-4 max-w-xl text-base text-white/85 md:text-lg">
              АО «Владикавказский завод «Электроконтактор» — контакторы КТ, КТП, КТЭ и
              низковольтная аппаратура. Прямые поставки с завода, публичные цены.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Button asChild size="lg" variant="accent">
                <Link href="/catalog">Подобрать контактор</Link>
              </Button>
              <Button
                asChild
                size="lg"
                variant="outline"
                className="border-white/30 bg-transparent text-white hover:bg-white/10 hover:text-white"
              >
                <Link href="/about">О заводе</Link>
              </Button>
            </div>
          </div>

          <div className="hero-product-stage mx-auto w-full max-w-lg lg:mx-0 lg:max-w-none lg:justify-self-end">
            <div className="hero-product-shadow" aria-hidden />
            <Image
              src={publicAssetSrc("/photos/КТ6023-fotor-bg-remover-20260713162710.png")}
              alt="Контактор КТ6023 — продукция завода Электроконтактор"
              width={900}
              height={680}
              priority
              className="hero-product-3d mx-auto"
              sizes="(max-width: 1024px) 92vw, 620px"
            />
          </div>
        </div>
      </div>
    </section>
  );
}

export function SeriesGrid() {
  return (
    <section className="section-py bg-muted" aria-labelledby="series-heading">
      <div className="container-page">
        <h2 id="series-heading" className="font-display text-2xl font-bold md:text-3xl">
          Серии продукции
        </h2>
        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {SERIES_BLOCKS.map((item) => (
            <Link
              key={item.title}
              href={item.href}
              className="rounded-lg border bg-card p-6 shadow-sm transition hover:border-primary hover:shadow-md"
            >
              <h3 className="font-display text-lg font-semibold">{item.title}</h3>
              <p className="mt-2 text-sm text-muted-foreground">{item.description}</p>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}

export function TrustBadges() {
  return (
    <section className="border-y bg-background py-8" aria-label="Преимущества производителя">
      <div className="container-page grid gap-6 sm:grid-cols-3">
        {TRUST_BADGES.map((item) => (
          <div key={item.label} className="flex items-start gap-4">
            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg bg-[#FAFF00]/40 p-1.5">
              {"logo" in item ? (
                <Image
                  src={publicAssetSrc(item.logo)}
                  alt=""
                  width={44}
                  height={44}
                  unoptimized
                  className="h-full w-full object-contain"
                />
              ) : (
                <item.icon className="h-5 w-5 text-primary" aria-hidden />
              )}
            </div>
            <div>
              <p className="font-display font-semibold">{item.label}</p>
              <p className="mt-1 text-sm text-muted-foreground">{item.desc}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

export { HonestSignSection };

export function AntiCounterfeitBanner() {
  return (
    <section className="container-page py-8">
      <AntiCounterfeitBlock />
    </section>
  );
}

export function PartnersSection() {
  return (
    <section className="section-py bg-muted/50" aria-labelledby="partners-heading">
      <div className="container-page">
        <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <h2 id="partners-heading" className="font-display text-2xl font-bold md:text-3xl">
              Партнёры
            </h2>
            <p className="mt-3 max-w-2xl text-muted-foreground">
              Официальные партнёры и дилеры завода — поставки продукции «Электроконтактор» по всей
              России.
            </p>
          </div>
          <Button asChild variant="outline" className="hidden sm:inline-flex">
            <Link href="/partners">Все партнёры</Link>
          </Button>
        </div>
        <div className="mt-8">
          <PartnersCarousel partners={PARTNERS} />
        </div>
      </div>
    </section>
  );
}
