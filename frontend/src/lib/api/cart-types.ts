export interface CartItemDto {
  id: number;
  variant_id: number;
  sku_code: string;
  product_name: string;
  product_slug: string;
  category_slug: string;
  quantity: number;
  unit_price: string;
  line_total: string;
  image_url: string | null;
  coil_voltage_v: number | null;
}

export interface CartDto {
  items: CartItemDto[];
  item_count: number;
  subtotal: string;
  vat_included: boolean;
}

export interface QuoteSubmitPayload {
  contact_name: string;
  company_name: string;
  email: string;
  phone: string;
  city?: string;
  inn?: string;
  kpp?: string;
  comment?: string;
  privacy_accepted: boolean;
  privacy_policy_version?: string;
  website?: string;
  utm_source?: string;
  utm_medium?: string;
  utm_campaign?: string;
}

export interface QuoteSubmitResponse {
  number: string;
}
