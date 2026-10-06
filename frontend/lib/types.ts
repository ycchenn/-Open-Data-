export interface Material {
  name: string | null;
  amount: number | null;
  unit: string | null;
}

export interface Activity {
  type: string;
  description: string;
  target: string | null;
  materials: Material[];
}

export interface FarmLog {
  id?: string;
  created_at?: string;
  date: string;
  crop: string | null;
  field: string | null;
  area: string | null;
  weather: string | null;
  activities: Activity[];
  harvest: { amount: number | null; unit: string | null } | null;
  notes: string | null;
  raw_text: string;
  corrected_text: string;
  corrections: { from: string; to: string; count: number }[];
  engine: "openai" | "rule-based";
}

export interface TraceabilityDraft {
  sections: Record<string, Record<string, string | null>[]>;
  missing_fields: string[];
  disclaimer: string;
}

export interface MarketingResult {
  four_p: { product: string; price: string; place: string; promotion: string };
  brand_story: string;
  social_post: string;
  product_description: string;
  hashtags: string[];
  engine: string;
}

export interface Source {
  text: string;
  source: string;
  url: string | null;
  score?: number;
}

export interface QAResult {
  answer: string;
  insufficient: boolean;
  sources: Source[];
  risk: { level: "high" | "normal"; categories: string[]; warnings: string[] };
}

export interface HealthStatus {
  status: string;
  services: Record<string, boolean | number | string>;
}
