import type { ContentPage } from "@/lib/types";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";

interface ContentPageLayoutProps {
  page: ContentPage;
  breadcrumbs: { label: string; href?: string }[];
  children?: React.ReactNode;
}

export function ContentPageLayout({ page, breadcrumbs, children }: ContentPageLayoutProps) {
  return (
    <div className="section-py">
      <div className="container-page">
        <Breadcrumbs items={breadcrumbs} className="mb-6" />
        <h1 className="font-display text-3xl font-bold md:text-4xl">{page.h1 || page.title}</h1>
        {children}
        <div
          className="prose prose-slate mt-8 max-w-none"
          dangerouslySetInnerHTML={{ __html: page.body }}
        />
      </div>
    </div>
  );
}
