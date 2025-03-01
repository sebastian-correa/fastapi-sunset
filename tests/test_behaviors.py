import json
import warnings
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from fastapi import status
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel

from fastapi_sunset import SunsetConfiguration
from fastapi_sunset.behaviors import (
    BasePeriodBehavior,
    DoNothing,
    RedirectUsers,
    RespondError,
    WarnDevelopers,
)


class TestBehaviorBase:
    """Base class for testing behaviors."""

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
            upcoming_sunset_behavior=behavior,
            pre_sunset_grace_period_behavior=behavior,
            pre_sunset_grace_period_length=timedelta(days=7),
            post_sunset_grace_period_behavior=behavior,
            post_sunset_grace_period_length=timedelta(days=7),
            sunset_period_behavior=behavior,
        )


class TestBasePeriodBehavior(TestBehaviorBase):
    """Test the `BasePeriodBehavior` class."""

    def test_base_behavior_initialization(self) -> None:
        """Test that BasePeriodBehavior can be initialized."""
        behavior = BasePeriodBehavior()
        assert isinstance(behavior, BaseModel)
        assert behavior.include_headers is True

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


class TestDoNothingBehavior(TestBehaviorBase):
    """Test the `DoNothing` class."""

    @pytest.fixture
    def behavior(self) -> DoNothing:
        """Return a `DoNothing` instance for testing."""
        return DoNothing()

    def test_base_behavior_initialization(self) -> None:
        """Test that BasePeriodBehavior can be initialized."""
        behavior = BasePeriodBehavior()
        assert isinstance(behavior, BaseModel)
        assert behavior.include_headers is True

    def test_inheritance(self, behavior: DoNothing) -> None:
        """Test that DoNothing inherits from BasePeriodBehavior."""
        assert isinstance(behavior, BasePeriodBehavior)

    def test_behave_with_does_nothing(
        self, behavior: DoNothing, sunset_config: SunsetConfiguration
    ) -> None:
        """Test that behave_with method doesn't alter anything."""
        initial_config = sunset_config.model_dump()

        with warnings.catch_warnings():
            warnings.simplefilter("error")
            outcome = behavior.behave_with(sunset_config)

        final_config = sunset_config.model_dump()
        assert initial_config == final_config
        assert outcome is None


class TestRedirectUsers(TestBehaviorBase):
    """Test the `RedirectUsers` class."""

    @pytest.fixture
    def redirect_url(self) -> str:
        """Provide a test URL."""
        return "https://api.example.com/v2"

    @pytest.fixture
    def behavior(self, redirect_url: str) -> RedirectUsers:
        """Create a RedirectUsers instance for testing."""
        return RedirectUsers(url=redirect_url)

    def test_initialization(self, behavior: RedirectUsers, redirect_url: str) -> None:
        """Test that RedirectUsers initializes correctly."""
        assert isinstance(behavior, RedirectUsers)
        assert issubclass(RedirectUsers, BasePeriodBehavior)
        assert behavior.url == redirect_url

    def test_behave_with_returns_redirect(
        self,
        behavior: RedirectUsers,
        sunset_config: SunsetConfiguration,
        redirect_url: str,
    ) -> None:
        """Test that behave_with returns correct RedirectResponse."""
        response = behavior.behave_with(sunset_config)
        assert isinstance(response, RedirectResponse)
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        assert response.headers["location"] == redirect_url


class TestRespondError(TestBehaviorBase):
    """Test the `RespondError` class."""

    @pytest.fixture
    def behavior(self) -> RespondError:
        """Return a RespondError instance for testing."""
        return RespondError(message="Test message")

    def test_respond_error_initialization(self) -> None:
        """Test RespondError can be initialized with custom message and error code."""
        behavior = RespondError(message="Custom message", error_code=status.HTTP_418_IM_A_TEAPOT)
        assert behavior.message == "Custom message"
        assert behavior.error_code == status.HTTP_418_IM_A_TEAPOT

    def test_respond_error_default_error_code(self, behavior: RespondError) -> None:
        """Test RespondError uses HTTP 410 Gone as default error code."""
        assert behavior.error_code == status.HTTP_410_GONE

    def test_behave_with_response_structure(
        self, behavior: RespondError, sunset_config: SunsetConfiguration
    ) -> None:
        """Test behave_with returns properly structured JSONResponse."""
        response = behavior.behave_with(sunset_config)

        assert isinstance(response, JSONResponse)
        assert isinstance(response.body, bytes)

        body = json.loads(response.body)
        assert body["detail"] == "Test message"

    def test_behave_with_status_code(self, sunset_config: SunsetConfiguration) -> None:
        """Test behave_with returns correct status code."""
        behavior = RespondError(message="Test message", error_code=status.HTTP_418_IM_A_TEAPOT)
        response = behavior.behave_with(sunset_config)
        assert response.status_code == status.HTTP_418_IM_A_TEAPOT

    def test_message_formatting_with_sunset_date(self, sunset_config: SunsetConfiguration) -> None:
        """Test message formatting includes sunset date."""
        behavior = RespondError(message="API sunsets on {sunset_on}")
        response = behavior.behave_with(sunset_config)

        body = json.loads(response.body)
        assert "2024-01-01" in body["detail"]

    def test_message_formatting_with_alternative_url(
        self, sunset_config: SunsetConfiguration
    ) -> None:
        """Test message formatting includes alternative URL."""
        behavior = RespondError(message="Please use {alternative_url}")
        response = behavior.behave_with(sunset_config)

        body = json.loads(response.body)
        assert "https://api.example.com/v2" in body["detail"]


class TestWarnDevelopers(TestBehaviorBase):
    """Test the `WarnDevelopers` class."""

    @pytest.fixture
    def behavior(self) -> WarnDevelopers:
        """Return a WarnDevelopers instance for testing."""
        return WarnDevelopers(
            message="API will sunset on {sunset_on}. Use {alternative_url} instead."
        )

    def test_warning_message_formatting(
        self, behavior: WarnDevelopers, sunset_config: SunsetConfiguration
    ) -> None:
        """Test that the warning message is correctly formatted."""
        with pytest.warns(FutureWarning) as warning_info:
            behavior.behave_with(sunset_config)

        expected_message = (
            "API will sunset on 2024-01-01 12:00:00+00:00. Use https://api.example.com/v2 instead."
        )
        assert str(warning_info[0].message) == expected_message

    def test_warning_without_alternative_url(
        self, behavior: WarnDevelopers, sunset_config: SunsetConfiguration
    ) -> None:
        """Test warning formatting when alternative_url is None."""
        sunset_config.alternative_url = None
        with pytest.warns(FutureWarning) as warning_info:
            behavior.behave_with(sunset_config)

        expected_message = "API will sunset on 2024-01-01 12:00:00+00:00. Use None instead."
        assert str(warning_info[0].message) == expected_message

    def test_custom_warning_category(self, sunset_config: SunsetConfiguration) -> None:
        """Test that custom warning category is respected."""
        behavior = WarnDevelopers(message="Test message", category=DeprecationWarning)

        with pytest.warns(DeprecationWarning):
            behavior.behave_with(sunset_config)

    def test_warning_stacklevel(
        self, behavior: WarnDevelopers, sunset_config: SunsetConfiguration
    ) -> None:
        """Test that warning is emitted with correct stacklevel."""
        with patch("warnings.warn") as mock_warn:
            behavior.behave_with(sunset_config)

        mock_warn.assert_called_once()
        assert mock_warn.call_args[1]["stacklevel"] == 2  # noqa: PLR2004; it's just level 2.

    def test_default_warning_category(self, behavior: WarnDevelopers) -> None:
        """Test that default warning category is FutureWarning."""
        assert issubclass(behavior.category, FutureWarning)
