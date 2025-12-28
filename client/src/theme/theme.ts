import { createM3Theme } from './m3utils.ts';

/**
 * Deep Material 3 (M3) Design Theme - "VeriFit Premium"
 * 
 * Philosophy:
 * - Expressive: Uses Google Sans Flex with aggressive optical sizing.
 * - Tonal: Uses Surface Container colors (not just white) for depth.
 * - Playful: Large border radius (28px+), pill buttons.
 */

// Generate theme from VeriFit Teal seed
export const theme = createM3Theme('#006A60');

// Types (kept for module augmentation)
declare module '@mui/material/styles' {
    interface Palette {
        surfaceContainerLow: string;
        surfaceContainer: string;
        surfaceContainerHigh: string;
    }
    interface PaletteOptions {
        surfaceContainerLow?: string;
        surfaceContainer?: string;
        surfaceContainerHigh?: string;
    }

    interface SimplePaletteColorOptions {
        container?: string;
    }

    interface PaletteColor {
        container: string;
    }
}
