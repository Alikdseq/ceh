export interface Category {
  id: number;
  name: string;
  slug: string;
  description?: string;
  meta_title?: string;
  meta_description?: string;
  h1?: string;
  noindex?: boolean;
  canonical_override?: string;
  sort_order: number;
  product_count?: number;
  children?: Category[];
}

export interface ProductImage {
  url: string;
  alt: string;
  is_placeholder?: boolean;
}

export interface ProductVariant {
  id: number;
  sku_code: string;
  slug: string;
  execution: string;
  coil_type: string;
  coil_voltage_v: number | null;
  aux_contacts?: string;
  price: string;
  stock_status?: string;
  is_default: boolean;
}

export interface ProductGroup {
  id: number;
  name: string;
  slug: string;
  short_description: string;
  series_code: string;
  product_type: string;
  nominal_current_a: number | null;
  nominal_voltage_v: number;
  poles: number | null;
  honest_sign: boolean;
  is_featured: boolean;
  price_from: string | null;
  category_name: string;
  category_slug: string;
  category_path?: string[];
  primary_image: ProductImage | null;
  default_variant: ProductVariant | null;
  variants_preview?: ProductVariant[];
  /** Distinct aux-contact labels for catalog cards (2З+2Р, 3З+3Р, …). */
  aux_contacts_options?: string[];
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface NewsPost {
  id: number;
  title: string;
  slug: string;
  excerpt: string;
  published_at: string;
}

export interface NewsPostDetail extends NewsPost {
  body: string;
  meta_title: string;
  meta_description: string;
}

export interface ContentPage {
  title: string;
  slug: string;
  body: string;
  meta_title: string;
  meta_description: string;
  h1: string;
  updated_at: string;
}

export interface SiteSettings {
  company_name: string;
  phone_main: string;
  phone_sales: string;
  email_main: string;
  order_emails_list?: string[];
  address: string;
  requisites: string;
  yandex_metrika_id?: string;
  ga4_id?: string;
}

export interface ProductImageDetail {
  id: number;
  url?: string;
  image?: string;
  alt: string;
  sort_order: number;
  is_primary: boolean;
}

export interface ProductSpec {
  spec_key: string;
  spec_value: string;
  spec_unit: string;
  filterable: boolean;
  sort_order: number;
}

export interface ProductDocumentLink {
  id: number;
  document: {
    id: number;
    name: string;
    doc_type: string;
    file_url: string | null;
    file_size: number | null;
    is_public: boolean;
  };
  sort_order: number;
}

export interface ProductGroupDetail extends ProductGroup {
  full_description: string;
  application_category: string;
  designation_structure: string;
  meta_title: string;
  meta_description: string;
  h1: string;
  variants: ProductVariant[];
  specs: ProductSpec[];
  images: ProductImageDetail[];
  documents: ProductDocumentLink[];
  related: ProductGroup[];
}

export interface FAQItem {
  id: number;
  category: string;
  question: string;
  answer: string;
  sort_order: number;
}

export interface CompareVariant extends ProductVariant {
  group_name: string;
  group_slug: string;
  weight_net_kg?: string | null;
  weight_gross_kg?: string | null;
  dimensions?: Record<string, unknown>;
  specs: ProductSpec[];
  nominal_current_a: number | null;
  poles: number | null;
  product_type: string;
}

export interface CompareResponse {
  variants: CompareVariant[];
  spec_keys: string[];
}
