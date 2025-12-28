import React, { useState } from 'react';
import { Box, Typography, Paper } from '@mui/material';
import { alpha, useTheme } from '@mui/material/styles';
import { motion } from 'framer-motion';
import { AutoAwesome as SparkleIcon } from '@mui/icons-material';

interface SkillFlashcardProps {
    skill: string;
    index: number;
}

/**
 * Interactive Skill Flashcard - NotebookLM Style
 * Features: Hover elevation, subtle rotation, and flip interaction
 */
const SkillFlashcard: React.FC<SkillFlashcardProps> = ({ skill, index }) => {
    const theme = useTheme();
    const [isHovered, setIsHovered] = useState(false);
    const [isFlipped, setIsFlipped] = useState(false);

    // Generate a consistent category based on skill keywords
    const getSkillCategory = (skill: string): string => {
        const lowerSkill = skill.toLowerCase();
        if (lowerSkill.includes('management') || lowerSkill.includes('leadership')) return 'Leadership';
        if (lowerSkill.includes('design') || lowerSkill.includes('ux') || lowerSkill.includes('ui')) return 'Design';
        if (lowerSkill.includes('python') || lowerSkill.includes('react') || lowerSkill.includes('javascript')) return 'Technical';
        if (lowerSkill.includes('analysis') || lowerSkill.includes('data')) return 'Analytics';
        if (lowerSkill.includes('communication') || lowerSkill.includes('stakeholder')) return 'Soft Skills';
        return 'Core Skill';
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05, duration: 0.3 }}
            whileHover={{
                scale: 1.03,
                rotateY: 5,
                transition: { duration: 0.2 }
            }}
            whileTap={{ scale: 0.98 }}
            onHoverStart={() => setIsHovered(true)}
            onHoverEnd={() => setIsHovered(false)}
            onClick={() => setIsFlipped(!isFlipped)}
            style={{
                cursor: 'pointer',
                perspective: '1000px',
            }}
        >
            <Paper
                elevation={isHovered ? 4 : 0}
                sx={{
                    p: 2,
                    borderRadius: 3,
                    bgcolor: isHovered
                        ? alpha(theme.palette.primary.main, 0.08)
                        : 'background.paper',
                    border: '1px solid',
                    borderColor: isHovered ? 'primary.main' : 'divider',
                    transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
                    transform: isFlipped ? 'rotateY(180deg)' : 'rotateY(0deg)',
                    transformStyle: 'preserve-3d',
                    minHeight: 80,
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'center',
                    alignItems: 'center',
                    position: 'relative',
                    overflow: 'hidden',
                    boxShadow: isHovered
                        ? `0 8px 24px ${alpha(theme.palette.primary.main, 0.2)}`
                        : 'none',
                }}
            >
                {/* Front of card */}
                <Box
                    sx={{
                        backfaceVisibility: 'hidden',
                        display: isFlipped ? 'none' : 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        gap: 0.5,
                    }}
                >
                    {isHovered && (
                        <motion.div
                            initial={{ opacity: 0, scale: 0 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ duration: 0.2 }}
                        >
                            <SparkleIcon
                                sx={{
                                    fontSize: 16,
                                    color: 'primary.main',
                                    mb: 0.5
                                }}
                            />
                        </motion.div>
                    )}
                    <Typography
                        variant="body2"
                        fontWeight={isHovered ? 600 : 500}
                        sx={{
                            textAlign: 'center',
                            lineHeight: 1.4,
                            color: isHovered ? 'primary.main' : 'text.primary',
                            transition: 'all 0.2s ease',
                        }}
                    >
                        {skill}
                    </Typography>
                </Box>

                {/* Back of card (shown when flipped) */}
                <Box
                    sx={{
                        backfaceVisibility: 'hidden',
                        display: isFlipped ? 'flex' : 'none',
                        flexDirection: 'column',
                        alignItems: 'center',
                        gap: 0.5,
                        transform: 'rotateY(180deg)',
                    }}
                >
                    <Typography
                        variant="caption"
                        color="primary"
                        fontWeight={600}
                    >
                        {getSkillCategory(skill)}
                    </Typography>
                    <Typography
                        variant="caption"
                        color="text.secondary"
                        sx={{ textAlign: 'center' }}
                    >
                        Detected in your resume
                    </Typography>
                </Box>

                {/* Hover indicator */}
                {isHovered && (
                    <Box
                        sx={{
                            position: 'absolute',
                            bottom: 0,
                            left: 0,
                            right: 0,
                            height: 3,
                            bgcolor: 'primary.main',
                            borderBottomLeftRadius: 12,
                            borderBottomRightRadius: 12,
                        }}
                    />
                )}
            </Paper>
        </motion.div>
    );
};

interface SkillFlashcardGridProps {
    skills: Array<{ category: string; items: string[] }>;
}

/**
 * Grid of interactive skill flashcards
 */
export const SkillFlashcardGrid: React.FC<SkillFlashcardGridProps> = ({ skills }) => {
    const theme = useTheme();

    // Flatten skills from all categories
    const allSkills = skills.flatMap(cat => cat.items);

    if (allSkills.length === 0) {
        return (
            <Paper sx={{ p: 4, borderRadius: 4, textAlign: 'center' }}>
                <Typography color="text.secondary">No skills detected</Typography>
            </Paper>
        );
    }

    return (
        <Paper sx={{ p: 4, borderRadius: 4 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
                <Typography variant="h5" sx={{ fontWeight: 700 }}>
                    Detected Skills
                </Typography>
                <Typography
                    variant="caption"
                    sx={{
                        bgcolor: alpha(theme.palette.primary.main, 0.1),
                        color: 'primary.main',
                        px: 1.5,
                        py: 0.5,
                        borderRadius: 2,
                        fontWeight: 600,
                    }}
                >
                    {allSkills.length} found
                </Typography>
            </Box>

            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Click any card to see its category
            </Typography>

            <Box
                sx={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))',
                    gap: 2,
                }}
            >
                {allSkills.map((skill, index) => (
                    <SkillFlashcard
                        key={skill}
                        skill={skill}
                        index={index}
                    />
                ))}
            </Box>
        </Paper>
    );
};

export default SkillFlashcard;
