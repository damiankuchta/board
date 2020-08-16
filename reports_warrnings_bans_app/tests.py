from django.test import TestCase

# Create your tests here.
class TestWarrning(TestCase):
    def setUp(self) -> None:
        pass

    def test_staffuser_give_warrning(self):
        pass

    def test_non_staffuser_give_warrning(self):
        pass

class TestBan(TestCase):
    def setUp(self) -> None:
        pass

    def test_staffuser_give_ban(self):
        pass

    def test_non_staffuser_give_ban(self):
        pass

    def test_can_banned_user_login(self):
        pass

    def test_can_user_login_after_ban_expiry(self):
        pass

class TestReport(TestCase):
    def setUp(self) -> None:
        pass

    def test_user_send_report(self):
        pass

    def test_not_user_send_report(self):
        pass
