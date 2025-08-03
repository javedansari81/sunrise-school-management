import { useTheme } from '@mui/material/styles';
import { useMediaQuery } from '@mui/material';

/**
 * Custom hook for responsive design utilities
 * Provides breakpoint checks and responsive values
 */
export const useResponsive = () => {
  const theme = useTheme();
  
  // Breakpoint checks
  const isMobile = useMediaQuery(theme.breakpoints.down('sm')); // < 600px
  const isTablet = useMediaQuery(theme.breakpoints.between('sm', 'md')); // 600px - 900px
  const isDesktop = useMediaQuery(theme.breakpoints.up('md')); // >= 900px
  const isLargeDesktop = useMediaQuery(theme.breakpoints.up('lg')); // >= 1200px
  
  // Specific size checks
  const isXSmall = useMediaQuery(theme.breakpoints.down('sm'));
  const isSmall = useMediaQuery(theme.breakpoints.between('sm', 'md'));
  const isMedium = useMediaQuery(theme.breakpoints.between('md', 'lg'));
  const isLarge = useMediaQuery(theme.breakpoints.up('lg'));
  
  // Dialog responsiveness
  const shouldUseFullScreenDialog = isMobile;
  const dialogMaxWidth = isMobile ? 'xs' : isTablet ? 'sm' : 'md';
  
  // Table responsiveness
  const tableSize = isMobile ? 'small' : 'medium';
  const shouldHideTableColumns = isMobile;
  
  // Button responsiveness
  const buttonSize = isMobile ? 'small' : 'medium';
  
  // Typography responsiveness
  const getResponsiveFontSize = (base: string) => ({
    xs: isMobile ? '0.875rem' : base,
    sm: base,
    md: base,
  });
  
  // Spacing responsiveness
  const getResponsiveSpacing = (mobile: number, desktop: number) => ({
    xs: mobile,
    sm: mobile,
    md: desktop,
  });
  
  // Grid responsiveness
  const getResponsiveGridColumns = (mobile: number, tablet: number, desktop: number) => ({
    xs: mobile,
    sm: tablet,
    md: desktop,
  });
  
  // Card responsiveness
  const getResponsiveCardProps = () => ({
    sx: {
      borderRadius: { xs: 2, sm: 3 },
      p: { xs: 2, sm: 3 },
      m: { xs: 1, sm: 2 },
    }
  });
  
  // Container responsiveness
  const getResponsiveContainerProps = () => ({
    sx: {
      px: { xs: 1, sm: 2, md: 3 },
      py: { xs: 1, sm: 2, md: 3 },
    }
  });
  
  return {
    // Breakpoint checks
    isMobile,
    isTablet,
    isDesktop,
    isLargeDesktop,
    isXSmall,
    isSmall,
    isMedium,
    isLarge,
    
    // Component-specific responsiveness
    shouldUseFullScreenDialog,
    dialogMaxWidth,
    tableSize,
    shouldHideTableColumns,
    buttonSize,
    
    // Utility functions
    getResponsiveFontSize,
    getResponsiveSpacing,
    getResponsiveGridColumns,
    getResponsiveCardProps,
    getResponsiveContainerProps,
    
    // Theme reference
    theme,
  };
};

export default useResponsive;
