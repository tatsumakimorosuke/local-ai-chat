
from django.test import TestCase
from django.urls import reverse


class LoginRequiredTests(TestCase):

    def test_chat_requires_login(self):
        response = self.client.get(reverse("index"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            "/accounts/login/",
            response["Location"]
        )

    def test_chat_accessible_after_login(self):
        from django.contrib.auth import get_user_model

        # テスト専用のユーザーを作成
        get_user_model().objects.create_user(
            username="testuser",
            password="testpass123"
        )

        # ログインしてチャット画面にアクセス
        self.client.login(
            username="testuser",
            password="testpass123"
        )

        response = self.client.get(reverse("index"))

        # 正常に画面が表示されることを確認
        self.assertEqual(response.status_code, 200)

class ConversationTests(TestCase):

    def test_new_chat_creates_conversation(self):
        from django.contrib.auth import get_user_model
        from .models import Conversation

        # テスト用ユーザーを作成してログイン
        user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.client.force_login(user)

        # 新しい会話を作成
        response = self.client.post(reverse("new_chat"))

        # 会話が1件保存されたことを確認
        self.assertEqual(Conversation.objects.count(), 1)

        # チャット画面へ戻ることを確認
        self.assertEqual(response.status_code, 302)

    def test_delete_chat_removes_conversation(self):
        from django.contrib.auth import get_user_model
        from .models import Conversation

        # テスト用ユーザーでログイン
        user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.client.force_login(user)

        # テスト用の会話を作成
        conversation = Conversation.objects.create(
            title="削除テスト"
        )

        # 会話を削除
        response = self.client.post(
            reverse("delete_chat", args=[conversation.id])
        )

        # データベースから削除されたことを確認
        self.assertFalse(
            Conversation.objects.filter(id=conversation.id).exists()
        )

        # チャット画面へ戻ることを確認
        self.assertEqual(response.status_code, 302)
