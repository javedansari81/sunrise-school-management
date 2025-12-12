import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Snackbar,
  Alert,
  Tabs,
  Tab,
  Button,
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
  useTheme
} from '@mui/material';
import {
  Add as AddIcon,
  Visibility as VisibilityIcon
} from '@mui/icons-material';
import StockProcurementsTab from './inventory/StockProcurementsTab';
import StockLevelsTab from './inventory/StockLevelsTab';
import PricingDialog from './inventory/PricingDialog';
import CollapsibleFilterSection from '../common/CollapsibleFilterSection';
import { getPricing, InventoryPricing } from '../../services/inventoryService';
import { configurationService } from '../../services/configurationService';

interface StockProcurementManagementSystemProps {
  configuration: any;
}

const StockProcurementManagementSystem: React.FC<StockProcurementManagementSystemProps> = ({ configuration }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  // Tab state
  const [activeTab, setActiveTab] = useState(0);

  // Unified filter state
  const [itemTypeId, setItemTypeId] = useState<number | null>(null);
  const [sizeTypeId, setSizeTypeId] = useState<number | null>(null);
  const [fromDate, setFromDate] = useState<string>('');
  const [toDate, setToDate] = useState<string>('');
  const [stockStatus, setStockStatus] = useState<string>('all');
  const [pricingStatus, setPricingStatus] = useState<boolean>(true);

  // Dialog control state
  const [procurementDialogOpen, setProcurementDialogOpen] = useState(false);
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

  // Load pricing data when Pricing tab is active
  useEffect(() => {
    const loadPricingData = async () => {
      if (activeTab !== 1) return;

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
    };

    loadPricingData();
  }, [activeTab, currentSessionYearId, pricingStatus, itemTypeId]);

  // Reload pricing after successful save
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

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

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

  // Get action buttons based on active tab
  const getActionButtons = () => {
    const buttons = [];

    if (activeTab === 0) {
      buttons.push(
        <Button
          key="new-procurement"
          variant="contained"
          startIcon={!isMobile && <AddIcon />}
          onClick={() => setProcurementDialogOpen(true)}
          size="small"
          fullWidth={isMobile}
          sx={{ fontSize: { xs: '0.8125rem', sm: '0.875rem' } }}
        >
          New Procurement
        </Button>
      );
    }

    if (activeTab === 1) {
      buttons.push(
        <Button
          key="add-price"
          variant="contained"
          startIcon={!isMobile && <AddIcon />}
          onClick={() => {
            setSelectedPricing(null);
            setPricingDialogOpen(true);
          }}
          size="small"
          fullWidth={isMobile}
          sx={{ fontSize: { xs: '0.8125rem', sm: '0.875rem' } }}
        >
          Add New Price
        </Button>
      );
    }

    return buttons.length > 0 ? (
      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
        {buttons}
      </Box>
    ) : null;
  };

  return (
    <Box sx={{ width: '100%' }}>
      {/* Collapsible Filter Section */}
      <CollapsibleFilterSection
        title="Filters"
        defaultExpanded={true}
        persistKey="stock-procurement"
        actionButtons={getActionButtons()}
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
            label="Size"
            value={sizeTypeId || ''}
            onChange={(e) => setSizeTypeId(e.target.value ? Number(e.target.value) : null)}
            sx={{ minWidth: { xs: '100%', sm: 150 } }}
            size="small"
            fullWidth={isMobile}
          >
            <MenuItem value="">All Sizes</MenuItem>
            {configuration?.inventory_size_types?.map((size: any) => (
              <MenuItem key={size.id} value={size.id}>
                {size.name}
              </MenuItem>
            ))}
          </TextField>

          <TextField
            type="date"
            label="From Date"
            value={fromDate}
            onChange={(e) => setFromDate(e.target.value)}
            slotProps={{ inputLabel: { shrink: true } }}
            size="small"
            fullWidth={isMobile}
          />

          <TextField
            type="date"
            label="To Date"
            value={toDate}
            onChange={(e) => setToDate(e.target.value)}
            slotProps={{ inputLabel: { shrink: true } }}
            size="small"
            fullWidth={isMobile}
          />

          {/* Stock Status filter - only for Stock Levels tab */}
          {activeTab === 2 && (
            <TextField
              select
              label="Stock Status"
              value={stockStatus}
              onChange={(e) => setStockStatus(e.target.value)}
              sx={{ minWidth: { xs: '100%', sm: 150 } }}
              size="small"
              fullWidth={isMobile}
            >
              <MenuItem value="all">All Stock</MenuItem>
              <MenuItem value="low">Low Stock Only</MenuItem>
            </TextField>
          )}

          {/* Pricing Status filter - only for Pricing tab */}
          {activeTab === 1 && (
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
          )}
        </Box>
      </CollapsibleFilterSection>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          variant={isMobile ? 'scrollable' : 'standard'}
          scrollButtons={isMobile ? 'auto' : false}
          allowScrollButtonsMobile
          sx={{
            '& .MuiTab-root': {
              fontSize: { xs: '0.8125rem', sm: '0.875rem' },
              minWidth: { xs: 'auto', sm: 160 },
              px: { xs: 2, sm: 3 }
            }
          }}
        >
          <Tab label="Procurements" />
          <Tab label="Pricing" />
          <Tab label="Stock Levels" />
        </Tabs>
      </Box>

      {/* Tab 0: Stock Procurements */}
      {activeTab === 0 && (
        <StockProcurementsTab
          configuration={configuration}
          onError={(message: string) => setSnackbar({ open: true, message, severity: 'error' })}
          onSuccess={(message: string) => setSnackbar({ open: true, message, severity: 'success' })}
          fromDate={fromDate}
          toDate={toDate}
          dialogOpen={procurementDialogOpen}
          onDialogClose={() => setProcurementDialogOpen(false)}
        />
      )}

      {/* Tab 1: Pricing */}
      {activeTab === 1 && (
        <Box>
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
        </Box>
      )}

      {/* Tab 2: Stock Levels */}
      {activeTab === 2 && (
        <StockLevelsTab
          configuration={configuration}
          onError={(message: string) => setSnackbar({ open: true, message, severity: 'error' })}
          itemTypeId={itemTypeId}
          sizeTypeId={sizeTypeId}
          stockStatus={stockStatus}
        />
      )}

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
    </Box>
  );
};

export default StockProcurementManagementSystem;

