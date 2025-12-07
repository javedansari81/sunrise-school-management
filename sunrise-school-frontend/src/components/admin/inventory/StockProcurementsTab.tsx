import React, { useState, useEffect } from 'react';
import {
  Box,
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
  CircularProgress,
  Tooltip,
  useMediaQuery,
  useTheme
} from '@mui/material';
import {
  Visibility as VisibilityIcon
} from '@mui/icons-material';
import {
  getStockProcurements,
  InventoryStockProcurement,
  InventoryStockProcurementListResponse
} from '../../../services/inventoryService';
import { DEFAULT_PAGE_SIZE } from '../../../config/pagination';
import StockProcurementDialog from './StockProcurementDialog';
import StockProcurementDetailsDialog from './StockProcurementDetailsDialog';

interface StockProcurementsTabProps {
  configuration: any;
  onError: (message: string) => void;
  onSuccess: (message: string) => void;
  // Filters passed from parent
  fromDate?: string;
  toDate?: string;
  // Dialog control from parent
  dialogOpen?: boolean;
  onDialogClose?: () => void;
}

const StockProcurementsTab: React.FC<StockProcurementsTabProps> = ({
  configuration,
  onError,
  onSuccess,
  fromDate: parentFromDate,
  toDate: parentToDate,
  dialogOpen: parentDialogOpen,
  onDialogClose: parentOnDialogClose
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  // State
  const [procurements, setProcurements] = useState<InventoryStockProcurement[]>([]);
  const [totalProcurements, setTotalProcurements] = useState(0);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(DEFAULT_PAGE_SIZE);
  const [procurementDialogOpen, setProcurementDialogOpen] = useState(false);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [selectedProcurement, setSelectedProcurement] = useState<InventoryStockProcurement | null>(null);

  // Use parent filters if provided
  const fromDate = parentFromDate ?? '';
  const toDate = parentToDate ?? '';

  // Handle parent dialog control
  useEffect(() => {
    if (parentDialogOpen !== undefined) {
      setProcurementDialogOpen(parentDialogOpen);
    }
  }, [parentDialogOpen]);

  useEffect(() => {
    fetchProcurements();
  }, [page, rowsPerPage, fromDate, toDate]);

  const fetchProcurements = async () => {
    setLoading(true);
    try {
      const params: any = {
        page: page + 1,
        per_page: rowsPerPage
      };

      if (fromDate) params.from_date = fromDate;
      if (toDate) params.to_date = toDate;

      const data: InventoryStockProcurementListResponse = await getStockProcurements(params);
      setProcurements(data.procurements);
      setTotalProcurements(data.total);
    } catch (err: any) {
      console.error('Error fetching procurements:', err);
      onError(err.response?.data?.detail || 'Failed to fetch procurements');
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = (procurement: InventoryStockProcurement) => {
    setSelectedProcurement(procurement);
    setDetailsDialogOpen(true);
  };

  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleProcurementSuccess = () => {
    onSuccess('Stock procurement created successfully');
    fetchProcurements();
    // Notify parent to close dialog if controlled
    if (parentOnDialogClose) {
      parentOnDialogClose();
    }
  };

  const handleDialogClose = () => {
    setProcurementDialogOpen(false);
    if (parentOnDialogClose) {
      parentOnDialogClose();
    }
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  const formatCurrency = (amount: number): string => {
    return `₹${amount.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  return (
    <Box>

      {/* Procurements Table */}
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <Paper sx={{ overflow: 'hidden' }}>
          <TableContainer sx={{ maxHeight: { xs: '60vh', sm: '70vh' }, overflowX: 'auto' }}>
            <Table size={isMobile ? 'small' : 'medium'} stickyHeader>
              <TableHead>
                <TableRow sx={{ bgcolor: 'white' }}>
                  <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' }, py: { xs: 1, sm: 1.5 }, minWidth: 100 }}>
                    Date
                  </TableCell>
                  <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' }, py: { xs: 1, sm: 1.5 }, minWidth: 120 }}>
                    Invoice #
                  </TableCell>
                  <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' }, py: { xs: 1, sm: 1.5 }, minWidth: 150 }}>
                    Vendor
                  </TableCell>
                  <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' }, py: { xs: 1, sm: 1.5 }, minWidth: 80 }} align="right">
                    Items
                  </TableCell>
                  <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' }, py: { xs: 1, sm: 1.5 }, minWidth: 120 }} align="right">
                    Total Amount
                  </TableCell>
                  <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' }, py: { xs: 1, sm: 1.5 }, minWidth: 120 }}>
                    Payment Method
                  </TableCell>
                  <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' }, py: { xs: 1, sm: 1.5 }, minWidth: 120 }}>
                    Payment Status
                  </TableCell>
                  <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' }, py: { xs: 1, sm: 1.5 }, minWidth: 80 }} align="center">
                    Actions
                  </TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {procurements.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} align="center" sx={{ py: 4 }}>
                      <Typography variant="body2" color="text.secondary">
                        No procurements found
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  procurements.map((procurement) => (
                    <TableRow key={procurement.id} hover>
                      <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' }, py: { xs: 0.5, sm: 1 } }}>
                        {formatDate(procurement.procurement_date)}
                      </TableCell>
                      <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' }, py: { xs: 0.5, sm: 1 } }}>
                        {procurement.invoice_number || 'N/A'}
                      </TableCell>
                      <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' }, py: { xs: 0.5, sm: 1 } }}>
                        {procurement.vendor_name || 'No Vendor'}
                      </TableCell>
                      <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' }, py: { xs: 0.5, sm: 1 } }} align="right">
                        {procurement.items.length}
                      </TableCell>
                      <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' }, py: { xs: 0.5, sm: 1 }, fontWeight: 600 }} align="right">
                        {formatCurrency(procurement.total_amount)}
                      </TableCell>
                      <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' }, py: { xs: 0.5, sm: 1 } }}>
                        {procurement.payment_method_name}
                      </TableCell>
                      <TableCell sx={{ py: { xs: 0.5, sm: 1 } }}>
                        <Chip
                          label={procurement.payment_status_name}
                          size="small"
                          color={procurement.payment_status_name === 'Paid' ? 'success' : 'warning'}
                          sx={{ fontSize: { xs: '0.7rem', sm: '0.75rem' } }}
                        />
                      </TableCell>
                      <TableCell sx={{ py: { xs: 0.5, sm: 1 } }} align="center">
                        <Tooltip title="View Details">
                          <IconButton
                            size="small"
                            onClick={() => handleViewDetails(procurement)}
                            sx={{ fontSize: { xs: '1rem', sm: '1.25rem' } }}
                          >
                            <VisibilityIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
          <TablePagination
            rowsPerPageOptions={[10, 25, 50, 100]}
            component="div"
            count={totalProcurements}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
          />
        </Paper>
      )}

      {/* New Procurement Dialog */}
      <StockProcurementDialog
        open={procurementDialogOpen}
        onClose={handleDialogClose}
        configuration={configuration}
        onSuccess={handleProcurementSuccess}
        onError={onError}
      />

      {/* Procurement Details Dialog */}
      <StockProcurementDetailsDialog
        open={detailsDialogOpen}
        onClose={() => setDetailsDialogOpen(false)}
        procurement={selectedProcurement}
      />
    </Box>
  );
};

export default StockProcurementsTab;

