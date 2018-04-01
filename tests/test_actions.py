import logging
import random
import unittest
from unittest.mock import patch

from tests.helper_func import load_fixture_config, get_fixture
from yatcobot.actions import Favorite, Follow, TagFriendAction
from yatcobot.config import TwitterConfig

logging.disable(logging.ERROR)


class TestFollow(unittest.TestCase):

    @patch('yatcobot.bot.TwitterClient')
    @patch('yatcobot.bot.TwitterConfig')
    def setUp(self, config_mock, client_mock):
        self.config = config_mock
        self.client = client_mock
        load_fixture_config()
        self.action = Follow(self.client)

    def test_follow(self):
        TwitterConfig.get()['actions']['follow']['keywords'] = [' follow ']

        post = (
            {'id': 0, 'full_text': 'test follow tests', 'user': {'id': random.randint(1, 1000), 'screen_name': 'test'},
             'retweeted': False})

        self.action.process(post)
        self.client.follow.assert_called_once_with(post['user']['screen_name'])

    def test_no_follow(self):
        TwitterConfig.get()['actions']['follow']['keywords'] = [' follow ']

        post = (
            {'id': 0, 'full_text': 'test tests', 'user': {'id': random.randint(1, 1000), 'screen_name': 'test'},
             'retweeted': False})

        self.action.process(post)
        self.assertFalse(self.client.follow.called)

    def test_follow_with_remove_oldest(self):
        TwitterConfig.get()['actions']['follow']['keywords'] = [' follow ']

        post = (
            {'id': 0, 'full_text': 'test follow tests', 'user': {'id': random.randint(1, 1000), 'screen_name': 'test'},
             'retweeted': False})

        follows = [x for x in range(TwitterConfig.get()['actions']['follow']['max_following'] + 1)]
        self.client.get_friends_ids.return_value = follows

        self.action.process(post)
        self.client.follow.assert_called_once_with(post['user']['screen_name'])
        self.client.unfollow.assert_called_with(TwitterConfig.get()['actions']['follow']['max_following'])

    def test_remove_oldest_follow_empty(self):
        follows = [x for x in range(TwitterConfig.get()['actions']['follow']['max_following'] - 1)]
        self.client.get_friends_ids.return_value = follows
        self.action.remove_oldest_follow()
        self.assertFalse(self.client.unfollow.called)

    def test_remove_oldest_follow_full(self):
        follows = [x for x in range(TwitterConfig.get()['actions']['follow']['max_following'] + 1)]
        self.client.get_friends_ids.return_value = follows
        self.action.remove_oldest_follow()
        self.client.unfollow.assert_called_with(TwitterConfig.get()['actions']['follow']['max_following'])

    def test_multiple_follows(self):
        TwitterConfig.get()['actions']['follow']['multiple'] = True

        post = get_fixture('post_multiple_mentions.json')

        self.action.process(post)

        self.assertEqual(self.client.follow.call_count, 2)
        for user in post['entities']['user_mentions']:
            self.client.follow.assert_any_call(user['screen_name'])


class TestFavorite(unittest.TestCase):

    @patch('yatcobot.bot.TwitterClient')
    @patch('yatcobot.bot.TwitterConfig')
    def setUp(self, config_mock, client_mock):
        self.config = config_mock
        self.client = client_mock
        self.action = Favorite(self.client)
        load_fixture_config()

    def test_favorite(self):
        self.action = Favorite(self.client)
        TwitterConfig.get()['actions']['favorite']['keywords'] = [' favorite ']

        post = (
            {'id': 0, 'full_text': 'test favorite tests',
             'user': {'id': random.randint(1, 1000), 'screen_name': 'test'},
             'retweeted': False})

        self.action.process(post)

        self.client.favorite.assert_called_once_with(post['id'])


class TestTagFriend(unittest.TestCase):

    @patch('yatcobot.bot.TwitterClient')
    @patch('yatcobot.bot.TwitterConfig')
    def setUp(self, config_mock, client_mock):
        load_fixture_config()
        self.config = config_mock
        self.client = client_mock
        self.action = TagFriendAction(self.client)

    def test_tag_needed(self):

        post = get_fixture('post_tag_one_friend.json')
        self.assertTrue(self.action.tag_needed(post))

        post['full_text'] = " Testestset asdasda testesadst astagaring!"
        self.assertFalse(self.action.tag_needed(post))

    def test_friends_required(self):

        post = {'full_text': 'friend test test! #test tag or not a friend and tag a friend'}
        self.assertEqual(self.action.get_friends_required(post), 1)

        post = {'full_text': 'sfdsfsdhkjtag sdfskhsf friend tag ONE friend asdfsd sfsfd'}
        self.assertEqual(self.action.get_friends_required(post), 1)

        post = {'full_text': 'sfdsfsdhkjtag sdfskhsf friend tag 1 FRIEND asdfsd sfsfd'}
        self.assertEqual(self.action.get_friends_required(post), 1)

        post = {'full_text': 'hsdfsfsffrient sntagf friend and TAG two friends sfsdf'}
        self.assertEqual(self.action.get_friends_required(post), 2)

    def test_process(self):

        post = get_fixture('post_tag_one_friend.json')
        self.action.process(post)
        self.client.update.assert_called_once()




