#!/usr/bin/env python3

import argparse
import json
import pathlib
import urllib.request
import urllib.error
import urllib.parse


def _download_json(url: str) -> dict:
    headers = {
        "User-Agent": "pixi-buildfarm/ros-jazzy filter_repodata.py",
        "Accept": "application/json",
    }

    class _NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, hdrs, newurl):  # type: ignore[override]
            return None

    opener = urllib.request.build_opener(_NoRedirect)

    current_url = url
    for _ in range(10):
        req = urllib.request.Request(current_url, headers=headers)
        try:
            with opener.open(req, timeout=60) as resp:
                data = resp.read()
            return json.loads(data.decode("utf-8"))
        except urllib.error.HTTPError as err:
            if err.code in {301, 302, 303, 307, 308}:
                location = err.headers.get("Location")
                if not location:
                    raise
                current_url = urllib.parse.urljoin(current_url, location)
                continue
            raise

    raise RuntimeError(f"Too many redirects while fetching {url}")


def _remove_packages(repodata: dict, remove_names: set[str]) -> dict:
    out = dict(repodata)
    packages = dict(out.get("packages", {}))
    packages_conda = dict(out.get("packages.conda", {}))

    def keep_pkg(meta: dict) -> bool:
        name = meta.get("name")
        return name not in remove_names

    packages = {fn: meta for fn, meta in packages.items() if keep_pkg(meta)}
    packages_conda = {fn: meta for fn, meta in packages_conda.items() if keep_pkg(meta)}

    out["packages"] = packages
    out["packages.conda"] = packages_conda
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Download and filter conda repodata.json")
    parser.add_argument(
        "--url",
        default="https://repo.prefix.dev/robostack-jazzy/linux-64/repodata.json",
        help="Repodata URL to download",
    )
    parser.add_argument(
        "--out",
        help="Output path for filtered repodata.json (writes a single file)",
    )
    parser.add_argument(
        "--out-channel",
        help=(
            "Output channel root directory (writes <out-channel>/<subdir>/repodata.json). "
            "Useful for passing to vinca -s."
        ),
    )
    parser.add_argument(
        "--subdir",
        default="linux-64",
        help="Conda subdir to write under --out-channel (default: linux-64)",
    )
    parser.add_argument(
        "--remove",
        nargs="*",
        default=[],
        help="Package names to remove (repeat or pass a list)",
    )
    args = parser.parse_args()

    if not args.out and not args.out_channel:
        parser.error("One of --out or --out-channel is required")

    repodata = _download_json(args.url)
    filtered = _remove_packages(repodata, set(args.remove))

    filtered_text = json.dumps(filtered, indent=2, sort_keys=True)

    if args.out:
        out_path = pathlib.Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(filtered_text)

    if args.out_channel:
        channel_root = pathlib.Path(args.out_channel)
        repodata_path = channel_root / args.subdir / "repodata.json"
        repodata_path.parent.mkdir(parents=True, exist_ok=True)
        repodata_path.write_text(filtered_text)


if __name__ == "__main__":
    main()
