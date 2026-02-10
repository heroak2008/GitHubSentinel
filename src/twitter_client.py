import requests
from datetime import datetime
import os
from logger import LOG


class TwitterClient:
    def __init__(self, bearer_token=None):
        """
        初始化 Twitter 客户端
        Args:
            bearer_token: Twitter API Bearer Token，如果未提供则从环境变量读取
        """
        self.bearer_token = bearer_token or os.getenv('TWITTER_BEARER_TOKEN')
        if not self.bearer_token:
            LOG.warning("未配置 Twitter Bearer Token，Twitter 功能将受限。")
        
        self.api_url = 'https://api.twitter.com/2/tweets/search/recent'
        self.headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'User-Agent': 'GitHubSentinel/1.0'
        }

    def fetch_ai_tweets(self, max_results=50):
        """
        获取与AI相关的最新推文
        Args:
            max_results: 返回的最大推文数量 (10-100)
        Returns:
            list: 推文列表
        """
        LOG.debug(f"准备获取最新的AI相关推文，数量限制：{max_results}")
        
        if not self.bearer_token:
            LOG.error("缺少 Twitter Bearer Token，无法获取推文。")
            return []
        
        try:
            # 构建搜索查询，关注AI相关话题
            # 使用英文和中文关键词，排除转发
            query = '(AI OR "Artificial Intelligence" OR "Machine Learning" OR "Deep Learning" OR LLM OR GPT OR "人工智能" OR "机器学习" OR "深度学习") -is:retweet lang:en OR lang:zh'
            
            params = {
                'query': query,
                'max_results': min(max_results, 100),  # API 限制最多100条
                'tweet.fields': 'created_at,public_metrics,author_id',
                'expansions': 'author_id',
                'user.fields': 'username,name',
                'sort_order': 'relevancy'  # 按相关性排序
            }
            
            response = requests.get(
                self.api_url,
                headers=self.headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            tweets = self.parse_tweets(data)
            LOG.info(f"成功获取 {len(tweets)} 条AI相关推文。")
            return tweets
            
        except Exception as e:
            LOG.error(f"获取Twitter AI推文失败：{str(e)}")
            return []

    def parse_tweets(self, data):
        """
        解析Twitter API返回的数据
        Args:
            data: Twitter API返回的JSON数据
        Returns:
            list: 格式化的推文列表
        """
        LOG.debug("解析Twitter API返回的数据。")
        
        tweets = []
        if 'data' not in data or not data['data']:
            LOG.warning("Twitter API未返回任何数据。")
            return tweets
        
        # 创建用户ID到用户信息的映射
        users = {}
        if 'includes' in data and 'users' in data['includes']:
            users = {user['id']: user for user in data['includes']['users']}
        
        for tweet_data in data['data']:
            author_id = tweet_data.get('author_id')
            user = users.get(author_id, {})
            
            tweet = {
                'text': tweet_data.get('text', ''),
                'created_at': tweet_data.get('created_at', ''),
                'tweet_id': tweet_data.get('id', ''),
                'author_name': user.get('name', 'Unknown'),
                'author_username': user.get('username', 'unknown'),
                'metrics': tweet_data.get('public_metrics', {})
            }
            tweets.append(tweet)
        
        return tweets

    def export_ai_tweets(self, date=None, hour=None, max_results=50):
        """
        导出AI相关推文到文件
        Args:
            date: 日期字符串，格式为 YYYY-MM-DD，默认为当前日期
            hour: 小时字符串，格式为 HH，默认为当前小时
            max_results: 获取的推文数量
        Returns:
            str: 导出文件的路径，如果失败则返回None
        """
        LOG.debug("准备导出Twitter AI推文。")
        tweets = self.fetch_ai_tweets(max_results)
        
        if not tweets:
            LOG.warning("未找到任何AI相关推文。")
            return None
        
        # 如果未提供 date 和 hour 参数，使用当前日期和时间
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        if hour is None:
            hour = datetime.now().strftime('%H')
        
        # 构建存储路径
        dir_path = os.path.join('twitter_ai_news', date)
        os.makedirs(dir_path, exist_ok=True)
        
        file_path = os.path.join(dir_path, f'{hour}.md')
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(f"# Twitter AI News ({date} {hour}:00)\n\n")
            file.write(f"收集了 {len(tweets)} 条AI相关推文\n\n")
            
            for idx, tweet in enumerate(tweets, start=1):
                author = tweet['author_name']
                username = tweet['author_username']
                text = tweet['text'].replace('\n', ' ')  # 移除换行符
                tweet_id = tweet['tweet_id']
                tweet_url = f"https://twitter.com/{username}/status/{tweet_id}"
                metrics = tweet['metrics']
                
                file.write(f"{idx}. **@{username}** ({author})\n")
                file.write(f"   {text}\n")
                file.write(f"   👍 {metrics.get('like_count', 0)} | "
                          f"💬 {metrics.get('reply_count', 0)} | "
                          f"🔄 {metrics.get('retweet_count', 0)}\n")
                file.write(f"   [{tweet_url}]({tweet_url})\n\n")
        
        LOG.info(f"Twitter AI推文文件生成：{file_path}")
        return file_path


if __name__ == "__main__":
    client = TwitterClient()
    client.export_ai_tweets()
