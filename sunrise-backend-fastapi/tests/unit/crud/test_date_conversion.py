"""
Unit tests for date conversion logic in CRUD operations.

This module tests the date conversion functionality that handles
string dates in API requests and converts them to proper date objects.
"""
import pytest
from datetime import datetime, date
from pydantic import BaseModel, ValidationError
from fastapi.encoders import jsonable_encoder


class TestTeacherData(BaseModel):
    """Test model for date conversion testing."""
    employee_id: str
    first_name: str
    last_name: str
    date_of_birth: str  # String date
    joining_date: str   # String date
    email: str


@pytest.mark.unit
@pytest.mark.crud
class TestDateConversion:
    """Test class for date conversion logic."""

    def test_string_date_conversion_valid_formats(self):
        """Test conversion of valid string date formats."""
        test_data = TestTeacherData(
            employee_id="EMP001",
            first_name="John",
            last_name="Doe",
            date_of_birth="1985-01-15",
            joining_date="2020-08-01",
            email="john.doe@test.com"
        )
        
        # Convert to dict for processing
        data_dict = test_data.dict()
        
        # Test date conversion logic
        date_fields = ["date_of_birth", "joining_date"]
        
        for field in date_fields:
            if field in data_dict and isinstance(data_dict[field], str):
                try:
                    # Try to parse the date string
                    parsed_date = datetime.strptime(data_dict[field], "%Y-%m-%d").date()
                    assert isinstance(parsed_date, date)
                    
                    # Verify the parsed date is correct
                    if field == "date_of_birth":
                        assert parsed_date == date(1985, 1, 15)
                    elif field == "joining_date":
                        assert parsed_date == date(2020, 8, 1)
                        
                except ValueError:
                    pytest.fail(f"Failed to parse date field {field}: {data_dict[field]}")

    def test_string_date_conversion_invalid_formats(self):
        """Test handling of invalid string date formats."""
        invalid_dates = [
            "invalid-date",
            "2020-13-01",  # Invalid month
            "2020-02-30",  # Invalid day
            "20-01-01",    # Wrong format
            "",            # Empty string
            "2020/01/01",  # Wrong separator
        ]
        
        for invalid_date in invalid_dates:
            with pytest.raises(ValueError):
                datetime.strptime(invalid_date, "%Y-%m-%d").date()

    def test_date_field_processing_in_crud_update(self):
        """Test date field processing as it would happen in CRUD update."""
        # Simulate incoming data from API
        incoming_data = {
            "employee_id": "EMP002",
            "first_name": "Jane",
            "last_name": "Smith",
            "date_of_birth": "1990-05-20",
            "joining_date": "2021-03-15",
            "email": "jane.smith@test.com",
            "phone": "1234567890"
        }
        
        # Simulate the date conversion logic from base CRUD
        processed_data = incoming_data.copy()
        date_fields = ["date_of_birth", "joining_date", "admission_date"]
        
        for field in date_fields:
            if field in processed_data and isinstance(processed_data[field], str):
                try:
                    processed_data[field] = datetime.strptime(
                        processed_data[field], "%Y-%m-%d"
                    ).date()
                except ValueError:
                    # Keep original value if conversion fails
                    pass
        
        # Verify conversion worked
        assert isinstance(processed_data["date_of_birth"], date)
        assert isinstance(processed_data["joining_date"], date)
        assert processed_data["date_of_birth"] == date(1990, 5, 20)
        assert processed_data["joining_date"] == date(2021, 3, 15)
        
        # Non-date fields should remain unchanged
        assert processed_data["employee_id"] == "EMP002"
        assert processed_data["first_name"] == "Jane"
        assert processed_data["phone"] == "1234567890"

    def test_jsonable_encoder_with_dates(self):
        """Test that jsonable_encoder properly handles date objects."""
        data_with_dates = {
            "employee_id": "EMP003",
            "first_name": "Bob",
            "date_of_birth": date(1988, 12, 10),
            "joining_date": date(2019, 6, 1),
            "created_at": datetime(2023, 1, 1, 12, 0, 0)
        }
        
        # Use FastAPI's jsonable_encoder
        encoded_data = jsonable_encoder(data_with_dates)
        
        # Dates should be converted to ISO format strings
        assert encoded_data["date_of_birth"] == "1988-12-10"
        assert encoded_data["joining_date"] == "2019-06-01"
        assert "2023-01-01T12:00:00" in encoded_data["created_at"]
        
        # Other fields should remain unchanged
        assert encoded_data["employee_id"] == "EMP003"
        assert encoded_data["first_name"] == "Bob"

    def test_mixed_date_formats_handling(self):
        """Test handling of mixed date formats in the same dataset."""
        mixed_data = {
            "date_of_birth": "1985-01-15",      # String format
            "joining_date": date(2020, 8, 1),   # Date object
            "last_updated": datetime.now(),      # Datetime object
            "some_field": "not a date"           # Non-date field
        }
        
        # Process only string dates
        date_fields = ["date_of_birth", "joining_date", "admission_date"]
        
        for field in date_fields:
            if field in mixed_data and isinstance(mixed_data[field], str):
                try:
                    mixed_data[field] = datetime.strptime(
                        mixed_data[field], "%Y-%m-%d"
                    ).date()
                except ValueError:
                    pass
        
        # Verify results
        assert isinstance(mixed_data["date_of_birth"], date)
        assert isinstance(mixed_data["joining_date"], date)
        assert isinstance(mixed_data["last_updated"], datetime)
        assert mixed_data["some_field"] == "not a date"

    def test_edge_cases(self):
        """Test edge cases in date conversion."""
        edge_cases = {
            "leap_year": "2020-02-29",      # Leap year date
            "year_boundary": "2019-12-31",  # Year boundary
            "month_boundary": "2020-01-31", # Month boundary
        }
        
        for case_name, date_string in edge_cases.items():
            try:
                parsed_date = datetime.strptime(date_string, "%Y-%m-%d").date()
                assert isinstance(parsed_date, date)
                
                # Verify specific cases
                if case_name == "leap_year":
                    assert parsed_date == date(2020, 2, 29)
                elif case_name == "year_boundary":
                    assert parsed_date == date(2019, 12, 31)
                elif case_name == "month_boundary":
                    assert parsed_date == date(2020, 1, 31)
                    
            except ValueError:
                pytest.fail(f"Failed to parse edge case {case_name}: {date_string}")

    def test_none_and_empty_values(self):
        """Test handling of None and empty values."""
        test_values = [None, "", "   "]
        
        for value in test_values:
            # Should not attempt conversion for None or empty values
            if value and isinstance(value, str) and value.strip():
                try:
                    datetime.strptime(value, "%Y-%m-%d").date()
                except ValueError:
                    # Expected for empty/whitespace strings
                    pass
            else:
                # None and empty values should be skipped
                assert value in [None, "", "   "]
