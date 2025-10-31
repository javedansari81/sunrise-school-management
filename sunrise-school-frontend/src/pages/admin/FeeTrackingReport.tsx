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
  FormControlLabel,
  Checkbox,
} from '@mui/material';
import { DEFAULT_PAGE_SIZE, PAGINATION_UI_CONFIG } from '../../config/pagination';
import {
  ClassDropdown,
  SessionYearDropdown,
} from '../../components/common/MetadataDropdown';
import ServiceConfigurationLoader from '../../components/common/ServiceConfigurationLoader';
import {
  FilterList,
  Search,
  Download,
  PictureAsPdf,
  TableChart,
  ExpandMore,
  ExpandLess,
} from '@mui/icons-material';
import AdminLayout from '../../components/Layout/AdminLayout';
import { reportsAPI } from '../../services/api';
import * as XLSX from 'xlsx';

interface FeeTrackingData {
  student_id: number;
  admission_number: string;
  first_name: string;
  last_name: string;
  full_name: string;
  class_id: number;
  class_name: string;
  section: string | null;
  session_year_id: number;
  session_year_name: string;

  // Fee Information
  total_fee_amount: string;
  paid_fee_amount: string;
  pending_fee_amount: string;
  fee_collection_rate: number;
  fee_payment_status: string;

  // Transport Information
  transport_opted: boolean;
  transport_type: string | null;
  monthly_transport_fee: string | null;
  total_transport_amount: string | null;
  paid_transport_amount: string | null;
  pending_transport_amount: string | null;
  transport_collection_rate: number | null;
  transport_payment_status: string | null;

  // Combined Totals
  total_amount: string;
  total_paid: string;
  total_pending: string;
  overall_collection_rate: number;
}

const FeeTrackingReport: React.FC = () => {
  // State management
  const [feeData, setFeeData] = useState<FeeTrackingData[]>([]);
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });
  const [filtersExpanded, setFiltersExpanded] = useState(true);

  // Filters
  const [filterSessionYear, setFilterSessionYear] = useState<string>('');
  const [filterClass, setFilterClass] = useState<string>('all');
  const [filterSection, setFilterSection] = useState<string>('all');
  const [filterPaymentStatus, setFilterPaymentStatus] = useState<string>('all');
  const [filterTransportOpted, setFilterTransportOpted] = useState<string>('all');
  const [filterPendingOnly, setFilterPendingOnly] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // Pagination
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalRecords, setTotalRecords] = useState(0);
  const perPage = DEFAULT_PAGE_SIZE;

  // Available sections (dynamically populated)
  const [availableSections, setAvailableSections] = useState<string[]>([]);

  // Load fee tracking data from API
  const loadFeeData = async () => {
    if (!filterSessionYear || filterSessionYear === 'all') {
      setSnackbar({
        open: true,
        message: 'Please select a session year',
        severity: 'error'
      });
      return;
    }

    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.append('session_year_id', filterSessionYear);
      params.append('page', page.toString());
      params.append('per_page', perPage.toString());

      // Add filters
      if (filterClass !== 'all') params.append('class_id', filterClass);
      if (filterSection !== 'all') params.append('section', filterSection);
      if (filterPaymentStatus !== 'all') params.append('payment_status', filterPaymentStatus);
      if (filterTransportOpted !== 'all') params.append('transport_opted', filterTransportOpted);
      if (filterPendingOnly) params.append('pending_only', 'true');
      if (searchTerm) params.append('search', searchTerm);

      const response = await reportsAPI.getFeeTrackingReport(params);
      setFeeData(response.records || []);
      setTotalPages(response.total_pages);
      setTotalRecords(response.total);

      // Extract unique sections from data
      const sections = Array.from(new Set((response.records || []).map((d: FeeTrackingData) => d.section).filter(Boolean)));
      setAvailableSections(sections as string[]);

    } catch (error: any) {
      console.error('Error loading fee tracking data:', error);
      setSnackbar({
        open: true,
        message: error.response?.data?.detail || 'Failed to load fee tracking data',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (filterSessionYear && filterSessionYear !== 'all') {
      loadFeeData();
    }
  }, [page, filterSessionYear, filterClass, filterSection, filterPaymentStatus, filterTransportOpted, filterPendingOnly, searchTerm]);

  // Reset to page 1 when filters change
  useEffect(() => {
    setPage(1);
  }, [filterSessionYear, filterClass, filterSection, filterPaymentStatus, filterTransportOpted, filterPendingOnly, searchTerm]);

  // Export to Excel
  const handleExportExcel = () => {
    if (!feeData || feeData.length === 0) {
      setSnackbar({
        open: true,
        message: 'No data to export',
        severity: 'error'
      });
      return;
    }

    try {
      const exportData = feeData.map(record => ({
        'Admission Number': record.admission_number,
        'Student Name': record.full_name,
        'Class': record.class_name,
        'Section': record.section || 'N/A',
        'Session Year': record.session_year_name,
        'Total Fee Amount': `₹${record.total_fee_amount}`,
        'Paid Fee Amount': `₹${record.paid_fee_amount}`,
        'Pending Fee Amount': `₹${record.pending_fee_amount}`,
        'Fee Collection Rate': `${record.fee_collection_rate.toFixed(2)}%`,
        'Fee Payment Status': record.fee_payment_status,
        'Transport Opted': record.transport_opted ? 'Yes' : 'No',
        'Transport Type': record.transport_type || 'N/A',
        'Monthly Transport Fee': record.monthly_transport_fee ? `₹${record.monthly_transport_fee}` : 'N/A',
        'Total Transport Amount': record.total_transport_amount ? `₹${record.total_transport_amount}` : 'N/A',
        'Paid Transport Amount': record.paid_transport_amount ? `₹${record.paid_transport_amount}` : 'N/A',
        'Pending Transport Amount': record.pending_transport_amount ? `₹${record.pending_transport_amount}` : 'N/A',
        'Transport Collection Rate': record.transport_collection_rate ? `${record.transport_collection_rate.toFixed(2)}%` : 'N/A',
        'Transport Payment Status': record.transport_payment_status || 'N/A',
        'Total Amount': `₹${record.total_amount}`,
        'Total Paid': `₹${record.total_paid}`,
        'Total Pending': `₹${record.total_pending}`,
        'Overall Collection Rate': `${record.overall_collection_rate.toFixed(2)}%`,
      }));

      const worksheet = XLSX.utils.json_to_sheet(exportData);
      const workbook = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(workbook, worksheet, 'Fee Tracking Report');

      // Auto-size columns
      const maxWidth = 50;
      const colWidths = Object.keys(exportData[0] || {}).map(key => ({
        wch: Math.min(Math.max(key.length, 10), maxWidth)
      }));
      worksheet['!cols'] = colWidths;

      XLSX.writeFile(workbook, `Fee_Tracking_Report_${new Date().toISOString().split('T')[0]}.xlsx`);

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

  const getPaymentStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'paid':
        return 'success';
      case 'partial':
        return 'warning';
      case 'pending':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <AdminLayout>
      <Box sx={{ p: { xs: 1, sm: 2, md: 3 } }}>
        <ServiceConfigurationLoader service="fee-management">
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
                {!filtersExpanded && (
                  <Chip
                    label={`${filterSessionYear ? 'Session: ' + filterSessionYear : 'Select session year'}`}
                    size="small"
                    color={filterSessionYear ? 'primary' : 'default'}
                    sx={{ ml: 1 }}
                  />
                )}
              </Box>
              <Box display="flex" alignItems="center" gap={1}>
                <Button
                  variant="contained"
                  startIcon={<TableChart />}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleExportExcel();
                  }}
                  disabled={feeData.length === 0}
                  size="small"
                >
                  Export
                </Button>
                {filtersExpanded ? <ExpandLess /> : <ExpandMore />}
              </Box>
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
                  mb={1.5}
                >
                  <SessionYearDropdown
                    value={filterSessionYear}
                    onChange={(value) => setFilterSessionYear(value as string)}
                    label="Session Year *"
                    size="small"
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
                    <InputLabel>Payment Status</InputLabel>
                    <Select
                      value={filterPaymentStatus}
                      label="Payment Status"
                      onChange={(e) => setFilterPaymentStatus(e.target.value)}
                    >
                      <MenuItem value="all">All Status</MenuItem>
                      <MenuItem value="paid">Paid</MenuItem>
                      <MenuItem value="partial">Partial</MenuItem>
                      <MenuItem value="pending">Pending</MenuItem>
                    </Select>
                  </FormControl>
                  <FormControl size="small" fullWidth>
                    <InputLabel>Transport</InputLabel>
                    <Select
                      value={filterTransportOpted}
                      label="Transport"
                      onChange={(e) => setFilterTransportOpted(e.target.value)}
                    >
                      <MenuItem value="all">All Students</MenuItem>
                      <MenuItem value="true">Transport Opted</MenuItem>
                      <MenuItem value="false">No Transport</MenuItem>
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
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={filterPendingOnly}
                      onChange={(e) => setFilterPendingOnly(e.target.checked)}
                      size="small"
                    />
                  }
                  label="Show only students with pending payments"
                  sx={{ ml: 0.5 }}
                />
              </Box>
            )}
          </Paper>

          {/* Fee Tracking Data Table */}
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
                        <TableCell>Admission No</TableCell>
                        <TableCell>Student Name</TableCell>
                        <TableCell>Class</TableCell>
                        <TableCell>Section</TableCell>
                        <TableCell>Total Fee</TableCell>
                        <TableCell>Fee Paid</TableCell>
                        <TableCell>Transport Paid</TableCell>
                        <TableCell>Total Paid</TableCell>
                        <TableCell>Pending</TableCell>
                        <TableCell>Collection Rate</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Transport</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {feeData.length === 0 ? (
                        <TableRow>
                          <TableCell colSpan={12} align="center">
                            <Typography variant="body2" color="text.secondary" sx={{ py: 3 }}>
                              {filterSessionYear ? 'No records found' : 'Please select a session year'}
                            </Typography>
                          </TableCell>
                        </TableRow>
                      ) : (
                        feeData.map((record) => (
                          <TableRow key={record.student_id} hover>
                            <TableCell>{record.admission_number}</TableCell>
                            <TableCell>{record.full_name}</TableCell>
                            <TableCell>{record.class_name}</TableCell>
                            <TableCell>{record.section || 'N/A'}</TableCell>
                            <TableCell>₹{record.total_fee_amount}</TableCell>
                            <TableCell>₹{record.paid_fee_amount}</TableCell>
                            <TableCell>₹{record.paid_transport_amount || '0.00'}</TableCell>
                            <TableCell>₹{record.total_paid}</TableCell>
                            <TableCell>
                              <Typography
                                variant="body2"
                                color={parseFloat(record.total_pending) > 0 ? 'error' : 'success.main'}
                                fontWeight="bold"
                              >
                                ₹{record.total_pending}
                              </Typography>
                            </TableCell>
                            <TableCell>{record.overall_collection_rate.toFixed(1)}%</TableCell>
                            <TableCell>
                              <Chip
                                label={record.fee_payment_status}
                                color={getPaymentStatusColor(record.fee_payment_status)}
                                size="small"
                              />
                            </TableCell>
                            <TableCell>
                              {record.transport_opted ? (
                                <Chip label="Yes" color="primary" size="small" />
                              ) : (
                                <Chip label="No" size="small" />
                              )}
                            </TableCell>
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

          {/* Snackbar for notifications */}
          <Snackbar
            open={snackbar.open}
            autoHideDuration={6000}
            onClose={() => setSnackbar({ ...snackbar, open: false })}
            anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
          >
            <Alert
              onClose={() => setSnackbar({ ...snackbar, open: false })}
              severity={snackbar.severity}
              sx={{ width: '100%' }}
            >
              {snackbar.message}
            </Alert>
          </Snackbar>
        </ServiceConfigurationLoader>
      </Box>
    </AdminLayout>
  );
};

export default FeeTrackingReport;

