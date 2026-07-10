import type { Metadata } from "next";

import { ShareholdersPageContent } from "@/components/content/ShareholdersPageContent";

export const metadata: Metadata = {
  title: "Акционерам | Электроконтактор",
  description:
    "Информация для акционеров АО «Владикавказский завод «Электроконтактор»: устав, аффилированные лица, раскрытие информации.",
};

export default function ShareholdersPage() {
  return <ShareholdersPageContent />;
}
