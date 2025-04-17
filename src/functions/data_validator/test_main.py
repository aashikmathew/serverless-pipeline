import pytest
from main import data_validator, validate_email
from unittest.mock import Mock

def test_validate_email():
    assert validate_email("test@example.com") == True
    assert validate_email("invalid-email") == False
    assert validate_email("test@.com") == False
    assert validate_email("@example.com") == False

def test_data_validator_missing_fields():
    request = Mock()
    request.get_json = Mock(return_value={"name": "Test"})
    response, status_code = data_validator(request)
    assert status_code == 400
    assert "missing_fields" in response

def test_data_validator_invalid_email():
    request = Mock()
    request.get_json = Mock(return_value={
        "name": "Test",
        "email": "invalid-email",
        "age": 25
    })
    response, status_code = data_validator(request)
    assert status_code == 400
    assert "INVALID_EMAIL" in response

def test_data_validator_invalid_age():
    request = Mock()
    request.get_json = Mock(return_value={
        "name": "Test",
        "email": "test@example.com",
        "age": -1
    })
    response, status_code = data_validator(request)
    assert status_code == 400
    assert "INVALID_AGE_VALUE" in response

def test_data_validator_valid_data():
    request = Mock()
    request.get_json = Mock(return_value={
        "name": "Test User",
        "email": "test@example.com",
        "age": 25
    })
    response, status_code = data_validator(request)
    assert status_code == 200
    assert "SUCCESS" in response 