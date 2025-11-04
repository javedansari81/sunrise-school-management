import React, { useState, useEffect } from 'react';
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
  CardContent
} from '@mui/material';
import {
  Visibility as VisibilityIcon,
  Add as AddIcon
} from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';
import CollapsibleFilterSection from '../common/CollapsibleFilterSection';
import NewPurchaseDialog from './inventory/NewPurchaseDialog';
import PurchaseDetailsDialog from './inventory/PurchaseDetailsDialog';
import PricingDialog from './inventory/PricingDialog';
import {
  getPurchases,
  getStatistics,
  getPricing,
  InventoryPurchase,
  InventoryPurchaseListResponse,
  InventoryStatistics,
  InventoryPricing
} from '../../services/inventoryService';
import { DEFAULT_PAGE_SIZE } from '../../config/pagination';

interface InventoryManagementSystemProps {
  configuration: any;
}

const InventoryManagementSystem: React.FC<InventoryManagementSystemProps> = ({ configuration }) => {
  const { user } = useAuth();

  // State
  const [purchases, setPurchases] = useState<InventoryPurchase[]>([]);
  const [totalPurchases, setTotalPurchases] = useState(0);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(DEFAULT_PAGE_SIZE);
  const [activeTab, setActiveTab] = useState(0);

  // Filters
  const [sessionYearId, setSessionYearId] = useState<number>(4); // Default to current session
  const [classId, setClassId] = useState<number | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [fromDate, setFromDate] = useState<string>('');
  const [toDate, setToDate] = useState<string>('');

  // Statistics
  const [statistics, setStatistics] = useState<InventoryStatistics | null>(null);

  // Pricing
  const [pricingList, setPricingList] = useState<InventoryPricing[]>([]);
  const [pricingFilters, setPricingFilters] = useState({
    item_type_id: null as number | null,
    is_active: true,
  });

  // Dialogs
  const [newPurchaseDialogOpen, setNewPurchaseDialogOpen] = useState(false);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [selectedPurchase, setSelectedPurchase] = useState<InventoryPurchase | null>(null);
  const [pricingDialogOpen, setPricingDialogOpen] = useState(false);
  const [selectedPricing, setSelectedPricing] = useState<InventoryPricing | null>(null);

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

  // Load purchases
  useEffect(() => {
    if (activeTab === 0) {
      loadPurchases();
    }
  }, [page, rowsPerPage, sessionYearId, classId, searchQuery, fromDate, toDate, activeTab]);

  // Load statistics
  useEffect(() => {
    if (activeTab === 2) {
      loadStatistics();
    }
  }, [sessionYearId, fromDate, toDate, activeTab]);

  // Load pricing
  useEffect(() => {
    if (activeTab === 3) {
      loadPricing();
    }
  }, [pricingFilters, activeTab]);

  const loadPurchases = async () => {
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
  };

  const loadStatistics = async () => {
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
  };

  const loadPricing = async () => {
    try {
      setLoading(true);
      const params: any = {
        session_year_id: sessionYearId,
        is_active: pricingFilters.is_active,
      };
      if (pricingFilters.item_type_id) {
        params.item_type_id = pricingFilters.item_type_id;
      }
      const data = await getPricing(params);
      setPricingList(data);
    } catch (err) {
      console.error('Error loading pricing:', err);
      showSnackbar('Failed to load pricing', 'error');
    } finally {
      setLoading(false);
    }
  };



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

  const handleEditPricing = (pricing: InventoryPricing) => {
    setSelectedPricing(pricing);
    setPricingDialogOpen(true);
  };

  const handlePricingSuccess = () => {
    showSnackbar('Pricing saved successfully', 'success');
    loadPricing();
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
    <Box sx={{ p: 3 }}>
      {/* Filters */}
      <CollapsibleFilterSection
        title="Filters"
        defaultExpanded
        actionButtons={
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setNewPurchaseDialogOpen(true)}
            size="small"
          >
            New Purchase
          </Button>
        }
      >
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <TextField
            select
            label="Session Year"
            value={sessionYearId}
            onChange={(e) => setSessionYearId(Number(e.target.value))}
            sx={{ minWidth: 200 }}
            size="small"
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
            sx={{ minWidth: 150 }}
            size="small"
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
            sx={{ minWidth: 250 }}
            size="small"
          />

          <TextField
            type="date"
            label="From Date"
            value={fromDate}
            onChange={(e) => setFromDate(e.target.value)}
            InputLabelProps={{ shrink: true }}
            size="small"
          />

          <TextField
            type="date"
            label="To Date"
            value={toDate}
            onChange={(e) => setToDate(e.target.value)}
            InputLabelProps={{ shrink: true }}
            size="small"
          />
        </Box>
      </CollapsibleFilterSection>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs value={activeTab} onChange={handleTabChange}>
          <Tab label="All Purchases" />
          <Tab label="Recent (30 Days)" />
          <Tab label="Statistics" />
          <Tab label="Pricing" />
        </Tabs>
      </Box>

      {/* Content based on active tab */}
      {activeTab === 0 && (
        <Paper>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow sx={{ bgcolor: 'white' }}>
                  <TableCell>Receipt</TableCell>
                  <TableCell>Date</TableCell>
                  <TableCell>Student</TableCell>
                  <TableCell>Class</TableCell>
                  <TableCell>Items</TableCell>
                  <TableCell align="right">Amount</TableCell>
                  <TableCell>Payment</TableCell>
                  <TableCell align="center">Actions</TableCell>
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
                      <Typography color="text.secondary">No purchases found</Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  purchases.map((purchase) => (
                    <TableRow key={purchase.id} hover>
                      <TableCell>
                        <Typography variant="body2" fontWeight={500}>
                          {purchase.receipt_number}
                        </Typography>
                      </TableCell>
                      <TableCell>{formatDate(purchase.purchase_date)}</TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {purchase.student_name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {purchase.student_admission_number}
                        </Typography>
                      </TableCell>
                      <TableCell>{purchase.student_class_name}</TableCell>
                      <TableCell>
                        <Chip
                          label={`${purchase.items.length} item${purchase.items.length > 1 ? 's' : ''}`}
                          size="small"
                          color="primary"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" fontWeight={500}>
                          ₹{Number(purchase.total_amount).toFixed(2)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="caption">
                          {purchase.payment_method_name}
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        <IconButton
                          size="small"
                          onClick={() => handleViewDetails(purchase)}
                          color="primary"
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
          />
        </Paper>
      )}

      {activeTab === 1 && (
        <Paper>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow sx={{ bgcolor: 'white' }}>
                  <TableCell>Receipt</TableCell>
                  <TableCell>Date</TableCell>
                  <TableCell>Student</TableCell>
                  <TableCell>Class</TableCell>
                  <TableCell>Items</TableCell>
                  <TableCell align="right">Amount</TableCell>
                  <TableCell>Payment</TableCell>
                  <TableCell align="center">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {getRecentPurchases().length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} align="center">
                      <Typography color="text.secondary">No recent purchases</Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  getRecentPurchases().map((purchase) => (
                    <TableRow key={purchase.id} hover>
                      <TableCell>
                        <Typography variant="body2" fontWeight={500}>
                          {purchase.receipt_number}
                        </Typography>
                      </TableCell>
                      <TableCell>{formatDate(purchase.purchase_date)}</TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {purchase.student_name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {purchase.student_admission_number}
                        </Typography>
                      </TableCell>
                      <TableCell>{purchase.student_class_name}</TableCell>
                      <TableCell>
                        <Chip
                          label={`${purchase.items.length} item${purchase.items.length > 1 ? 's' : ''}`}
                          size="small"
                          color="primary"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" fontWeight={500}>
                          ₹{Number(purchase.total_amount).toFixed(2)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="caption">
                          {purchase.payment_method_name}
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        <IconButton
                          size="small"
                          onClick={() => handleViewDetails(purchase)}
                          color="primary"
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
            <Grid container spacing={3}>
              {/* Summary Cards */}
              <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                <Card>
                  <CardContent>
                    <Typography color="text.secondary" gutterBottom>
                      Total Purchases
                    </Typography>
                    <Typography variant="h4">
                      {statistics.total_purchases}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                <Card>
                  <CardContent>
                    <Typography color="text.secondary" gutterBottom>
                      Total Revenue
                    </Typography>
                    <Typography variant="h4" color="primary">
                      ₹{(Number(statistics.total_revenue) || 0).toFixed(2)}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                <Card>
                  <CardContent>
                    <Typography color="text.secondary" gutterBottom>
                      Total Students
                    </Typography>
                    <Typography variant="h4">
                      {statistics.total_students || 0}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                <Card>
                  <CardContent>
                    <Typography color="text.secondary" gutterBottom>
                      Avg per Purchase
                    </Typography>
                    <Typography variant="h4">
                      ₹{statistics.total_purchases > 0 ? ((Number(statistics.total_revenue) || 0) / statistics.total_purchases).toFixed(2) : '0.00'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              {/* Top Selling Items */}
              <Grid size={{ xs: 12, md: 6 }}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    Top Selling Items
                  </Typography>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow sx={{ bgcolor: 'white' }}>
                          <TableCell>Item</TableCell>
                          <TableCell align="right">Quantity Sold</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {statistics.top_selling_items.length === 0 ? (
                          <TableRow>
                            <TableCell colSpan={2} align="center">
                              <Typography color="text.secondary">No data available</Typography>
                            </TableCell>
                          </TableRow>
                        ) : (
                          statistics.top_selling_items.map((item, index) => (
                            <TableRow key={index}>
                              <TableCell>{item.item_name}</TableCell>
                              <TableCell align="right">{item.quantity}</TableCell>
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
                <Paper sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    Sales by Item Type
                  </Typography>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow sx={{ bgcolor: 'white' }}>
                          <TableCell>Item</TableCell>
                          <TableCell align="right">Quantity</TableCell>
                          <TableCell align="right">Revenue</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {statistics.items_sold_by_type.length === 0 ? (
                          <TableRow>
                            <TableCell colSpan={3} align="center">
                              <Typography color="text.secondary">No data available</Typography>
                            </TableCell>
                          </TableRow>
                        ) : (
                          statistics.items_sold_by_type.map((item, index) => (
                            <TableRow key={index}>
                              <TableCell>{item.item_name}</TableCell>
                              <TableCell align="right">{item.quantity}</TableCell>
                              <TableCell align="right">₹{item.revenue.toFixed(2)}</TableCell>
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
                <Paper sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    Monthly Purchases
                  </Typography>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow sx={{ bgcolor: 'white' }}>
                          <TableCell>Month</TableCell>
                          <TableCell align="right">Purchase Count</TableCell>
                          <TableCell align="right">Revenue</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {statistics.purchases_by_month.length === 0 ? (
                          <TableRow>
                            <TableCell colSpan={3} align="center">
                              <Typography color="text.secondary">No data available</Typography>
                            </TableCell>
                          </TableRow>
                        ) : (
                          statistics.purchases_by_month.map((month, index) => (
                            <TableRow key={index}>
                              <TableCell>{month.month}</TableCell>
                              <TableCell align="right">{month.count}</TableCell>
                              <TableCell align="right">₹{month.revenue.toFixed(2)}</TableCell>
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
              <Typography color="text.secondary">No statistics available</Typography>
            </Box>
          )}
        </Box>
      )}

      {/* Pricing Tab */}
      {activeTab === 3 && (
        <Box>
          {/* Pricing Filters and Actions */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <TextField
                select
                label="Item Type"
                value={pricingFilters.item_type_id || ''}
                onChange={(e) => setPricingFilters({ ...pricingFilters, item_type_id: e.target.value ? Number(e.target.value) : null })}
                sx={{ minWidth: 200 }}
                size="small"
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
                value={pricingFilters.is_active ? 'active' : 'inactive'}
                onChange={(e) => setPricingFilters({ ...pricingFilters, is_active: e.target.value === 'active' })}
                sx={{ minWidth: 150 }}
                size="small"
              >
                <MenuItem value="active">Active</MenuItem>
                <MenuItem value="inactive">Inactive</MenuItem>
              </TextField>
            </Box>

            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => {
                setSelectedPricing(null);
                setPricingDialogOpen(true);
              }}
            >
              Add New Price
            </Button>
          </Box>

          {/* Pricing Table */}
          <Paper>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow sx={{ bgcolor: 'white' }}>
                    <TableCell>Image</TableCell>
                    <TableCell>Item</TableCell>
                    <TableCell>Size</TableCell>
                    <TableCell>Class</TableCell>
                    <TableCell align="right">Price</TableCell>
                    <TableCell>Effective From</TableCell>
                    <TableCell>Effective To</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell align="center">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {loading ? (
                    <TableRow>
                      <TableCell colSpan={9} align="center">
                        <CircularProgress size={40} />
                      </TableCell>
                    </TableRow>
                  ) : pricingList.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={9} align="center">
                        <Typography color="text.secondary">No pricing records found</Typography>
                      </TableCell>
                    </TableRow>
                  ) : (
                    pricingList.map((pricing) => (
                      <TableRow key={pricing.id} hover>
                        <TableCell>
                          {pricing.item_image_url ? (
                            <Box
                              component="img"
                              src={pricing.item_image_url}
                              alt={pricing.item_type_description}
                              sx={{
                                width: 50,
                                height: 50,
                                objectFit: 'cover',
                                borderRadius: 1,
                              }}
                            />
                          ) : (
                            <Box
                              sx={{
                                width: 50,
                                height: 50,
                                bgcolor: 'grey.200',
                                borderRadius: 1,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                              }}
                            >
                              <Typography variant="caption" color="text.secondary">
                                No Image
                              </Typography>
                            </Box>
                          )}
                        </TableCell>
                        <TableCell>{pricing.item_type_description}</TableCell>
                        <TableCell>{pricing.size_name || 'All'}</TableCell>
                        <TableCell>{pricing.class_name || 'All'}</TableCell>
                        <TableCell align="right">₹{pricing.unit_price}</TableCell>
                        <TableCell>
                          {pricing.effective_from ? new Date(pricing.effective_from).toLocaleDateString() : '-'}
                        </TableCell>
                        <TableCell>
                          {pricing.effective_to ? new Date(pricing.effective_to).toLocaleDateString() : '-'}
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={pricing.is_active ? 'Active' : 'Inactive'}
                            color={pricing.is_active ? 'success' : 'default'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell align="center">
                          <IconButton
                            size="small"
                            onClick={() => handleEditPricing(pricing)}
                            title="Edit"
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
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default InventoryManagementSystem;

