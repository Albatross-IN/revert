import os

from odoo import fields, http
from odoo.http import request
from odoo.http.stream import content_disposition
from odoo.modules import get_module_path
from odoo.tools.mimetypes import guess_mimetype

from odoo.addons.rvt_base.photos import sized
from odoo.addons.rvt_project.models.rvt_picture import MONTHS, WEEKDAYS
from odoo.addons.web.controllers.home import Home

DESK_URL = "/rvt/desk"
# the order matters: plain scripts that share one scope, as in the approved preview
DESK_SCRIPTS = ["logo.js", "data.js", "core.js", "draw.js", "blocks.js", "sheets.js", "desk.js", "apps.js", "shell.js", "live.js"]


def _stamp():
    """A cache key that changes whenever a desk file changes."""
    folder = _folder()
    try:
        return str(int(max(os.path.getmtime(os.path.join(folder, f)) for f in os.listdir(folder))))
    except (OSError, ValueError):
        return "0"


def _folder():
    return os.path.join(get_module_path("rvt_desk"), "static", "src", "desk")


def _is_staff(user):
    return user.has_group("rvt_base.group_rvt_staff") or user.has_group("base.group_system")


class RvtDeskController(http.Controller):

    @http.route(DESK_URL, type="http", auth="user")
    def desk(self, **kw):
        if not _is_staff(request.env.user):
            return request.redirect("/web")
        response = request.render("rvt_desk.desk_page", {"stamp": _stamp()})
        response.headers["Cache-Control"] = "no-store"
        return response

    @http.route(DESK_URL + "/app.js", type="http", auth="user")
    def desk_script(self, **kw):
        """The screen code as one script, in one scope, exactly as the approved preview is built."""
        folder = _folder()
        parts = []
        for name in DESK_SCRIPTS:
            with open(os.path.join(folder, name), encoding="utf-8") as handle:
                parts.append(handle.read())
        body = '(function(){"use strict";\n%s\nliveBoot();})();\n' % "\n".join(parts)
        return request.make_response(body, headers=[
            ("Content-Type", "application/javascript; charset=utf-8"),
            ("Cache-Control", "private, max-age=31536000, immutable"),
        ])


    @http.route(DESK_URL + "/revision/<int:revision_id>/pdf", type="http", auth="user")
    def desk_revision_pdf(self, revision_id, **kw):
        """A revision's PDF for staff: read with the person's own rights."""
        if not _is_staff(request.env.user):
            return request.not_found()
        revision = request.env["rvt.drawing.revision"].browse(revision_id).exists()
        try:
            revision.check_access("read")
        except Exception:  # noqa: BLE001  (a missing or foreign revision is simply not found)
            return request.not_found()
        if not revision or not revision.file:
            return request.not_found()
        name = revision.file_name or "%s.pdf" % revision.display_name
        return request.make_response(revision.file.content, headers=[
            ("Content-Type", "application/pdf"),
            ("Content-Disposition", content_disposition(name, "inline")),
            ("Cache-Control", "private, max-age=300"),
        ])


    @http.route(DESK_URL + "/mom/pdf", type="http", auth="user")
    def desk_mom_pdf(self, kind="mom", a="", b="all", **kw):
        """The MOM of a visit (whole, or one party's points) or the open points of a project."""
        env = request.env
        if not _is_staff(env.user):
            return request.not_found()
        number = lambda ref: int("".join(ch for ch in str(ref) if ch.isdigit()) or 0)
        try:
            if kind == "points":
                # the points of a project: one visit or all (v), one party or all (b), open or all (st)
                project = env["project.project"].browse(number(a)).exists()
                name, pdf = project.rvt_points_pdf(
                    visit_id=number(kw.get("v")) or None, party=project._rvt_party_of(b), state=kw.get("st") or "open")
            elif kind == "open":
                project = env["project.project"].browse(number(a)).exists()
                project.check_access("read")
                pdf = env["ir.actions.report"].sudo()._render_qweb_pdf("rvt_mom.action_report_open_points", project.ids)[0]
                name = "Open points - %s.pdf" % project.name
            else:
                visit = env["rvt.visit"].browse(number(a)).exists()
                party = False
                if b in ("all", ""):
                    pass
                elif b.startswith("v:"):
                    party = {"kind": "vendor", "name": b[2:]}
                elif b == "client":
                    party = {"kind": "client"}
                elif b.startswith("a"):
                    party = {"kind": "agency", "partner_id": number(b)}
                elif b.startswith("s"):
                    party = {"kind": "staff", "user_id": number(b)}
                pdf = visit.rvt_pdf(party)
                name = "MOM - %s - visit %s.pdf" % (visit.project_id.name, visit.number)
        except Exception:  # noqa: BLE001  (no access or nothing there: not found)
            return request.not_found()
        return request.make_response(pdf, headers=[
            ("Content-Type", "application/pdf"),
            ("Content-Disposition", content_disposition(name, "inline")),
            ("Cache-Control", "private, no-store"),
        ])

    @http.route(DESK_URL + "/question/<int:question_id>/photo", type="http", auth="user")
    def desk_question_photo(self, question_id, size=None, **kw):
        """The photo an agency sent with its question on a drawing."""
        if not _is_staff(request.env.user):
            return request.not_found()
        question = request.env["rvt.drawing.question"].browse(question_id).exists()
        try:
            question.check_access("read")
        except Exception:  # noqa: BLE001
            return request.not_found()
        if not question or not question.photo:
            return request.not_found()
        content = sized(question.photo.content, size)
        return request.make_response(content, headers=[
            ("Content-Type", guess_mimetype(content, default="image/jpeg")),
            ("Cache-Control", "private, max-age=3600"),
        ])

    @http.route(DESK_URL + "/point/<int:point_id>/photo", type="http", auth="user")
    def desk_point_photo(self, point_id, close=None, size=None, **kw):
        if not _is_staff(request.env.user):
            return request.not_found()
        point = request.env["rvt.point"].browse(point_id).exists()
        try:
            point.check_access("read")
        except Exception:  # noqa: BLE001
            return request.not_found()
        value = point.close_photo if close else point.photo
        if not point or not value:
            return request.not_found()
        content = sized(value.content, size)
        return request.make_response(content, headers=[
            ("Content-Type", guess_mimetype(content, default="image/jpeg")),
            ("Cache-Control", "private, max-age=3600"),
        ])


class RvtHome(Home):

    @http.route()
    def web_login(self, redirect=None, **kw):
        """The standard log-in in every respect, shown as the desk's own page. The system parameter
        ``rvt.desk_login`` (on unless set to False) switches it off: everybody then gets the standard
        page, as on a live database where the office has not moved to the desk yet."""
        response = super().web_login(redirect=redirect, **kw)
        own = request.env["ir.config_parameter"].sudo().get_bool("rvt.desk_login", True)
        if own and getattr(response, "is_qweb", False) and response.template == "web.login" and not kw.get("classic"):
            today = request.env["rvt.config"].today()
            response.qcontext.update({
                "stamp": _stamp(), "redirect": redirect or False,
                "today_label": "%s %s %s" % (WEEKDAYS[today.weekday()], today.day, MONTHS[today.month - 1]),
            })
            response.template = "rvt_desk.login_page"
        return response

    def _login_redirect(self, uid, redirect=None):
        """Staff land on the desk after logging in; administrators land where they always did."""
        if not redirect:
            user = request.env["res.users"].sudo().browse(uid)
            if user.has_group("rvt_base.group_rvt_staff") and not user.has_group("base.group_system"):
                return DESK_URL
        return super()._login_redirect(uid, redirect=redirect)
