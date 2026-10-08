export type CoolingType = "direct_evaporative" | "air_cooled" | "cooling_tower";

type Location =
  | { huc8: string; latitude?: never; longitude?: never }
  | { huc8?: string; latitude: number; longitude: number };

export type ForecastRequest = Location & {
  facility_mw: number;
  cooling_type: CoolingType;
  /** Calendar month, 1–12. Conditions come from historical monthly observations. */
  seasonal_target: number;
};

export interface ForecastResponse {
  huc8: string;
  seasonal_target: number;
  thermodynamic_bounds: {
    min_mgd: number;
    max_mgd: number;
    thermal_load_kwh_day: number;
    max_liters_per_thermal_kwh: number;
    max_site_wue_l_per_it_kwh: number;
    pue: number;
    utilization: number;
    evaporative_fraction_max: number;
  };
  /** On-site cooling consumption proxy, not a municipal water-stress index. */
  predicted_collateral_stress_mgd: number;
  raw_prediction_mgd: number;
  /** Held-out fit metric; null for constant targets. */
  heldout_r2: number | null;
  prediction_interval90: {
    nominal_coverage: number;
    min_mgd: number;
    max_mgd: number;
    method: string;
  };
  model_name: string;
  model_data_kind: "observed" | "synthetic";
  environment_data_kind: "observed" | "synthetic";
  source_period_start: string;
  source_period_end: string;
  regulatory_risk_summary: string;
  citations: Array<{
    document_id: string;
    title: string;
    section: string;
    source_url: string;
    excerpt: string;
    is_example: boolean;
  }>;
  warnings: string[];
}

export class ForecastError extends Error {
  constructor(public readonly status: number, public readonly detail: unknown) {
    super(`ECOllateral forecast failed (${status})`);
    this.name = "ForecastError";
  }
}

export async function forecastFacility(
  baseUrl: string,
  request: ForecastRequest,
  signal?: AbortSignal,
): Promise<ForecastResponse> {
  const response = await fetch(`${baseUrl.replace(/\/$/, "")}/forecast`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
    ...(signal ? { signal } : {}),
  });
  if (!response.ok) {
    const detail: unknown = response.headers.get("content-type")?.includes("application/json")
      ? await response.json()
      : await response.text();
    throw new ForecastError(response.status, detail);
  }
  return response.json() as Promise<ForecastResponse>;
}
