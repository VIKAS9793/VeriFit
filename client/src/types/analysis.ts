export interface ResumeAnalysis {
    veriscore: number;
    executive_summary: string;
    skills: {
        category: string;
        items: string[];
    }[];
    gaps: {
        severity: 'high' | 'medium' | 'low';
        description: string;
        suggestion: string;
    }[];
    impact_score: number;
    brevity_score: number;
    style_score: number;
}
