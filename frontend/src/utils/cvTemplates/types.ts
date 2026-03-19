/**
 * Types shared by all CV PDF templates.
 */

export interface CvData {
  full_name?: string;
  title?: string;
  email?: string;
  phone?: string;
  location?: string;
  linkedin?: string;
  github?: string;
  summary?: string;
  experiences?: Experience[];
  projects?: Project[];
  education?: Education[];
  skills?: Record<string, string[]> | string[];
  languages?: string[];
  certifications?: string[];
}

export interface Experience {
  title?: string;
  company?: string;
  location?: string;
  start_date?: string;
  end_date?: string;
  bullets?: string[];
}

export interface Project {
  name?: string;
  description?: string;
  bullets?: string[];
}

export interface Education {
  degree?: string;
  institution?: string;
  school?: string;
  location?: string;
  year?: string;
}

export interface ParsedAudit {
  ats_score?: number;
  original_ats_score?: number;
  candidate_name?: string;
  candidate_title?: string;
}

export type CvTemplateBuilder = (cvData: CvData, parsedAudit: ParsedAudit | null) => string;

export interface CvTemplate {
  id: string;
  label: string;
  description: string;
  accentColor: string; // for preview swatch
  build: CvTemplateBuilder;
}
