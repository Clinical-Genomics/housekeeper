"""Tests for date parsing module"""
import datetime

import pytest

from housekeeper.date import get_date, match_date


def test_match_date_dash():
    """Test to match common string formated date"""
    # GIVEN a datestring separated by '-'
    date_str = "2015-05-10"
    # WHEN checking if it is a valid datestring
    res = match_date(date_str)
    # THEN assert the result is True
    assert res is True


def test_match_date_dot():
    """Test to match common string formated date"""
    # GIVEN a datestring separated by '.'
    date_str = "2015.05.10"
    # WHEN checking if it is a valid datestring
    res = match_date(date_str)
    # THEN assert the result is True
    assert res is True


def test_match_invalid_date():
    """Test to match a bad formated date string"""
    # GIVEN a datestring without separators
    date_str = "20150510"
    # WHEN checking if it is a valid datestring
    res = match_date(date_str)
    # THEN assert the result is False
    assert res is False


def test_match_non_date():
    """Test to match non date string"""
    # GIVEN a datestring not even similar to a date
    date_str = "hello"
    # WHEN checking if it is a valid datestring
    res = match_date(date_str)
    # THEN assert the result is False
    assert res is False


def test_valid_date_str():
    """Test to get a date object from a valid date string"""
    # GIVEN a datestring separated by '-'
    date_str = "2015-05-10"
    # WHEN converting to a datetime object
    date_obj = get_date(date_str)
    # THEN assert a succesfull conversion
    assert isinstance(date_obj, datetime.datetime)


def test_valid_date_str_no_value():
    """Test get a datetime object when date string has no value"""
    # GIVEN no datestring
    date_str = None
    # WHEN fetching a date object
    date_obj = get_date(date_str)
    # THEN assert a valid date was returned
    assert isinstance(date_obj, datetime.datetime)


def test_datetime_str():
    """Test get a datetime object the string is a datetime str"""
    # GIVEN a datestring directly from datetime
    date = datetime.datetime.now()
    date_str = str(date)

    # WHEN converting the string to a datetime object
    new_date = get_date(date_str)

    # THEN assert the new date is the same as original
    assert new_date == date


def test_datetime_timestamp(timestamp):
    """Test get a datetime object the string is a datetime str"""
    # GIVEN a datestring directly from datetime
    date_str = str(timestamp)

    # WHEN converting the string to a datetime object
    new_date = get_date(date_str)

    # THEN assert the new date is the same as original
    assert new_date == timestamp
