import tweepy
import time, datetime
from random import randint
import csv
import json


class TwitterTools:
    import tweepy

    api = None
    user = None
    auth = None


    def set_auth(self, file_name):
        with open(str(file_name), 'r') as keys_csv:
            v = csv.DictReader(keys_csv, )
            for row in v:
                self.auth = tweepy.OAuthHandler(str(row['OauthHandler1']), str(row['OauthHandler2']))
                self.auth.set_access_token(str(row['AccessToken1']), str(row['AccessToken2']))

    def check_limits(self):
        rate_limits_data = json.loads(str(self.api.rate_limit_status()).replace("\'", "\""))
        rate_limits_data = rate_limits_data['resources']
        # this will possibly be used later to show percentages.
        rate_limits = {}
        rate_limits_remaining = {}

        for i in rate_limits_data.keys():

            for j in rate_limits_data[i].keys():
                rate_limits_remaining[j] = rate_limits_data[i][j]['remaining']
                rate_limits[j] = rate_limits_data[i][j]['limit']

        for i in rate_limits_remaining.items():
            if i[1] < 5:
                # print("Rate limit for " + i[0] + " reached.")
                return str("Rate limit for " + i[0] + " reached.")
            else:
                return False

        # Maybe useful for determining when limits should be watched.
        # for i in rate_limits_remaining.items():
        #
        #     # if 5 < i[1] < 50:
        #     #     print("Rate limit for " + i[0] + " below 50.")

        return rate_limits_remaining

    def follow_all_followers(self):
        followers = [i for i in self.api.followers_ids()]
        followed = [i for i in self.api.friends_ids()]
        people_followed = 0
        for person in followers:
            try:
                if person not in followed:
                    self.api.create_friendship(id=person)
                    people_followed += 1
                    print(self.api.get_user(person).screen_name + ' followed!')
            except tweepy.error.TweepError as e:
                print("can't follow ", person, " try someone else")
                print(e.reason)
        print(str(people_followed) + ' People followed.')

    def like_tweets_of_specific_search_keyword(self, keyword, num_tweets):
        while type(num_tweets) != int:
            num_tweets = input('How many tweets do you want to like?\n')
            try:
                num_tweets = int(num_tweets)
                if num_tweets < 1:
                    print('Please input a number greater than 0')
            except ValueError as e:
                print('Please input an integer')

        # Tweets pulled from searching keyword .
        # there are a larger number than num_tweets because the user may have liked some of the tweets already.
        keyword_tweets = [tweet.id for tweet in tweepy.Cursor(self.api.search, keyword).items(num_tweets * 2)]

        # list of my favorited tweets.
        my_favorites_list = [my_favorited_tweet.id for my_favorited_tweet in tweepy.Cursor(self.api.favorites).items()]

        liked_tweets = 0
        for i in range(0, len(keyword_tweets)):
            if liked_tweets == num_tweets:
                break
            elif keyword_tweets[i] not in my_favorites_list:
                try:
                    self.api.create_favorite(keyword_tweets[i])
                    liked_tweets += 1
                    if liked_tweets > 1:
                        print('Liked ' + str(liked_tweets) + ' Tweets with keyword: ' + keyword)
                    else:
                        print('Liked ' + str(liked_tweets) + ' Tweet with keyword: ' + keyword)

                except tweepy.TweepError as e:
                    print('    ' + e.reason)
                    print('     Skipped tweet. Moving to the next one.')
                except StopIteration:
                    break
        print('you liked ', num_tweets, ' tweets.')

    def retweet_tweets_of_specific_search_keyword(self, keyword, num_tweets):
        if keyword == '' or num_tweets != int or num_tweets < 1:
            keyword = input("What is your search Keyword?\nThis is what you'd put into the Twitter search bar.\n")
            num_tweets = input('How many tweets do you want to like?\n')

        while type(num_tweets) != int:
            num_tweets = input('How many tweets do you want to like?\n')
            try:
                num_tweets = int(num_tweets)
            except ValueError as e:
                print('Please input an integer')
        # Tweets pulled from searching keyword.
        # there are a larger number than num_tweets because the user may have liked some of the tweets already.

        keyword_tweets = [tweet.id for tweet in tweepy.Cursor(self.api.search, keyword).items(num_tweets * 3)]

        # list of my retweeted tweets.

        my_tweets = [my_tweet.id for my_tweet in tweepy.Cursor(self.api.user_timeline).items()]

        retweeted_tweets = 0
        for i in range(0, len(keyword_tweets)):
            if retweeted_tweets == num_tweets:
                break
            elif keyword_tweets[i] not in my_tweets:
                try:
                    self.api.retweet(keyword_tweets[i])
                    retweeted_tweets += 1
                    if retweeted_tweets > 1:
                        print('RT ' + str(retweeted_tweets) + ' Tweets with keyword: ' + keyword)
                    else:
                        print('RT ' + str(retweeted_tweets) + ' Tweet with keyword: ' + keyword)

                except tweepy.TweepError as e:
                    print('Skipped tweet. Moving to the next one.')
                    print(e.reason)
                except StopIteration:
                    break
        print("you retweeted " + str(retweeted_tweets) + " tweets.")

    def follow_everyone_someone_else_follows(self, handle_of_the_other_person):
        your_followed_list = [i for i in self.api.friends_ids()]
        the_other_persons_follower_list = []

        # populates the_other_persons_follower_list with only people that will not cause an error.
        for i in self.api.friends_ids(screen_name=handle_of_the_other_person):
            if (i not in your_followed_list) or (not i == self.user.id):
                the_other_persons_follower_list.append(i)

        # used to determine number of people followed. This is the before metric.
        peopleFollowedBefore = len(your_followed_list)

        print(str(len(the_other_persons_follower_list)) + ' accounts to follow!\n')

        # iterates through the the_other_persons_follower_list and follows each account.
        # if a rate error occurs, it is caught, printed, and the account is skipped.
        for person in the_other_persons_follower_list:
            try:
                self.api.create_friendship(person)
                print(self.api.get_user(person).screen_name + ' followed!')
                your_followed_list.append(person)


            # catches rate errors
            except tweepy.TweepError as e:
                print('there was an error: ' + e.reason + '. skipping this account!')

        # calculation of number of people followed during this process.
        numPeopleFollowed = len(your_followed_list) - peopleFollowedBefore

        print('\nYou followed ' + str(numPeopleFollowed) + ' people.\n'
              + 'You now follow ' + str(len(your_followed_list)) + ' people total.')

    def unfollow_everyone_someone_else_follows(self, handle_of_the_other_person):
        the_other_persons_follower_list = [i for i in self.api.friends_ids(screen_name=handle_of_the_other_person)]
        your_followed_list = [i for i in self.api.friends_ids()]
        unfollowed_count = 0
        for i in the_other_persons_follower_list:

            if i in your_followed_list:
                unfollowed_count += 1

                try:
                    self.api.destroy_friendship(i)
                    print(str(self.api.get_user(i).name) + ' unfollowed')
                except tweepy.TweepError as e:
                    print(e.reason)
        print('you unfollowed ' + str(unfollowed_count) + ' accounts!')

    def like_a_users_tweets(self, handle, num_tweets_to_like, ):
        status = []
        for i in range(1, 3):
            for tweetID in self.api.user_timeline(screen_name=handle, page=i):
                status.append(tweetID.id)

        if len(status) < num_tweets_to_like:
            num_tweets_to_like = len(status)
        print(str(num_tweets_to_like) + ' Tweets to Like')

        j = 1
        for tweet in range(0, num_tweets_to_like):
            if randint(0, 2) == 1:
                try:
                    self.api.create_favorite(status[tweet])

                    print('liked tweet #' + str(j) + '/' + str(num_tweets_to_like))

                except tweepy.TweepError as e:
                    print(e.reason)
                    print("can't like tweet #" + str(j) + '/' + str(num_tweets_to_like))

            else:
                print('skipped tweet #' + str(j) + '/' + str(num_tweets_to_like))

            j += 1

    def retweet_a_users_tweets(self, handle, num_tweets_to_RT, ):
        total_num_tweets_to_RT = num_tweets_to_RT
        status = []
        for i in range(1, 3):
            for tweetID in self.api.user_timeline(screen_name=handle, page=i):
                status.append(tweetID.id)

        if len(status) < num_tweets_to_RT:
            num_tweets_to_RT = len(status)

        print(str(num_tweets_to_RT) + ' Tweets to Retweet')

        j = 1
        for tweet in range(0, 50):
            if num_tweets_to_RT == 0:
                break
            elif randint(0, 1) == 1:
                try:
                    self.api.retweet(status[tweet])

                    print('Confirmed Retweet #' + str(j) + '/' + str(total_num_tweets_to_RT))
                    num_tweets_to_RT -= 1
                    j += 1

                except tweepy.TweepError as e:
                    print(e.reason)
                    print("can't retweet #" + str(j) + '/' + str(total_num_tweets_to_RT))

            else:
                print('skipped tweet #' + str(j) + '/' + str(total_num_tweets_to_RT))

                j += 1

    def record_num_followers(self):
        with open('followers.csv', 'a', newline='\n') as csvfile:
            fieldnames = ['date', 'num_followers']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            print(len([i for i in self.api.followers_ids()]))
            writer.writerow(
                {'date': str(datetime.date.today()), 'num_followers': len([i for i in self.api.followers_ids()])})

    # friends are people that you follow
    def record_num_friends(self):
        with open('friends.csv', 'a', newline='\n') as csvfile:
            fieldnames = ['date', 'num_friends']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            print(len([i for i in self.api.friends_ids()]))
            writer.writerow(
                {'date': str(datetime.date.today()), 'num_friends': len([i for i in self.api.friends_ids()])})

    def unfollow_all_accounts_that_do_not_follow_you(self):
        friends = [friend for friend in self.tweepy.Cursor(self.api.friends_ids).items()]
        followers = [follower for follower in self.tweepy.Cursor(self.api.followers_ids).items()]

        remaining = 0
        deleted = 0
        for f in friends:
            if f not in followers:
                try:
                    self.api.destroy_friendship(f)
                    print('destroyed friendship with {}'.format(f))
                    deleted += 1
                except self.tweepy.TweepError as e:
                    print(e.reason)
            else:
                print('remaining friendship: {}'.format(f))
                remaining += 1

        print('remaining = {}'.format(remaining))
        print('deleted = {}'.format(deleted))

    def remove_retweets_from_all_except_non_followers(self,):

        my_tweets = [tweet for tweet in self.tweepy.Cursor(self.api.user_timeline).items()]
        my_follower_list = [i for i in self.api.followers_ids()]

        counter = 0
        for tweet in my_tweets:

            # RATE LIMIT CHECKING IS BROKEN
            # rate_limit_msg = twbot.check_limits()
            # print(rate_limit_msg)
            # while rate_limit_msg:
            #     print(rate_limit_msg)
            #     time.sleep(60)
            #     rate_limit_msg = twbot.check_limits()

            if tweet.author.id_str in my_follower_list and tweet.author.id_str != self.user.id_str:
                self.api.unretweet(tweet.id_str)
                counter += 1
                if counter == 1:
                    print("{} retweet removed".format(counter))
                else:
                    print("{} retweets removed".format(counter))
                print('tweet text = {}'.format(tweet.text))

            else:
                print('tweet does not meet criteria')
                print('tweet text = {}'.format(tweet.text))

        print('{} tweets removed total.'.format(counter))

    @classmethod
    def from_external_file(cls, file_name):
        new_instance = cls()
        new_instance.set_auth(file_name)
        new_instance.api = tweepy.API(new_instance.auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        new_instance.user = new_instance.api.me()
        return new_instance

    @classmethod
    def from_args(cls, OauthHandler1, OauthHandler2, AccessToken1, AccessToken2, ):
        new_instance = cls()
        new_instance.auth = tweepy.OAuthHandler(OauthHandler1, OauthHandler2)
        new_instance.auth.set_access_token(AccessToken1, AccessToken2, )
        new_instance.api = tweepy.API(new_instance.auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        new_instance.user = new_instance.api.me()
        return new_instance
