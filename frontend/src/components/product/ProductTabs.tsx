import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import type { ProductGroupDetail } from "@/lib/types";
import { specKeyLabel } from "@/lib/utils";

interface ProductTabsProps {
  product: ProductGroupDetail;
}

export function ProductTabs({ product }: ProductTabsProps) {
  const publicDocs = product.documents.filter((d) => d.document.is_public && d.document.file_url);

  return (
    <Tabs defaultValue="specs" className="mt-12">
      <TabsList className="w-full justify-start overflow-x-auto">
        <TabsTrigger value="specs">Характеристики</TabsTrigger>
        <TabsTrigger value="docs">Документация</TabsTrigger>
        <TabsTrigger value="description">Описание</TabsTrigger>
        {product.designation_structure && (
          <TabsTrigger value="designation">Обозначение</TabsTrigger>
        )}
      </TabsList>

      <TabsContent value="specs" className="mt-6">
        {product.specs.length > 0 ? (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Параметр</TableHead>
                <TableHead>Значение</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {product.specs.map((spec) => (
                <TableRow key={spec.spec_key}>
                  <TableCell className="font-medium">{specKeyLabel(spec.spec_key)}</TableCell>
                  <TableCell>
                    {spec.spec_value}
                    {spec.spec_unit ? ` ${spec.spec_unit}` : ""}
                  </TableCell>
                </TableRow>
              ))}
              {product.nominal_current_a && (
                <TableRow>
                  <TableCell className="font-medium">Номинальный ток</TableCell>
                  <TableCell>{product.nominal_current_a} А</TableCell>
                </TableRow>
              )}
              {product.application_category && (
                <TableRow>
                  <TableCell className="font-medium">Категория применения</TableCell>
                  <TableCell>{product.application_category}</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        ) : (
          <p className="text-muted-foreground">Характеристики уточняйте у менеджера</p>
        )}
      </TabsContent>

      <TabsContent value="docs" className="mt-6">
        {publicDocs.length > 0 ? (
          <ul className="space-y-3">
            {publicDocs.map((link) => (
              <li key={link.id}>
                <a
                  href={link.document.file_url!}
                  className="flex items-center justify-between rounded-lg border px-4 py-3 hover:border-primary"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <span>{link.document.name}</span>
                  <span className="text-xs uppercase text-muted-foreground">
                    {link.document.doc_type}
                  </span>
                </a>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-muted-foreground">
            Документы будут добавлены. Свяжитесь с отделом сбыта для получения паспорта.
          </p>
        )}
      </TabsContent>

      <TabsContent value="description" className="mt-6">
        {product.full_description ? (
          <div
            className="prose prose-slate max-w-none"
            dangerouslySetInnerHTML={{ __html: product.full_description }}
          />
        ) : product.short_description ? (
          <p className="text-muted-foreground">{product.short_description}</p>
        ) : (
          <p className="text-muted-foreground">Описание готовится</p>
        )}
      </TabsContent>

      {product.designation_structure && (
        <TabsContent value="designation" className="mt-6">
          <div
            className="prose prose-slate max-w-none rounded-lg border bg-muted/30 p-6"
            dangerouslySetInnerHTML={{ __html: product.designation_structure }}
          />
          <p className="mt-4 text-sm text-muted-foreground">
            Пример: КТ6043Б-У3 — контактор серии 6043, исполнение Б, климатическое исполнение У3.
          </p>
        </TabsContent>
      )}
    </Tabs>
  );
}
