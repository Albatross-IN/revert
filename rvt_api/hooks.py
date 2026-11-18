import logging
import secrets

_logger = logging.getLogger(__name__)
PARAM_SECRET = "rvt_api.jwt_secret"


def post_init_hook(env):
    params = env["ir.config_parameter"].sudo()
    if not params.get_str(PARAM_SECRET):
        # one secret per database; changing it signs every device out at once
        params.set_str(PARAM_SECRET, secrets.token_urlsafe(64))
        _logger.info("rvt_api: signing secret created")
    endpoint = env.ref("rvt_api.fastapi_endpoint_rvt", raise_if_not_found=False)
    if endpoint:
        # the routes are mounted when the record is synced, not when it is created
        endpoint.action_sync_registry()
