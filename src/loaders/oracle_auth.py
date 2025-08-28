from functools import lru_cache
from structlog import get_logger

from oci import config
from oci.retry import RetryStrategyBuilder
from oci.auth.signers import InstancePrincipalsSecurityTokenSigner


class OracleAuthLoader:
    """
    Load Oracle Cloud Infrastructure (OCI) authentication details on startup.
    Designed to be blocked until authentication is complete.
    The bot only can be up and running after authentication is successful.
    """

    retry_strategy = RetryStrategyBuilder().add_max_attempts(1).get_retry_strategy()
    signer_kwargs = {
        'retry_strategy': retry_strategy
    }

    def __init__(self):
        self.logger = get_logger('OracleAuthLoader')
        self.config = self._get_config()
        self.signer = self._get_signer()
        self.kwargs = self._get_kwargs()
        self.tenancy_id = self._get_tenancy_id()

    @lru_cache
    def _get_config(self) -> dict:
        try:
            self.logger.debug("Trying to load OCI config from file...")
            return config.from_file()
        except Exception:
            self.logger.warning("Was not possible to load OCI config!")
            return {}
        
    @lru_cache
    def _get_signer(self) -> InstancePrincipalsSecurityTokenSigner | None:
        try:
            self.logger.debug("Trying to load OCI signer using instance principals...")
            return InstancePrincipalsSecurityTokenSigner(**self.signer_kwargs)
        except Exception:
            self.logger.warning("Was not possible to load OCI signer!")
            return None
        
    @lru_cache
    def _get_kwargs(self) -> dict:
        kwargs = {}
        if self.signer:
            kwargs["signer"] = self.signer
        return kwargs

    @lru_cache
    def _get_tenancy_id(self) -> str:
        self.logger.debug("Trying to load OCI tenancy ID...")
        if self.signer:
            return str(self.signer.tenancy_id)
        if self.config:
            return str(self.config["tenancy"])
        raise ValueError("OCI credential not found!")
