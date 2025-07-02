# 動作確認データ
class TestData:
    """app/seeders/seed_data.pyで使用するテストデータを格納する。
    pytestに影響があるテストデータのみ定数化する。
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
