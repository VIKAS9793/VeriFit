import { useState, useCallback } from 'react';
import { Box, Typography, Paper, Grid, LinearProgress } from '@mui/material';
import { useTheme, alpha } from '@mui/material/styles';
import { motion } from 'framer-motion';
import ExplanationPanel from './ExplanationPanel';
import { SkillFlashcardGrid } from './SkillFlashcard';
import RewritePanel from './RewritePanel';
import { explainScore } from '../api/client';

interface ScoreBreakdown {
    component: string;
    score: number;
    summary: string;
    reasoning_chain: string[];
    findings: any[];
    confidence: number;
    generated_at: string;
}

interface Explanations {
    format_score?: ScoreBreakdown;
    structure_score?: ScoreBreakdown;
    keyword_score?: ScoreBreakdown;
    readability_score?: ScoreBreakdown;
}

// Mock Data for scaffolding
const MOCK_ANALYSIS = {
    veriscore: 78,
    impact_score: 85,
    brevity_score: 92,
    style_score: 65,
    skills: [
        { category: 'Languages', items: ['Python', 'TypeScript', 'Rust'] },
        { category: 'Frameworks', items: ['React', 'Flask', 'FastAPI'] }
    ]
};

interface ScoreCardProps {
    title: string;
    score: number;
    color: string;
    scoreKey: string;
    explanation: ScoreBreakdown | null;
    isLoadingExplanation: boolean;
    onRequestExplanation: () => void;
}

const ScoreCard = ({
    title,
    score,
    color,
    explanation,
    isLoadingExplanation,
    onRequestExplanation
}: ScoreCardProps) => (
    <Paper sx={{ p: 3, borderRadius: 4, bgcolor: 'background.paper', height: '100%' }}>
        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            {title}
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'end', gap: 1, mb: 2 }}>
            <Typography variant="h3" sx={{ fontWeight: 800, color: color }}>
                {score}
            </Typography>
            <Typography variant="h6" color="text.secondary" sx={{ mb: 1 }}>/100</Typography>
        </Box>
        <LinearProgress
            variant="determinate"
            value={score}
            sx={{
                height: 8,
                borderRadius: 4,
                bgcolor: alpha(color, 0.1),
                '& .MuiLinearProgress-bar': { bgcolor: color }
            }}
        />
        {/* XAI Layer: Why This Score? */}
        <ExplanationPanel
            componentName={title}
            breakdown={explanation}
            isLoading={isLoadingExplanation}
            onRequestExplanation={onRequestExplanation}
        />
    </Paper>
);

export const AnalysisDashboard = ({ data = MOCK_ANALYSIS, rawScore }: { data?: any; rawScore?: any }) => {
    const theme = useTheme();
    const [explanations, setExplanations] = useState<Explanations>({});
    const [loadingExplanations, setLoadingExplanations] = useState<Record<string, boolean>>({});

    const handleRequestExplanation = useCallback(async (scoreKey: string) => {
        if (!rawScore) return;

        setLoadingExplanations(prev => ({ ...prev, [scoreKey]: true }));

        try {
            const result = await explainScore(rawScore);
            if (result.explanations) {
                setExplanations(prev => ({
                    ...prev,
                    [scoreKey]: result.explanations[scoreKey]
                }));
            }
        } catch (error) {
            console.error('Failed to get explanation:', error);
        } finally {
            setLoadingExplanations(prev => ({ ...prev, [scoreKey]: false }));
        }
    }, [rawScore]);

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
        >
            <Box sx={{ mt: 4 }}>
                {/* Header Section */}
                <Box sx={{ mb: 6, textAlign: 'center' }}>
                    <Typography variant="overline" color="primary" sx={{ fontWeight: 700, letterSpacing: 2 }}>
                        ANALYSIS REPORT
                    </Typography>
                    <Typography variant="h3" sx={{ fontWeight: 700, mt: 1 }}>
                        VeriScore: <Box component="span" sx={{ color: 'primary.main' }}>{data.veriscore}</Box>
                    </Typography>
                    <Typography variant="body1" color="text.secondary" sx={{ mt: 2, maxWidth: 600, mx: 'auto' }}>
                        Based on 12 key performance indicators. Your profile demonstrates strong clear impact but lacks stylistic consistency.
                    </Typography>
                </Box>

                {/* Scores Grid with XAI */}
                <Grid container spacing={3} sx={{ mb: 6 }}>
                    <Grid item xs={12} md={4}>
                        <ScoreCard
                            title="Impact & Quantities"
                            score={data.impact_score}
                            color={theme.palette.success.main}
                            scoreKey="format_score"
                            explanation={explanations.format_score || null}
                            isLoadingExplanation={loadingExplanations['format_score'] || false}
                            onRequestExplanation={() => handleRequestExplanation('format_score')}
                        />
                    </Grid>
                    <Grid item xs={12} md={4}>
                        <ScoreCard
                            title="Brevity & Clarity"
                            score={data.brevity_score}
                            color={theme.palette.info.main}
                            scoreKey="structure_score"
                            explanation={explanations.structure_score || null}
                            isLoadingExplanation={loadingExplanations['structure_score'] || false}
                            onRequestExplanation={() => handleRequestExplanation('structure_score')}
                        />
                    </Grid>
                    <Grid item xs={12} md={4}>
                        <ScoreCard
                            title="Style & ATS"
                            score={data.style_score}
                            color={theme.palette.warning.main}
                            scoreKey="readability_score"
                            explanation={explanations.readability_score || null}
                            isLoadingExplanation={loadingExplanations['readability_score'] || false}
                            onRequestExplanation={() => handleRequestExplanation('readability_score')}
                        />
                    </Grid>
                </Grid>

                {/* Skills Snapshot - Interactive NotebookLM Flashcard Style */}
                <SkillFlashcardGrid skills={data.skills} />

                {/* HITL Rewrite Interface */}
                <Box sx={{ mt: 4 }}>
                    <RewritePanel resumeData={data.raw_resume} />
                </Box>
            </Box>
        </motion.div>
    );
};
