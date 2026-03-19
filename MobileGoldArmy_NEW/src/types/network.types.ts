import { StatusKey } from './crm.types';

export interface HrProfile {
  name: string;
  snippet: string;
  url?: string;
}

export interface DecisionMaker {
  name: string;
  role: string;
  snippet: string;
  linkedin_url?: string;
}

export interface NetworkContact {
  id: string;
  company_name: string;
  site_url?: string;
  emails: string[];
  phone?: string;
  category: string;
  last_updated: string;
}

export interface EmailDraft {
  subject: string;
  body: string;
}

export interface DraftRequest {
  company_name: string;
  hr_name: string;
  request_type: 'emploi' | 'stage';
  target_domain: string;
  cv_text?: string;
}
