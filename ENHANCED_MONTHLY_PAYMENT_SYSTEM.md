# Enhanced Monthly Payment System

## Overview

The Sunrise School Management System now includes a sophisticated month-wise payment system that supports:

1. **Flexible Payment Amounts** - Full, partial, or multi-month payments
2. **Automatic Allocation** - Smart distribution across months (e.g., 3200 rs = 3 full months + 200 rs partial)
3. **Duplicate Prevention** - Cannot pay for already-paid months
4. **Session Year Support** - Payments are tracked per academic session
5. **Admin Month Selection** - Admins can select specific months to pay

## Database Structure

### Existing Tables (No Changes Required)

✅ **All required tables already exist:**

1. **`monthly_fee_tracking`** - Individual month payment tracking
2. **`monthly_payment_allocations`** - Payment-to-month allocation mapping
3. **`fee_payments`** - Payment transaction records
4. **`fee_records`** - Main fee records
5. **`students`** - Student information
6. **`fee_structures`** - Class-wise fee structures

### Performance Improvements

Run the SQL script: `Database/Versioning/07_enhanced_monthly_payment_indexes.sql`

## API Endpoints

### 1. Get Available Months for Payment

```
GET /api/v1/fees/available-months/{student_id}?session_year=2025-26
```

**Response:**
```json
{
  "student": {
    "id": 5,
    "name": "John Doe",
    "admission_number": "2025001",
    "class": "Class 10"
  },
  "session_year": "2025-26",
  "monthly_fee": 1000.0,
  "available_months": [
    {
      "month": 4,
      "month_name": "April",
      "monthly_fee": 1000.0,
      "paid_amount": 0,
      "balance_amount": 1000.0,
      "status": "Pending",
      "can_pay": true
    }
  ],
  "paid_months": [
    {
      "month": 5,
      "month_name": "May", 
      "monthly_fee": 1000.0,
      "paid_amount": 1000.0,
      "balance_amount": 0,
      "status": "Paid",
      "can_pay": false
    }
  ]
}
```

### 2. Enhanced Monthly Payment

```
POST /api/v1/fees/pay-monthly-enhanced/{student_id}
```

**Request Body:**
```json
{
  "amount": 3200,
  "payment_method_id": 1,
  "selected_months": [4, 5, 6, 7],
  "session_year": "2025-26",
  "transaction_id": "TXN123456",
  "remarks": "Payment for April to July"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Payment of ₹3200 allocated successfully across 4 month(s)",
  "payment_id": 123,
  "student": {
    "id": 5,
    "name": "John Doe",
    "admission_number": "2025001",
    "class": "Class 10"
  },
  "payment_summary": {
    "total_amount": 3200,
    "amount_allocated": 3200,
    "amount_remaining": 0,
    "months_affected": 4,
    "fully_paid_months": 3,
    "partial_months": 1
  },
  "month_wise_breakdown": [
    {
      "month": 4,
      "month_name": "April",
      "monthly_fee": 1000.0,
      "previous_paid": 0,
      "allocated_amount": 1000.0,
      "new_paid_amount": 1000.0,
      "remaining_balance": 0,
      "status": "Paid"
    },
    {
      "month": 5,
      "month_name": "May",
      "monthly_fee": 1000.0,
      "previous_paid": 0,
      "allocated_amount": 1000.0,
      "new_paid_amount": 1000.0,
      "remaining_balance": 0,
      "status": "Paid"
    },
    {
      "month": 6,
      "month_name": "June",
      "monthly_fee": 1000.0,
      "previous_paid": 0,
      "allocated_amount": 1000.0,
      "new_paid_amount": 1000.0,
      "remaining_balance": 0,
      "status": "Paid"
    },
    {
      "month": 7,
      "month_name": "July",
      "monthly_fee": 1000.0,
      "previous_paid": 0,
      "allocated_amount": 200.0,
      "new_paid_amount": 200.0,
      "remaining_balance": 800.0,
      "status": "Partial"
    }
  ]
}
```

## Payment Logic Examples

### Example 1: Exact Multi-Month Payment
- **Payment**: ₹3000 for ₹1000/month
- **Result**: 3 months fully paid
- **Allocation**: April (₹1000), May (₹1000), June (₹1000)

### Example 2: Partial Payment with Overflow
- **Payment**: ₹3200 for ₹1000/month  
- **Result**: 3 months fully paid + 1 month partial
- **Allocation**: April (₹1000), May (₹1000), June (₹1000), July (₹200 partial, ₹800 balance)

### Example 3: Single Month Partial Payment
- **Payment**: ₹500 for ₹1000/month
- **Result**: 1 month partial payment
- **Allocation**: April (₹500 partial, ₹500 balance)

## Error Handling

### Duplicate Payment Prevention
```json
{
  "detail": "The following months are already fully paid: April, May. Please select different months."
}
```

### Invalid Month Selection
```json
{
  "detail": "Invalid month: 13. Must be between 1 and 12"
}
```

### Insufficient Data
```json
{
  "detail": "Fee structure not found for student's class"
}
```

## Frontend Integration

### Month Selection UI
- Show available months with balance amounts
- Disable already-paid months
- Calculate total amount for selected months
- Show payment breakdown preview

### Payment Form
- Amount input with validation
- Month selection checkboxes
- Payment method dropdown
- Transaction ID field
- Remarks field

### Payment Confirmation
- Show detailed breakdown before payment
- Display month-wise allocation
- Confirm payment details

## Database Queries

### Get Student Payment Status
```sql
SELECT 
    mft.academic_month,
    mft.month_name,
    mft.monthly_amount,
    mft.paid_amount,
    (mft.monthly_amount - mft.paid_amount) as balance,
    CASE 
        WHEN mft.paid_amount >= mft.monthly_amount THEN 'Paid'
        WHEN mft.paid_amount > 0 THEN 'Partial'
        ELSE 'Pending'
    END as status
FROM monthly_fee_tracking mft
WHERE mft.student_id = ? AND mft.session_year_id = ?
ORDER BY mft.academic_month;
```

### Payment History with Allocations
```sql
SELECT 
    fp.payment_date,
    fp.amount as payment_amount,
    fp.transaction_id,
    mpa.amount as allocated_amount,
    mft.academic_month,
    mft.month_name
FROM fee_payments fp
JOIN monthly_payment_allocations mpa ON fp.id = mpa.payment_id
JOIN monthly_fee_tracking mft ON mpa.monthly_tracking_id = mft.id
WHERE mft.student_id = ?
ORDER BY fp.payment_date DESC, mft.academic_month;
```

## Testing Scenarios

1. **Test exact month payment**: ₹1000 for 1 month
2. **Test multi-month payment**: ₹3000 for 3 months  
3. **Test partial overflow**: ₹3200 for 4 months (3 full + 1 partial)
4. **Test duplicate prevention**: Try paying already-paid month
5. **Test session year filtering**: Different payments for different years
6. **Test partial month completion**: Pay remaining balance of partial month

## Next Steps

1. **Run the index script** to improve performance
2. **Test the enhanced endpoints** with the provided examples
3. **Update the frontend** to use the new payment system
4. **Add validation** for business rules (e.g., payment deadlines)
5. **Create reports** for payment tracking and analytics
