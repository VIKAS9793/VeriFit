/**
 * RewritePanel.tsx
 * HITL Rewrite Interface - Shows AI suggestions with diff and approval buttons
 * Compliance: SYSTEM.md Section 6 (Pause, Show Diff, Require Approval, Log)
 */

import React, { useState } from 'react';
import {
    Box,
    Paper,
    Typography,
    Button,
    Chip,
    LinearProgress,
    Divider,
    Alert,
    Collapse,
} from '@mui/material';
import { useTheme, alpha } from '@mui/material/styles';
import { motion, AnimatePresence } from 'framer-motion';
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import DifferenceIcon from '@mui/icons-material/Difference';
import { requestRewrite, approveRewrite } from '../api/client';

interface RewriteSuggestion {
    id: string;
    section: string;
    original_text: string;
    suggested_text: string;
    diff: string;
    rationale: string;
    risk_level: 'low' | 'medium' | 'high';
    validation: {
        is_valid: boolean;
        issues: string[];
    };
}

interface RewritePanelProps {
    resumeData: any;
    disabled?: boolean;
}

const getRiskColor = (risk: string) => {
    switch (risk) {
        case 'low': return 'success';
        case 'medium': return 'warning';
        case 'high': return 'error';
        default: return 'default';
    }
};

const RewritePanel: React.FC<RewritePanelProps> = ({ resumeData, disabled = false }) => {
    const theme = useTheme();
    const [isLoading, setIsLoading] = useState(false);
    const [suggestions, setSuggestions] = useState<RewriteSuggestion[]>([]);
    const [error, setError] = useState<string | null>(null);
    const [approvedIds, setApprovedIds] = useState<Set<string>>(new Set());
    const [rejectedIds, setRejectedIds] = useState<Set<string>>(new Set());
    const [expanded] = useState(true);

    const handleRequestSuggestions = async () => {
        if (!resumeData) return;

        setIsLoading(true);
        setError(null);
        setSuggestions([]);
        setApprovedIds(new Set());
        setRejectedIds(new Set());

        try {
            const response = await requestRewrite(resumeData);
            if (response.suggestions && response.suggestions.length > 0) {
                setSuggestions(response.suggestions);
            } else {
                setError('No improvement suggestions generated. Your resume is already well-optimized!');
            }
        } catch (err: any) {
            setError(err.message || 'Failed to generate suggestions');
        } finally {
            setIsLoading(false);
        }
    };

    const handleApprove = async (suggestion: RewriteSuggestion) => {
        try {
            await approveRewrite(suggestion.id, true);
            setApprovedIds(prev => new Set([...prev, suggestion.id]));
        } catch (err) {
            console.error('Approval failed:', err);
        }
    };

    const handleReject = async (suggestion: RewriteSuggestion) => {
        try {
            await approveRewrite(suggestion.id, false);
            setRejectedIds(prev => new Set([...prev, suggestion.id]));
        } catch (err) {
            console.error('Rejection failed:', err);
        }
    };

    const pendingSuggestions = suggestions.filter(
        s => !approvedIds.has(s.id) && !rejectedIds.has(s.id)
    );

    return (
        <Paper
            elevation={0}
            sx={{
                p: 3,
                borderRadius: 4,
                border: '1px solid',
                borderColor: 'divider',
                bgcolor: alpha(theme.palette.primary.main, 0.02),
            }}
        >
            {/* Header */}
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                    <AutoFixHighIcon sx={{ color: 'primary.main' }} />
                    <Typography variant="h6" fontWeight={600}>
                        AI-Powered Improvements
                    </Typography>
                    <Chip
                        label="HITL Required"
                        size="small"
                        color="warning"
                        variant="outlined"
                        sx={{ ml: 1 }}
                    />
                </Box>
                <Button
                    variant="contained"
                    onClick={handleRequestSuggestions}
                    disabled={disabled || isLoading || !resumeData}
                    startIcon={<AutoFixHighIcon />}
                    sx={{ borderRadius: 3 }}
                >
                    {isLoading ? 'Analyzing...' : 'Suggest Improvements'}
                </Button>
            </Box>

            {/* Loading State */}
            {isLoading && (
                <Box sx={{ mb: 2 }}>
                    <LinearProgress sx={{ borderRadius: 2 }} />
                    <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                        🧠 AI is analyzing your resume for improvement opportunities...
                    </Typography>
                </Box>
            )}

            {/* Error State */}
            {error && (
                <Alert severity="info" sx={{ mb: 2, borderRadius: 2 }}>
                    {error}
                </Alert>
            )}

            {/* Suggestions List */}
            <AnimatePresence>
                {suggestions.length > 0 && (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0 }}
                    >
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                            <DifferenceIcon fontSize="small" color="primary" />
                            <Typography variant="subtitle2">
                                {pendingSuggestions.length} pending review • {approvedIds.size} approved • {rejectedIds.size} rejected
                            </Typography>
                        </Box>

                        <Collapse in={expanded}>
                            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                                {suggestions.map((suggestion, index) => {
                                    const isApproved = approvedIds.has(suggestion.id);
                                    const isRejected = rejectedIds.has(suggestion.id);
                                    const isDecided = isApproved || isRejected;

                                    return (
                                        <motion.div
                                            key={suggestion.id}
                                            initial={{ opacity: 0, x: -10 }}
                                            animate={{ opacity: isDecided ? 0.6 : 1, x: 0 }}
                                            transition={{ delay: index * 0.1 }}
                                        >
                                            <Paper
                                                elevation={0}
                                                sx={{
                                                    p: 2.5,
                                                    borderRadius: 3,
                                                    border: '1px solid',
                                                    borderColor: isApproved
                                                        ? 'success.main'
                                                        : isRejected
                                                            ? 'error.light'
                                                            : 'divider',
                                                    bgcolor: isApproved
                                                        ? alpha(theme.palette.success.main, 0.05)
                                                        : isRejected
                                                            ? alpha(theme.palette.error.main, 0.02)
                                                            : 'background.paper',
                                                    transition: 'all 0.3s ease',
                                                }}
                                            >
                                                {/* Suggestion Header */}
                                                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                        <Chip
                                                            label={suggestion.section}
                                                            size="small"
                                                            color="primary"
                                                            variant="outlined"
                                                        />
                                                        <Chip
                                                            label={`Risk: ${suggestion.risk_level}`}
                                                            size="small"
                                                            color={getRiskColor(suggestion.risk_level) as any}
                                                            icon={suggestion.risk_level === 'high' ? <WarningAmberIcon /> : undefined}
                                                        />
                                                        {isApproved && (
                                                            <Chip label="✓ Approved" size="small" color="success" />
                                                        )}
                                                        {isRejected && (
                                                            <Chip label="✗ Rejected" size="small" color="error" variant="outlined" />
                                                        )}
                                                    </Box>
                                                </Box>

                                                {/* Diff View */}
                                                <Box sx={{
                                                    display: 'grid',
                                                    gridTemplateColumns: '1fr 1fr',
                                                    gap: 2,
                                                    mb: 2
                                                }}>
                                                    {/* Original */}
                                                    <Box sx={{
                                                        p: 2,
                                                        borderRadius: 2,
                                                        bgcolor: alpha(theme.palette.error.main, 0.05),
                                                        border: `1px solid ${alpha(theme.palette.error.main, 0.2)}`,
                                                    }}>
                                                        <Typography variant="caption" color="error.main" fontWeight={600} gutterBottom>
                                                            ORIGINAL
                                                        </Typography>
                                                        <Typography variant="body2" sx={{ mt: 1, lineHeight: 1.6 }}>
                                                            {suggestion.original_text}
                                                        </Typography>
                                                    </Box>

                                                    {/* Suggested */}
                                                    <Box sx={{
                                                        p: 2,
                                                        borderRadius: 2,
                                                        bgcolor: alpha(theme.palette.success.main, 0.05),
                                                        border: `1px solid ${alpha(theme.palette.success.main, 0.2)}`,
                                                    }}>
                                                        <Typography variant="caption" color="success.main" fontWeight={600} gutterBottom>
                                                            SUGGESTED
                                                        </Typography>
                                                        <Typography variant="body2" sx={{ mt: 1, lineHeight: 1.6 }}>
                                                            {suggestion.suggested_text}
                                                        </Typography>
                                                    </Box>
                                                </Box>

                                                {/* Rationale */}
                                                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 2 }}>
                                                    💡 {suggestion.rationale}
                                                </Typography>

                                                {/* Validation Issues */}
                                                {!suggestion.validation.is_valid && (
                                                    <Alert severity="warning" sx={{ mb: 2, borderRadius: 2 }}>
                                                        <strong>Validation Warning:</strong> {suggestion.validation.issues.join(', ')}
                                                    </Alert>
                                                )}

                                                <Divider sx={{ my: 2 }} />

                                                {/* Action Buttons */}
                                                {!isDecided && (
                                                    <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                                                        <Button
                                                            variant="outlined"
                                                            color="error"
                                                            startIcon={<CancelIcon />}
                                                            onClick={() => handleReject(suggestion)}
                                                            sx={{ borderRadius: 2 }}
                                                        >
                                                            Reject
                                                        </Button>
                                                        <Button
                                                            variant="contained"
                                                            color="success"
                                                            startIcon={<CheckCircleIcon />}
                                                            onClick={() => handleApprove(suggestion)}
                                                            sx={{ borderRadius: 2 }}
                                                        >
                                                            Approve
                                                        </Button>
                                                    </Box>
                                                )}
                                            </Paper>
                                        </motion.div>
                                    );
                                })}
                            </Box>
                        </Collapse>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Empty State */}
            {!isLoading && suggestions.length === 0 && !error && (
                <Box sx={{
                    textAlign: 'center',
                    py: 4,
                    color: 'text.secondary'
                }}>
                    <AutoFixHighIcon sx={{ fontSize: 48, opacity: 0.3, mb: 1 }} />
                    <Typography variant="body2">
                        Click "Suggest Improvements" to get AI-powered recommendations
                    </Typography>
                    <Typography variant="caption" sx={{ mt: 0.5, display: 'block' }}>
                        All suggestions require your approval before any changes are made
                    </Typography>
                </Box>
            )}
        </Paper>
    );
};

export default RewritePanel;
