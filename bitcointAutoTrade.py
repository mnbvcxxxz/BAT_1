import time
import pyupbit
import datetime
import requests
import numpy as np

access = "NoRVfwch6I71UZHCZq3ji9Z5xcXz8r7U2QnxlGQn"
secret = "J7t7vx31yrnbETxKroRJ6M1nyiddgGR571UL1YfG"
myToken = "xoxb-2022008201107-2046141877680-eT16j1cCTiN3OqWGuSLIMdnO"
upbit = pyupbit.Upbit(access, secret)


"""주문 기본정보 및 기준"""
Coin_KRW = "KRW-DOGE" #ticker_KRW
Coin = "DOGE" #ticker
intervals = "minute30"
K = 0.3  # 추후 자동 K값 산출하기~~~~~~~~~~~

print("코인잔고(",Coin_KRW,") : ", upbit.get_balance(Coin_KRW))     # KRW-XRP 조회
print("현금잔고(원) : ", upbit.get_balance("KRW"))         # 보유 현금 조회
print("세팅 K값 : ",K)
print("최근추세 : ", pyupbit.get_ohlcv(Coin_KRW, interval=intervals, count=10),sep='\n')


def post_message(token, channel, text):
    """슬랙 메시지 전송"""
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval=intervals, count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval=intervals, count=1)
    start_time = df.index[0]
    return start_time

def get_ma15(ticker):
    """15일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval=intervals, count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15

    """잔고 조회"""
def get_balance(coin):
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

    """ 원화 5000원을 코인으로 환산"""
def coin_over_5000KRW(coin):
    return 5000/pyupbit.get_current_price(coin)

def get_ror(k=0.5):
    df = pyupbit.get_ohlcv(Coin_KRW,interval=intervals, count=24)
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)

    df['ror'] = np.where(df['high'] > df['target'],
                         df['close'] / df['target'],
                         1)

    ror = df['ror'].cumprod()[-2]
    return ror

print("\n------최근 12시간 K값 산출------\n")

for k in np.arange(0.1, 1.0, 0.1):
    ror = get_ror(k)
    print("%.1f %f" % (k, ror))

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("\n--------Autotrade start--------\n")

# 시작 메세지 슬랙 전송
post_message(myToken,"#거래-내역", "autotrade start")

#자동매매코드
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time(Coin_KRW)
        end_time = start_time + datetime.timedelta(minutes=30)

        if start_time < now < end_time - datetime.timedelta(seconds=10):  # 현재 시간이 시작시간과 종료시간-10초 사이에있다면
            target_price = get_target_price(Coin_KRW, K)                  # 내가 설정한 코인과 K값으로 타겟매수가 설정
            ma15 = get_ma15(Coin_KRW)                                     # 15일 이동평균을 분석하고
            current_price = pyupbit.get_current_price(Coin_KRW)                   # 코인의 현재 가격을 조회한다
            print(target_price,current_price and ma15,current_price)
            if target_price < current_price and ma15 < current_price:     # 타겟매수가가 ma15충족, 현재가보다 낮다면
                krw = get_balance("KRW")                                  # 내 원화통장 잔고를 확인해보고
                if 5000 < krw :                                            # 통장잔고가 5000원 이상 있을경우
                    buy_result = upbit.buy_market_order(Coin_KRW, 100000)    # 수수료 제외한 원화로 시장가매수
                    post_message(myToken,"#거래-내역", "Coin buy : " +str(buy_result))   # 결과를 Slack 전송
                    print("매수결과 : ",krw*0.9995,"원", buy_result, upbit.get_balance())
                    # if 200000 <= krw:
                    #     buy_result = upbit.buy_market_order(Coin_KRW, krw*(200000/krw))  # 최대매수한도 20만원
                    #     print("매수결과 : ", krw*(200000/krw),"원", buy_result, upbit.get_balance())
                # else:
                #     print("원화가 부족합니다")

        else:
            coin_price = get_balance(Coin)                                 # 설정 코인의 잔고를 조회하고
            if coin_price > coin_over_5000KRW(Coin_KRW):                   # 잔고가 5000원 있을 경우
                sell_result = upbit.sell_market_order(Coin_KRW, coin_price*0.9995)   # 수수료 제외한 코인가격을 시장가 매도
                post_message(myToken,"#거래-내역", "Coin sell : " +str(sell_result))   # 결과 Slack전송
                print("매도결과 : ", coin_price*0.9995,"ETH",sell_result, upbit.get_balance())
        time.sleep(1)
    except Exception as e:
        print(e)
        post_message(myToken,"#거래-내역", e)
        time.sleep(1)