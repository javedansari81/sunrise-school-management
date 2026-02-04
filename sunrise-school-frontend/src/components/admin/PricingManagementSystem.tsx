import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Snackbar,
  Alert,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  MenuItem,
  Chip,
  IconButton,
  CircularProgress,
  Typography,
  useMediaQuery,
  useTheme,
  Fab,
} from '@mui/material';
import {
  Add as AddIcon,
  Visibility as VisibilityIcon
} from '@mui/icons-material';
import PricingDialog from './inventory/PricingDialog';
import CollapsibleFilterSection from '../common/CollapsibleFilterSection';
import { getPricing, InventoryPricing } from '../../services/inventoryService';
import { configurationService } from '../../services/configurationService';

interface PricingManagementSystemProps {
  configuration: any;
}

const PricingManagementSystem: React.FC<PricingManagementSystemProps> = ({ configuration }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  // Filter state
  const [itemTypeId, setItemTypeId] = useState<number | null>(null);
  const [pricingStatus, setPricingStatus] = useState<boolean>(true);

  // Dialog control state
  const [pricingDialogOpen, setPricingDialogOpen] = useState(false);
  const [selectedPricing, setSelectedPricing] = useState<InventoryPricing | null>(null);

  // Pricing state
  const [pricingList, setPricingList] = useState<InventoryPricing[]>([]);
  const [pricingLoading, setPricingLoading] = useState(false);

  // Get current session year ID from centralized configuration service
  const currentSessionYearId = configurationService.getCurrentSessionYearId();

  // Snackbar
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'info' | 'warning';
  }>({
    open: false,
    message: '',
    severity: 'success'
  });

  // Load pricing data
  const loadPricing = useCallback(async () => {
    try {
      setPricingLoading(true);
      const params: any = {
        session_year_id: currentSessionYearId,
        is_active: pricingStatus,
      };
      if (itemTypeId) {
        params.item_type_id = itemTypeId;
      }
      const data = await getPricing(params);
      setPricingList(data);
    } catch (err) {
      console.error('Error loading pricing:', err);
      setSnackbar({ open: true, message: 'Failed to load pricing', severity: 'error' });
    } finally {
      setPricingLoading(false);
    }
  }, [currentSessionYearId, pricingStatus, itemTypeId]);

  useEffect(() => {
    loadPricing();
  }, [loadPricing]);

  const handleSnackbarClose = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const handleEditPricing = (pricing: InventoryPricing) => {
    setSelectedPricing(pricing);
    setPricingDialogOpen(true);
  };

  const handlePricingSuccess = () => {
    setSnackbar({ open: true, message: 'Pricing saved successfully', severity: 'success' });
    loadPricing();
  };

  return (
    <Box sx={{ width: '100%' }}>
      {/* Collapsible Filter Section */}
      <CollapsibleFilterSection
        title="Filters"
        defaultExpanded={true}
        persistKey="pricing-management"
      >
        <Box sx={{
          display: 'flex',
          gap: { xs: 1.5, sm: 2 },
          flexWrap: 'wrap',
          flexDirection: { xs: 'column', sm: 'row' }
        }}>
          <TextField
            select
            label="Item Type"
            value={itemTypeId || ''}
            onChange={(e) => setItemTypeId(e.target.value ? Number(e.target.value) : null)}
            sx={{ minWidth: { xs: '100%', sm: 200 } }}
            size="small"
            fullWidth={isMobile}
          >
            <MenuItem value="">All Items</MenuItem>
            {configuration?.inventory_item_types?.map((item: any) => (
              <MenuItem key={item.id} value={item.id}>
                {item.description}
              </MenuItem>
            ))}
          </TextField>

          <TextField
            select
            label="Status"
            value={pricingStatus ? 'active' : 'inactive'}
            onChange={(e) => setPricingStatus(e.target.value === 'active')}
            sx={{ minWidth: { xs: '100%', sm: 150 } }}
            size="small"
            fullWidth={isMobile}
          >
            <MenuItem value="active">Active</MenuItem>
            <MenuItem value="inactive">Inactive</MenuItem>
          </TextField>
        </Box>
      </CollapsibleFilterSection>

      {/* Pricing Table */}
      <Paper sx={{ overflow: 'hidden' }}>
        <TableContainer sx={{
          maxHeight: { xs: '60vh', sm: '70vh' },
          overflowX: 'auto'
        }}>
          <Table size={isMobile ? 'small' : 'medium'} stickyHeader>
            <TableHead>
              <TableRow sx={{ bgcolor: 'white' }}>
                <TableCell sx={{
                  fontSize: { xs: '0.75rem', sm: '0.875rem' },
                  py: { xs: 1, sm: 1.5 },
                  minWidth: { xs: 50, sm: 60 }
                }}>
                  Image
                </TableCell>
                <TableCell sx={{
                  fontSize: { xs: '0.75rem', sm: '0.875rem' },
                  py: { xs: 1, sm: 1.5 },
                  minWidth: { xs: 100, sm: 120 }
                }}>
                  Item
                </TableCell>
                <TableCell sx={{
                  fontSize: { xs: '0.75rem', sm: '0.875rem' },
                  py: { xs: 1, sm: 1.5 },
                  minWidth: { xs: 60, sm: 80 }
                }}>
                  Size
                </TableCell>
                <TableCell sx={{
                  fontSize: { xs: '0.75rem', sm: '0.875rem' },
                  py: { xs: 1, sm: 1.5 },
                  minWidth: { xs: 60, sm: 80 }
                }}>
                  Class
                </TableCell>
                <TableCell
                  align="right"
                  sx={{
                    fontSize: { xs: '0.75rem', sm: '0.875rem' },
                    py: { xs: 1, sm: 1.5 },
                    minWidth: { xs: 80, sm: 100 }
                  }}
                >
                  Price
                </TableCell>
                <TableCell sx={{
                  fontSize: { xs: '0.75rem', sm: '0.875rem' },
                  py: { xs: 1, sm: 1.5 },
                  minWidth: { xs: 100, sm: 120 }
                }}>
                  Effective From
                </TableCell>
                <TableCell sx={{
                  fontSize: { xs: '0.75rem', sm: '0.875rem' },
                  py: { xs: 1, sm: 1.5 },
                  minWidth: { xs: 100, sm: 120 }
                }}>
                  Effective To
                </TableCell>
                <TableCell sx={{
                  fontSize: { xs: '0.75rem', sm: '0.875rem' },
                  py: { xs: 1, sm: 1.5 },
                  minWidth: { xs: 70, sm: 80 }
                }}>
                  Status
                </TableCell>
                <TableCell
                  align="center"
                  sx={{
                    fontSize: { xs: '0.75rem', sm: '0.875rem' },
                    py: { xs: 1, sm: 1.5 },
                    minWidth: { xs: 60, sm: 80 }
                  }}
                >
                  Actions
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {pricingLoading ? (
                <TableRow>
                  <TableCell colSpan={9} align="center">
                    <CircularProgress size={40} />
                  </TableCell>
                </TableRow>
              ) : pricingList.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={9} align="center">
                    <Typography
                      color="text.secondary"
                      sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }}
                    >
                      No pricing records found
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                pricingList.map((pricing) => (
                  <TableRow key={pricing.id} hover>
                    <TableCell sx={{ py: { xs: 0.5, sm: 1 } }}>
                      {pricing.item_image_url ? (
                        <Box
                          component="img"
                          src={pricing.item_image_url}
                          alt={pricing.item_type_description}
                          sx={{
                            width: { xs: 40, sm: 50 },
                            height: { xs: 40, sm: 50 },
                            objectFit: 'cover',
                            borderRadius: 1,
                          }}
                        />
                      ) : (
                        <Box
                          sx={{
                            width: { xs: 40, sm: 50 },
                            height: { xs: 40, sm: 50 },
                            bgcolor: 'grey.200',
                            borderRadius: 1,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                          }}
                        >
                          <Typography
                            variant="caption"
                            color="text.secondary"
                            sx={{ fontSize: { xs: '0.65rem', sm: '0.75rem' } }}
                          >
                            No Image
                          </Typography>
                        </Box>
                      )}
                    </TableCell>
                    <TableCell sx={{
                      py: { xs: 0.75, sm: 1.5 },
                      fontSize: { xs: '0.75rem', sm: '0.875rem' }
                    }}>
                      {pricing.item_type_description}
                    </TableCell>
                    <TableCell sx={{
                      py: { xs: 0.75, sm: 1.5 },
                      fontSize: { xs: '0.75rem', sm: '0.875rem' }
                    }}>
                      {pricing.size_name || 'All'}
                    </TableCell>
                    <TableCell sx={{
                      py: { xs: 0.75, sm: 1.5 },
                      fontSize: { xs: '0.75rem', sm: '0.875rem' }
                    }}>
                      {pricing.class_name || 'All'}
                    </TableCell>
                    <TableCell
                      align="right"
                      sx={{
                        py: { xs: 0.75, sm: 1.5 },
                        fontSize: { xs: '0.75rem', sm: '0.875rem' }
                      }}
                    >
                      ₹{pricing.unit_price}
                    </TableCell>
                    <TableCell sx={{
                      py: { xs: 0.75, sm: 1.5 },
                      fontSize: { xs: '0.75rem', sm: '0.875rem' }
                    }}>
                      {pricing.effective_from ? new Date(pricing.effective_from).toLocaleDateString() : '-'}
                    </TableCell>
                    <TableCell sx={{
                      py: { xs: 0.75, sm: 1.5 },
                      fontSize: { xs: '0.75rem', sm: '0.875rem' }
                    }}>
                      {pricing.effective_to ? new Date(pricing.effective_to).toLocaleDateString() : '-'}
                    </TableCell>
                    <TableCell sx={{ py: { xs: 0.75, sm: 1.5 } }}>
                      <Chip
                        label={pricing.is_active ? 'Active' : 'Inactive'}
                        color={pricing.is_active ? 'success' : 'default'}
                        size="small"
                        sx={{
                          fontSize: { xs: '0.65rem', sm: '0.75rem' },
                          height: { xs: 20, sm: 24 }
                        }}
                      />
                    </TableCell>
                    <TableCell
                      align="center"
                      sx={{ py: { xs: 0.75, sm: 1.5 } }}
                    >
                      <IconButton
                        size="small"
                        onClick={() => handleEditPricing(pricing)}
                        title="Edit"
                        sx={{
                          p: { xs: 0.5, sm: 1 },
                          minWidth: { xs: 36, sm: 40 },
                          minHeight: { xs: 36, sm: 40 }
                        }}
                      >
                        <VisibilityIcon fontSize="small" />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Dialogs */}
      <PricingDialog
        open={pricingDialogOpen}
        onClose={() => {
          setPricingDialogOpen(false);
          setSelectedPricing(null);
        }}
        onSuccess={handlePricingSuccess}
        pricing={selectedPricing}
        configuration={configuration}
      />

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleSnackbarClose} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>

      {/* Floating Action Button */}
      <Fab
        color="primary"
        aria-label="add price"
        variant="extended"
        onClick={() => {
          setSelectedPricing(null);
          setPricingDialogOpen(true);
        }}
        sx={{
          position: 'fixed',
          bottom: { xs: 16, sm: 24 },
          right: { xs: 16, sm: 24 },
          zIndex: 1000,
          minWidth: { xs: '48px', sm: '56px' },
          width: { xs: '48px', sm: '56px' },
          height: { xs: '48px', sm: '56px' },
          borderRadius: { xs: '24px', sm: '28px' },
          padding: { xs: '0 12px', sm: '0 16px' },
          transition: 'all 0.3s ease-in-out',
          overflow: 'hidden',
          boxShadow: 3,
          '& .MuiSvgIcon-root': {
            transition: 'margin 0.3s ease-in-out',
            marginRight: 0,
            fontSize: { xs: '1.25rem', sm: '1.5rem' },
          },
          '& .fab-text': {
            opacity: 0,
            width: 0,
            whiteSpace: 'nowrap',
            transition: 'opacity 0.3s ease-in-out, width 0.3s ease-in-out',
            overflow: 'hidden',
            fontSize: '0.875rem',
            fontWeight: 500,
            display: { xs: 'none', sm: 'inline' },
          },
          '@media (hover: hover) and (pointer: fine)': {
            '&:hover': {
              width: 'auto',
              minWidth: '170px',
              paddingRight: '20px',
              paddingLeft: '16px',
              boxShadow: 6,
              '& .MuiSvgIcon-root': {
                marginRight: '8px',
              },
              '& .fab-text': {
                opacity: 1,
                width: 'auto',
              },
            },
          },
          '&:active': {
            boxShadow: 6,
            transform: 'scale(0.95)',
          },
          '@media (max-width: 360px)': {
            bottom: '12px',
            right: '12px',
            minWidth: '44px',
            width: '44px',
            height: '44px',
            borderRadius: '22px',
          },
        }}
      >
        <AddIcon />
        <Box component="span" className="fab-text">
          Add New Price
        </Box>
      </Fab>
    </Box>
  );
};

export default PricingManagementSystem;

