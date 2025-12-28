import {
    argbFromHex,
    themeFromSourceColor,
    hexFromArgb
} from "@material/material-color-utilities";
import { createTheme, alpha } from '@mui/material/styles';

/**
 * Generate a full Material 3 MUI Theme from a single seed color.
 * Uses Google's official algorithm (HCT color space) for harmonious tones.
 */
export const createM3Theme = (seedColor: string = '#006A60') => {
    // 1. Generate M3 Tonal Palette
    const m3Theme = themeFromSourceColor(argbFromHex(seedColor));
    const scheme = m3Theme.schemes.light; // Focusing on Light mode for MVP
    const palettes = m3Theme.palettes;

    // 2. Map Key Colors to Hex
    const primary = hexFromArgb(scheme.primary);
    const secondary = hexFromArgb(scheme.secondary);
    const error = hexFromArgb(scheme.error);

    const background = hexFromArgb(scheme.background);
    const surface = hexFromArgb(scheme.surface);

    // M3 Specific Surfaces (Using Tonal Palette for direct control)
    const surfaceContainerLow = hexFromArgb(palettes.neutral.tone(96));
    const surfaceContainer = hexFromArgb(palettes.neutral.tone(94));
    const surfaceContainerHigh = hexFromArgb(palettes.neutral.tone(92));

    const onPrimary = hexFromArgb(scheme.onPrimary);
    const primaryContainer = hexFromArgb(scheme.primaryContainer);

    // 3. Construct MUI Theme
    return createTheme({
        palette: {
            mode: 'light',
            primary: {
                main: primary,
                contrastText: onPrimary,
                light: primaryContainer, // Approximate mapping
                dark: onPrimary,
            },
            secondary: {
                main: secondary,
                contrastText: hexFromArgb(scheme.onSecondary),
                light: hexFromArgb(scheme.secondaryContainer),
            },
            error: {
                main: error,
                container: hexFromArgb(scheme.errorContainer),
            },
            background: {
                default: background,
                paper: surface,
            },
            // Custom M3 Tokens
            surfaceContainerLow,
            surfaceContainer,
            surfaceContainerHigh,

            text: {
                primary: hexFromArgb(scheme.onSurface),
                secondary: hexFromArgb(scheme.onSurfaceVariant),
            },
        },
        // Keep our Typography & Shape overrides
        typography: {
            fontFamily: [
                "'Google Sans Flex'",
                "'Google Sans'",
                "'Inter'",
                "sans-serif"
            ].join(','),
            h1: {
                fontFamily: "'Google Sans Flex', sans-serif",
                fontWeight: 800,
                fontSize: '4.5rem',
                lineHeight: 1.1,
                letterSpacing: '-0.025em',
                fontVariationSettings: "'opsz' 72, 'GRAD' 0",
            },
            h2: {
                fontFamily: "'Google Sans Flex', sans-serif",
                fontWeight: 700,
                fontSize: '3rem',
                lineHeight: 1.2,
                letterSpacing: '-0.02em',
                fontVariationSettings: "'opsz' 48, 'GRAD' 0",
            },
            h3: {
                fontFamily: "'Google Sans Flex', sans-serif",
                fontWeight: 600,
                fontSize: '2.25rem',
                fontVariationSettings: "'opsz' 36",
            },
            h6: {
                fontWeight: 600,
                letterSpacing: '0.01em',
            },
            body1: {
                fontFamily: "'Google Sans Flex', sans-serif",
                fontSize: '1.125rem',
                lineHeight: 1.6,
                letterSpacing: '0.01em',
                fontVariationSettings: "'opsz' 18",
            },
            button: {
                fontFamily: "'Google Sans Flex', sans-serif",
                fontWeight: 600,
                textTransform: 'none',
                letterSpacing: '0.02em',
                fontSize: '1rem',
            },
        },
        shape: {
            borderRadius: 24,
        },
        components: {
            MuiCssBaseline: {
                styleOverrides: {
                    body: {
                        backgroundColor: surfaceContainerLow, // Dynamic surface background
                        scrollbarWidth: 'thin',
                    },
                },
            },
            MuiButton: {
                styleOverrides: {
                    root: {
                        borderRadius: 100,
                        padding: '12px 32px',
                        boxShadow: 'none',
                        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                        '&:hover': {
                            boxShadow: `0px 4px 8px ${alpha(hexFromArgb(scheme.shadow), 0.15)}`, // Dynamic subtle shadow
                            transform: 'translateY(-1px)',
                        },
                    },
                    contained: {
                        backgroundColor: primary, // Ensure dynamic primary
                    }
                },
            },
            MuiCard: {
                styleOverrides: {
                    root: {
                        borderRadius: 28,
                        backgroundColor: surfaceContainerLow,
                        boxShadow: '0px 2px 12px rgba(0,0,0,0.04)',
                    }
                }
            }
        }
    } as any); // Type cast for custom palette props
};
