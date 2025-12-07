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
  Avatar,
  Tooltip,
  useMediaQuery,
  useTheme
} from '@mui/material';
import {
  Edit as EditIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';
import { getStockLevels, InventoryStock } from '../../../services/inventoryService';
import { DEFAULT_PAGE_SIZE } from '../../../config/pagination';
import StockThresholdDialog from './StockThresholdDialog';

interface StockLevelsTabProps {
  configuration: any;
  onError: (message: string) => void;
  // Filters passed from parent
  itemTypeId?: number | null;
  sizeTypeId?: number | null;
  stockStatus?: string;
}

const StockLevelsTab: React.FC<StockLevelsTabProps> = ({
  configuration,
  onError,
  itemTypeId: parentItemTypeId,
  sizeTypeId: parentSizeTypeId,
  stockStatus: parentStockStatus
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  // State
  const [stocks, setStocks] = useState<InventoryStock[]>([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(DEFAULT_PAGE_SIZE);
  const [selectedStock, setSelectedStock] = useState<InventoryStock | null>(null);
  const [thresholdDialogOpen, setThresholdDialogOpen] = useState(false);

  // Use parent filters if provided
  const itemTypeFilter = parentItemTypeId ?? '';
  const sizeTypeFilter = parentSizeTypeId ?? '';
  const lowStockFilter = parentStockStatus ?? 'all';

  useEffect(() => {
    fetchStocks();
  }, [itemTypeFilter, sizeTypeFilter, lowStockFilter]);

  const fetchStocks = async () => {
    setLoading(true);
    try {
      const params: any = {
        page: 1,
        per_page: 500 // Get all for client-side pagination
      };

      if (itemTypeFilter) params.item_type_id = itemTypeFilter;
      if (sizeTypeFilter) params.size_type_id = sizeTypeFilter;
      if (lowStockFilter === 'low') params.low_stock_only = true;

      const data = await getStockLevels(params);
      setStocks(data);
      setPage(0);
    } catch (err: any) {
      console.error('Error fetching stocks:', err);
      onError(err.response?.data?.detail || 'Failed to fetch stock levels');
    } finally {
      setLoading(false);
    }
  };

  const handleEditThreshold = (stock: InventoryStock) => {
    setSelectedStock(stock);
    setThresholdDialogOpen(true);
  };

  const handleThresholdDialogClose = () => {
    setThresholdDialogOpen(false);
    setSelectedStock(null);
  };

  const handleThresholdUpdateSuccess = () => {
    fetchStocks();
  };

  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const getStockStatusChip = (stock: InventoryStock) => {
    if (stock.current_quantity === 0) {
      return (
        <Chip
          label="OUT OF STOCK"
          color="error"
          size="small"
          icon={<WarningIcon />}
          sx={{ fontSize: { xs: '0.7rem', sm: '0.75rem' } }}
        />
      );
    } else if (stock.is_low_stock) {
      return (
        <Chip
          label="LOW STOCK"
          color="warning"
          size="small"
          icon={<WarningIcon />}
          sx={{ fontSize: { xs: '0.7rem', sm: '0.75rem' } }}
        />
      );
    } else {
      return (
        <Chip
          label="IN STOCK"
          color="success"
          size="small"
          icon={<CheckCircleIcon />}
          sx={{ fontSize: { xs: '0.7rem', sm: '0.75rem' } }}
        />
      );
    }
  };

  const formatDate = (dateString: string | undefined): string => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  // Pagination
  const paginatedStocks = stocks.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  return (
    <Box>
      {/* Stock Table */}
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
                  <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' }, py: { xs: 1, sm: 1.5 }, minWidth: 60 }}>
                    Image
                  </TableCell>
                  <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' }, py: { xs: 1, sm: 1.5 }, minWidth: 150 }}>
                    Item
                  </TableCell>
                  <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' }, py: { xs: 1, sm: 1.5 }, minWidth: 80 }}>
                    Size
                  </TableCell>
                  <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' }, py: { xs: 1, sm: 1.5 }, minWidth: 100 }} align="right">
                    Current Qty
                  </TableCell>
                  <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' }, py: { xs: 1, sm: 1.5 }, minWidth: 100 }} align="right">
                    Min Threshold
                  </TableCell>
                  <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' }, py: { xs: 1, sm: 1.5 }, minWidth: 100 }} align="right">
                    Reorder Qty
                  </TableCell>
                  <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' }, py: { xs: 1, sm: 1.5 }, minWidth: 120 }}>
                    Status
                  </TableCell>
                  <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' }, py: { xs: 1, sm: 1.5 }, minWidth: 120 }}>
                    Last Restocked
                  </TableCell>
                  <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' }, py: { xs: 1, sm: 1.5 }, minWidth: 80 }} align="center">
                    Actions
                  </TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {paginatedStocks.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={9} align="center" sx={{ py: 4 }}>
                      <Typography variant="body2" color="text.secondary">
                        No stock records found
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  paginatedStocks.map((stock) => (
                    <TableRow key={stock.id} hover>
                      <TableCell sx={{ py: { xs: 0.5, sm: 1 } }}>
                        <Avatar
                          src={stock.item_image_url}
                          alt={stock.item_type_description}
                          variant="rounded"
                          sx={{ width: { xs: 32, sm: 40 }, height: { xs: 32, sm: 40 } }}
                        >
                          {stock.item_type_description.charAt(0)}
                        </Avatar>
                      </TableCell>
                      <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' }, py: { xs: 0.5, sm: 1 } }}>
                        <Typography variant="body2" sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}>
                          {stock.item_type_description}
                        </Typography>
                        {stock.item_category && (
                          <Typography variant="caption" color="text.secondary" sx={{ fontSize: { xs: '0.65rem', sm: '0.75rem' } }}>
                            {stock.item_category}
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' }, py: { xs: 0.5, sm: 1 } }}>
                        {stock.size_name || 'N/A'}
                      </TableCell>
                      <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' }, py: { xs: 0.5, sm: 1 } }} align="right">
                        <Typography
                          variant="body2"
                          sx={{
                            fontSize: { xs: '0.75rem', sm: '0.875rem' },
                            fontWeight: stock.current_quantity === 0 ? 'bold' : 'normal',
                            color: stock.current_quantity === 0 ? 'error.main' : 'inherit'
                          }}
                        >
                          {stock.current_quantity}
                        </Typography>
                      </TableCell>
                      <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' }, py: { xs: 0.5, sm: 1 } }} align="right">
                        {stock.minimum_threshold}
                      </TableCell>
                      <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' }, py: { xs: 0.5, sm: 1 } }} align="right">
                        {stock.reorder_quantity}
                      </TableCell>
                      <TableCell sx={{ py: { xs: 0.5, sm: 1 } }}>
                        {getStockStatusChip(stock)}
                      </TableCell>
                      <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' }, py: { xs: 0.5, sm: 1 } }}>
                        {formatDate(stock.last_restocked_date)}
                      </TableCell>
                      <TableCell sx={{ py: { xs: 0.5, sm: 1 } }} align="center">
                        <Tooltip title="Edit Thresholds">
                          <IconButton
                            size="small"
                            onClick={() => handleEditThreshold(stock)}
                            sx={{ fontSize: { xs: '1rem', sm: '1.25rem' } }}
                          >
                            <EditIcon fontSize="small" />
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
            count={stocks.length}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
          />
        </Paper>
      )}

      {/* Stock Threshold Dialog */}
      <StockThresholdDialog
        open={thresholdDialogOpen}
        onClose={handleThresholdDialogClose}
        stock={selectedStock}
        onSuccess={handleThresholdUpdateSuccess}
        onError={onError}
      />
    </Box>
  );
};

export default StockLevelsTab;

