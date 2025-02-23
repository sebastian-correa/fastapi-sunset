"""SunsetConfigutaion model."""

from __future__ import annotations

import logging
from datetime import (
    timedelta,  # noqa: TC003; pydantic needs this outside TYPE_CHECKING block to define the model
)
from typing import TYPE_CHECKING

from pydantic import AwareDatetime, BaseModel

from fastapi_sunset.behaviors import (
    BasePeriodBehavior,  # noqa: TC001; pydantic needs this outside TYPE_CHECKING block to define the model
)

if TYPE_CHECKING:
    from datetime import datetime

logger = logging.getLogger(__name__)


class SunsetConfiguration(BaseModel):
    """Endpoint sunset configuration.

    The timeline around `sunset_on` is divided into 4 periods:
        - **Upcoming sunset:** The period before the pre-sunset grace period. The
            `upcoming_sunset_behavior` is assumed during this period.
        - **Pre-sunset grace period:** The period before `sunset_on` but after the given offset. The
            `pre_sunset_grace_period_behavior` is assumed during this period.
        - **Post-sunset grace period:** The period after `sunset_on` but before the given offset.
            The `post_sunset_grace_period_behavior` is assumed during this period.
        - **Sunset period:** The period after the post-sunset grace period. The
            `sunset_period_behavior` is assumed during this period.

    This is better understood with the following diagram:
    ```
        Upcoming           Pre-sunset                           Post-sunset                   Sunset
        sunset            grace period                          grace period                  period
    ............│←──pre_sunset_grace_period_length──→│←──post_sunset_grace_period_length──→│........
                │                                    │                                     │
                │                                sunset_on                                 │
                │                                    ▼                                     │
    ◀───────────┘                                    │                                     └───────▶
    ```

    Consult `self.find_period_behavior` for more.
    """

    sunset_on: AwareDatetime
    """When the endpoint will be deprecated.

    Timezone aware datetimes are mandated to avoid ambiguity, since naive datetimes will be treated
    as local time which might differ from server to server.
    """
    alternative_url: str | None = None
    """URL to the new endpoint or documentation."""

    upcoming_sunset_behavior: BasePeriodBehavior
    """Behavior to take before the pre-sunset grace period."""

    pre_sunset_grace_period_length: timedelta
    """How long before `sunset_on` to assume the `pre_sunset_grace_period_behavior`.

    To disable this period, set to `timedelta(0)`.
    """
    pre_sunset_grace_period_behavior: BasePeriodBehavior
    """Behavior to take during the pre-sunset grace period."""
    post_sunset_grace_period_length: timedelta
    """How long after `sunset_on` to assume the `post_sunset_grace_period_behavior`.

    To disable this period, set to `timedelta(0)`.
    """
    post_sunset_grace_period_behavior: BasePeriodBehavior
    """Behavior to take during the post-sunset grace period."""
    sunset_period_behavior: BasePeriodBehavior
    """Behavior to take after the post-sunset grace period ends."""

    def find_period_behavior(self, as_of: datetime) -> BasePeriodBehavior:
        """Find the behavior we should assume for this moment in time.

        Note that intervals are treated as half open (left inclusive and right exclusive) to
        maintain consistency with Python intervals.

        Args:
            as_of (datetime): The moment in time to classify

        Returns:
            BasePeriodBehavior: The behavior to take in the period.
        """
        if as_of < (self.sunset_on - self.pre_sunset_grace_period_length):
            logger.debug(f"Identified {as_of} as in upcoming sunset period.")
            return self.upcoming_sunset_behavior
        if as_of < self.sunset_on:
            logger.debug(f"Identified {as_of} as in the pre sunset grace period.")
            return self.pre_sunset_grace_period_behavior
        if as_of < (self.sunset_on + self.post_sunset_grace_period_length):
            logger.debug(f"Identified {as_of} as in the post sunset grace period.")
            return self.post_sunset_grace_period_behavior
        logger.debug(f"Identified {as_of} as in the sunset period.")
        return self.sunset_period_behavior
