export interface ExperienceEntry {
  title?: string;
  company?: string;
  duration?: string;
  description?: string;
}

export interface EducationEntry {
  school?: string;
  degree?: string;
}

export interface PersonalInfo {
  name?: string;
  headline?: string;
  location?: string;
  current_role?: string;
  company?: string;
  summary?: string;
  experience?: ExperienceEntry[];
  education?: EducationEntry[];
  skills?: string[];
  languages?: string[];
}

export interface InvestmentProfile {
  is_investor: boolean;
  investment_role?: string;
  investment_focus?: string[];
  portfolio_companies?: string[];
  sectors_of_interest?: string[];
  investment_stage?: string[];
  investment_mentions?: string[];
}

export interface Profile {
  name: string;
  linkedin_url: string;
  personal_info: PersonalInfo;
  investment_profile: InvestmentProfile;
  extraction_status?: string;
  sources_used?: string[];
  relevance_score?: number; // 0-100 relevance score from FAISS search
}

export interface SearchFilters {
  is_investor: boolean | null;
  investment_role: string;
  location: string;
  sectors_of_interest: string[];
  investment_stage: string[];
}

export interface SearchRequest {
  query: string;
  max_results: number;
  filters: SearchFilters | null;
}

export interface SearchResponse {
  results: Profile[];
  total_found: number;
  query: string;
  relevance_scores?: number[]; // 0-100 relevance scores for each result
}

