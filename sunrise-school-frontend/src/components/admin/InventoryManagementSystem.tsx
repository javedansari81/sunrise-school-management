import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Typography,
  Chip,
  IconButton,
  Snackbar,
  Alert,
  CircularProgress,
  TextField,
  MenuItem,
  Tabs,
  Tab,
  Grid,
  Card,
  CardContent,
  useMediaQuery,
  useTheme,
  Fab,
} from '@mui/material';
import {
  Visibility as VisibilityIcon,
  Add as AddIcon
} from '@mui/icons-material';
import CollapsibleFilterSection from '../common/CollapsibleFilterSection';
import NewPurchaseDialog from './inventory/NewPurchaseDialog';
import PurchaseDetailsDialog from './inventory/PurchaseDetailsDialog';
import {
  getPurchases,
  getStatistics,
  InventoryPurchase,
  InventoryPurchaseListResponse,
  InventoryStatistics
} from '../../services/inventoryService';
import { configurationService } from '../../services/configurationService';
import { DEFAULT_PAGE_SIZE } from '../../config/pagination';

interface InventoryManagementSystemProps {
  configuration: any;
}

const InventoryManagementSystem: React.FC<InventoryManagementSystemProps> = ({ configuration }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  // State
  const [purchases, setPurchases] = useState<InventoryPurchase[]>([]);
  const [totalPurchases, setTotalPurchases] = useState(0);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(DEFAULT_PAGE_SIZE);
  const [activeTab, setActiveTab] = useState(0);

  // Filters - use centralized session year service
  const [sessionYearId, setSessionYearId] = useState<number>(configurationService.getCurrentSessionYearId());
  const [classId, setClassId] = useState<number | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [fromDate, setFromDate] = useState<string>('');
  const [toDate, setToDate] = useState<string>('');

  // Statistics
  const [statistics, setStatistics] = useState<InventoryStatistics | null>(null);

  // Dialogs
  const [newPurchaseDialogOpen, setNewPurchaseDialogOpen] = useState(false);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [selectedPurchase, setSelectedPurchase] = useState<InventoryPurchase | null>(null);

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

  const loadPurchases = useCallback(async () => {
    setLoading(true);
    try {
      const response: InventoryPurchaseListResponse = await getPurchases({
        session_year_id: sessionYearId,
        class_id: classId || undefined,
        search: searchQuery || undefined,
        from_date: fromDate || undefined,
        to_date: toDate || undefined,
        page: page + 1,
        per_page: rowsPerPage
      });
      setPurchases(response.purchases);
      setTotalPurchases(response.total);
    } catch (err) {
      console.error('Error loading purchases:', err);
      showSnackbar('Failed to load purchases', 'error');
    } finally {
      setLoading(false);
    }
  }, [sessionYearId, classId, searchQuery, fromDate, toDate, page, rowsPerPage]);

  const loadStatistics = useCallback(async () => {
    setLoading(true);
    try {
      const stats = await getStatistics({
        session_year_id: sessionYearId,
        from_date: fromDate || undefined,
        to_date: toDate || undefined
      });
      setStatistics(stats);
    } catch (err) {
      console.error('Error loading statistics:', err);
      showSnackbar('Failed to load statistics', 'error');
    } finally {
      setLoading(false);
    }
  }, [sessionYearId, fromDate, toDate]);

  // Load purchases
  useEffect(() => {
    if (activeTab === 0) {
      loadPurchases();
    }
  }, [activeTab, loadPurchases]);

  // Load statistics
  useEffect(() => {
    if (activeTab === 2) {
      loadStatistics();
    }
  }, [activeTab, loadStatistics]);

  const handleViewDetails = (purchase: InventoryPurchase) => {
    setSelectedPurchase(purchase);
    setDetailsDialogOpen(true);
  };

  const handleNewPurchaseSuccess = () => {
    showSnackbar('Purchase created successfully', 'success');
    loadPurchases();
  };

  const handleNewPurchaseError = (message: string) => {
    showSnackbar(message, 'error');
  };

  const showSnackbar = (message: string, severity: 'success' | 'error' | 'info' | 'warning') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const handleChangePage = (_: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
    setPage(0);
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  const getRecentPurchases = (): InventoryPurchase[] => {
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    return purchases.filter(p => new Date(p.purchase_date) >= thirtyDaysAgo);
  };



  return (
    <>
      {/* Filters */}
      <CollapsibleFilterSection
        title="Filters"
        defaultExpanded
      >
        <Box sx={{
          display: 'flex',
          gap: { xs: 1.5, sm: 2 },
          flexWrap: 'wrap',
          flexDirection: { xs: 'column', sm: 'row' }
        }}>
          <TextField
            select
            label="Session Year"
            value={sessionYearId}
            onChange={(e) => setSessionYearId(Number(e.target.value))}
            sx={{ minWidth: { xs: '100%', sm: 200 } }}
            size="small"
            fullWidth={isMobile}
          >
            {configuration?.session_years?.map((year: any) => (
              <MenuItem key={year.id} value={year.id}>
                {year.description}
              </MenuItem>
            ))}
          </TextField>

          <TextField
            select
            label="Class"
            value={classId || ''}
            onChange={(e) => setClassId(e.target.value ? Number(e.target.value) : null)}
            sx={{ minWidth: { xs: '100%', sm: 150 } }}
            size="small"
            fullWidth={isMobile}
          >
            <MenuItem value="">All Classes</MenuItem>
            {configuration?.classes?.map((cls: any) => (
              <MenuItem key={cls.id} value={cls.id}>
                {cls.description}
              </MenuItem>
            ))}
          </TextField>

          <TextField
            label="Search Student"
            placeholder="Name or admission number"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            sx={{ minWidth: { xs: '100%', sm: 250 } }}
            size="small"
            fullWidth={isMobile}
          />

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
          <Tab label="All Purchases" />
          <Tab label="Recent (30 Days)" />
          <Tab label="Statistics" />
        </Tabs>
      </Box>

      {/* Content based on active tab */}
      {activeTab === 0 && (
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
                    minWidth: { xs: 100, sm: 120 }
                  }}>
                    Receipt
                  </TableCell>
                  <TableCell sx={{
                    fontSize: { xs: '0.75rem', sm: '0.875rem' },
                    py: { xs: 1, sm: 1.5 },
                    minWidth: { xs: 90, sm: 100 }
                  }}>
                    Date
                  </TableCell>
                  <TableCell sx={{
                    fontSize: { xs: '0.75rem', sm: '0.875rem' },
                    py: { xs: 1, sm: 1.5 },
                    minWidth: { xs: 120, sm: 150 }
                  }}>
                    Student
                  </TableCell>
                  <TableCell sx={{
                    fontSize: { xs: '0.75rem', sm: '0.875rem' },
                    py: { xs: 1, sm: 1.5 },
                    minWidth: { xs: 80, sm: 100 }
                  }}>
                    Class
                  </TableCell>
                  <TableCell sx={{
                    fontSize: { xs: '0.75rem', sm: '0.875rem' },
                    py: { xs: 1, sm: 1.5 },
                    minWidth: { xs: 70, sm: 80 }
                  }}>
                    Items
                  </TableCell>
                  <TableCell
                    align="right"
                    sx={{
                      fontSize: { xs: '0.75rem', sm: '0.875rem' },
                      py: { xs: 1, sm: 1.5 },
                      minWidth: { xs: 90, sm: 100 }
                    }}
                  >
                    Amount
                  </TableCell>
                  <TableCell sx={{
                    fontSize: { xs: '0.75rem', sm: '0.875rem' },
                    py: { xs: 1, sm: 1.5 },
                    minWidth: { xs: 80, sm: 100 }
                  }}>
                    Payment
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
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={8} align="center">
                      <CircularProgress size={40} />
                    </TableCell>
                  </TableRow>
                ) : purchases.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} align="center">
                      <Typography
                        color="text.secondary"
                        sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }}
                      >
                        No purchases found
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  purchases.map((purchase) => (
                    <TableRow key={purchase.id} hover>
                      <TableCell sx={{ py: { xs: 0.75, sm: 1.5 } }}>
                        <Typography
                          variant="body2"
                          fontWeight={500}
                          sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}
                        >
                          {purchase.receipt_number}
                        </Typography>
                      </TableCell>
                      <TableCell sx={{
                        py: { xs: 0.75, sm: 1.5 },
                        fontSize: { xs: '0.75rem', sm: '0.875rem' }
                      }}>
                        {formatDate(purchase.purchase_date)}
                      </TableCell>
                      <TableCell sx={{ py: { xs: 0.75, sm: 1.5 } }}>
                        <Typography
                          variant="body2"
                          sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}
                        >
                          {purchase.student_name}
                        </Typography>
                        <Typography
                          variant="caption"
                          color="text.secondary"
                          sx={{ fontSize: { xs: '0.65rem', sm: '0.75rem' } }}
                        >
                          {purchase.student_admission_number}
                        </Typography>
                      </TableCell>
                      <TableCell sx={{
                        py: { xs: 0.75, sm: 1.5 },
                        fontSize: { xs: '0.75rem', sm: '0.875rem' }
                      }}>
                        {purchase.student_class_name}
                      </TableCell>
                      <TableCell sx={{ py: { xs: 0.75, sm: 1.5 } }}>
                        <Chip
                          label={`${purchase.items.length} item${purchase.items.length > 1 ? 's' : ''}`}
                          size="small"
                          color="primary"
                          variant="outlined"
                          sx={{
                            fontSize: { xs: '0.65rem', sm: '0.75rem' },
                            height: { xs: 20, sm: 24 }
                          }}
                        />
                      </TableCell>
                      <TableCell
                        align="right"
                        sx={{ py: { xs: 0.75, sm: 1.5 } }}
                      >
                        <Typography
                          variant="body2"
                          fontWeight={500}
                          sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}
                        >
                          ₹{Number(purchase.total_amount).toFixed(2)}
                        </Typography>
                      </TableCell>
                      <TableCell sx={{ py: { xs: 0.75, sm: 1.5 } }}>
                        <Typography
                          variant="caption"
                          sx={{ fontSize: { xs: '0.65rem', sm: '0.75rem' } }}
                        >
                          {purchase.payment_method_name}
                        </Typography>
                      </TableCell>
                      <TableCell
                        align="center"
                        sx={{ py: { xs: 0.75, sm: 1.5 } }}
                      >
                        <IconButton
                          size="small"
                          onClick={() => handleViewDetails(purchase)}
                          color="primary"
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
          <TablePagination
            component="div"
            count={totalPurchases}
            page={page}
            onPageChange={handleChangePage}
            rowsPerPage={rowsPerPage}
            onRowsPerPageChange={handleChangeRowsPerPage}
            rowsPerPageOptions={[10, 25, 50, 100]}
            sx={{
              '& .MuiTablePagination-toolbar': {
                fontSize: { xs: '0.75rem', sm: '0.875rem' },
                minHeight: { xs: 48, sm: 52 }
              },
              '& .MuiTablePagination-selectLabel, & .MuiTablePagination-displayedRows': {
                fontSize: { xs: '0.75rem', sm: '0.875rem' }
              }
            }}
          />
        </Paper>
      )}

      {activeTab === 1 && (
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
                    minWidth: { xs: 100, sm: 120 }
                  }}>
                    Receipt
                  </TableCell>
                  <TableCell sx={{
                    fontSize: { xs: '0.75rem', sm: '0.875rem' },
                    py: { xs: 1, sm: 1.5 },
                    minWidth: { xs: 90, sm: 100 }
                  }}>
                    Date
                  </TableCell>
                  <TableCell sx={{
                    fontSize: { xs: '0.75rem', sm: '0.875rem' },
                    py: { xs: 1, sm: 1.5 },
                    minWidth: { xs: 120, sm: 150 }
                  }}>
                    Student
                  </TableCell>
                  <TableCell sx={{
                    fontSize: { xs: '0.75rem', sm: '0.875rem' },
                    py: { xs: 1, sm: 1.5 },
                    minWidth: { xs: 80, sm: 100 }
                  }}>
                    Class
                  </TableCell>
                  <TableCell sx={{
                    fontSize: { xs: '0.75rem', sm: '0.875rem' },
                    py: { xs: 1, sm: 1.5 },
                    minWidth: { xs: 70, sm: 80 }
                  }}>
                    Items
                  </TableCell>
                  <TableCell
                    align="right"
                    sx={{
                      fontSize: { xs: '0.75rem', sm: '0.875rem' },
                      py: { xs: 1, sm: 1.5 },
                      minWidth: { xs: 90, sm: 100 }
                    }}
                  >
                    Amount
                  </TableCell>
                  <TableCell sx={{
                    fontSize: { xs: '0.75rem', sm: '0.875rem' },
                    py: { xs: 1, sm: 1.5 },
                    minWidth: { xs: 80, sm: 100 }
                  }}>
                    Payment
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
                {getRecentPurchases().length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} align="center">
                      <Typography
                        color="text.secondary"
                        sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }}
                      >
                        No recent purchases
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  getRecentPurchases().map((purchase) => (
                    <TableRow key={purchase.id} hover>
                      <TableCell sx={{ py: { xs: 0.75, sm: 1.5 } }}>
                        <Typography
                          variant="body2"
                          fontWeight={500}
                          sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}
                        >
                          {purchase.receipt_number}
                        </Typography>
                      </TableCell>
                      <TableCell sx={{
                        py: { xs: 0.75, sm: 1.5 },
                        fontSize: { xs: '0.75rem', sm: '0.875rem' }
                      }}>
                        {formatDate(purchase.purchase_date)}
                      </TableCell>
                      <TableCell sx={{ py: { xs: 0.75, sm: 1.5 } }}>
                        <Typography
                          variant="body2"
                          sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}
                        >
                          {purchase.student_name}
                        </Typography>
                        <Typography
                          variant="caption"
                          color="text.secondary"
                          sx={{ fontSize: { xs: '0.65rem', sm: '0.75rem' } }}
                        >
                          {purchase.student_admission_number}
                        </Typography>
                      </TableCell>
                      <TableCell sx={{
                        py: { xs: 0.75, sm: 1.5 },
                        fontSize: { xs: '0.75rem', sm: '0.875rem' }
                      }}>
                        {purchase.student_class_name}
                      </TableCell>
                      <TableCell sx={{ py: { xs: 0.75, sm: 1.5 } }}>
                        <Chip
                          label={`${purchase.items.length} item${purchase.items.length > 1 ? 's' : ''}`}
                          size="small"
                          color="primary"
                          variant="outlined"
                          sx={{
                            fontSize: { xs: '0.65rem', sm: '0.75rem' },
                            height: { xs: 20, sm: 24 }
                          }}
                        />
                      </TableCell>
                      <TableCell
                        align="right"
                        sx={{ py: { xs: 0.75, sm: 1.5 } }}
                      >
                        <Typography
                          variant="body2"
                          fontWeight={500}
                          sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}
                        >
                          ₹{Number(purchase.total_amount).toFixed(2)}
                        </Typography>
                      </TableCell>
                      <TableCell sx={{ py: { xs: 0.75, sm: 1.5 } }}>
                        <Typography
                          variant="caption"
                          sx={{ fontSize: { xs: '0.65rem', sm: '0.75rem' } }}
                        >
                          {purchase.payment_method_name}
                        </Typography>
                      </TableCell>
                      <TableCell
                        align="center"
                        sx={{ py: { xs: 0.75, sm: 1.5 } }}
                      >
                        <IconButton
                          size="small"
                          onClick={() => handleViewDetails(purchase)}
                          color="primary"
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
      )}

      {activeTab === 2 && (
        <Box>
          {loading ? (
            <Box display="flex" justifyContent="center" p={5}>
              <CircularProgress />
            </Box>
          ) : statistics ? (
            <Grid container spacing={{ xs: 2, sm: 3 }}>
              {/* Summary Cards */}
              <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                <Card>
                  <CardContent sx={{ py: { xs: 2, sm: 2 } }}>
                    <Typography
                      color="text.secondary"
                      gutterBottom
                      sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }}
                    >
                      Total Purchases
                    </Typography>
                    <Typography
                      variant="h4"
                      sx={{ fontSize: { xs: '1.75rem', sm: '2.125rem' } }}
                    >
                      {statistics.total_purchases}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                <Card>
                  <CardContent sx={{ py: { xs: 2, sm: 2 } }}>
                    <Typography
                      color="text.secondary"
                      gutterBottom
                      sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }}
                    >
                      Total Revenue
                    </Typography>
                    <Typography
                      variant="h4"
                      color="primary"
                      sx={{ fontSize: { xs: '1.75rem', sm: '2.125rem' } }}
                    >
                      ₹{(Number(statistics.total_revenue) || 0).toFixed(2)}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                <Card>
                  <CardContent sx={{ py: { xs: 2, sm: 2 } }}>
                    <Typography
                      color="text.secondary"
                      gutterBottom
                      sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }}
                    >
                      Total Students
                    </Typography>
                    <Typography
                      variant="h4"
                      sx={{ fontSize: { xs: '1.75rem', sm: '2.125rem' } }}
                    >
                      {statistics.total_students || 0}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                <Card>
                  <CardContent sx={{ py: { xs: 2, sm: 2 } }}>
                    <Typography
                      color="text.secondary"
                      gutterBottom
                      sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }}
                    >
                      Avg per Purchase
                    </Typography>
                    <Typography
                      variant="h4"
                      sx={{ fontSize: { xs: '1.75rem', sm: '2.125rem' } }}
                    >
                      ₹{statistics.total_purchases > 0 ? ((Number(statistics.total_revenue) || 0) / statistics.total_purchases).toFixed(2) : '0.00'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              {/* Top Selling Items */}
              <Grid size={{ xs: 12, md: 6 }}>
                <Paper sx={{ p: { xs: 1.5, sm: 2 } }}>
                  <Typography
                    variant="h6"
                    gutterBottom
                    sx={{ fontSize: { xs: '1rem', sm: '1.25rem' } }}
                  >
                    Top Selling Items
                  </Typography>
                  <TableContainer sx={{
                    maxHeight: { xs: '300px', sm: '400px' },
                    overflowX: 'auto'
                  }}>
                    <Table size="small">
                      <TableHead>
                        <TableRow sx={{ bgcolor: 'white' }}>
                          <TableCell sx={{
                            fontSize: { xs: '0.75rem', sm: '0.875rem' },
                            py: { xs: 1, sm: 1.5 }
                          }}>
                            Item
                          </TableCell>
                          <TableCell
                            align="right"
                            sx={{
                              fontSize: { xs: '0.75rem', sm: '0.875rem' },
                              py: { xs: 1, sm: 1.5 }
                            }}
                          >
                            Quantity Sold
                          </TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {statistics.top_selling_items.length === 0 ? (
                          <TableRow>
                            <TableCell colSpan={2} align="center">
                              <Typography
                                color="text.secondary"
                                sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }}
                              >
                                No data available
                              </Typography>
                            </TableCell>
                          </TableRow>
                        ) : (
                          statistics.top_selling_items.map((item, index) => (
                            <TableRow key={index}>
                              <TableCell sx={{
                                fontSize: { xs: '0.75rem', sm: '0.875rem' },
                                py: { xs: 0.75, sm: 1 }
                              }}>
                                {item.item_name}
                              </TableCell>
                              <TableCell
                                align="right"
                                sx={{
                                  fontSize: { xs: '0.75rem', sm: '0.875rem' },
                                  py: { xs: 0.75, sm: 1 }
                                }}
                              >
                                {item.quantity}
                              </TableCell>
                            </TableRow>
                          ))
                        )}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Paper>
              </Grid>

              {/* Items Sold by Type */}
              <Grid size={{ xs: 12, md: 6 }}>
                <Paper sx={{ p: { xs: 1.5, sm: 2 } }}>
                  <Typography
                    variant="h6"
                    gutterBottom
                    sx={{ fontSize: { xs: '1rem', sm: '1.25rem' } }}
                  >
                    Sales by Item Type
                  </Typography>
                  <TableContainer sx={{
                    maxHeight: { xs: '300px', sm: '400px' },
                    overflowX: 'auto'
                  }}>
                    <Table size="small">
                      <TableHead>
                        <TableRow sx={{ bgcolor: 'white' }}>
                          <TableCell sx={{
                            fontSize: { xs: '0.75rem', sm: '0.875rem' },
                            py: { xs: 1, sm: 1.5 }
                          }}>
                            Item
                          </TableCell>
                          <TableCell
                            align="right"
                            sx={{
                              fontSize: { xs: '0.75rem', sm: '0.875rem' },
                              py: { xs: 1, sm: 1.5 }
                            }}
                          >
                            Quantity
                          </TableCell>
                          <TableCell
                            align="right"
                            sx={{
                              fontSize: { xs: '0.75rem', sm: '0.875rem' },
                              py: { xs: 1, sm: 1.5 }
                            }}
                          >
                            Revenue
                          </TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {statistics.items_sold_by_type.length === 0 ? (
                          <TableRow>
                            <TableCell colSpan={3} align="center">
                              <Typography
                                color="text.secondary"
                                sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }}
                              >
                                No data available
                              </Typography>
                            </TableCell>
                          </TableRow>
                        ) : (
                          statistics.items_sold_by_type.map((item, index) => (
                            <TableRow key={index}>
                              <TableCell sx={{
                                fontSize: { xs: '0.75rem', sm: '0.875rem' },
                                py: { xs: 0.75, sm: 1 }
                              }}>
                                {item.item_name}
                              </TableCell>
                              <TableCell
                                align="right"
                                sx={{
                                  fontSize: { xs: '0.75rem', sm: '0.875rem' },
                                  py: { xs: 0.75, sm: 1 }
                                }}
                              >
                                {item.quantity}
                              </TableCell>
                              <TableCell
                                align="right"
                                sx={{
                                  fontSize: { xs: '0.75rem', sm: '0.875rem' },
                                  py: { xs: 0.75, sm: 1 }
                                }}
                              >
                                ₹{item.revenue.toFixed(2)}
                              </TableCell>
                            </TableRow>
                          ))
                        )}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Paper>
              </Grid>

              {/* Purchases by Month */}
              <Grid size={{ xs: 12 }}>
                <Paper sx={{ p: { xs: 1.5, sm: 2 } }}>
                  <Typography
                    variant="h6"
                    gutterBottom
                    sx={{ fontSize: { xs: '1rem', sm: '1.25rem' } }}
                  >
                    Monthly Purchases
                  </Typography>
                  <TableContainer sx={{
                    maxHeight: { xs: '300px', sm: '400px' },
                    overflowX: 'auto'
                  }}>
                    <Table size="small">
                      <TableHead>
                        <TableRow sx={{ bgcolor: 'white' }}>
                          <TableCell sx={{
                            fontSize: { xs: '0.75rem', sm: '0.875rem' },
                            py: { xs: 1, sm: 1.5 }
                          }}>
                            Month
                          </TableCell>
                          <TableCell
                            align="right"
                            sx={{
                              fontSize: { xs: '0.75rem', sm: '0.875rem' },
                              py: { xs: 1, sm: 1.5 }
                            }}
                          >
                            Purchase Count
                          </TableCell>
                          <TableCell
                            align="right"
                            sx={{
                              fontSize: { xs: '0.75rem', sm: '0.875rem' },
                              py: { xs: 1, sm: 1.5 }
                            }}
                          >
                            Revenue
                          </TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {statistics.purchases_by_month.length === 0 ? (
                          <TableRow>
                            <TableCell colSpan={3} align="center">
                              <Typography
                                color="text.secondary"
                                sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }}
                              >
                                No data available
                              </Typography>
                            </TableCell>
                          </TableRow>
                        ) : (
                          statistics.purchases_by_month.map((month, index) => (
                            <TableRow key={index}>
                              <TableCell sx={{
                                fontSize: { xs: '0.75rem', sm: '0.875rem' },
                                py: { xs: 0.75, sm: 1 }
                              }}>
                                {month.month}
                              </TableCell>
                              <TableCell
                                align="right"
                                sx={{
                                  fontSize: { xs: '0.75rem', sm: '0.875rem' },
                                  py: { xs: 0.75, sm: 1 }
                                }}
                              >
                                {month.count}
                              </TableCell>
                              <TableCell
                                align="right"
                                sx={{
                                  fontSize: { xs: '0.75rem', sm: '0.875rem' },
                                  py: { xs: 0.75, sm: 1 }
                                }}
                              >
                                ₹{month.revenue.toFixed(2)}
                              </TableCell>
                            </TableRow>
                          ))
                        )}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Paper>
              </Grid>
            </Grid>
          ) : (
            <Box display="flex" justifyContent="center" p={5}>
              <Typography
                color="text.secondary"
                sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }}
              >
                No statistics available
              </Typography>
            </Box>
          )}
        </Box>
      )}

      {/* Dialogs */}
      <NewPurchaseDialog
        open={newPurchaseDialogOpen}
        onClose={() => setNewPurchaseDialogOpen(false)}
        configuration={configuration}
        onSuccess={handleNewPurchaseSuccess}
        onError={handleNewPurchaseError}
      />

      <PurchaseDetailsDialog
        open={detailsDialogOpen}
        onClose={() => setDetailsDialogOpen(false)}
        purchase={selectedPurchase}
      />

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>

      {/* Floating Action Button for New Purchase with Animated Expansion */}
      <Fab
        color="primary"
        aria-label="add purchase"
        variant="extended"
        onClick={() => setNewPurchaseDialogOpen(true)}
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
              minWidth: '160px',
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
          New Purchase
        </Box>
      </Fab>
    </>
  );
};

export default InventoryManagementSystem;

