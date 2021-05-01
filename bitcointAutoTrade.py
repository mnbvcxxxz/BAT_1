import time
import pyupbit
import datetime
import requests

access = "NoRVfwch6I71UZHCZq3ji9Z5xcXz8r7U2QnxlGQn"
secret = "J7t7vx31yrnbETxKroRJ6M1nyiddgGR571UL1YfG"
myToken = "xoxb-2022008201107-2018729025317-bVjaXVu5ycIWBEd0qqQcQQTh" #슬랙토큰

# 코인 정의
Etherium = "KRW-ETH"
Bitcoin = "KRW-BTC"

# 매매 인터벌, 최근 조회데이터 수 정의
intervals = "minute30"
counts = 7

#K값 세팅 ->나중에 최적 K값 자동계산하도록
K=0.3

def post_message(token, channel, text):
    """슬랙 메시지 전송"""
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_ma15(ticker):
    """15일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15

def get_balance(coin):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == coin:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
# 시작 메세지 슬랙 전송
post_message(myToken,"#crypto", "autotrade start")

# 자동매매코드
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time(Etherium)
        end_time = start_time + datetime.timedelta(minutes=30) #days로 해야하나 minute으로 해야하나

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price(Etherium, K)
            ma15 = get_ma15(Etherium)
            current_price = get_current_price(Etherium)
            if target_price < current_price and ma15 < current_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    buy_result = upbit.buy_market_order(Etherium, krw*0.9995)
                    post_message(myToken,"#거래-내역", "BTC buy : " +str(buy_result))
        else:
            btc = get_balance("BTC")
            if btc > 0.00008: #현재 가격이 5천원일경우? 수정 필요할듯
                sell_result = upbit.sell_market_order(Etherium, btc*0.9995)
                post_message(myToken,"#거래-내역", "BTC buy : " +str(sell_result))
        time.sleep(1)
    except Exception as e:
        print(e)
        post_message(myToken,"#거래-내역", e)
        time.sleep(1)