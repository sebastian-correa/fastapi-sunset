from datetime import datetime, timedelta, timezone

import pytest
from fastapi import status
from pydantic import ValidationError

from fastapi_sunset import (
    BasePeriodBehavior,
    DoNothing,
    RespondError,
    SunsetConfiguration,
    WarnDevelopers,
)


class TestSunsetConfiguration:
    """Test the `SunsetConfiguration` class."""

    @pytest.fixture
    def behaviors(self) -> dict[str, BasePeriodBehavior]:
        """Create distinct behavior instances for each period."""
        return {
            "upcoming": BasePeriodBehavior(),
            "pre_grace": BasePeriodBehavior(),
            "post_grace": BasePeriodBehavior(),
            "sunset": BasePeriodBehavior(),
        }

    def test_valid_initialization(self, behaviors: dict[str, BasePeriodBehavior]) -> None:
        """Test that SunsetConfiguration can be initialized with valid parameters."""
        test_config = SunsetConfiguration(
            sunset_on=datetime(2024, 1, 1, 12, tzinfo=timezone.utc),
            alternative_url="https://api.example.com/v2",
            upcoming_sunset_behavior=behaviors["upcoming"],
            pre_sunset_grace_period_length=timedelta(days=7),
            pre_sunset_grace_period_behavior=behaviors["pre_grace"],
            post_sunset_grace_period_length=timedelta(days=7),
            post_sunset_grace_period_behavior=behaviors["post_grace"],
            sunset_period_behavior=behaviors["sunset"],
        )
        assert isinstance(test_config.sunset_on, datetime)
        assert test_config.alternative_url == "https://api.example.com/v2"
        assert isinstance(test_config.upcoming_sunset_behavior, BasePeriodBehavior)
        assert isinstance(test_config.pre_sunset_grace_period_behavior, BasePeriodBehavior)
        assert isinstance(test_config.post_sunset_grace_period_behavior, BasePeriodBehavior)
        assert isinstance(test_config.sunset_period_behavior, BasePeriodBehavior)

    def test_find_period_behavior_with_both_grace_periods(
        self, behaviors: dict[str, BasePeriodBehavior]
    ) -> None:
        """Test period behavior identification at period boundaries."""
        test_config = SunsetConfiguration(
            sunset_on=datetime(2024, 1, 1, 12, tzinfo=timezone.utc),
            alternative_url="https://api.example.com/v2",
            upcoming_sunset_behavior=behaviors["upcoming"],
            pre_sunset_grace_period_length=timedelta(days=7),
            pre_sunset_grace_period_behavior=behaviors["pre_grace"],
            post_sunset_grace_period_length=timedelta(days=7),
            post_sunset_grace_period_behavior=behaviors["post_grace"],
            sunset_period_behavior=behaviors["sunset"],
        )

        # Test around pre-sunset grace period start.
        pre_grace_period_start = test_config.sunset_on - test_config.pre_sunset_grace_period_length
        dt = timedelta(microseconds=1)
        assert (
            test_config.find_period_behavior(pre_grace_period_start - dt)
            is test_config.upcoming_sunset_behavior
        )
        assert (
            test_config.find_period_behavior(pre_grace_period_start)
            is test_config.pre_sunset_grace_period_behavior
        )
        assert (
            test_config.find_period_behavior(pre_grace_period_start + dt)
            is test_config.pre_sunset_grace_period_behavior
        )

        # Test around sunset time
        assert (
            test_config.find_period_behavior(test_config.sunset_on - dt)
            is test_config.pre_sunset_grace_period_behavior
        )
        assert (
            test_config.find_period_behavior(test_config.sunset_on)
            is test_config.post_sunset_grace_period_behavior
        )
        assert (
            test_config.find_period_behavior(test_config.sunset_on + dt)
            is test_config.post_sunset_grace_period_behavior
        )

        # Test around post-sunset grace period end
        post_grace_period_end = test_config.sunset_on + test_config.post_sunset_grace_period_length
        assert (
            test_config.find_period_behavior(post_grace_period_end - dt)
            is test_config.post_sunset_grace_period_behavior
        )
        assert (
            test_config.find_period_behavior(post_grace_period_end)
            is test_config.sunset_period_behavior
        )
        assert (
            test_config.find_period_behavior(post_grace_period_end + dt)
            is test_config.sunset_period_behavior
        )

    def test_find_period_behavior_without_pre_grace_periods(
        self, behaviors: dict[str, BasePeriodBehavior]
    ) -> None:
        """Test period behavior identification at period boundaries."""
        test_config = SunsetConfiguration(
            sunset_on=datetime(2024, 1, 1, 12, tzinfo=timezone.utc),
            alternative_url="https://api.example.com/v2",
            upcoming_sunset_behavior=behaviors["upcoming"],
            pre_sunset_grace_period_length=timedelta(days=0),
            pre_sunset_grace_period_behavior=behaviors["pre_grace"],
            post_sunset_grace_period_length=timedelta(days=7),
            post_sunset_grace_period_behavior=behaviors["post_grace"],
            sunset_period_behavior=behaviors["sunset"],
        )

        dt = timedelta(microseconds=1)

        # Test around sunset time
        assert (
            test_config.find_period_behavior(test_config.sunset_on - dt)
            is test_config.upcoming_sunset_behavior
        )
        assert (
            test_config.find_period_behavior(test_config.sunset_on)
            is test_config.post_sunset_grace_period_behavior
        )
        assert (
            test_config.find_period_behavior(test_config.sunset_on + dt)
            is test_config.post_sunset_grace_period_behavior
        )

        # Test around post-sunset grace period end
        post_grace_period_end = test_config.sunset_on + test_config.post_sunset_grace_period_length
        assert (
            test_config.find_period_behavior(post_grace_period_end - dt)
            is test_config.post_sunset_grace_period_behavior
        )
        assert (
            test_config.find_period_behavior(post_grace_period_end)
            is test_config.sunset_period_behavior
        )
        assert (
            test_config.find_period_behavior(post_grace_period_end + dt)
            is test_config.sunset_period_behavior
        )

    def test_find_period_behavior_without_post_grace_periods(
        self, behaviors: dict[str, BasePeriodBehavior]
    ) -> None:
        """Test period behavior identification at period boundaries."""
        test_config = SunsetConfiguration(
            sunset_on=datetime(2024, 1, 1, 12, tzinfo=timezone.utc),
            alternative_url="https://api.example.com/v2",
            upcoming_sunset_behavior=behaviors["upcoming"],
            pre_sunset_grace_period_length=timedelta(days=7),
            pre_sunset_grace_period_behavior=behaviors["pre_grace"],
            post_sunset_grace_period_length=timedelta(days=0),
            post_sunset_grace_period_behavior=behaviors["post_grace"],
            sunset_period_behavior=behaviors["sunset"],
        )

        # Test around pre-sunset grace period start.
        pre_grace_period_start = test_config.sunset_on - test_config.pre_sunset_grace_period_length
        dt = timedelta(microseconds=1)
        assert (
            test_config.find_period_behavior(pre_grace_period_start - dt)
            is test_config.upcoming_sunset_behavior
        )
        assert (
            test_config.find_period_behavior(pre_grace_period_start)
            is test_config.pre_sunset_grace_period_behavior
        )
        assert (
            test_config.find_period_behavior(pre_grace_period_start + dt)
            is test_config.pre_sunset_grace_period_behavior
        )

        # Test around sunset time
        assert (
            test_config.find_period_behavior(test_config.sunset_on - dt)
            is test_config.pre_sunset_grace_period_behavior
        )
        assert (
            test_config.find_period_behavior(test_config.sunset_on)
            is test_config.sunset_period_behavior
        )
        assert (
            test_config.find_period_behavior(test_config.sunset_on + dt)
            is test_config.sunset_period_behavior
        )

    def test_find_period_behavior_without_pre_and_post_grace_periods(
        self, behaviors: dict[str, BasePeriodBehavior]
    ) -> None:
        """Test period behavior identification at period boundaries."""
        test_config = SunsetConfiguration(
            sunset_on=datetime(2024, 1, 1, 12, tzinfo=timezone.utc),
            alternative_url="https://api.example.com/v2",
            upcoming_sunset_behavior=behaviors["upcoming"],
            pre_sunset_grace_period_length=timedelta(days=0),
            pre_sunset_grace_period_behavior=behaviors["pre_grace"],
            post_sunset_grace_period_length=timedelta(days=0),
            post_sunset_grace_period_behavior=behaviors["post_grace"],
            sunset_period_behavior=behaviors["sunset"],
        )

        dt = timedelta(microseconds=1)

        # Test around sunset time
        assert (
            test_config.find_period_behavior(test_config.sunset_on - dt)
            is test_config.upcoming_sunset_behavior
        )
        assert (
            test_config.find_period_behavior(test_config.sunset_on)
            is test_config.sunset_period_behavior
        )
        assert (
            test_config.find_period_behavior(test_config.sunset_on + dt)
            is test_config.sunset_period_behavior
        )

    def test_alternative_url_optional(self, behaviors: dict[str, BasePeriodBehavior]) -> None:
        """Test that alternative_url is optional."""
        config = SunsetConfiguration(
            sunset_on=datetime(2024, 1, 1, 12, tzinfo=timezone.utc),
            upcoming_sunset_behavior=behaviors["upcoming"],
            pre_sunset_grace_period_length=timedelta(days=7),
            pre_sunset_grace_period_behavior=behaviors["pre_grace"],
            post_sunset_grace_period_length=timedelta(days=7),
            post_sunset_grace_period_behavior=behaviors["post_grace"],
            sunset_period_behavior=behaviors["sunset"],
        )
        assert config.alternative_url is None

    def test_naive_datetime_raises_error(self, behaviors: dict[str, BasePeriodBehavior]) -> None:
        """Test that using naive datetime raises ValidationError."""
        with pytest.raises(ValidationError):
            SunsetConfiguration(
                sunset_on=datetime(2024, 1, 1, 12),  # noqa: DTZ001; naive datetime necessary for the test.
                alternative_url="https://api.example.com/v2",
                upcoming_sunset_behavior=behaviors["upcoming"],
                pre_sunset_grace_period_length=timedelta(days=7),
                pre_sunset_grace_period_behavior=behaviors["pre_grace"],
                post_sunset_grace_period_length=timedelta(days=7),
                post_sunset_grace_period_behavior=behaviors["post_grace"],
                sunset_period_behavior=behaviors["sunset"],
            )

    def test_sunset_configuration_defaults(self) -> None:
        """Test that SunsetConfiguration default values."""
        sunset_configuration = SunsetConfiguration(
            sunset_on=datetime(2024, 1, 1, 12, tzinfo=timezone.utc)
        )

        assert sunset_configuration.alternative_url is None
        assert isinstance(sunset_configuration.upcoming_sunset_behavior, DoNothing)
        assert sunset_configuration.upcoming_sunset_behavior.include_headers

        assert sunset_configuration.pre_sunset_grace_period_length == timedelta(14)
        behavior = sunset_configuration.pre_sunset_grace_period_behavior
        assert isinstance(behavior, WarnDevelopers)
        assert behavior.include_headers
        assert behavior.category is DeprecationWarning

        assert sunset_configuration.post_sunset_grace_period_length == timedelta(14)
        behavior = sunset_configuration.post_sunset_grace_period_behavior
        assert isinstance(behavior, WarnDevelopers)
        assert behavior.include_headers
        assert behavior.category is DeprecationWarning

        behavior = sunset_configuration.sunset_period_behavior
        assert isinstance(behavior, RespondError)
        assert behavior.include_headers
        assert behavior.error_code == status.HTTP_410_GONE
