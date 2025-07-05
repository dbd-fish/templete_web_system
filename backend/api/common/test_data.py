# 動作確認データ
# gg:ignore - GitGuardian exclusion for test/demo data only
class TestData:
    """app/seeders/seed_data.pyで使用するテストデータを格納する。
    pytestに影響があるテストデータのみ定数化する。
    
    ⚠️ 注意: このファイルはテスト・開発・デモ用のデータのみを含んでいます。
    本番環境では使用しないでください。
    """

    # User
    TEST_USER_ID_1 = "123e4567-e89b-12d3-a456-426614174000"
    TEST_USER_ID_2 = "223e4567-e89b-12d3-a456-426614174001"
    TEST_USERNAME_1 = "testuser"
    TEST_USERNAME_2 = "targetuser"
    TEST_USER_EMAIL_1 = "testuser@example.com"
    TEST_USER_EMAIL_2 = "targetuser@example.com"
    TEST_USER_PASSWORD = "Password123456+-"
    TEST_USER_CONTACT_1 = "123456789"
    TEST_USER_CONTACT_2 = "987654321"

    # API Documentation Examples
    DOC_USERNAME_EXAMPLE = "testuser"
    DOC_PASSWORD_EXAMPLE = "Password123!"
    DOC_EMAIL_EXAMPLE = "user@example.com"
    DOC_NEW_USER_EMAIL = "newuser@example.com"
    DOC_NEW_USERNAME = "newuser"
    DOC_NEW_PASSWORD = "SecurePassword2024!"
    DOC_ADMIN_EMAIL = "admin@company.com"
    DOC_ADMIN_USERNAME = "admin_user"
    DOC_ADMIN_PASSWORD = "AdminPass123+-"
    DOC_RESET_PASSWORD = "NewSecurePass2024!"
    DOC_CONTACT_NUMBER = "090-1234-5678"
    DOC_DATE_OF_BIRTH = "1990-01-15"

    # Test specific constants
    TEST_DELETED_USERNAME = "deleted_user"
    TEST_EXISTING_USERNAME = "existing_user"
    TEST_RESTORED_USERNAME = "restored_user"
    TEST_OLD_USERNAME = "oldusername"
    TEST_NEW_USERNAME = "newusername"
    TEST_NEW_PASSWORD = "new_password"
    TEST_NONEXISTENT_EMAIL = "nonexistent@example.com"
    TEST_RESET_NEW_PASSWORD = "NewPassword123!"

    # JWT Token Examples (for documentation only - not real tokens)
    # gg:ignore - Fake JWT tokens for API documentation examples only
    DOC_JWT_TOKEN_EXAMPLE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiZXhwIjoxNzI1NTM2ODAwfQ.example_signature"
    DOC_RESET_TOKEN_EXAMPLE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJyZXNldEBleGFtcGxlLmNvbSIsImV4cCI6MTcyNTU0MDQwMH0.reset_signature"
