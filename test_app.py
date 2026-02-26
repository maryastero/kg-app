import unittest
from unittest.mock import patch, MagicMock
from streamlit.testing.v1 import AppTest

class TestBioGraphApp(unittest.TestCase):
    @patch('langchain_openai.ChatOpenAI') # Intercept the LLM initialization
    def test_app_smoke(self, mock_chat):
        # 1. Setup the mock behavior
        # We make the mock return a dummy object so it doesn't crash
        mock_instance = MagicMock()
        mock_chat.return_value = mock_instance
        
        # 2. Point to your main app file
        at = AppTest.from_file("app.py", default_timeout=30)
        
        # 3. Run the app simulation
        at.run()
        
        # 4. Check for errors
        # If there's no API key, but we've mocked ChatOpenAI, 
        # this should now pass without an OpenAIError!
        assert not at.exception

if __name__ == "__main__":
    unittest.main()
