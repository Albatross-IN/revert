# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).

from unittest.mock import MagicMock, patch

from odoo.tests.common import TransactionCase

from odoo.addons.fastapi import patch as fastapi_patch


class TestPatchSetSessionAndDbname(TransactionCase):
    """Tests for the _patched_set_session_and_dbname patch.

    Odoo 20 port: Request._get_session_and_dbname() became the module
    function odoo.http.router._set_session_and_dbname(request), which
    assigns request.session / request.db itself; the patch and these tests
    follow that shape. The patch resolves the database from a ?db= query
    parameter or a Referer header when Odoo's normal session mechanism
    cannot determine the database (e.g. multi-database staging setups).
    """

    def _make_request(self, db_param="", referer=""):
        mock_request = MagicMock()
        mock_request.httprequest.args = {"db": db_param} if db_param else {}
        mock_request.httprequest.headers = {"Referer": referer} if referer else {}
        mock_request.httprequest.environ = {"HTTP_HOST": "example.com"}
        return mock_request

    def _call_patched(self, mock_request, original_db, db_filter_return):
        def _original(request):
            request.db = original_db

        with (
            patch.object(
                fastapi_patch,
                "_original_set_session_and_dbname",
                side_effect=_original,
            ),
            patch.object(
                fastapi_patch,
                "db_filter",
                return_value=db_filter_return,
            ),
        ):
            fastapi_patch._patched_set_session_and_dbname(mock_request)
        return mock_request

    def test_db_already_resolved(self):
        """When the original function resolves a dbname, the patch must not interfere."""
        request = self._call_patched(
            self._make_request(db_param="otherdb"),
            original_db="existing_db",
            db_filter_return=["existing_db", "otherdb"],
        )
        self.assertEqual(request.db, "existing_db")

    def test_db_from_query_param(self):
        """When dbname is absent, resolve it from the ?db= query parameter."""
        request = self._call_patched(
            self._make_request(db_param="mydb"),
            original_db=None,
            db_filter_return=["mydb"],
        )
        self.assertEqual(request.db, "mydb")
        self.assertEqual(request.session.db, "mydb")

    def test_db_from_referer_header(self):
        """When ?db= is absent, fall back to the db param in the Referer header.

        This covers browser sub-requests (e.g. openapi.json, Swagger UI assets)
        where the Referer points to the docs page carrying ?db=.
        """
        request = self._call_patched(
            self._make_request(referer="https://example.com/docs?db=mydb"),
            original_db=None,
            db_filter_return=["mydb"],
        )
        self.assertEqual(request.db, "mydb")
        self.assertEqual(request.session.db, "mydb")

    def test_db_rejected_by_filter(self):
        """A db name that fails db_filter must not be used."""
        request = self._call_patched(
            self._make_request(db_param="forbidden_db"),
            original_db=None,
            db_filter_return=[],
        )
        self.assertIsNone(request.db)
