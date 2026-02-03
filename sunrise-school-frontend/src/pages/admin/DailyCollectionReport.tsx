import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
  Snackbar,
  Pagination,
  TextField,
  Chip,
  Fab,
  Card,
  CardContent,
  Grid,
} from '@mui/material';
import { DEFAULT_PAGE_SIZE, PAGINATION_UI_CONFIG } from '../../config/pagination';
import {
  ClassDropdown,
} from '../../components/common/MetadataDropdown';
import ServiceConfigurationLoader from '../../components/common/ServiceConfigurationLoader';
import {
  FilterList,
  Search,
  TableChart,
  ExpandMore,
  ExpandLess,
} from '@mui/icons-material';
import AdminLayout from '../../components/Layout/AdminLayout';
import { reportsAPI } from '../../services/api';
import { useServiceConfiguration } from '../../contexts/ConfigurationContext';
import * as XLSX from 'xlsx';

interface DailyCollectionData {
  payment_id: number;
  receipt_number: string | null;
  payment_date: string;
  amount: string;
  payment_method: string;
  transaction_id: string | null;
  student_id: number;
  admission_number: string;
  student_name: string;
  class_name: string;
  section: string | null;
  fee_record_id: number;
  session_year_name: string;
  payment_type: string;
  remarks: string | null;
  created_by_name: string | null;
  created_at: string;
}

interface ReportSummary {
  total_collections: number;
  total_amount: string;
  cash_amount: string;
  online_amount: string;
  upi_amount: string;
  cheque_amount: string;
  card_amount: string;
  fee_collections: string;
  transport_collections: string;
}

const DailyCollectionReport: React.FC = () => {
  const { isLoaded } = useServiceConfiguration('fee-management');

  // State management
  const [collectionData, setCollectionData] = useState<DailyCollectionData[]>([]);
  const [summary, setSummary] = useState<ReportSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });
  const [filtersExpanded, setFiltersExpanded] = useState(true);

  // Get today's date in YYYY-MM-DD format
  const getTodayDate = () => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  };

  // Filters - Initialize with today's date
  const [filterFromDate, setFilterFromDate] = useState<string>(getTodayDate());
  const [filterToDate, setFilterToDate] = useState<string>(getTodayDate());
  const [filterClass, setFilterClass] = useState<string>('all');
  const [filterSection, setFilterSection] = useState<string>('all');
  const [filterPaymentMethod, setFilterPaymentMethod] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');

  // Pagination
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalRecords, setTotalRecords] = useState(0);
  const perPage = DEFAULT_PAGE_SIZE;

  // Available sections (dynamically populated)
  const [availableSections, setAvailableSections] = useState<string[]>([]);

  // Load collection data from API
  const loadCollectionData = async () => {
    if (!filterFromDate || !filterToDate) {
      setSnackbar({
        open: true,
        message: 'Please select both From Date and To Date',
        severity: 'error'
      });
      return;
    }

    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.append('from_date', filterFromDate);
      params.append('to_date', filterToDate);
      params.append('page', page.toString());
      params.append('per_page', perPage.toString());

      // Add filters
      if (filterClass !== 'all') params.append('class_id', filterClass);
      if (filterSection !== 'all') params.append('section', filterSection);
      if (filterPaymentMethod !== 'all') params.append('payment_method_id', filterPaymentMethod);
      if (searchTerm) params.append('search', searchTerm);

      const response = await reportsAPI.getDailyCollectionReport(params);
      setCollectionData(response.records || []);
      setSummary(response.summary || null);
      setTotalPages(response.total_pages);
      setTotalRecords(response.total);

      // Extract unique sections from data
      const sections = Array.from(new Set((response.records || []).map((d: DailyCollectionData) => d.section).filter(Boolean)));
      setAvailableSections(sections as string[]);

    } catch (error: any) {
      console.error('Error loading daily collection data:', error);
      setSnackbar({
        open: true,
        message: error.response?.data?.detail || 'Failed to load daily collection data',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (filterFromDate && filterToDate) {
      loadCollectionData();
    }
  }, [page, filterFromDate, filterToDate, filterClass, filterSection, filterPaymentMethod, searchTerm]);

  // Reset to page 1 when filters change
  useEffect(() => {
    setPage(1);
  }, [filterFromDate, filterToDate, filterClass, filterSection, filterPaymentMethod, searchTerm]);

  // Export to Excel
  const handleExportExcel = () => {
    if (!collectionData || collectionData.length === 0) {
      setSnackbar({
        open: true,
        message: 'No data to export',
        severity: 'error'
      });
      return;
    }

    try {
      const exportData = collectionData.map(record => ({
        'Receipt No': record.receipt_number || 'N/A',
        'Payment Date': record.payment_date,
        'Admission Number': record.admission_number,
        'Student Name': record.student_name,
        'Class': record.class_name,
        'Section': record.section || 'N/A',
        'Session Year': record.session_year_name || 'N/A',
        'Payment Type': record.payment_type,
        'Amount': `₹${record.amount}`,
        'Payment Method': record.payment_method,
        'Transaction ID': record.transaction_id || 'N/A',
        'Remarks': record.remarks || '',
        'Collected By': record.created_by_name || 'N/A',
      }));

      const worksheet = XLSX.utils.json_to_sheet(exportData);
      const workbook = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(workbook, worksheet, 'Daily Collection Report');

      // Auto-size columns
      const maxWidth = 50;
      const colWidths = Object.keys(exportData[0] || {}).map(key => ({
        wch: Math.min(Math.max(key.length, 10), maxWidth)
      }));
      worksheet['!cols'] = colWidths;

      const fileName = filterFromDate === filterToDate
        ? `Daily_Collection_Report_${filterFromDate}.xlsx`
        : `Collection_Report_${filterFromDate}_to_${filterToDate}.xlsx`;

      XLSX.writeFile(workbook, fileName);

      setSnackbar({
        open: true,
        message: 'Report exported successfully!',
        severity: 'success'
      });
    } catch (error) {
      console.error('Error exporting to Excel:', error);
      setSnackbar({
        open: true,
        message: 'Failed to export report',
        severity: 'error'
      });
    }
  };

  const getPaymentTypeColor = (type: string) => {
    return type === 'Fee' ? 'primary' : 'secondary';
  };

  const getPaymentMethodColor = (method: string) => {
    switch (method.toLowerCase()) {
      case 'cash':
        return 'success';
      case 'upi':
        return 'info';
      case 'online':
        return 'primary';
      case 'cheque':
        return 'warning';
      case 'card':
        return 'secondary';
      default:
        return 'default';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
  };

  return (
    <AdminLayout>
      <ServiceConfigurationLoader service="fee-management">
        {/* Summary Cards */}
        {summary && (
          <Grid container spacing={2} mb={2}>
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Card sx={{ bgcolor: 'primary.main', color: 'white', height: '100%' }}>
                <CardContent sx={{ py: 1.5, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                  <Typography variant="body2">Total Collection</Typography>
                  <Typography variant="h5" fontWeight="bold">₹{summary.total_amount}</Typography>
                  <Typography variant="caption">{summary.total_collections} transactions</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Card sx={{ bgcolor: 'success.main', color: 'white', height: '100%' }}>
                <CardContent sx={{ py: 1.5, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                  <Typography variant="body2">Fee Collection</Typography>
                  <Typography variant="h5" fontWeight="bold">₹{summary.fee_collections}</Typography>
                  <Typography variant="caption">&nbsp;</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Card sx={{ bgcolor: 'secondary.main', color: 'white', height: '100%' }}>
                <CardContent sx={{ py: 1.5, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                  <Typography variant="body2">Transport Collection</Typography>
                  <Typography variant="h5" fontWeight="bold">₹{summary.transport_collections}</Typography>
                  <Typography variant="caption">&nbsp;</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Card sx={{ bgcolor: 'info.main', color: 'white', height: '100%' }}>
                <CardContent sx={{ py: 1.5, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                  <Typography variant="body2">Cash: ₹{summary.cash_amount}</Typography>
                  <Typography variant="body2">UPI: ₹{summary.upi_amount}</Typography>
                  <Typography variant="body2">Online: ₹{summary.online_amount}</Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        {/* Filters - Compact & Collapsible */}
        <Paper elevation={2} sx={{ mb: 2 }}>
          <Box
            display="flex"
            justifyContent="space-between"
            alignItems="center"
            sx={{
              p: { xs: 1.5, sm: 2 },
              cursor: 'pointer',
              '&:hover': { bgcolor: 'rgba(0, 0, 0, 0.02)' }
            }}
            onClick={() => setFiltersExpanded(!filtersExpanded)}
          >
            <Box display="flex" alignItems="center" gap={1}>
              <FilterList sx={{ fontSize: 20 }} />
              <Typography variant="subtitle1" fontWeight={600}>
                Filters
              </Typography>
              {!filtersExpanded && filterFromDate && filterToDate && (
                <Chip
                  label={`${filterFromDate} to ${filterToDate}`}
                  size="small"
                  color="primary"
                  sx={{ ml: 1 }}
                />
              )}
            </Box>
            {filtersExpanded ? <ExpandLess /> : <ExpandMore />}
          </Box>

          {filtersExpanded && (
            <Box sx={{ px: { xs: 1.5, sm: 2 }, pb: 2 }}>
              <Box
                display="grid"
                gridTemplateColumns={{
                  xs: '1fr',
                  sm: 'repeat(2, 1fr)',
                  md: 'repeat(3, 1fr)',
                  lg: 'repeat(6, 1fr)'
                }}
                gap={1.5}
              >
                <TextField
                  size="small"
                  label="From Date *"
                  type="date"
                  value={filterFromDate}
                  onChange={(e) => setFilterFromDate(e.target.value)}
                  slotProps={{
                    inputLabel: { shrink: true }
                  }}
                  fullWidth
                  required
                />
                <TextField
                  size="small"
                  label="To Date *"
                  type="date"
                  value={filterToDate}
                  onChange={(e) => setFilterToDate(e.target.value)}
                  slotProps={{
                    inputLabel: { shrink: true }
                  }}
                  fullWidth
                  required
                />
                <ClassDropdown
                  value={filterClass}
                  onChange={(value) => setFilterClass(value as string)}
                  label="Class"
                  size="small"
                  includeAll
                />
                <FormControl size="small" fullWidth>
                  <InputLabel>Section</InputLabel>
                  <Select
                    value={filterSection}
                    label="Section"
                    onChange={(e) => setFilterSection(e.target.value)}
                  >
                    <MenuItem value="all">All Sections</MenuItem>
                    {availableSections.map((section) => (
                      <MenuItem key={section} value={section}>
                        Section {section}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
                <FormControl size="small" fullWidth>
                  <InputLabel>Payment Method</InputLabel>
                  <Select
                    value={filterPaymentMethod}
                    label="Payment Method"
                    onChange={(e) => setFilterPaymentMethod(e.target.value)}
                  >
                    <MenuItem value="all">All Methods</MenuItem>
                    <MenuItem value="1">Cash</MenuItem>
                    <MenuItem value="2">Cheque</MenuItem>
                    <MenuItem value="3">Online</MenuItem>
                    <MenuItem value="4">UPI</MenuItem>
                    <MenuItem value="5">Card</MenuItem>
                  </Select>
                </FormControl>
                <TextField
                  size="small"
                  label="Search"
                  placeholder="Name/Admission No"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  slotProps={{
                    input: {
                      startAdornment: <Search sx={{ mr: 0.5, color: 'text.secondary', fontSize: 20 }} />,
                    }
                  }}
                  fullWidth
                />
              </Box>
            </Box>
          )}
        </Paper>

        {/* Collection Data Table */}
        <Paper elevation={2}>
          {loading ? (
            <Box display="flex" justifyContent="center" p={4}>
              <CircularProgress />
            </Box>
          ) : (
            <>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 'bold' }}>Receipt No</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>Payment Date</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>Admission No</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>Student Name</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>Class</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>Section</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>Session Year</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>Type</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }} align="right">Amount</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>Method</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>Transaction ID</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>Collected By</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {collectionData.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={12} align="center">
                          <Typography variant="body2" color="text.secondary" sx={{ py: 3 }}>
                            No records found for the selected date range
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ) : (
                      collectionData.map((record) => (
                        <TableRow key={`${record.payment_type}-${record.payment_id}`} hover>
                          <TableCell>{record.receipt_number || '-'}</TableCell>
                          <TableCell>{formatDate(record.payment_date)}</TableCell>
                          <TableCell>{record.admission_number}</TableCell>
                          <TableCell>{record.student_name}</TableCell>
                          <TableCell>{record.class_name}</TableCell>
                          <TableCell>{record.section || '-'}</TableCell>
                          <TableCell>{record.session_year_name || '-'}</TableCell>
                          <TableCell>
                            <Chip
                              label={record.payment_type}
                              color={getPaymentTypeColor(record.payment_type)}
                              size="small"
                            />
                          </TableCell>
                          <TableCell align="right" sx={{ fontWeight: 'medium' }}>
                            ₹{record.amount}
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={record.payment_method}
                              color={getPaymentMethodColor(record.payment_method) as any}
                              size="small"
                              variant="outlined"
                            />
                          </TableCell>
                          <TableCell>{record.transaction_id || '-'}</TableCell>
                          <TableCell>{record.created_by_name || '-'}</TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </TableContainer>

              {/* Pagination */}
              {totalPages > 1 && (
                <Box display="flex" justifyContent="center" mt={3} pb={3}>
                  <Pagination
                    count={totalPages}
                    page={page}
                    onChange={(_, newPage) => setPage(newPage)}
                    color={PAGINATION_UI_CONFIG.color}
                    showFirstButton={PAGINATION_UI_CONFIG.showFirstLastButtons}
                    showLastButton={PAGINATION_UI_CONFIG.showFirstLastButtons}
                  />
                </Box>
              )}
            </>
          )}
        </Paper>

        {/* Floating Action Button for Export with Animated Expansion */}
        <Fab
          color="primary"
          aria-label="export report"
          variant="extended"
          onClick={handleExportExcel}
          disabled={collectionData.length === 0}
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
          <TableChart />
          <Box component="span" className="fab-text">
            Export Excel
          </Box>
        </Fab>

        {/* Snackbar */}
        <Snackbar
          open={snackbar.open}
          autoHideDuration={6000}
          onClose={() => setSnackbar({ ...snackbar, open: false })}
        >
          <Alert
            severity={snackbar.severity}
            onClose={() => setSnackbar({ ...snackbar, open: false })}
          >
            {snackbar.message}
          </Alert>
        </Snackbar>
      </ServiceConfigurationLoader>
    </AdminLayout>
  );
};

export default DailyCollectionReport;