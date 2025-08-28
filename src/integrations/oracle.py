import asyncio

from functools import cached_property

from oci import Response
from oci.core import ComputeClient
from oci.usage_api import UsageapiClient
from oci.usage_api.models import RequestSummarizedUsagesDetails, Filter, Dimension

from src.loaders.oracle_auth import OracleAuthLoader
from src.utils.datetime import (
    get_current_month,
    get_current_month_end_datetime,
    get_current_month_start_datetime
)


class OracleIntegration:

    def __init__(
        self,
        machine_id: str,
        auth: OracleAuthLoader
    ):
        self.machine_id = machine_id
        self.auth = auth

    @cached_property
    def _compute_client(self):
        return ComputeClient(self.auth.config, **self.auth.kwargs)

    @cached_property
    def _usage_client(self):
        return UsageapiClient(self.auth.config, **self.auth.kwargs)

    @cached_property
    def usage_payload(self):
        return RequestSummarizedUsagesDetails(
            tenant_id=self.auth.tenancy_id,
            granularity="MONTHLY",
            query_type="COST",
            time_usage_ended=get_current_month_end_datetime(),
            time_usage_started=get_current_month_start_datetime(),
            filter=Filter(
                operator="AND",
                dimensions=[
                    Dimension(
                        key="resourceId",
                        value=self.machine_id
                    )
                ]
            )
        )

    async def is_machine_running(self) -> bool:
        response = await asyncio.to_thread(self._compute_client.get_instance, self.machine_id)
        if isinstance(response, Response):
            return response.data.lifecycle_state == "RUNNING"
        return False
    
    async def start_machine(self):
        await asyncio.to_thread(self._compute_client.instance_action, self.machine_id, "START")

    async def stop_machine(self):
        await asyncio.to_thread(self._compute_client.instance_action, self.machine_id, "SOFTSTOP")

    async def current_cost(self) -> tuple[float, str, str]:
        response = await asyncio.to_thread(self._usage_client.request_summarized_usages, self.usage_payload)
        if isinstance(response, Response):
            item = response.data.items[0]
            return item.computed_amount, item.currency, get_current_month()
        return 0.0, "BRL", get_current_month()
