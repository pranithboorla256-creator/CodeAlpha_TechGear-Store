"""Cache the original online catalog images as local static files."""
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from .seed_store import IMAGES

MIME_EXTENSIONS = {
    "image/jpeg": ".jpg", "image/jpg": ".jpg", "image/png": ".png", "image/webp": ".webp",
    "image/gif": ".gif", "image/avif": ".avif", "image/svg+xml": ".svg",
}

class Command(BaseCommand):
    help = "Cache original product images from their online product listings."

    def handle(self, *args, **options):
        output_dir = settings.BASE_DIR / "static" / "products"
        output_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = output_dir / "manifest.json"
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            manifest = {}
        failures = []
        for name, source in IMAGES.items():
            previous_path = manifest.get(name, "")
            if previous_path and (settings.BASE_DIR / previous_path.lstrip("/")).is_file():
                continue
            try:
                request = Request(source, headers={
                    "User-Agent": "Mozilla/5.0 (compatible; TechGearStore/1.0)",
                    "Accept": "image/avif,image/webp,image/*,*/*;q=0.8",
                })
                with urlopen(request, timeout=25) as response:
                    content_type = response.headers.get_content_type().lower()
                    body = response.read(15 * 1024 * 1024 + 1)
                if len(body) > 15 * 1024 * 1024:
                    raise ValueError("source image exceeds 15 MB")
                extension = MIME_EXTENSIONS.get(content_type)
                if not extension:
                    raise ValueError(f"source returned {content_type}, not a supported image")
                filename = slugify(name) + extension
                (output_dir / filename).write_bytes(body)
                manifest[name] = f"/static/products/{filename}"
                self.stdout.write(self.style.SUCCESS(f"Saved {name}"))
            except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
                failures.append((name, str(exc)))
                self.stderr.write(self.style.WARNING(f"Skipped {name}: {exc}"))
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        self.stdout.write(f"Saved {len(manifest)} of {len(IMAGES)} product images.")
        if failures:
            self.stdout.write(self.style.WARNING("Unavailable sources remain online URLs when the catalog is seeded."))
