from datetime import datetime, timedelta, timezone

import pytest
from pydantic import BaseModel

from fastapi_sunset import SunsetConfiguration
from fastapi_sunset.behaviors import BasePeriodBehavior


class TestBasePeriodBehavior:
    """Test the `BasePeriodBehavior` class."""

    @pytest.fixture
    def behavior(self) -> BasePeriodBehavior:
        """Default implementation returning a BasePeriodBehavior.

        This should return an as-default-as-possible behavior.
        """
        return BasePeriodBehavior()

    @pytest.fixture
    def sunset_config(self, behavior: BasePeriodBehavior) -> SunsetConfiguration:
        """Create a basic sunset configuration."""
        return SunsetConfiguration(
            sunset_on=datetime(2024, 1, 1, 12, tzinfo=timezone.utc),
            alternative_url="https://api.example.com/v2",
            upcoming_sunset_behavior=BasePeriodBehavior(),
            pre_sunset_grace_period_length=timedelta(days=7),
            pre_sunset_grace_period_behavior=BasePeriodBehavior(),
            post_sunset_grace_period_length=timedelta(days=7),
            post_sunset_grace_period_behavior=BasePeriodBehavior(),
            sunset_period_behavior=BasePeriodBehavior(),
        )

    def test_base_behavior_initialization(self) -> None:
        """Test that BasePeriodBehavior can be initialized."""
        behavior = BasePeriodBehavior()
        assert isinstance(behavior, BaseModel)
        assert behavior.include_headres is True

    def test_format_message_without_message_attribute(
        self, sunset_config: SunsetConfiguration
    ) -> None:
        """Test format_message returns empty string when no message attribute exists."""
        behavior = BasePeriodBehavior()
        result = behavior.format_message(sunset_config)
        assert result == ""

    def test_format_message_with_message_attribute(
        self, sunset_config: SunsetConfiguration
    ) -> None:
        """Test format_message formats the message correctly when message attribute exists."""

        class CustomBehavior(BasePeriodBehavior):
            message: str = "API will sunset on {sunset_on}. Please use {alternative_url}"

        behavior = CustomBehavior()
        result = behavior.format_message(sunset_config)
        assert (
            result
            == "API will sunset on 2024-01-01 12:00:00+00:00. Please use https://api.example.com/v2"
        )

    def test_format_message_with_extra_message_attribute(
        self, sunset_config: SunsetConfiguration
    ) -> None:
        """Test format_message formats the message correctly when message attribute exists."""

        class CustomBehavior(BasePeriodBehavior):
            message: str = "Here is an {incompatible} placeholder."

        behavior = CustomBehavior()
        with pytest.raises(RuntimeError) as exc_info:
            behavior.format_message(sunset_config)

        assert str(exc_info.value).startswith(
            "Only `sunset_on` and `alternative_url` are supported as `message` format parameters."
        )

    def test_behave_with_raises_not_implemented(self, sunset_config: SunsetConfiguration) -> None:
        """Test that behave_with raises NotImplementedError."""
        behavior = BasePeriodBehavior()
        with pytest.raises(NotImplementedError) as exc_info:
            behavior.behave_with(sunset_config)

        assert str(exc_info.value) == (
            "You should implement different behaviors in subclasses of BasePeriodBehavior."
        )
