import pyupbit
import numpy as np

# 위키독스 링크: https://wikidocs.net/book/1665
# 위키도독스 깃헙링크:  https://github.com/sharebook-kr/book-cryptocurrency
# 조코딩 깃헙링크:  https://github.com/youtube-jocoding/pyupbit-autotrade

access = "NoRVfwch6I71UZHCZq3ji9Z5xcXz8r7U2QnxlGQn"          # 본인 값으로 변경
secret = "J7t7vx31yrnbETxKroRJ6M1nyiddgGR571UL1YfG"          # 본인 값으로 변경
upbit = pyupbit.Upbit(access, secret)

# 코인 정의
Etherium = "KRW-ETH"
Bitcoin = "KRW-BTC"

# 매매 인터벌, 최근 조회데이터 수 정의
intervals = "minute60"
counts = 100

#K값 세팅
K=0.5

#
print(upbit.get_balance(Etherium))     # KRW-XRP 조회
print(upbit.get_balance("KRW"))         # 보유 현금 조회
# print(pyupbit.get_tickers(fiat="KRW"))  # 특정Fiat로 매매 가능한 목록 조회
#
print(pyupbit.get_ohlcv(Etherium, interval=intervals, count=counts))


# OHLCV(open, high, low, close, volume)로 당일 시가, 고가, 저가, 종가, 거래량에 대한 데이터
print("지난 데이터 추출")

df = pyupbit.get_ohlcv(Etherium, interval=intervals, count=counts)
print(df)


# 변동폭 * k 계산, (고가 - 저가) * k값
print("k=0.3")

df['range'] = (df['high'] - df['low']) * K

print(df['range'])

df['target'] = df['open'] + df['range'].shift(1) # target(목표매수가), range 컬럼을 한칸씩 밑으로 내림(.shift(1))

print(df['target'])

# ror(수익률), np.where(조건문, 참일때 값, 거짓일때 값)
df['ror'] = np.where(df['high'] > df['target'],
                     df['close'] / df['target'],
                     1)


df['hpr'] = df['ror'].cumprod()  # 누적 곱 계산(cumprod) => 누적 수익률

df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100 # Draw Down 계산 (누적 최대 값과 현재 hpr 차이 / 누적 최대값 * 100)


print("누적수익률(%):", df['hpr'])   #hpr 프린트
print("MDD(%): ", df['dd'].max())   #MDD 계산/프린트

#엑셀로 출력
# df.to_excel("dd.xlsx")

# 가장좋은 K값을 구하는 방법 (상승장일 경우K가 낮을수록, 하락장일수록 K가 높을수록 유리)
print("가장 좋은 K값을 구하는 방법")
def get_ror(k=0.5):
    df = pyupbit.get_ohlcv(Etherium,interval=intervals, count=counts)
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)

    df['ror'] = np.where(df['high'] > df['target'],
                         df['close'] / df['target'],
                         1)

    ror = df['ror'].cumprod()[-2]
    return ror


for k in np.arange(0.1, 1.0, 0.1):
    ror = get_ror(k)
    print("%.1f %f" % (k, ror))

# Max_ror = max()
# print(Max_ror)