import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# 添加 src 目录到模块搜索路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from twitter_client import TwitterClient
from logger import LOG


class TestTwitterClient(unittest.TestCase):
    def setUp(self):
        self.client = TwitterClient(bearer_token="test_token")

    @patch('twitter_client.requests.get')
    def test_fetch_ai_tweets_success(self, mock_get):
        # 模拟Twitter API响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [
                {
                    'id': '123456',
                    'text': 'Exciting developments in AI!',
                    'created_at': '2024-01-01T12:00:00.000Z',
                    'author_id': 'user1',
                    'public_metrics': {
                        'like_count': 10,
                        'retweet_count': 5,
                        'reply_count': 2
                    }
                }
            ],
            'includes': {
                'users': [
                    {
                        'id': 'user1',
                        'name': 'AI Expert',
                        'username': 'aiexpert'
                    }
                ]
            }
        }
        mock_get.return_value = mock_response
        
        # 调用方法并验证返回值
        tweets = self.client.fetch_ai_tweets(max_results=10)
        self.assertEqual(len(tweets), 1)
        self.assertEqual(tweets[0]['text'], 'Exciting developments in AI!')
        self.assertEqual(tweets[0]['author_username'], 'aiexpert')

    @patch('twitter_client.requests.get')
    def test_fetch_ai_tweets_no_bearer_token(self, mock_get):
        # 测试没有bearer token的情况
        client = TwitterClient(bearer_token=None)
        tweets = client.fetch_ai_tweets()
        self.assertEqual(tweets, [])
        mock_get.assert_not_called()

    @patch('twitter_client.requests.get')
    def test_fetch_ai_tweets_failure(self, mock_get):
        # 模拟HTTP请求失败
        mock_get.side_effect = Exception("Connection error")
        
        # 调用方法并验证返回值
        tweets = self.client.fetch_ai_tweets()
        self.assertEqual(tweets, [])

    @patch('twitter_client.requests.get')
    def test_fetch_ai_tweets_empty_response(self, mock_get):
        # 模拟空响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': []}
        mock_get.return_value = mock_response
        
        tweets = self.client.fetch_ai_tweets()
        self.assertEqual(tweets, [])

    @patch('twitter_client.requests.get')
    @patch('twitter_client.os.makedirs')
    @patch('twitter_client.open', new_callable=unittest.mock.mock_open)
    def test_export_ai_tweets(self, mock_open, mock_makedirs, mock_get):
        # 模拟Twitter API响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [
                {
                    'id': '123456',
                    'text': 'AI is amazing!',
                    'created_at': '2024-01-01T12:00:00.000Z',
                    'author_id': 'user1',
                    'public_metrics': {
                        'like_count': 100,
                        'retweet_count': 50,
                        'reply_count': 20
                    }
                }
            ],
            'includes': {
                'users': [
                    {
                        'id': 'user1',
                        'name': 'AI Researcher',
                        'username': 'airesearcher'
                    }
                ]
            }
        }
        mock_get.return_value = mock_response
        
        # 调用方法
        file_path = self.client.export_ai_tweets(date="2024-01-01", hour="12")
        
        # 验证目录和文件创建
        mock_makedirs.assert_called_once_with('twitter_ai_news/2024-01-01', exist_ok=True)
        mock_open.assert_called_once_with('twitter_ai_news/2024-01-01/12.md', 'w', encoding='utf-8')
        
        # 验证文件路径
        self.assertEqual(file_path, 'twitter_ai_news/2024-01-01/12.md')

    @patch('twitter_client.requests.get')
    @patch('twitter_client.os.makedirs')
    @patch('twitter_client.open', new_callable=unittest.mock.mock_open)
    def test_export_ai_tweets_no_tweets(self, mock_open, mock_makedirs, mock_get):
        # 模拟空响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': []}
        mock_get.return_value = mock_response
        
        # 调用方法
        file_path = self.client.export_ai_tweets(date="2024-01-01", hour="12")
        
        # 验证没有创建文件
        mock_makedirs.assert_not_called()
        mock_open.assert_not_called()
        self.assertIsNone(file_path)


if __name__ == '__main__':
    unittest.main()
