import { useCallback, useState } from 'react';
import { Box, Typography, Paper, CircularProgress, Alert, Chip } from '@mui/material';
import { useTheme, alpha } from '@mui/material/styles';
import { motion, AnimatePresence } from 'framer-motion';
import { CloudUpload, PictureAsPdf, Description } from '@mui/icons-material';
import { uploadResume, analyzeResume } from '../api/client';

interface UploadZoneProps {
    onUploadComplete: (data: any) => void;
}

export const UploadZone = ({ onUploadComplete }: UploadZoneProps) => {
    const theme = useTheme();
    const [isDragActive, setIsDragActive] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const [statusText, setStatusText] = useState('');

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragActive(true);
    }, []);

    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragActive(false);
    }, []);

    const handleDrop = useCallback(async (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            await processFile(e.dataTransfer.files[0]);
        }
    }, []);

    const handleFileInput = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            await processFile(e.target.files[0]);
        }
    };

    const processFile = async (file: File) => {
        if (file.size > 10 * 1024 * 1024) {
            setError("File exceeds 10MB limit");
            return;
        }
        const ext = file.name.split('.').pop()?.toLowerCase();
        if (!['pdf', 'docx', 'doc', 'txt'].includes(ext || '')) {
            setError("Invalid file type. Please upload PDF, DOCX, or TXT.");
            return;
        }

        setLoading(true);
        setError(null);

        try {
            // 1. Upload & Parse
            setStatusText('Verifying & Parsing...');
            const parseResponse = await uploadResume(file);
            console.log('Parse result:', parseResponse);

            // 2. Analyze
            setStatusText('Generating Analysis Scores...');
            const analyzeResponse = await analyzeResume(parseResponse.data);
            console.log('Analysis result:', analyzeResponse);

            // 3. Map Data for Dashboard
            const dashboardData = {
                veriscore: analyzeResponse.score.overall_score,
                impact_score: analyzeResponse.score.keyword_score?.score || analyzeResponse.score.format_score?.score || 75,
                brevity_score: analyzeResponse.score.structure_score?.score || 75,
                style_score: analyzeResponse.score.readability_score?.score || 75,
                skills: [
                    {
                        category: "Detected Skills",
                        items: parseResponse.data.skills?.map((s: any) => s.name) || []
                    }
                ],
                // Raw score object for XAI Layer (Why This Score?)
                raw_score: analyzeResponse.score,
                // Add raw parsed data for reference if needed
                raw_resume: parseResponse.data
            };

            setStatusText('Analysis Complete!');

            // Wait for success animation
            await new Promise(resolve => setTimeout(resolve, 1000));
            onUploadComplete(dashboardData);
        } catch (err: any) {
            console.error(err);
            setError(err.response?.data?.error || "Upload failed. Please try again.");
        } finally {
            setLoading(false);
            setStatusText('');
        }
    };

    return (
        <Box sx={{ width: '100%' }}>
            <AnimatePresence>
                {error && (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.9 }}
                    >
                        <Alert
                            severity="error"
                            sx={{
                                mb: 2,
                                borderRadius: 3,
                                boxShadow: '0 4px 12px rgba(186, 26, 26, 0.1)'
                            }}
                        >
                            {error}
                        </Alert>
                    </motion.div>
                )}
            </AnimatePresence>

            <Paper
                component={motion.div}
                whileHover={{
                    y: -4,
                    boxShadow: '0px 12px 24px rgba(0,0,0,0.08)'
                }}
                whileTap={{ scale: 0.995 }}
                elevation={0}
                sx={{
                    p: 8,
                    border: `2px dashed ${isDragActive ? theme.palette.primary.main : alpha(theme.palette.primary.main, 0.2)}`,
                    backgroundColor: isDragActive
                        ? alpha(theme.palette.primary.main, 0.08)
                        : alpha(theme.palette.primary.main, 0.02), // Subtle branded tint
                    borderRadius: 8,
                    cursor: 'pointer',
                    textAlign: 'center',
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                    position: 'relative',
                    overflow: 'hidden',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    boxShadow: 'none', // Flat M3 look, color provides separation
                    '&:hover': {
                        backgroundColor: alpha(theme.palette.primary.main, 0.04),
                        borderColor: alpha(theme.palette.primary.main, 0.4),
                    }
                }}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => document.getElementById('file-input')?.click()}
            >
                <input
                    id="file-input"
                    type="file"
                    accept=".pdf,.docx,.doc,.txt"
                    onChange={handleFileInput}
                    style={{ display: 'none' }}
                />

                {loading ? (
                    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 3 }}>
                        <CircularProgress size={56} thickness={4} />
                        <Typography variant="h6" sx={{ fontWeight: 600 }}>
                            {statusText || 'Processing...'}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            Checking structural integrity & magic numbers
                        </Typography>
                    </Box>
                ) : (
                    <>
                        <motion.div
                            initial={{ scale: 1 }}
                            animate={{ scale: isDragActive ? 1.1 : 1 }}
                            transition={{ duration: 0.2 }}
                        >
                            <Box sx={{
                                width: 80,
                                height: 80,
                                borderRadius: '50%',
                                bgcolor: isDragActive ? 'primary.light' : 'rgba(0,0,0,0.03)',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                mb: 3,
                                color: isDragActive ? 'white' : 'text.secondary'
                            }}>
                                <CloudUpload sx={{ fontSize: 40 }} />
                            </Box>
                        </motion.div>

                        <Typography variant="h4" gutterBottom sx={{
                            color: isDragActive ? 'primary.main' : 'text.primary',
                            fontWeight: 700
                        }}>
                            {isDragActive ? 'Drop to Verify' : 'Initiate Analysis'}
                        </Typography>

                        <Typography variant="body1" color="text.secondary" sx={{ mb: 4, maxWidth: 360 }}>
                            Securely upload to begin evidence-based verification.
                            <br />
                            <Typography component="span" variant="caption" color="text.disabled">
                                Supported: PDF, DOCX (Max 10MB)
                            </Typography>
                        </Typography>

                        <Box sx={{ display: 'flex', gap: 2 }}>
                            <Chip icon={<PictureAsPdf fontSize="small" />} label="PDF" sx={{ bgcolor: 'rgba(0,0,0,0.04)' }} />
                            <Chip icon={<Description fontSize="small" />} label="DOCX" sx={{ bgcolor: 'rgba(0,0,0,0.04)' }} />
                        </Box>
                    </>
                )}
            </Paper>
        </Box>
    );
};

// Helper for Chips
// import { Chip } from '@mui/material'; // Removed

