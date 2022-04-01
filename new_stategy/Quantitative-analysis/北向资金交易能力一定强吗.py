#pip install git+https://github.com/JoinQuant/jqdatasdk.git -i https://mirrors.aliyun.com/pypi/simple/


import datetime
import numpy as np
import pandas as pd
import empyrical as ep # ���������������

# ʱ�䴦��
import calendar
import empyrical as ep # ����ָ�����
from alphalens.utils import print_table
from dateutil.parser import parse

import itertools # ������
import collections # ����

from tqdm import tqdm_notebook # ������

#jqdata  ̫���ˣ������ˣ��滻tushare
#from jqdata import *
#from jqdatasdk import *
#from jqdatasdk import *auth('�˺�','����')
#jqdatasdk.auth('*****','')
# ��ͼ
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker  # ���������������ģ��

import sys 
sys.path.append("C://Users//huangtuo//Documents//GitHub//PairsTrading//new_stategy//Quantitative-analysis//") 
import foundation_tushare 
import json

# ������Լ��������дts��token
setting = json.load(open('C:\config\config.json'))
my_pro = foundation_tushare.TuShare(setting['token'], max_retry=60)

plt.rcParams['font.sans-serif'] = ['SimHei'] # ָ��Ĭ������
plt.rcParams['axes.unicode_minus'] = False # �������ͼ���Ǹ���'-'��ʾΪ���������
plt.style.use('seaborn')

def query_northmoney(start: str, end: str, fields: list) -> pd.DataFrame:
    '''�����ʽ�ɽ���ѯ'''

    select_type = ['����ͨ', '���ͨ']

    select_fields = ','.join([f"finance.STK_ML_QUOTA.%s" % i for i in fields])

    q = query(select_fields).filter(finance.STK_ML_QUOTA.day >= start,
                                    finance.STK_ML_QUOTA.day <= end,
                                    finance.STK_ML_QUOTA.link_name.in_(select_type))

    return finance.run_query(q)


def query_north_hold(start: str, end: str, fields: list) -> pd.DataFrame:
    
    '''����ֹ����ݲ�ѯ 2017��3��17�ſ�ʼ����'''

    select_type = ['����ͨ', '���ͨ']

    select_fields = ','.join(
        [f"finance.STK_HK_HOLD_INFO.%s" % i for i in fields])

    periods = get_trade_days(start, end)

    df_list = []

    for d in tqdm_notebook(periods, desc='��ѯ����ֹ�����'):
        
        for n in select_type:
            # �����ѯ
            q = query(select_fields).filter(finance.STK_HK_HOLD_INFO.link_name == n,
                                            finance.STK_HK_HOLD_INFO.day == d)

            df_list.append(finance.run_query(q))

    return pd.concat(df_list)


def is_index_cons(df: pd.DataFrame, index_symbol: list) -> pd.DataFrame:
    '''
    �ж��Ƿ�Ϊָ���ɷֹɲ����
    ---------
    df ����������� |day|code|
        day����Ϊdatetime.date
    '''

    start = min(df['day']).year
    end = max(df['day']).year

    year_list = range(start, end + 1)

    dic_list = []  # ���������

    d = collections.defaultdict(list)

    # ��ȡÿ�������սڵ�
    for y, m in itertools.product(year_list, (6, 12)):

        change_day = OffsetDate(find_change_day(y, m, 'Friday', '2nd'), 1)
        def index_name(x): return get_security_info(x).name
        dic_list += [[(code, index_name(index_code)) for code in get_index_stocks(index_code, date=change_day)]
                     for index_code in index_symbol]

    temp_list = []
    for i in dic_list:
        temp_list += i

    for k, v in temp_list:

        d[k].append(v)

    df['is_cons'] = df['code'].apply(
        lambda x: ",".join(set(d.get(x, ['OTHER']))))

    return df


# �ж�ĳ��ĳ�µĵ�N���ܼ�������
# ���� 2019��6�µĵ�2�������Ǽ���
# ��ָ֤�������϶���ÿ��6\12�µڶ���������¸�������
def find_change_day(year, month, weekday, spec_weekday):
    '''
    find_day(y, 12, "Friday", "2nd")
    ================
    return datetime.date
        y��12�µڶ�������
    '''
    DAY_NAMES = [day for day in calendar.day_name]
    day_index = DAY_NAMES.index(weekday)
    possible_dates = [
        week[day_index]
        for week in calendar.monthcalendar(year, month)
        if week[day_index]]  # remove zeroes

    if spec_weekday == 'teenth':

        for day_num in possible_dates:
            if 13 <= day_num <= 19:
                return datetime.date(year, month, day_num)

    elif spec_weekday == 'last':
        day_index = -1
    elif spec_weekday == 'first':
        day_index = 0
    else:
        day_index = int(spec_weekday[0]) - 1
    return datetime.date(year, month, possible_dates[day_index])


# ���ڻ�׼��ƫ��
def OffsetDate(end_date: str, count: int) -> datetime.date:
    '''
    end_date:Ϊ��׼����
    count:Ϊ������ƣ���Ϊǰ��
    -----------
    return datetime.date
    '''

    trade_date = get_trade_days(end_date=end_date, count=1)[0]
    if count > 0:
        # ��end_dateתΪ������

        trade_cal = get_all_trade_days().tolist()

        trade_idx = trade_cal.index(trade_date)

        return trade_cal[trade_idx + count]

    elif count < 0:

        return get_trade_days(end_date=trade_date, count=abs(count))[0]

    else:

        raise ValueError('���֣�')
        



def get_strategy_risk(algorithm_ret) -> pd.Series:

    ser = pd.Series({'�껯������': ep.annual_return(algorithm_ret),
                     '�껯������': ep.annual_volatility(algorithm_ret),
                     '���س�': ep.max_drawdown(algorithm_ret),
                     'Sharpe': ep.sharpe_ratio(algorithm_ret),
                     '����س���': ep.calmar_ratio(algorithm_ret)})

    ser.name = '����ָ��'

    return ser
    
    
start = '20141117'
end = '20200827'
daily_northmoney = distributed_other_query(my_pro.moneyflow_hsgt,
                                   start,
                                   end)
                                   
                                   
test_t=daily_northmoney
daily_northmoney.index=daily_northmoney['trade_date']
daily_northmoney=daily_northmoney[['trade_date','north_money']]
daily_northmoney=daily_northmoney.sort_index()
net_flow=daily_northmoney


index_df = my_pro.query('index_daily', ts_code='000001.SH', 
start_date=start, end_date=end,fields='trade_date,close') 
index_df.index=index_df['trade_date']
index_df=pd.DataFrame(index_df['close'])
index_df=index_df.sort_index() 


df=pd.merge(index_df,net_flow,left_index=True,right_index=True,how='outer')
df=df[['close','north_money']]
df=df.reset_index()
df.dropna(axis=1,how='any')
df.columns = [ 'date','close','north_money'] 

line = df.plot.line(x='date', y='close', secondary_y=True,
                    color='r', figsize=(18, 8), title='�����ʽ���ʷ��Ƶ�ʽ���')
df.plot.bar(x='date', y='north_money', ax=getattr(
    line, 'left_ax', line), color='DeepSkyBlue', rot=90)


xticks = list(range(0, len(df), 50))
xlabels = df['date'].loc[xticks].values.tolist()
plt.xticks(xticks, xlabels, rotation=90);


import talib

from sklearn.base import TransformerMixin, BaseEstimator
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


# ���챱����ֵ
def get_net_north_flow(start:str,end:str)->pd.Series:
    
    # ��ȡ�����������
    fields = ['day', 'link_name', 'buy_amount', 'sell_amount', 'sum_amount']
    north_money = distributed_query(query_northmoney, start, end, fields=fields)

    # �նȺϼƸ���ָ��
    daily_northmoney = north_money.groupby('day').sum()
    daily_northmoney.index = pd.to_datetime(daily_northmoney.index)

    # ���㾻��
    return daily_northmoney['buy_amount'] - daily_northmoney['sell_amount']


# ����������ָ�깹��
class Northflow(TransformerMixin, BaseEstimator):

    def __init__(self, shortperiod: int, longperiod: int):

        self.shortperiod = shortperiod
        self.longperiod = longperiod

    def fit(self, X, y=None):

        return self

    def transform(self, X):

        l = X.ewm(span=self.longperiod, adjust=False).mean()

        s = X.ewm(span=self.shortperiod, adjust=False).mean()

        north_factor = (s - l) / X.rolling(self.longperiod).std()
       

        return north_factor.dropna()

    
# �ʽ������Թ���
class NorthflowStrategy(BaseEstimator):

    def __init__(self, threshold_h: float, threshold_l: float):

        self.threshold_h = threshold_h
        self.threshold_l = threshold_l

    # ���������ѵ����
    def fit(self, X, y):
        '''
        X:������ʱ����
        y:��������
        '''

        return self.predict(X) * y.shift(-1)

    # ������ν����ź�����
    def predict(self, X):
        '''X:������ʱ����'''
        flag = pd.Series(index=X.index)
        per_s = X.shift(1)

        previous_day = X.index[0]

        for trade, v in X.items():

            if v > self.threshold_h:

                flag[trade] = 1
            elif v < self.threshold_l:
                flag[trade] = 0

            else:

                flag[trade] = np.nan_to_num(flag[previous_day])

            previous_day = trade

        return flag

    # ����жϲ�������������
    def score(self, X, y):

        returns = self.fit(X, y)

        # �Ż�ָ��Ϊ�� ������� + ����
        # ����Խ��Խ��
        
        risk = ep.calmar_ratio(returns) + ep.sharpe_ratio(returns)
        
        return risk
        
##########����#################
from sklearn.model_selection import RandomizedSearchCV
import scipy.stats as st

# �ز�ʱ������
start = '2017-01-01'
end = '2020-08-27'

# ��ȡ��������
net_flow = get_net_north_flow(start,end)

# ��׼
index_df = get_price('000300.XSHG', start, end, fields='close')

ret_ser = index_df['close'].pct_change().reindex(net_flow.index)

# ����PIPELINE
north_factor = Pipeline([('creatfactor', Northflow(5, 10)),
                         ('backtesting', NorthflowStrategy(0.2, -0.1))])

# Ѱ�η�Χ����
## ��ֵ
norm_rv = st.norm(loc=-0.5, scale=0.45)
## north_indictor���� ema�������ڴ�3��100
randint = st.randint(low=3, high=100)


# ��������
param_grid = {'creatfactor__shortperiod': randint,
              'creatfactor__longperiod': randint,
              'backtesting__threshold_h': norm_rv,
              'backtesting__threshold_l': norm_rv}


grid_search = RandomizedSearchCV(
    north_factor, param_grid, n_iter=400, verbose=2, n_jobs=3,random_state=42)

grid_search.fit(net_flow, ret_ser)

#############################################

# ���Ų���
grid_search.best_params_


#�鿴���Ų�����ֵ
# ʹ�����Ų���������ƽ�� ʹ�����Ź���
flag = grid_search.best_estimator_.predict(net_flow)

# ����������
algorithm_ret = flag * ret_ser.shift(-1)
# ��ͼ
np.exp(np.log1p(algorithm_ret).cumsum()).plot(
     figsize=(18, 8), label='North_flow')
    
np.exp(np.log1p(ret_ser).cumsum()).plot(label='HS300')

plt.legend()


# ��������
print_table(get_strategy_risk(algorithm_ret).apply(
    lambda x: '{:.2%}'.format(x)))
    	
# ���ڳ���
def get_params(X:pd.Series,y:pd.Series,high_limit:int):
    
    norm_rv = st.norm(loc=-0.5, scale=0.45)
    
    randint = st.randint(low=3, high=high_limit)
    
    # ��������
    param_grid = {'creatfactor__shortperiod': randint,
                  'creatfactor__longperiod': randint,
                  'backtesting__threshold_h': norm_rv,
                  'backtesting__threshold_l': norm_rv}
    # ����PIPELINE
    north_factor = Pipeline([('creatfactor', Northflow(5, 10)),
                             ('backtesting', NorthflowStrategy(0.2, -0.1))])

    grid_search = RandomizedSearchCV(
        north_factor, param_grid, n_iter=400, n_jobs=3)

    grid_search.fit(X, y)
    
    return grid_search.best_estimator_
        	
# ÿ��10�ո���һ�β���
basce = 0

window = 90 # ѵ������
step = 10 # ÿ10�ո���һ�β���
length = len(net_flow)
flag_list = []

for i in tqdm_notebook(range(window,length - step,step),desc='������'):
    
    X = net_flow.iloc[basce:i]
    y = ret_ser.iloc[basce:i]
    
    if i < 255:
        
        tmp = get_params(X, y,30).predict(net_flow.iloc[basce:i+step])
        
        idx = net_flow.index[i:i+step]
        flag_list.append(tmp.loc[idx])
        
    else:
        
        tmp = get_params(X, y,60).predict(net_flow.iloc[basce:i+step])
        
        idx = net_flow.index[i:i+step]
        flag_list.append(tmp.loc[idx])
        

flag_ser = pd.concat(flag_list)

algorithm_ret = flag_ser * ret_ser.reindex(flag_ser.index).shift(-1)
np.exp(np.log1p(algorithm_ret).cumsum()).plot(
    figsize=(12, 6), label='algorithm')
np.exp(np.log1p(ret_ser).cumsum()).plot(label='HS300')
plt.legend()

# ��������
print_table(get_strategy_risk(algorithm_ret).apply(
    lambda x: '{:.2%}'.format(x)))
    	


  