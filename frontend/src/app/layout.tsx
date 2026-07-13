import type { Metadata } from "next";
import { Inter, Manrope } from "next/font/google";
import "./globals.css";
import { AnalyticsProvider } from "@/components/analytics/AnalyticsProvider";
import { Footer } from "@/components/layout/FooterWrapper";
import { Header } from "@/components/layout/Header";
import { CookieConsentProvider } from "@/components/privacy/CookieConsentProvider";

const inter = Inter({ subsets: ["latin", "cyrillic"], variable: "--font-inter" });
const manrope = Manrope({ subsets: ["latin", "cyrillic"], variable: "--font-manrope" });

export const metadata: Metadata = {
  metadataBase: new URL(
    (process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000").replace(/\/$/, ""),
  ),
  title: {
    default: "Электроконтактор — производитель контакторов",
    template: "%s | Электроконтактор",
  },
  description:
    "АО «Владикавказский завод «Электроконтактор» — производитель контакторов КТ, КТП, КТЭ. Прямые поставки с завода.",
  manifest: "/manifest.webmanifest",
  icons: {
    icon: [
      { url: "/photos/logonobag.png", type: "image/png", sizes: "512x512" },
      { url: "/photos/logonobag.png", type: "image/png", sizes: "192x192" },
    ],
    apple: [{ url: "/photos/logonobag.png", type: "image/png", sizes: "180x180" }],
    shortcut: ["/photos/logonobag.png"],
  },
};

export const dynamic = "force-dynamic";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru" className={`${inter.variable} ${manrope.variable} h-full`}>
      <body className="flex min-h-full flex-col antialiased">
        <a
          href="#main"
          className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-[100] focus:rounded-md focus:border-2 focus:border-primary focus:bg-white focus:px-4 focus:py-2 focus:text-foreground"
        >
          Перейти к содержанию
        </a>
        <Header />
        <main id="main" className="flex-1 pt-[var(--site-header-height)]">
          {children}
        </main>
        <Footer />
        <CookieConsentProvider />
        <AnalyticsProvider />
      </body>
    </html>
  );
}
