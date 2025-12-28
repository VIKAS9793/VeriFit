import { useState } from 'react';
import { Box, Typography, Container, AppBar, Toolbar, Fade, Button, Chip } from '@mui/material';
import { UploadZone } from './components/UploadZone.tsx';
import { AnalysisDashboard } from './components/AnalysisDashboard.tsx';
import Footer from './components/Footer.tsx';
import { motion } from 'framer-motion';
import { VerifiedUser, AutoAwesome } from '@mui/icons-material';

// Background Gradient Component
const BackgroundGradient = () => (
    <Box sx={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        height: '600px',
        background: 'radial-gradient(circle at 50% -20%, #BCEBE5 0%, rgba(244, 251, 249, 0) 70%)',
        zIndex: -1,
        opacity: 0.8,
    }} />
);

function App() {
    const [resumeData, setResumeData] = useState<any | null>(null);

    return (
        <Box sx={{ minHeight: '100vh', position: 'relative', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
            <BackgroundGradient />

            {/* Navigation - Minimal & Floating */}
            <AppBar position="fixed" color="transparent" elevation={0} sx={{ top: 0, backdropFilter: 'blur(10px)', borderBottom: '1px solid rgba(0,0,0,0.03)' }}>
                <Container maxWidth="xl">
                    <Toolbar sx={{ py: 1 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, flexGrow: 1 }}>
                            <Box sx={{
                                width: 40,
                                height: 40,
                                bgcolor: 'primary.main',
                                borderRadius: '12px',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                boxShadow: '0 4px 12px rgba(0,106,96,0.2)'
                            }}>
                                <VerifiedUser sx={{ color: 'white' }} />
                            </Box>
                            <Typography variant="h5" color="text.primary" sx={{ fontWeight: 700, letterSpacing: '-0.02em' }}>
                                VeriFit
                            </Typography>
                            <Chip
                                label="v1.0"
                                size="small"
                                sx={{
                                    bgcolor: 'primary.container',
                                    color: 'primary.dark',
                                    fontWeight: 600,
                                    height: 24
                                }}
                            />
                        </Box>

                        {/* Minimal Header - No fake links */}
                    </Toolbar>
                </Container>
            </AppBar>

            <Toolbar /> {/* Spacer */}

            <Container maxWidth="lg" sx={{ py: 8, flexGrow: 1 }}>
                <Fade in timeout={800}>
                    <Box>
                        {!resumeData ? (
                            <Box sx={{
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'center',
                                textAlign: 'center',
                                mt: 4
                            }}>
                                <motion.div
                                    initial={{ opacity: 0, y: 30 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ duration: 0.8, ease: "easeOut" }}
                                >
                                    <Typography variant="h1" gutterBottom sx={{
                                        backgroundImage: 'linear-gradient(135deg, #006A60 0%, #004D40 100%)',
                                        backgroundClip: 'text',
                                        textFillColor: 'transparent',
                                        WebkitBackgroundClip: 'text',
                                        WebkitTextFillColor: 'transparent',
                                        mb: 2
                                    }}>
                                        Verify Your True Fit.
                                    </Typography>
                                </motion.div>

                                <motion.div
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
                                >
                                    <Typography variant="h5" color="text.secondary" sx={{ mb: 6, maxWidth: 680, mx: 'auto', lineHeight: 1.6 }}>
                                        Align your experience with job requirements using evidence-based analysis.
                                        <br />
                                        <Box component="span" sx={{ color: 'primary.main', fontWeight: 600 }}>Private, precise, and practical.</Box>
                                    </Typography>
                                </motion.div>

                                <motion.div
                                    initial={{ opacity: 0, scale: 0.95 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    transition={{ duration: 0.6, delay: 0.4 }}
                                    style={{ width: '100%', maxWidth: '700px' }}
                                >
                                    <UploadZone onUploadComplete={setResumeData} />

                                    <Box sx={{ mt: 4, display: 'flex', gap: 2, justifyContent: 'center', opacity: 0.7 }}>
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                            <AutoAwesome fontSize="small" color="secondary" />
                                            <Typography variant="caption" fontWeight="600">Privacy First</Typography>
                                        </Box>
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                            <VerifiedUser fontSize="small" color="secondary" />
                                            <Typography variant="caption" fontWeight="600">No Hallucinations</Typography>
                                        </Box>
                                    </Box>
                                </motion.div>
                            </Box>
                        ) : (
                            <Fade in>
                                <Box>
                                    <Button onClick={() => setResumeData(null)} sx={{ mb: 2 }}>← New Audit</Button>
                                    {/* Pass real data when ready, using Mock for now if structure differs */}
                                    <AnalysisDashboard data={resumeData || undefined} rawScore={resumeData?.raw_score} />
                                </Box>
                            </Fade>
                        )}
                    </Box>
                </Fade>
            </Container>

            <Footer />
        </Box>
    );
}

export default App;
