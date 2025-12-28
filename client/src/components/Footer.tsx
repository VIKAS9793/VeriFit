import { Box, Container, Typography, Link } from '@mui/material';

const Footer = () => {
    const currentYear = new Date().getFullYear();

    return (
        <Box
            component="footer"
            sx={{
                py: 4,
                px: 2,
                mt: 'auto',
                borderTop: '1px solid',
                borderColor: 'divider',
                backgroundColor: 'background.paper', // Or 'surfaceContainerLow' 
            }}
        >
            <Container maxWidth="lg">
                <Box sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    flexDirection: { xs: 'column', sm: 'row' },
                    gap: 2
                }}>
                    <Typography variant="body2" color="text.secondary">
                        © {currentYear} <strong>Vikas Sahani</strong>. All rights reserved.
                    </Typography>

                    <Box sx={{ display: 'flex', gap: 3 }}>
                        <Link href="#" color="text.secondary" underline="hover" variant="body2">
                            Privacy Policy
                        </Link>
                        <Link href="#" color="text.secondary" underline="hover" variant="body2">
                            Terms of Service
                        </Link>
                    </Box>
                </Box>
            </Container>
        </Box>
    );
};

export default Footer;
