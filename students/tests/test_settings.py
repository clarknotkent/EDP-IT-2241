"""The deployment settings should fail loudly rather than fall back to a dev default.

The May 2024 submission shipped a single settings.py with DEBUG = True, an
empty ALLOWED_HOSTS, and its SECRET_KEY committed in plaintext to a public
repository. These tests pin down the replacement's contract.
"""
import importlib
import os
import sys
from unittest import mock

from django.test import SimpleTestCase


def load_prod(**env):
    """Import config.settings.prod fresh under a given environment."""
    sys.modules.pop('config.settings.prod', None)
    with mock.patch.dict(os.environ, env, clear=False):
        for key in ('DJANGO_SECRET_KEY', 'DJANGO_ALLOWED_HOSTS'):
            if key not in env:
                os.environ.pop(key, None)
        return importlib.import_module('config.settings.prod')


class ProdSettingsTests(SimpleTestCase):
    def tearDown(self):
        sys.modules.pop('config.settings.prod', None)

    def test_refuses_to_load_without_a_secret_key(self):
        with self.assertRaises(RuntimeError) as ctx:
            load_prod(DJANGO_ALLOWED_HOSTS='example.com')
        self.assertIn('DJANGO_SECRET_KEY', str(ctx.exception))

    def test_refuses_to_load_without_allowed_hosts(self):
        with self.assertRaises(RuntimeError) as ctx:
            load_prod(DJANGO_SECRET_KEY='x' * 50)
        self.assertIn('DJANGO_ALLOWED_HOSTS', str(ctx.exception))

    def test_loads_when_both_are_supplied(self):
        prod = load_prod(DJANGO_SECRET_KEY='x' * 50, DJANGO_ALLOWED_HOSTS='example.com,www.example.com')
        self.assertEqual(prod.ALLOWED_HOSTS, ['example.com', 'www.example.com'])

    def test_debug_is_off_and_cannot_be_switched_on_by_the_environment(self):
        prod = load_prod(DJANGO_SECRET_KEY='x' * 50, DJANGO_ALLOWED_HOSTS='example.com',
                         DJANGO_DEBUG='True')
        self.assertFalse(prod.DEBUG)

    def test_transport_security_is_on(self):
        prod = load_prod(DJANGO_SECRET_KEY='x' * 50, DJANGO_ALLOWED_HOSTS='example.com')
        self.assertTrue(prod.SESSION_COOKIE_SECURE)
        self.assertTrue(prod.CSRF_COOKIE_SECURE)
        self.assertTrue(prod.SECURE_SSL_REDIRECT)
        self.assertEqual(prod.X_FRAME_OPTIONS, 'DENY')
        self.assertGreaterEqual(prod.SECURE_HSTS_SECONDS, 31_536_000)

    def test_no_secret_key_is_committed_to_the_settings_package(self):
        from pathlib import Path
        pkg = Path(__file__).resolve().parent.parent.parent / 'config' / 'settings'
        for path in pkg.glob('*.py'):
            self.assertNotIn('django-insecure-', path.read_text(encoding='utf-8'),
                             f'{path.name} contains a generated Django key')
