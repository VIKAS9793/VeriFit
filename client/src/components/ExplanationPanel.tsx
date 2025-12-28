import React, { useState } from 'react';
import {
    Box,
    Paper,
    Typography,
    Chip,
    LinearProgress,
    IconButton,
    Collapse,
    Tooltip,
} from '@mui/material';
import { alpha, useTheme } from '@mui/material/styles';
import {
    ExpandMore as ExpandMoreIcon,
    ExpandLess as ExpandLessIcon,
    Lightbulb as LightbulbIcon,
    Warning as WarningIcon,
    Error as ErrorIcon,
    Psychology as PsychologyIcon,
    TrendingUp as TrendingUpIcon,
    CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

interface Finding {
    finding: string;
    location: string;
    impact: string;
    recommendation: string;
    severity: 'info' | 'warning' | 'critical';
}

interface ScoreBreakdown {
    component: string;
    score: number;
    summary: string;
    reasoning_chain: string[];
    findings: Finding[];
    confidence: number;
    generated_at: string;
}

interface ExplanationPanelProps {
    componentName: string;
    breakdown: ScoreBreakdown | null;
    isLoading?: boolean;
    onRequestExplanation?: () => void;
}

const getSeverityIcon = (severity: string) => {
    switch (severity) {
        case 'critical':
            return <ErrorIcon sx={{ fontSize: 18 }} />;
        case 'warning':
            return <WarningIcon sx={{ fontSize: 18 }} />;
        default:
            return <CheckCircleIcon sx={{ fontSize: 18 }} />;
    }
};

const getSeverityColor = (severity: string, theme: any) => {
    switch (severity) {
        case 'critical':
            return { bg: alpha(theme.palette.error.main, 0.08), border: alpha(theme.palette.error.main, 0.2), icon: theme.palette.error.main };
        case 'warning':
            return { bg: alpha(theme.palette.warning.main, 0.08), border: alpha(theme.palette.warning.main, 0.2), icon: theme.palette.warning.main };
        default:
            return { bg: alpha(theme.palette.success.main, 0.08), border: alpha(theme.palette.success.main, 0.2), icon: theme.palette.success.main };
    }
};

const ExplanationPanel: React.FC<ExplanationPanelProps> = ({
    componentName: _componentName,
    breakdown,
    isLoading = false,
    onRequestExplanation,
}) => {
    const theme = useTheme();
    const [showReasoningChain, setShowReasoningChain] = useState(false);

    if (isLoading) {
        return (
            <Box sx={{ mt: 2, p: 2, bgcolor: alpha(theme.palette.primary.main, 0.04), borderRadius: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <PsychologyIcon color="primary" sx={{ fontSize: 20 }} />
                    <Typography variant="body2" fontWeight={500}>
                        Generating explanation...
                    </Typography>
                </Box>
                <LinearProgress sx={{ borderRadius: 1 }} />
            </Box>
        );
    }

    if (!breakdown) {
        return (
            <Box sx={{ mt: 2 }}>
                <Tooltip title="Click to see why you got this score" arrow>
                    <Chip
                        icon={<PsychologyIcon sx={{ fontSize: 16 }} />}
                        label="Why this score?"
                        onClick={onRequestExplanation}
                        variant="outlined"
                        size="small"
                        sx={{
                            cursor: 'pointer',
                            borderColor: 'primary.main',
                            color: 'primary.main',
                            fontWeight: 500,
                            '&:hover': {
                                bgcolor: alpha(theme.palette.primary.main, 0.08),
                            }
                        }}
                    />
                </Tooltip>
            </Box>
        );
    }

    return (
        <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
        >
            <Box sx={{ mt: 2 }}>
                {/* Summary Card - NotebookLM Style */}
                <Paper
                    elevation={0}
                    sx={{
                        p: 2,
                        bgcolor: alpha(theme.palette.primary.main, 0.04),
                        border: `1px solid ${alpha(theme.palette.primary.main, 0.12)}`,
                        borderRadius: 3,
                    }}
                >
                    <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1.5 }}>
                        <TrendingUpIcon color="primary" sx={{ fontSize: 20, mt: 0.3 }} />
                        <Box sx={{ flex: 1 }}>
                            <Typography variant="body2" fontWeight={500} sx={{ lineHeight: 1.5 }}>
                                {breakdown.summary}
                            </Typography>
                        </Box>
                    </Box>

                    {/* Confidence Bar */}
                    <Box sx={{ mt: 2 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                            <Typography variant="caption" color="text.secondary">
                                AI Confidence
                            </Typography>
                            <Typography variant="caption" fontWeight={600} color="primary">
                                {Math.round(breakdown.confidence * 100)}%
                            </Typography>
                        </Box>
                        <LinearProgress
                            variant="determinate"
                            value={breakdown.confidence * 100}
                            sx={{
                                height: 4,
                                borderRadius: 2,
                                bgcolor: alpha(theme.palette.primary.main, 0.12),
                            }}
                        />
                    </Box>

                    {/* Reasoning Chain Toggle */}
                    {breakdown.reasoning_chain.length > 0 && (
                        <Box
                            onClick={() => setShowReasoningChain(!showReasoningChain)}
                            sx={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: 0.5,
                                mt: 2,
                                cursor: 'pointer',
                                color: 'text.secondary',
                                '&:hover': { color: 'primary.main' }
                            }}
                        >
                            <PsychologyIcon sx={{ fontSize: 16 }} />
                            <Typography variant="caption" fontWeight={500}>
                                Reasoning Chain ({breakdown.reasoning_chain.length} steps)
                            </Typography>
                            <IconButton size="small" sx={{ ml: 'auto', p: 0.5 }}>
                                {showReasoningChain ? <ExpandLessIcon fontSize="small" /> : <ExpandMoreIcon fontSize="small" />}
                            </IconButton>
                        </Box>
                    )}

                    <Collapse in={showReasoningChain}>
                        <Box sx={{ mt: 1.5, pl: 3 }}>
                            {breakdown.reasoning_chain.map((step, index) => (
                                <Box key={index} sx={{ display: 'flex', gap: 1, mb: 1 }}>
                                    <Chip
                                        label={index + 1}
                                        size="small"
                                        sx={{
                                            height: 20,
                                            minWidth: 20,
                                            fontSize: 11,
                                            fontWeight: 600,
                                            bgcolor: 'primary.main',
                                            color: 'white',
                                        }}
                                    />
                                    <Typography variant="caption" sx={{ lineHeight: 1.5, flex: 1 }}>
                                        {step}
                                    </Typography>
                                </Box>
                            ))}
                        </Box>
                    </Collapse>
                </Paper>

                {/* Findings - NotebookLM Flashcard Style */}
                {breakdown.findings.length > 0 && (
                    <Box sx={{ mt: 2 }}>
                        <Typography variant="caption" fontWeight={600} color="text.secondary" sx={{ mb: 1.5, display: 'block' }}>
                            Detailed Findings
                        </Typography>
                        <AnimatePresence>
                            {breakdown.findings.map((finding, index) => {
                                const colors = getSeverityColor(finding.severity, theme);
                                return (
                                    <motion.div
                                        key={index}
                                        initial={{ opacity: 0, x: -8 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: index * 0.08 }}
                                        whileHover={{
                                            scale: 1.02,
                                            transition: { duration: 0.2 }
                                        }}
                                        style={{ cursor: 'pointer' }}
                                    >
                                        <Paper
                                            elevation={0}
                                            sx={{
                                                p: 2,
                                                mb: 1.5,
                                                bgcolor: colors.bg,
                                                border: `1px solid ${colors.border}`,
                                                borderRadius: 2.5,
                                                transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
                                                cursor: 'pointer',
                                                '&:hover': {
                                                    boxShadow: `0 8px 24px ${colors.border}`,
                                                    borderColor: colors.icon,
                                                    transform: 'translateY(-2px)',
                                                }
                                            }}
                                        >
                                            {/* Finding Header */}
                                            <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1.5 }}>
                                                <Box sx={{ color: colors.icon, mt: 0.2 }}>
                                                    {getSeverityIcon(finding.severity)}
                                                </Box>
                                                <Box sx={{ flex: 1 }}>
                                                    <Typography variant="body2" fontWeight={500} sx={{ lineHeight: 1.5 }}>
                                                        {finding.finding}
                                                    </Typography>
                                                    <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                                                        📍 {finding.location}
                                                    </Typography>
                                                </Box>
                                            </Box>

                                            {/* Recommendation */}
                                            <Box sx={{
                                                display: 'flex',
                                                alignItems: 'flex-start',
                                                gap: 1,
                                                mt: 1.5,
                                                pt: 1.5,
                                                borderTop: `1px dashed ${colors.border}`,
                                            }}>
                                                <LightbulbIcon sx={{ fontSize: 16, color: 'warning.main', mt: 0.2 }} />
                                                <Typography variant="caption" sx={{ lineHeight: 1.5, flex: 1 }}>
                                                    {finding.recommendation}
                                                </Typography>
                                            </Box>
                                        </Paper>
                                    </motion.div>
                                );
                            })}
                        </AnimatePresence>
                    </Box>
                )}
            </Box>
        </motion.div>
    );
};

export default ExplanationPanel;
