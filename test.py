import tweepy,asyncio,json,requests,qrcode,os,time,config
from tweepy.asynchronous import AsyncStream
from websockets import Data 
from database import Database

consumer_key = config.consumer_key
consumer_secret = config.consumer_secret
access_token = config.access_token
access_token_secret = config.access_token_secret
api_key = config.api_key
min_amount=config.min_amount

async def main():
    printer = IDPrinter(consumer_key, consumer_secret,access_token, access_token_secret)
    #stream = StdOutListener(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    await printer.filter(track=["retweet4sats"])


class IDPrinter(AsyncStream):
    async def on_status(self, status):
      try:
        if hasattr(status, "_json"):
          print(status._json)
          ismentioned = False
          for mention in status.entities["user_mentions"]:
            if mention["screen_name"] == "retweet4sats":
              ismentioned = True
              break
          if ismentioned:
            id = status.id_str
            amount = min_amount
            text = status.text.lower()
            cmd = text[text.rfind('@retweet4sats'):]
            s = cmd.split(" ")
            auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
            api = tweepy.API(auth)
            real_status = api.get_status(status.in_reply_to_status_id_str)
            if real_status.retweeted:
              try:
                if s[1]=="unretweet":
                  print("unretweet")
                  amount = Database().getamount(status.in_reply_to_status_id_str)*2
                  print(amount)
                  if amount > 4000000:
                    amount = 4000000
                  print("replied to",status.in_reply_to_status_id_str)
                  invoice = requests.post("https://legend.lnbits.com/api/v1/payments", data = '{"out": false,"amount":'+str(amount)+'}', headers = {"X-Api-Key": api_key,"Content-type": "application/json"})
                  print(invoice.text)
                  auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
                  api = tweepy.API(auth)
                  kk = invoice.json()
                  img = qrcode.make(kk["payment_request"])
                  type(img)  # qrcode.image.pil.PilImage
                  img.save(str(id)+".png")
                  api.update_status_with_media("Pay "+str(amount)+"sat with lightning to unretweet this tweet!",filename=str(id)+".png",in_reply_to_status_id=id,auto_populate_reply_metadata=True)
                  os.remove(str(id)+".png")
                  Database().update_user_data(status.in_reply_to_status_id_str,kk["payment_hash"],kk["payment_request"],kk["checking_id"],amount,0,time.time(),1)

                else:
                  raise Exception('unretweet')
              except:
                auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
                api = tweepy.API(auth)
                api.update_status("This tweet has already been retweeted!",in_reply_to_status_id=id,auto_populate_reply_metadata=True)
            elif not Database().is_user_saved(status.in_reply_to_status_id_str):
                  if len(s)>1:
                    if s[1]=="unretweet":

                        auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
                        api = tweepy.API(auth)
                        api.update_status("This tweet hasn't been retweeted yet!",in_reply_to_status_id=id,auto_populate_reply_metadata=True)
                        raise Exception('fake unretweet')

                    elif int(s[1]) >= min_amount:         
                      amount = int(s[1])
                  
                  print(amount)
                  if amount > 4000000:
                    amount = 4000000
                  print("replied to",status.in_reply_to_status_id_str)
                  invoice = requests.post("https://legend.lnbits.com/api/v1/payments", data = '{"out": false,"amount":'+str(amount)+'}', headers = {"X-Api-Key": "410ee88f07374a38b0465d30dfdcd598","Content-type": "application/json"})
                  print(invoice.text)
                  auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
                  api = tweepy.API(auth)
                  kk = invoice.json()
                  img = qrcode.make(kk["payment_request"])
                  type(img)  # qrcode.image.pil.PilImage
                  img.save(str(id)+".png")
                  api.update_status_with_media("Pay "+str(amount)+"sat with lightning",filename=str(id)+".png",in_reply_to_status_id=id,auto_populate_reply_metadata=True)
                  os.remove(str(id)+".png")
                  Database().add_user(status.in_reply_to_status_id_str,kk["payment_hash"],kk["payment_request"],kk["checking_id"],amount,0,time.time(),0)
            else:
              auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
              api = tweepy.API(auth)
              api.update_status("This tweet is already pending transaction! try again in 15 minutes",in_reply_to_status_id=id,auto_populate_reply_metadata=True)
          return True
        else:
          # returning False disconnects the stream
          return False
      except:
        print("fucked")

asyncio.run(main())

