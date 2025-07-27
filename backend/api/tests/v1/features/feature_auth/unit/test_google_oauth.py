"""
Google OAuth 2.0認証機能の単体テスト（AAAパターン）
"""

from unittest.mock import patch

import pytest

from api.v1.features.feature_auth.google_oauth import (
    GoogleUserInfo,
    generate_username_from_google_info,
    verify_google_id_token,
)


class TestGoogleUserInfo:
    """GoogleUserInfoスキーマのテスト"""

    def test_google_user_info_creation(self):
        """GoogleUserInfo正常作成テスト

        【正常系】GoogleUserInfoが正常に作成されることを確認。
        """
        # Arrange: Googleユーザー情報のテストデータを準備
        email = "test@example.com"
        name = "Test User"
        sub = "12345"
        email_verified = True

        # Act: GoogleUserInfoインスタンスを作成
        user_info = GoogleUserInfo(email=email, name=name, sub=sub, email_verified=email_verified)

        # Assert: 各フィールドが正しく設定されることを確認
        assert user_info.email == email
        assert user_info.name == name
        assert user_info.sub == sub
        assert user_info.email_verified is email_verified

    def test_google_user_info_optional_fields(self):
        """GoogleUserInfoオプショナルフィールドテスト

        【正常系】GoogleUserInfoのオプショナルフィールドが正常に設定されることを確認。
        """
        # Arrange: オプショナルフィールドを含むテストデータを準備
        email = "test@example.com"
        name = "Test User"
        sub = "12345"
        given_name = "Test"
        family_name = "User"
        picture = "https://example.com/photo.jpg"
        locale = "ja"

        # Act: オプショナルフィールド付きでGoogleUserInfoインスタンスを作成
        user_info = GoogleUserInfo(
            email=email, name=name, sub=sub,
            given_name=given_name, family_name=family_name,
            picture=picture, locale=locale,
        )

        # Assert: 各オプショナルフィールドが正しく設定されることを確認
        assert user_info.given_name == given_name
        assert user_info.family_name == family_name
        assert user_info.picture == picture
        assert user_info.locale == locale


class TestVerifyGoogleIdToken:
    """verify_google_id_token関数のテスト"""

    @pytest.mark.asyncio
    @patch("api.v1.features.feature_auth.google_oauth.id_token.verify_oauth2_token")
    @patch("api.v1.features.feature_auth.google_oauth.auth_setting")
    async def test_verify_google_id_token_success(self, mock_auth_setting, mock_verify):
        """Google IDトークン検証成功テスト

        【正常系】有効なGoogle IDトークンが正常に検証されることを確認。
        """
        # Arrange: Google OAuth検証成功時のレスポンスを準備
        mock_auth_setting.GOOGLE_CLIENT_ID = "test-client-id"
        mock_verify.return_value = {
            "iss": "accounts.google.com",
            "aud": "test-client-id",
            "email": "test@example.com",
            "email_verified": True,
            "name": "Test User",
            "given_name": "Test",
            "family_name": "User",
            "picture": "https://example.com/photo.jpg",
            "locale": "ja",
            "sub": "12345",
        }
        test_token = "valid-token"

        # Act: Google IDトークンの検証を実行
        result = await verify_google_id_token(test_token)

        # Assert: GoogleUserInfoオブジェクトが正しく返されることを確認
        assert isinstance(result, GoogleUserInfo)
        assert result.email == "test@example.com"
        assert result.name == "Test User"
        assert result.sub == "12345"
        assert result.email_verified is True

    @pytest.mark.asyncio
    @patch("api.v1.features.feature_auth.google_oauth.id_token.verify_oauth2_token")
    async def test_verify_google_id_token_invalid_issuer(self, mock_verify):
        """無効なissuerでのトークン検証失敗テスト"""
        # モックの設定
        mock_verify.return_value = {"iss": "invalid-issuer.com", "aud": "test-client-id", "email": "test@example.com", "email_verified": True, "name": "Test User", "sub": "12345"}

        # テスト実行とアサーション
        with pytest.raises(ValueError, match="無効なトークン発行者です"):
            await verify_google_id_token("invalid-token")

    @pytest.mark.asyncio
    @patch("api.v1.features.feature_auth.google_oauth.id_token.verify_oauth2_token")
    @patch("api.v1.features.feature_auth.google_oauth.auth_setting")
    async def test_verify_google_id_token_invalid_audience(self, mock_auth_setting, mock_verify):
        """無効なaudienceでのトークン検証失敗テスト"""
        # モックの設定
        mock_auth_setting.GOOGLE_CLIENT_ID = "correct-client-id"
        mock_verify.return_value = {"iss": "accounts.google.com", "aud": "wrong-client-id", "email": "test@example.com", "email_verified": True, "name": "Test User", "sub": "12345"}

        # テスト実行とアサーション
        with pytest.raises(ValueError, match="無効なクライアントIDです"):
            await verify_google_id_token("invalid-token")

    @pytest.mark.asyncio
    @patch("api.v1.features.feature_auth.google_oauth.id_token.verify_oauth2_token")
    async def test_verify_google_id_token_email_not_verified(self, mock_verify):
        """メールアドレス未認証でのトークン検証失敗テスト"""
        # モックの設定
        mock_verify.return_value = {"iss": "accounts.google.com", "aud": "test-client-id", "email": "test@example.com", "email_verified": False, "name": "Test User", "sub": "12345"}

        # テスト実行とアサーション（クライアントID検証が先に実行される）
        with pytest.raises(ValueError, match="無効なクライアントIDです"):
            await verify_google_id_token("invalid-token")

    @pytest.mark.asyncio
    @patch("api.v1.features.feature_auth.google_oauth.id_token.verify_oauth2_token")
    async def test_verify_google_id_token_missing_required_fields(self, mock_verify):
        """必須フィールド不足でのトークン検証失敗テスト"""
        # モックの設定
        mock_verify.return_value = {
            "iss": "accounts.google.com",
            "aud": "test-client-id",
            "email_verified": True,
            "name": "Test User",
            # email と sub が不足
        }

        # テスト実行とアサーション
        with pytest.raises(ValueError, match="無効なクライアントIDです"):
            await verify_google_id_token("invalid-token")

    @pytest.mark.asyncio
    @patch("api.v1.features.feature_auth.google_oauth.id_token.verify_oauth2_token")
    async def test_verify_google_id_token_exception(self, mock_verify):
        """Google API例外発生時のテスト"""
        # モックの設定
        mock_verify.side_effect = Exception("Google API Error")

        # テスト実行とアサーション
        with pytest.raises(ValueError, match="IDトークンの検証に失敗しました"):
            await verify_google_id_token("invalid-token")


class TestGenerateUsernameFromGoogleInfo:
    """generate_username_from_google_info関数のテスト"""

    def test_generate_username_with_given_family_name(self):
        """given_name, family_nameが両方ある場合のユーザー名生成テスト"""
        user_info = GoogleUserInfo(email="test@example.com", name="Test User", given_name="Test", family_name="User", sub="12345", email_verified=True)

        result = generate_username_from_google_info(user_info)
        assert result == "TestUser"

    def test_generate_username_with_given_name_only(self):
        """given_nameのみがある場合のユーザー名生成テスト"""
        user_info = GoogleUserInfo(email="test@example.com", name="Test User", given_name="Test", sub="12345", email_verified=True)

        result = generate_username_from_google_info(user_info)
        assert result == "Test"

    def test_generate_username_with_name_fallback(self):
        """given_name, family_nameがない場合のname使用テスト"""
        user_info = GoogleUserInfo(email="test@example.com", name="Test User", sub="12345", email_verified=True)

        result = generate_username_from_google_info(user_info)
        assert result == "TestUser"

    def test_generate_username_with_email_fallback(self):
        """name情報がない場合のemail使用テスト"""
        user_info = GoogleUserInfo(email="testuser@example.com", name="", sub="12345", email_verified=True)

        result = generate_username_from_google_info(user_info)
        assert result == "testuser"

    def test_generate_username_sanitization(self):
        """特殊文字の削除・置換テスト"""
        user_info = GoogleUserInfo(email="test@example.com", name="Test@User#123", sub="12345", email_verified=True)

        result = generate_username_from_google_info(user_info)
        # 特殊文字が削除・置換されることを確認
        assert "@" not in result
        assert "#" not in result
        assert len(result) <= 50  # username制限確認
