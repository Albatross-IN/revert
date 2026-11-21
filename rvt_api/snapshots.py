"""One way to answer a snapshot: nothing at all when it has not changed since the caller's copy,
and compressed when it has. A snapshot is the largest answer of the API and is asked again after
every operation, so this is what makes the app light on a slow connection."""
import gzip
import hashlib
import json

from fastapi import Response

MIN_TO_COMPRESS = 1400      # below one network packet there is nothing to gain


def _tags(header):
    """The validators of an If-None-Match header; a proxy that compresses turns "x" into W/"x"."""
    return {tag.strip().removeprefix("W/") for tag in (header or "").split(",") if tag.strip()}


def snapshot_response(data, if_none_match=None, accept_encoding=None):
    body = json.dumps(data, separators=(",", ":"), ensure_ascii=False).encode()
    etag = '"%s"' % hashlib.sha1(body).hexdigest()
    headers = {"ETag": etag, "Vary": "Accept-Encoding", "Cache-Control": "no-store"}
    if etag in _tags(if_none_match):
        return Response(status_code=304, headers=headers)
    if "gzip" in (accept_encoding or "").lower() and len(body) >= MIN_TO_COMPRESS:
        body = gzip.compress(body, compresslevel=6)
        headers["Content-Encoding"] = "gzip"
    return Response(content=body, media_type="application/json", headers=headers)
