import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  IconButton,
  Collapse,
  Tooltip
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  FilterList as FilterListIcon
} from '@mui/icons-material';

interface CollapsibleFilterSectionProps {
  children: React.ReactNode;
  title?: string;
  defaultExpanded?: boolean;
  persistKey?: string; // Key for localStorage persistence
  actionButtons?: React.ReactNode; // Optional action buttons to show even when collapsed
}

const CollapsibleFilterSection: React.FC<CollapsibleFilterSectionProps> = ({
  children,
  title = 'Filters',
  defaultExpanded = true,
  persistKey,
  actionButtons
}) => {
  // Initialize state from localStorage if persistKey is provided
  const [expanded, setExpanded] = useState<boolean>(() => {
    if (persistKey) {
      const saved = localStorage.getItem(`filter-expanded-${persistKey}`);
      return saved !== null ? saved === 'true' : defaultExpanded;
    }
    return defaultExpanded;
  });

  // Save to localStorage when expanded state changes
  useEffect(() => {
    if (persistKey) {
      localStorage.setItem(`filter-expanded-${persistKey}`, expanded.toString());
    }
  }, [expanded, persistKey]);

  const handleToggle = () => {
    setExpanded(!expanded);
  };

  return (
    <Paper 
      elevation={3} 
      sx={{ 
        mb: 3,
        overflow: 'hidden',
        transition: 'all 0.3s ease-in-out'
      }}
    >
      {/* Header with toggle button */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          p: 2,
          borderBottom: expanded ? 1 : 0,
          borderColor: 'divider',
          bgcolor: 'background.paper'
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <FilterListIcon color="primary" />
          <Typography variant="h6" fontWeight="bold">
            {title}
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {/* Action buttons (always visible) */}
          {actionButtons && (
            <Box sx={{ mr: 1 }}>
              {actionButtons}
            </Box>
          )}

          {/* Toggle button */}
          <Tooltip title={expanded ? 'Collapse filters' : 'Expand filters'}>
            <IconButton
              onClick={handleToggle}
              size="small"
              sx={{
                transition: 'transform 0.3s ease-in-out',
                transform: expanded ? 'rotate(0deg)' : 'rotate(180deg)'
              }}
            >
              {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Collapsible filter content */}
      <Collapse in={expanded} timeout="auto">
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      </Collapse>
    </Paper>
  );
};

export default CollapsibleFilterSection;

