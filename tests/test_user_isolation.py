import os
import json
import tempfile
import unittest
from unittest.mock import patch

os.environ["USERS_DIR"] = tempfile.mkdtemp(prefix="autobrand_users_")

from services import user_manager as um
from services.linkedin_service import is_access_token, resolve_publish_token
from services.schedule_utils import detect_slot, weekend_kind_for_tests
from services.github_service import append_github_link_to_post
from services.image_card_service import generate_png_banner, _wrap
from services.telegram_bot import handle_telegram_update


class UserIsolationTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="users_")
        um.USERS_DIR = self.tmpdir

    def test_two_resumes_never_mix(self):
        a = um.save_user({
            "name": "Asha",
            "telegram_username": "asha_ui",
            "skills_summary": "Figma and dashboard design",
            "github_username": "asha",
        })
        b = um.save_user({
            "name": "Bala",
            "telegram_username": "bala_web",
            "skills_summary": "HTML websites and SEO",
            "github_username": "bala",
        })
        self.assertNotEqual(a["folder_key"], b["folder_key"])
        um.save_pending_post(a, {"content": "design post for asha"})
        um.save_pending_post(b, {"content": "website post for bala"})
        self.assertIn("asha", um.get_pending_post(a)["content"])
        self.assertIn("bala", um.get_pending_post(b)["content"])
        self.assertNotEqual(um.get_pending_post(a)["content"], um.get_pending_post(b)["content"])

    def test_lookup_does_not_create_ghost_folder(self):
        before = os.listdir(self.tmpdir) if os.path.isdir(self.tmpdir) else []
        self.assertIsNone(um.get_user_by_phone("9999999999"))
        after = os.listdir(self.tmpdir)
        self.assertEqual(before, after)

    def test_connect_code_bind(self):
        user = um.save_user({"name": "Sahil", "telegram_username": "sahilp"})
        found = um.get_user_by_connect_code(user["connect_code"])
        self.assertEqual(found["name"], "Sahil")
        um.bind_telegram_chat(found, 111, "sahilp")
        again = um.get_user_by_telegram_chat_id(111)
        self.assertEqual(again["name"], "Sahil")


class LinkedInTokenTests(unittest.TestCase):
    def test_profile_url_is_not_a_token(self):
        self.assertFalse(is_access_token("https://www.linkedin.com/in/sahil"))
        self.assertTrue(is_access_token("A" * 50))

    def test_resolve_uses_user_token_only_when_real(self):
        token, _, source = resolve_publish_token({
            "linkedin_token": "https://linkedin.com/in/x",
            "telegram_chat_id": "1",
        })
        self.assertEqual(source, "none")
        self.assertEqual(token, "")


class SlotTests(unittest.TestCase):
    def test_weekend_is_saturday_or_sunday(self):
        import datetime
        sat = datetime.datetime(2026, 11, 7, 10, 0)  # Saturday
        sun = datetime.datetime(2026, 11, 8, 10, 0)
        mon = datetime.datetime(2026, 11, 9, 10, 0)
        self.assertEqual(detect_slot(sat), "weekend")
        self.assertEqual(detect_slot(sun), "weekend")
        self.assertEqual(detect_slot(mon), "morning")
        self.assertEqual(weekend_kind_for_tests(5), "quiz")
        self.assertEqual(weekend_kind_for_tests(6), "poll")

    def test_github_link_before_hashtags(self):
        text = "Tip here\n\n#WebDesign #SEO"
        out = append_github_link_to_post(text, "sahilpareek")
        self.assertIn("github.com/sahilpareek", out)
        self.assertTrue(out.index("github.com") < out.index("#WebDesign"))


class BannerTests(unittest.TestCase):
    def test_png_banner_writes_file(self):
        try:
            import PIL  # noqa: F401
        except ImportError:
            self.skipTest("Pillow not installed")
        path = os.path.join(tempfile.mkdtemp(), "banner.png")
        generate_png_banner("48px buttons", "morning", filepath=path)
        self.assertTrue(os.path.isfile(path))
        self.assertGreater(os.path.getsize(path), 100)

    def test_wrap_keeps_short_lines(self):
        lines = _wrap("Make buttons big enough to tap with a thumb", 18)
        self.assertTrue(all(len(x) <= 24 or " " not in x for x in lines))


class TelegramFlowTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="tg_")
        um.USERS_DIR = self.tmpdir
        self.user = um.save_user({
            "name": "Tester",
            "telegram_username": "tester_bot",
            "skills_summary": "UI buttons",
        })
        um.save_pending_post(self.user, {"content": "old draft #UIUX"})

    @patch("services.telegram_bot.send_telegram_message")
    @patch("services.telegram_bot.send_user_welcome")
    def test_start_binds_chat(self, welcome, send_msg):
        update = {
            "message": {
                "chat": {"id": 42},
                "from": {"username": "tester_bot"},
                "text": f"/start {self.user['connect_code']}",
            }
        }
        result = handle_telegram_update(update)
        self.assertEqual(result["action"], "bind")
        stored = um.get_user_by_telegram_chat_id(42)
        self.assertEqual(stored["name"], "Tester")
        welcome.assert_called_once()

    @patch("services.telegram_bot.send_telegram_message")
    @patch("services.telegram_bot.send_callback_answer")
    @patch("services.telegram_bot.resolve_publish_token", return_value=("", "urn:li:person:me", "none"))
    def test_approve_without_token_does_not_crash(self, _token, _cb, send_msg):
        um.bind_telegram_chat(self.user, 99, "tester_bot")
        update = {
            "callback_query": {
                "id": "cb1",
                "data": "approve",
                "from": {"username": "tester_bot", "id": 99},
                "message": {"chat": {"id": 99}},
            }
        }
        result = handle_telegram_update(update)
        self.assertEqual(result["action"], "approve")
        self.assertIn("token", result["reply"].lower())
        self.assertIsNotNone(um.get_pending_post(self.user))

    @patch("services.telegram_bot.send_telegram_message")
    @patch("services.post_generator.refine_post", return_value="updated draft #UIUX")
    def test_edit_then_keep_pending(self, refine, send_msg):
        um.bind_telegram_chat(self.user, 7, "tester_bot")
        update = {
            "message": {
                "chat": {"id": 7},
                "from": {"username": "tester_bot"},
                "text": "make it shorter",
            }
        }
        result = handle_telegram_update(update)
        self.assertEqual(result["action"], "refine")
        self.assertEqual(um.get_pending_post(self.user)["content"], "updated draft #UIUX")
        refine.assert_called_once()

    def test_approve_words(self):
        self.assertTrue(um.is_approve_text("APPROVE"))
        self.assertTrue(um.is_approve_text("yes"))
        self.assertFalse(um.is_approve_text("make it shorter"))


if __name__ == "__main__":
    unittest.main()
