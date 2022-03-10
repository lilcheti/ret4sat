from database import Database
import requests,config,tweepy,time


while True:
    try:
        users = Database().get_all_users()
        for user in users:
            if user[6]==0:
                print(str(user[1]))
                checkinvoice = requests.get("https://legend.lnbits.com/api/v1/payments/"+str(user[2]), headers = {"X-Api-Key": config.api_key,"Content-type": "application/json"})
                print(checkinvoice.text)
                kk=checkinvoice.json()
                if kk["paid"]==True:
                    auth = tweepy.OAuth1UserHandler(config.consumer_key, config.consumer_secret, config.access_token, config.access_token_secret)
                    api = tweepy.API(auth)
                    status = api.get_status(user[1])
                    if status.retweeted and user[8]==1:
                        api.unretweet(user[1])
                        Database().delete_row(user[1])
                        print("unretweeted!")
                    else:
                        api.retweet(user[1])
                        Database().set_ispaid(1, user[0])
                        print("retweeted")
                if ((time.time()-user[7])>1200) and (user[8]==0):
                    Database().delete_row(user[1])
    except Exception as e:
        print(e)
    