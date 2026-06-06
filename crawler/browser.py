"""Playwright fallback for JS-rendered pages (bonus feature)."""

from __future__ import annotations

import logging

import config

log = logging.getLogger("cleancrawl.browser")


async def render_page(url: str) -> str | None:
    """Render a page with headless Chromium and return the HTML."""
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        log.warning("playwright not installed; JS rendering unavailable")
        return None

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(user_agent=config.USER_AGENT)
            page = await context.new_page()

            await page.route(
                "**/*",
                lambda route: (
                    route.abort()
                    if route.request.resource_type in ("image", "font", "media")
                    else route.continue_()
                ),
            )

            await page.goto(url, wait_until="networkidle", timeout=30000)
            html = await page.content()
            await browser.close()
            return html
    except Exception as e:
        log.error("Browser render failed for %s: %s", url, e)
        return None
