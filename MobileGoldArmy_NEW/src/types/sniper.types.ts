export interface SniperJob {
  id: string;
  title: string;
  company: string;
  location: string;
  source: string;
  match_score: number;
  salary?: string;
  type?: string;
  posted_date?: string;
  url?: string;
  description?: string;
}

export interface SniperSearchResult {
  success: boolean;
  total_jobs_found: number;
  matched_jobs: SniperJob[];
}

