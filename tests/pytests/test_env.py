import os
import pytest
from dotenv import load_dotenv, find_dotenv

dotenv_path = find_dotenv()


def test_env_variables():
    if dotenv_path:
        load_dotenv(dotenv_path)
        assert 'API_ID' in os.environ, 'API_ID is missing in .env file'
        assert 'API_HASH' in os.environ, 'API_HASH is missing in .env file'

        api_id = os.getenv('API_ID')
        cond0 = api_id is not None
        cond1 = api_id.isdigit()
        assert cond0 and cond1, 'API_ID should be a valid integer'

        api_hash = os.getenv('API_HASH')
        cond0 = api_hash is not None
        cond1 = len(api_hash) > 0
        assert cond0 and cond1, 'API_HASH should be a valid string'
    else:
        print('.env file not found... if this test runs on appveyor its ok...')


if __name__ == '__main__':
    pytest.main()

