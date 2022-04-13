# ���볣�ÿ�
import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf # ��λ���ع�����
import scipy.stats as st
import datetime as dt
import itertools # ����������
import math

#import pysnooper # debug
import pickle
from IPython.core.display import HTML

#from jqdata import *
#from jqfactor import *
import talib # ��������



# ��ͼ
import matplotlib.pyplot as plt
import matplotlib.dates as mdate
import seaborn as sns
# �������� ����������ʾ���ı�ǩ
plt.rcParams['font.sans-serif'] = ['SimHei']

# ����������ʾ����
plt.rcParams['axes.unicode_minus'] = False
# ͼ������
plt.style.use('ggplot')

# ���Ա���
import warnings
warnings.filterwarnings("ignore")


# ʹ��ts
#import tushare as ts
import sys 
sys.path.append("G://GitHub//PairsTrading//new_stategy//Quantitative-analysis//") 
import foundation_tushare 
import json

# ������Լ��������дts��token
setting = json.load(open('C:\config\config.json'))
my_ts  = foundation_tushare.TuShare(setting['token'], max_retry=60)



# ͼ��2 ��֤��ָ��ͬ�����µ���ʷ�����ʶԱȣ��ղ����ʣ�δ�껯��

start = '20000101'
end = '20220412'
# ��ȡ��֤��������
#close_df = get_price('000001.XSHG', start, end, fields=['close', 'pre_close'])
index_df = my_ts.query('index_daily', ts_code='000001.SH', 
start_date=start, end_date=end,fields='trade_date,close,pre_close') 
close_df=index_df
close_df['pct'] = close_df['close']/close_df['pre_close']-1
close_df.index=close_df['trade_date']
close_df=pd.DataFrame(close_df[['close', 'pre_close','pct']] )
close_df=close_df.sort_index() 
close_df.columns = ['close', 'pre_close','pct'] 
# ����������
#
from datetime import datetime
close_df.index=[datetime.strptime(x,'%Y%m%d') for x in close_df.index]
close_df=close_df.sort_index()

# ��ͼ
plt.figure(figsize=(22, 8))
# ����n�ղ�����  δ�껯����
for periods in [60, 120, 200, 250]:

    col = 'std_'+str(periods)
    close_df[col] = close_df['pct'].rolling(periods).std()
    plt.plot(close_df[col], label=col)

plt.legend(loc='best')
plt.xlabel('ʱ��')
plt.ylabel('������')
plt.title('��֤��ָ��ͬ�����µ���ʷ�����ʶԱȣ��ղ����ʣ�δ�껯��')
plt.show()


# ͼ��3 ��֤��ָ����250�ղ�����

y1 = close_df['close']  # ��ȡ��������
y2 = close_df['std_250']  # ��ȡ250�ղ�����
fig = plt.figure(figsize=(18, 8))  # ͼ���С����

ax1 = fig.add_subplot(111)

ax1.plot(y1, label='close')
ax1.set_ylabel('���̼�')
plt.legend(loc='upper left')


ax2 = ax1.twinx()  # ����˫Y�� �ؼ�function
ax2.plot(y2, '#87CEFA')
ax2.set_ylabel('������')
plt.legend(loc='best')

ax1.set_title("��֤��ָ����250�ղ�����")
ax1.xaxis.set_major_formatter(mdate.DateFormatter('%Y-%m'))  # x����ʾY-m
plt.xlabel('ʱ��')
plt.show()

'''���м���

'''
from multiprocessing import cpu_count
from joblib import Parallel, delayed
import time

def func(periods):
    col = 'std_'+str(periods)
    close_df[col] = close_df['pct'].rolling(periods).std()
    return close_df

start_time = time.time()
cpu_count = cpu_count()
print("cpu_count = ", cpu_count)

out = Parallel(n_jobs = cpu_count, backend='multiprocessing')(delayed(func)(periods) for i in [60, 120, 200, 250])
 
end_time = time.time()
print("use time: ", end_time - start_time)

'''���м�������
from multiprocessing import cpu_count
from joblib import Parallel, delayed
import time
 
 
 
# (1) parallel
 
def func(_input):
    time.sleep(1) # ǰ����Ҫ����server����������������࣬ǰ�ߵ���ʱ�����ں���
    return _input * 3
 
 
start_time = time.time()
cpu_count = cpu_count()
print("cpu_count = ", cpu_count)
 
out = Parallel(n_jobs = cpu_count, backend='multiprocessing')(delayed(func)(i) for i in range(100))
 
end_time = time.time()
print("use time: ", end_time - start_time)
 
# cpu_count =  4
# use time:  27.145534992218018
 
 
# (2) not parallel
 
start_time = time.time()
 
out1 = [func(i) for i in range(100)]
end_time = time.time()
print("use time: ", end_time - start_time)
 
# use time:  101.21378898620605
'''

#  ͼ��4:��֤��ָ�벨���ʵĹ������ϵ��

y1 = close_df['close'] # ��ȡ��������

# ��ȡ250�ղ����������̼۹���1�����ϵ��corr
y2 = close_df['close'].rolling(250).corr(close_df['std_250']) 

fig,ax = plt.subplots(1,1,figsize=(18,8)) # ͼ���С����


ax.plot(y1,label='close') 
ax.set_ylabel('���̼�')
plt.legend(loc='upper left')

ax1 = ax.twinx()  # ����˫Y�� �ؼ�function
ax1.plot(y2,'#87CEFA',label='corr')
ax1.set_ylabel('���ϵ��')
plt.legend(loc='upper right')

ax1.set_title("��֤��ָ����250�ղ�����")
ax1.xaxis.set_major_formatter(mdate.DateFormatter('%Y-%m')) # x����ʾY-m
plt.xlabel('ʱ��')
plt.show()

# ͼ5��6 ��֤��ָ�ջ�����(���������tushare���ݣ���Ҫtushare 400���ֲ��ܵ���)

# tushare=>float_share��ͨ�ɱ� ����ɣ���free_share������ͨ�ɱ� ����
# tushare ָ�����ݴ�2004�꿪ʼ�ṩ....�е��β�ѯ����
part_a = my_ts.index_dailybasic(ts_code='000001.SH',
                                start_date=start.replace('-', ''),
                                end_date='20160101',
                                fields='ts_code,trade_date,turnover_rate,turnover_rate_f')

part_b = my_ts.index_dailybasic(ts_code='000001.SH',
                                start_date='20160101',
                                end_date=end.replace('-', ''),
                                fields='ts_code,trade_date,turnover_rate,turnover_rate_f')

index_daily_df = part_a.append(part_b)  # �ϲ�����
index_daily_df.index = pd.to_datetime(index_daily_df.trade_date)  # ��������
index_daily_df.sort_index(inplace=True)  # ����

# ��ͼ
fig, ax = plt.subplots(1, 2, figsize=(18, 8))
fig.suptitle('��֤��ָ�ջ�����')

x = index_daily_df.index
ax[0].bar(x, index_daily_df['turnover_rate'])
ax[0].set_title('��������ͨ�ɱ��Ļ�����')

ax[1].bar(x, index_daily_df['turnover_rate_f'])
ax[1].set_title('����������ͨ�ɱ��Ļ�����')

plt.show()



# ͼ��7  ��֤��ָ��ͬ�����µ��վ�������

# ��ͼ
plt.figure(figsize=(18, 8))
for periods in [60, 120, 200, 250]:

    col = 'turnover_rate_'+str(periods)
    index_daily_df[col] = index_daily_df['turnover_rate_f'].rolling(
        periods).mean()
    plt.plot(index_daily_df[col], label=col)

plt.legend(loc='best')
plt.xlabel('ʱ��')
plt.ylabel('������')
plt.title('��֤��ָ��ͬ�����µ��վ�������')
plt.show()


# ͼ��8 ��֤��ָ�� 250 �ջ�����

close_df['turnover_rate_250'] = index_daily_df['turnover_rate_250']
y1 = close_df['close']  # ��ȡ��������
y2 = close_df['turnover_rate_250']  # ��ȡ250�ղ�����
fig = plt.figure(figsize=(18, 8))  # ͼ���С����

ax1 = fig.add_subplot(111)

ax1.plot(y1, label='close')
ax1.set_ylabel('���̼�')
plt.legend(loc='upper left')


ax2 = ax1.twinx()  # ����˫Y�� �ؼ�function
ax2.plot(y2, '#87CEFA')
ax2.set_ylabel('������')
plt.legend(loc='best')

ax1.set_title("��֤��ָ�� 250 �ջ�����")
ax1.xaxis.set_major_formatter(mdate.DateFormatter('%Y-%m'))  # x����ʾY-m
plt.xlabel('ʱ��')
plt.show()

'''
��֤��ָ�ǵ�����ʷ����
���ǽ����ڲ������뻻��������ά�������г����й۲죬��������Ͷ��ʱ�ӣ����Խ��г���Ϊ����״̬��
�����ʻ�����ͬʱ���С������ʻ�����ͬʱ���С����������л��������С� ���������л��������С�
������״̬��Ӧ���г������н�ǿ�Ĺ����ԡ��ڲ��������С��� �������е�״̬�£��г��ǵ��͵�����������
�г����µ�һ�����ʹ�ò��������У���һ �����ʹ�ɽ���ή������ɻ��������У��ڲ����ʺͻ�����ͬʱ����ʱ��
�г��ǵ��͵�ţ ���������г���������ʹ�ò��������У�Ͷ���ߵĽ����������ʹ�û��������У������� ���С�����������ʱ��
�г�����Ҳ�����ȽϺã�����׶ξ�����ţ�еĳ��ڻ�������֮�� �ķ����������ʺͻ�����ͬʱ���У����������������У�
����׶��г��ķ����Բ����жϣ��������µ�Ҳ���������ǡ�
'''

#  ͼ��9 �������뻻���ʶ���֤��ָ����״̬�Ļ���

y1 = close_df['close']  # ��ȡ��������
y2 = close_df['turnover_rate_250']  # ��ȡ250�ղ�����
y3 = close_df['std_250']*100*2  # ������Ϊ%����������Ҫ*100
fig = plt.figure(figsize=(18, 8))  # ͼ���С����

ax1 = fig.add_subplot(111)

ax1.plot(y1, linestyle='-.', label='close')
ax1.set_ylabel('���̼�')
plt.legend(loc='upper left')


ax2 = ax1.twinx()  # ����˫Y�� �ؼ�function
ax2.plot(y2, '#00FA9A')
ax2.plot(y3, '#00CED1')
ax2.set_ylabel('������\������')
plt.legend(loc='best')

ax1.set_title("�������뻻���ʶ���֤��ָ����״̬�Ļ���")
ax1.xaxis.set_major_formatter(mdate.DateFormatter('%Y-%m'))  # x����ʾY-m
plt.xlabel('ʱ��')
plt.show()


# ͼ��11

# ����ţ��ָ��

close_df['kernel_index'] = close_df['std_200'] / \
    index_daily_df['turnover_rate_200']

y1 = close_df['close']  # ��ȡ��������
y2 = close_df['kernel_index']  # ��ȡ250�ղ�����

fig = plt.figure(figsize=(18, 8))  # ͼ���С����

ax1 = fig.add_subplot(111)

ax1.plot(y1, label='close')
ax1.set_ylabel('���̼�')
plt.legend(loc='upper left')


ax2 = ax1.twinx()  # ����˫Y�� �ؼ�function
ax2.plot(y2, '#87CEFA')
ax2.set_ylabel('ţ��ָ��')
plt.legend(loc='best')

ax1.set_title("��֤��ָ���̼������Ӧ��ţ��ָ��")
ax1.xaxis.set_major_formatter(mdate.DateFormatter('%Y-%m'))  # x����ʾY-m
plt.xlabel('ʱ��')
plt.show()    

# ������������


'''
jqdata���� ָ������ò��û�� ������(����������ͨ�ɱ�),������(��������ͨ�ɱ�)
�Լ���������ͨ�ɱ�̫�鷳 ��Ϊ�б�˵�������첻�� ���Ծ͹��� ������(��������ͨ�ɱ�)

��������ٶȿ϶�����,�����ڷ���ʱ�һ�����ts����,���ʵ��û��tsȨ�޿���ʹ�����,
��������ts��turnover_rate�е����
'''


def Cal_index_turnover(indexId, start, end):
    '''
    indexId Ϊָ������
    ----------
    return Series
    '''
    tradeList = get_trade_days(start, end)

    temp = {}  # �����м�����
    for trade_date in tradeList:

        security = get_index_stocks(indexId, date=trade_date)  # ��ȡ�ɷֹ�

        # ��ѯ����ͨ�ɱ�
        q_circulating_cap = query(valuation.code,
                                  valuation.circulating_cap).filter(valuation.code.in_(security))

        circulating_cap = get_fundamentals(q_circulating_cap, date=trade_date)

        # ��ȡ�ɽ���,ע�Ͳ��ּ�����������ts���ݵ�����,��֪��Ϊʲô
        volume = get_price(indexId, end_date=trade_date,
                           count=1, fields='volume')
        # volume=get_price(security, end_date=trade_date,count=1, fields='volume,paused').to_frame()

        # ����ͨ�ɱ�������
        turnover = volume['volume'].sum(
        )/circulating_cap['circulating_cap'].sum()
        # turnover=volume.query('paused==0')['volume'].sum()/circulating_cap['circulating_cap'].sum()

        temp[trade_date] = turnover
        print('success', trade_date)

    ser = pd.Series(temp)
    ser.name = 'turnover_rate'
    return ser


# -----------------------------------------------------------------------
#               �����ź����ɼ�����ģ��
# -----------------------------------------------------------------------
'''
ģ��ʹ��ts��������
ts_code xxxxx.SH �Ϻ���xxxxxx.SZ ����

e.g:��֤���룺000001.SH,hs300:000300.SH,��֤500:000905.SH�����ʽ�Դ�����

���ڣ�yyyymmmdd
'''


class VT_Factor(object):

    def __init__(self, indexId, start, end, periods, forward_n=[5, 10, 15, 20]):

        self.indexId = indexId  # ָ������
        self.start = start  # ��ʼ����
        self.end = end  # ��������
        self.periods = periods  # Ϊָ���������
        self.forward_n = forward_n  # ��Ҫ��ȡδ��n�������list
    # ---------------------------------------------------------------------
    #                   ���ݻ�ȡ ts
    # ---------------------------------------------------------------------

    '''
    ��������Ϊ2004��1�¿�ʼ
    ts��һָ�������ȡ12�������,��ָ�����3000��
    '''
    @property
    def get_data(self):
        '''
        return df index-date columns-close|pct_chg|turnover_rate_f
        '''
        indexId = self.indexId
        start = self.start
        end = self.end

        # ��ȡ������ͨ ������
        '''
        turnover = my_ts.index_dailybasic(ts_code=indexId,
                                          start_date=start,
                                          end_date=end,
                                          fields='trade_date,turnover_rate_f').set_index('trade_date')                            
        '''

        turnover = self.get_turnover

        # ��ȡ���̼�����
        close = my_ts.index_daily(ts_code=indexId,
                                  start_date=start,
                                  end_date=end,
                                  fields='trade_date,close,pct_chg').set_index('trade_date')

        df = close.join(turnover)
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)
        return df

    # ��ȡts index_dailybasic �ƹ���ȡ����
    @property
    def get_turnover(self):

        indexId = self.indexId
        start = self.start
        end = self.end

        total = my_ts.trade_cal(exchange='SSE', start_date=start, end_date=end)
        trade_list = total.query('is_open==1').cal_date.values.tolist()
        trade_size = len(trade_list)  # ��ȡ�ܳ���
        

        if trade_size <= 3000:

            df = my_ts.index_dailybasic(ts_code=indexId,
                                        start_date=start,
                                        end_date=end,
                                        fields='trade_date,turnover_rate_f').set_index('trade_date')

            return df

        else:

            count = int(math.ceil(trade_size/3000.0))  # ��Ҫѭ���Ĵ���
            
            temp = []
            temp.append(min(trade_list))

            for i in range(1, count+1):
                
                idx = trade_list[min(i*3000,trade_size-1)]
                temp.append(idx)

            temp_df = []
            for x in zip(temp[:-1], temp[1:]):
                df = my_ts.index_dailybasic(ts_code=indexId,
                                            start_date=x[0],
                                            end_date=x[1],
                                            fields='trade_date,turnover_rate_f').set_index('trade_date')
                temp_df.append(df)

            return pd.concat(temp_df)

    # ---------------------------------------------------------------------
    #                   ţ��ָ�깹��
    # ---------------------------------------------------------------------

    # ����ţ��ָ��
    def _Calc_func(self, x_df):
        '''
        ����Ϊdf index-date column-turnovet_rate_f|close|pct_chg
        ============
        return series/pd index-date valus-ţ��ָ�� kernel_n
        '''
        df = x_df.copy()
        periods = self.periods  # ��ȡ��������
        if not isinstance(periods, list):
            periods = [periods]

        # ����ţ��ָ��
        series_temp = []
        for n in periods:
            turnover_ma = df['turnover_rate_f'].rolling(n).mean()
            std = df['pct_chg'].rolling(n).std(ddof=0)
            kernel_factor = std/turnover_ma
            kernel_factor.name = 'kernel_'+str(n)
            series_temp.append(kernel_factor)

        if len(series_temp) == 1:

            return kernel_factor

        else:

            return pd.concat(series_temp, axis=1)

    # ��ȡ�ź�
    @property
    def get_singal(self):
        '''
        return df index-date columns-close|pct_chg|kernel_n|turnover_rate_f

        '''
        data = self.get_data  # ��ȡ����
        singal_df = self._Calc_func(data)  # ��������
        data = data.join(singal_df)

        return data

    # ---------------------------------------------------------------------
    #                   �ź�ָ��δ��������ط�������
    # ---------------------------------------------------------------------

    # ����δ������
    def _Cal_forward_ret(self, x_df, singal_periods):
        '''
        dfΪ�ź����� index-date columns-close|pct_chg|kernel_n
        singal_periods int
        forwart_n ��Ҫ��ȡδ��n�������list
        ===========
        return df

        index-date colums kernel_n|δ��x������|pct_chg
        '''

        forward_n = self.forward_n  # ��ȡN��δ������

        df = x_df[['close', 'pct_chg', 'kernel_'+str(singal_periods)]].copy()

        # ��ȡָ������
        df['δ��1��������'] = df['pct_chg'].shift(-1)  # next_ret

        for n in forward_n:
            col = 'δ��{}��������'.format(n)
            df[col] = df['close'].pct_change(n).shift(-n)  # next_ret_n

        df = df.drop('close', axis=1)  # ��������Ҫ����

        return df

    # �źŷֶζ�Ӧ��������

    def forward_distribution_plot(self, singal_periods, bins=50):
        '''
        bins ����
        =============
        return ͼ��
        '''

        data = self.get_singal  # ��ȡ�ź�����
        forward_df = self._Cal_forward_ret(data, singal_periods)  # ��ȡδ������
        slice_arr = pd.cut(
            forward_df['kernel_'+str(singal_periods)], bins=bins)  # �źŷ�Ϊ��

        forward_df['barrel'] = slice_arr

        group_ret = [x for x in forward_df.columns if x.find(
            '��������') != -1]  # ��ȡδ��������

        list_size = len(group_ret)  # ��ͼ����

        # ��ͼ
        f, axarr = plt.subplots(list_size, figsize=(18, 15))  # sharex=True ����ͼ
        f.suptitle(' �źŶ�Ӧ����ֲ�')  # �����ܱ���

        # ������ͼ�����
        f.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.95, hspace=0.65,
                          wspace=0.35)

        for i in range(list_size):

            ret_series = forward_df.groupby('barrel')[group_ret[i]].mean()
            x = ret_series.index.astype('str').tolist()

            axarr[i].bar(x, ret_series.values)  # ����ͼ
            axarr[i].set_title(group_ret[i])  # ������ͼ����
            axarr[i].set_xticklabels(x, rotation=90)  # ������ͼ�̶ȱ�ǩ����ǩ��ת

        plt.show()

    # �����ź�λ������������ϵ��
    def QuantReg_plot(self, forward_ret_name, singal_periods):
        '''
        forward_ret_name ��Ҫ�Ƚϵ�δ�����������
        '''
        data = self.get_singal  # ��ȡ�ź�����

        forward_df = self._Cal_forward_ret(data, singal_periods)  # ��ȡδ������

        x = forward_ret_name  # ����δ����������
        traget = 'kernel_'+str(singal_periods)+'~'+x

        mod = smf.quantreg(traget, forward_df)
        res = mod.fit(q=.5)
        print(res.summary())

        quantiles = np.arange(.05, .96, .1)

        def fit_model(q):
            res = mod.fit(q=q)
            # conf_intΪ��������
            return [q, res.params['Intercept'], res.params[x]] + \
                res.conf_int().loc[x].tolist()

        models = [fit_model(q_i) for q_i in quantiles]
        models_df = pd.DataFrame(
            models, columns=['quantiles', 'Intercept', x, 'lb', 'ub'])

        n = models_df.shape[0]

        plt.figure(figsize=(18, 8))
        p1 = plt.plot(models_df['quantiles'], models_df[x],
                      color='red', label='Quantile Reg.')
        p2 = plt.plot(models_df['quantiles'], models_df['ub'],
                      linestyle='dotted', color='black')
        p3 = plt.plot(models_df['quantiles'], models_df['lb'],
                      linestyle='dotted', color='black')

        plt.ylabel(r'$\beta_{RETURNS}$')
        plt.xlabel('�źŷ�λ��')
        plt.legend()
        plt.show()

# ---------------------------------------------------------------------
#                   �ز�
# ---------------------------------------------------------------------


class BackTesting(object):
    '''
    �����df �������ź����� ������pct_chg
    '''

    def __init__(self, x_df, singal_name, method, hold=None, **threshold):

        self.df = x_df.copy()
        self.threshold = threshold
        self.hold = hold
        self.singal_name = singal_name  # ��Ҫ�ز��col_name
        self.method = method

    # ѡ��ز����
    @property
    def Choose_Strategy(self):

        threshold = self.threshold
        hold = self.hold
        method = self.method

        if method:
            if method == 'MA':
                return (4, '����������')
            elif method == 'BBANDS':
                return (5, '����ͨ������')
            else:
                return 0
        else:
            # ����ֵ��ΪԪ��ʱ˵��ֻ�е�ֵ����ֵĬ��Ϊ�����ź�
            k = list(threshold.keys())[0]  # key
            threshold_value = threshold[k]  # ���������ֵ��(a,b),��ֵΪa
            # ��ֵ+�гֲ�
            # 1.���ֿ����ź�ʱ����,����N���ƽ��
            if not isinstance(threshold_value, tuple) and hold != None:

                return (1, '���ֿ����ź�ʱ����,����N���ƽ��')

            # ��ֵ+�޳ֲ�
            # 2.���ڿ����źſ���,ֱ��С�ڿ����ź�ƽ��
            elif not isinstance(threshold_value, tuple) and hold == None:

                return (2, '���ڿ����źſ��֣�ֱ��С�ڿ����ź�ƽ��')

            # ˫ֵ+�޳ֲ�
            # 3. a<�ź�<b ʱ����,��֮���ֿղ�(�в�λ��ƽ��)
            elif isinstance(threshold_value, tuple) and hold == None:

                return (3, 'a<�ź�<b ʱ����,��֮���ֿղ�(�в�λ��ƽ��)')

            else:

                return 0  # ���ܳ����������

    # 1.���ֿ����ź�ʱ����,����N���ƽ��

    def Strategy_a(self, x_df):
        '''
        ���ֱ�ǵ� list
        '''
        threshold = self.threshold
        hold = self.hold
        count = hold
        data = x_df.copy()  # �����ź�

        k = list(threshold.keys())[0]  # key
        threshold_value = threshold[k]
        singal_arr = data['SINGAL'].values

        trade_mark = np.where(singal_arr > threshold_value, 1, 0)  # ��ǽ��׵�

        # ��ȡ�źŵ�
        position = []
        for x in trade_mark:
            if x == 1:
                position.append(1)
                count = 1
            else:
                if count < hold:
                    count += 1
                    position.append(1)
                else:
                    position.append(0)

        return position  # ���ֱ�ǵ�

    # 2.���ڿ����źſ���,ֱ��С�ڿ����ź�ƽ��

    def Strategy_b(self, x_df):

        threshold = self.threshold
        hold = self.hold

        data = x_df.copy()  # �����ź�

        k = list(threshold.keys())[0]  # key
        threshold_value = threshold[k]
        singal_arr = data['SINGAL'].values

        trade_mark = np.where(singal_arr > threshold_value, 1, 0)  # ��ǽ��׵�

        return list(trade_mark)

    # 3. a<�ź�<b ʱ����,��֮���ֿղ�(�в�λ��ƽ��)

    def Strategy_c(self, x_df):

        threshold = self.threshold
        hold = self.hold

        data = x_df.copy()  # �����ź�

        k = list(threshold.keys())[0]  # key
        threshold_value = threshold[k]

        open_singal = threshold_value[0]  # a
        close_singal = threshold_value[1]  # b

        singal_arr = data['SINGAL'].values

        # a<�ź�<b
        trade_mark = np.select([singal_arr < open_singal,
                                np.logical_and(
                                    singal_arr >= open_singal, singal_arr <= close_singal),
                                singal_arr > close_singal], [0, 1, 0])

        return list(trade_mark)

    # 4. ���߲���
    def Strategy_MA(self, x_df, inverts=False):
        '''
        inverts��True �������� False ��������
        ======
        returns list
        '''
        data = x_df.copy()
        singal_arr = self._Cal_MA(data)  # ��ȡ�״γ��ֽ������ı�ǵ� 1Ϊ��棬-1Ϊ����

        trade_mark = []
        # ��������
        if inverts:
            for i in singal_arr:
                if i == 1:
                    trade_mark.append(1)
                else:
                    if len(trade_mark) > 0 and trade_mark[-1] == 1 and i != -1:
                        trade_mark.append(1)
                    else:
                        trade_mark.append(0)

        else:
            # ������
            for i in singal_arr:
                if i == -1:
                    trade_mark.append(1)
                else:
                    if len(trade_mark) > 0 and trade_mark[-1] == 1 and i != 1:
                        trade_mark.append(1)
                    else:
                        trade_mark.append(0)

        return trade_mark  # list

    # 5.����ͨ������

    def Strategy_BBANDS(self, x_df, inverts=False):
        '''
        inverts��True �������� False ��������
        ======
        returns list
        '''
        data = x_df.copy()
        singal_arr = self._Cal_BBANDS(data)  # ��ȡ�״γ��ֽ������ı�ǵ� 1Ϊ��棬-1Ϊ����

        trade_mark = []
        # ��������
        if inverts:
            for i in singal_arr:
                if i == 1:
                    trade_mark.append(1)
                else:
                    if len(trade_mark) > 0 and trade_mark[-1] == 1 and i != -1:
                        trade_mark.append(1)
                    else:
                        trade_mark.append(0)

        else:
            # ������
            for i in singal_arr:
                if i == -1:
                    trade_mark.append(1)
                else:
                    if len(trade_mark) > 0 and trade_mark[-1] == 1 and i != 1:
                        trade_mark.append(1)
                    else:
                        trade_mark.append(0)

        return trade_mark  # list

    # -------------------------------------------------------------------------------------
    #                             ����������Ͳ���ͨ����ͻ��
    # ------------------------------------------------------------------------------------

    '''
    Cal_MA ������ߵĽ������ ���Ϊ1������Ϊ-1
    Cal_BBANDS ����ͻ�����¹� ͻ���Ϲ�1��ͻ���¹�-1
    ��ǵĶ���*�״�*���ֵ�

    '''
    # 4-1.����20�վ�����60�վ��ߵĽ�棬����

    def _Cal_MA(self, x_df):

        df = x_df.copy()

        df['MA_20'] = df['SINGAL'].rolling(20).mean()
        df['MA_60'] = df['SINGAL'].rolling(60).mean()
        df['diff'] = df['MA_20']-df['MA_60']  # Ϊ������ʾma20<ma60
        df['pre_diff'] = df['diff'].shift(1)  # ����diff

        # ���/���� ���1 ����-1 else 0a
        # if x['pre_diff']<0 and x['diff']>=0  ���
        # if x['pre_diff']>0 and x['diff']<=0 ����
        df['mark'] = df[['pre_diff', 'diff']].apply(lambda x: 1 if x['pre_diff'] < 0 and x['diff'] >= 0
                                                    else (-1 if x['pre_diff'] > 0 and x['diff'] <= 0 else 0), axis=1)

        return df['mark'].values.tolist()  # list

    # 5-1.����ͨ������
    def _Cal_BBANDS(self, x_df):

        df = x_df.copy()

        df['MA_20'] = df['SINGAL'].rolling(20).mean()
        std_arr = df['SINGAL'].rolling(20).std()
        df['UP'] = df['MA_20']+2*std_arr
        df['LOW'] = df['MA_20']-2*std_arr

        df['updiff'] = df['SINGAL']-df['UP']
        df['lowdiff'] = df['SINGAL']-df['LOW']

        df['pre_updiff'] = df['updiff'].shift(1)
        df['pre_lowdiff'] = df['lowdiff'].shift(1)

        def mark_func(x):
            return 1 if x['pre_updiff'] < 0 and x['updiff'] >= 0 else (-1 if x['pre_lowdiff'] > 0 and x['lowdiff'] <= 0 else 0)

        df['mark'] = df[['pre_updiff', 'updiff', 'pre_lowdiff', 'lowdiff']].apply(
            mark_func, axis=1)

        return df['mark'].values.tolist()

    # ----------------------------------------------------------------------

    # �ز�
    '''
    1.���ֿ����ź�ʱ����,����N���ƽ�֣�
    2.���ڿ����źſ���,ֱ��С�ڿ����ź�ƽ�֣�
    3. a<�ź�<b ʱ����,��֮���ֿղ�(�в�λ��ƽ��)��
    '''
    @property
    def back_testing(self):
        '''
        Ϊ�����źŴ��ϱ��
        return df x_trade_markΪ��ǵ�
        '''

        data = self.df  # �����df
        singal_name = self.singal_name

        strategy_dic = {1: self.Strategy_a,
                        2: self.Strategy_b, 3: self.Strategy_c,
                        4: self.Strategy_MA, 5: self.Strategy_BBANDS, 0: '��������'}

        if not isinstance(singal_name, list):
            singal_name = [singal_name]

        inverts = False  # Ĭ��Ϊţ��ָ��
        for s in singal_name:

            # ��Ŀ���źŸ�ΪSINGAL
            data = data.rename(columns={s: 'SINGAL'})

            # ��ȡ��ǵ�
            strategy_x = self.Choose_Strategy

            if strategy_x[0] < 4:

                # print(strategy_x[1])  # ��������߼�
                trade_mark = strategy_dic[strategy_x[0]](data)
                data[s+'_MARK'] = trade_mark
                # ���ָĻ�
                data.rename(columns={'SINGAL': s}, inplace=True)

            elif strategy_x[0] >= 4:

                if s == 'close':
                    inverts = True

                trade_mark = strategy_dic[strategy_x[0]](data, inverts)
                data[s+'_MARK'] = trade_mark
                # ���ָĻ�
                data.rename(columns={'SINGAL': s}, inplace=True)
            else:
                print(strategy_x[1])

        return data

    # ����ֵͼ
    @property
    def plot_net_value(self):

        back_df = self.back_testing  # ��ȡ�ز�����
        back_df['pct_chg'] = back_df['pct_chg']/100
        back_df['NEXT_RET'] = back_df['pct_chg'].shift(-1)

        # Ѱ�ұ����
        mark_list = [x for x in back_df.columns if x.split('_')[-1] == 'MARK']

        fig = plt.figure(figsize=(20, 10))
        ax1 = fig.add_subplot(1, 1, 1)

        # ����
        for n in mark_list:
            RET = back_df['NEXT_RET']*back_df[n]
            CUM = (1+RET).cumprod()
            ax1.plot(CUM, label=n)

        # ��׼��ֵ
        benchmark = (1+back_df['pct_chg']).cumprod()

        ax1.plot(benchmark, label='benchmark')

        ax1.xaxis.set_major_formatter(mdate.DateFormatter('%Y-%m'))
        plt.legend(loc='best')
        plt.xlabel('ʱ��')
        plt.ylabel('��ֵ')
        plt.title('���Ծ�ֵ����')
        plt.show()

    # �زⱨ��
    @property
    def summary(self):

        back_df = self.back_testing

        index_name = '�껯������,�ۼ�������,���ձ���,���س�,�ֲ�������,���״���,ƽ���ֲ�����,��������, \
        ��������,ʤ��(����),ƽ��ӯ����(����),ƽ��������(����),ƽ��ӯ����(����),ӯ������,�������, \
        �������ӯ��,����������,ʤ��(����),ƽ��ӯ����(����),ƽ��������(����),ƽ��ӯ����(����)'.split(
            ',')

        # Ѱ�ұ���
        mark_list = [x for x in back_df.columns if x.split('_')[-1] == 'MARK']

        temp = []
        mark_size = len(mark_list)  # ����

        if mark_size > 1:

            for m in mark_list:

                df = pd.DataFrame(self.risk_indicator(
                    back_df, m), index=index_name)
                temp.append(df)

            return pd.concat(temp, axis=1)

        else:

            return pd.DataFrame(risk_indicator(back_df, m), index=index_name)

    # �������ָ��

    def risk_indicator(self, x_df, mark_col):
        '''
        ���뾭back_testing

        '''
        df = x_df.copy()

        summary_dic = {}

        # ��ʽ������
        def format_x(x):
            return '{:.2%}'.format(x)

        # ��ȡ�ز�����
        df['pct_chg'] = df['pct_chg']/100
        df['NEXT_RET'] = df['pct_chg'].shift(-1)

        NOT_NAN_RET = df['NEXT_RET'].dropna()*df[mark_col]
        RET = df['NEXT_RET']*df[mark_col]

        CUM_RET = (1+RET).cumprod()  # series

        # �����껯������
        annual_ret = CUM_RET.dropna()[-1]**(250/len(NOT_NAN_RET)) - 1

        # �����ۼ�������
        cum_ret_rate = CUM_RET.dropna()[-1] - 1

        # ���س�
        max_nv = np.maximum.accumulate(np.nan_to_num(CUM_RET))
        mdd = -np.min(CUM_RET / max_nv - 1)

        # ����
        sharpe_ratio = np.mean(NOT_NAN_RET) / \
            np.nanstd(NOT_NAN_RET, ddof=1)*np.sqrt(250)

        # ӯ������
        temp_df = df.copy()

        diff = temp_df[mark_col] != temp_df[mark_col].shift(1)
        temp_df[mark_col+'_diff'] = diff.cumsum()
        cond = temp_df[mark_col] == 1
        # ÿ�ο��ֵ����������
        temp_df = temp_df[cond].groupby(mark_col+'_diff')['NEXT_RET'].sum()

        # �����������ʱ��
        mark = df[mark_col]
        pre_mark = np.nan_to_num(df[mark_col].shift(-1))
        # ����ʱ��
        trade = (mark == 1) & (pre_mark < mark)

        # ���״���
        trade_count = len(temp_df)

        # �ֲ�������
        total = np.sum(mark)

        # ƽ���ֲ�����
        mean_hold = total/trade_count
        # ��������
        win = np.sum(np.where(RET > 0, 1, 0))
        # ��������
        lose = np.sum(np.where(RET < 0, 1, 0))
        # ʤ��
        win_ratio = win/total
        # ƽ��ӯ���ʣ��죩
        mean_win_ratio = np.sum(np.where(RET > 0, RET, 0))/win
        # ƽ�������ʣ��죩
        mean_lose_ratio = np.sum(np.where(RET < 0, RET, 0))/lose
        # ӯ����(��)
        win_lose = win/lose

        # ӯ������
        win_count = np.sum(np.where(temp_df > 0, 1, 0))
        # �������
        lose_count = np.sum(np.where(temp_df < 0, 1, 0))
        # �������ӯ��
        max_win = np.max(temp_df)
        # ����������
        max_lose = np.min(temp_df)
        # ʤ��
        win_rat = win_count/len(temp_df)
        # ƽ��ӯ���ʣ��Σ�
        mean_win = np.sum(np.where(temp_df > 0, temp_df, 0))/len(temp_df)
        # ƽ�������ʣ��죩
        mean_lose = np.sum(np.where(temp_df < 0, temp_df, 0))/len(temp_df)
        # ӯ����(��)
        mean_wine_lose = win_count/lose_count

        summary_dic[mark_col] = [format_x(annual_ret), format_x(cum_ret_rate), sharpe_ratio, format_x(
            mdd), total, trade_count, mean_hold, win, lose, format_x(win_ratio), format_x(mean_win_ratio),
            format_x(mean_lose_ratio), win_lose, win_count, lose_count, format_x(
                max_win), format_x(max_lose),
            format_x(win_rat), format_x(mean_win), format_x(mean_lose), mean_wine_lose]

        return summary_dic

# ---------------------------------------------------------------------
#                   ͳ��ָ�꼰ͼ����غ���
# ---------------------------------------------------------------------

# ����ͳ��ָ��


def Statistical_indicator(x_df, col, pre=True):
    '''
    x_df:DataFrame
    col:��Ҫ��������
    pre:TrueΪ��ӡ���ݣ�False ����ָ���ֵ�
    ==============
    print OR dic
    '''

    data = x_df[col].copy()  # ��������
    data = data.dropna()  # ��ȥNAֵ

    avgRet = np.mean(data)  # ��ֵ
    medianRet = np.median(data)  # ��λ��
    stdRet = np.std(data)  # ��׼��

    skewRet = st.skew(data)  # ƫ��
    kurtRet = st.kurtosis(data)  # ���

    # ��ӡָ��
    if pre:

        print(
            """
        ƽ���� : %.4f
        ��λ�� : %.4f
        ��׼�� : %.4f
        ƫ��   : %.4f
        ���   : %.4f
        1 Standard Deviation : %.4f
        -1 Standard Deviation : %.4f
        Min:%.4f
        Max:%.4f
        """ % (avgRet, medianRet, stdRet, skewRet, kurtRet, avgRet+stdRet, avgRet-stdRet, min(data), max(data))
        )

    else:
        # ���ָ���ֵ�
        return {'avgRet': avgRet,
                'medianRet': medianRet,
                'stdRet': medianRet,
                'skewRet': skewRet,
                '1_Standard_Deviation': avgRet+stdRet,
                '-1_Standard_Deviation': avgRet-stdRet,
                'Min': min(data),
                'Max': max(data)}


# �������ݷֲ�
def Data_Distribution_Plot(x_df, col):

    data = x_df[col].dropna()  # ��ȡ����
    Statistical_indicator_dic = Statistical_indicator(
        x_df, col, False)  # ��ȡͳ��ָ��

    avgRet = Statistical_indicator_dic['avgRet']
    stdRet = Statistical_indicator_dic['stdRet']

    # �������ݷֲ�ֱ��ͼ
    fig = plt.figure(figsize=(18, 9))
    x = np.linspace(avgRet - 3*stdRet, avgRet + 3*stdRet, 100)
    y = st.norm.pdf(x, avgRet, stdRet)
    kde = st.gaussian_kde(data)  # ���ݸ�˹�˹���
    data_size = len(data)  # ���ݴ�С

    # plot the histogram
    plt.subplot(121)
    plt.hist(data, 50, weights=np.ones(data_size)/data_size, alpha=0.4)
    plt.axvline(x=avgRet, color='red', linestyle='--',
                linewidth=0.8, label='Mean Count')
    plt.axvline(x=avgRet - 1 * stdRet, color='blue', linestyle='--',
                linewidth=0.8, label='-1 Standard Deviation')
    plt.axvline(x=avgRet + 1 * stdRet, color='blue', linestyle='--',
                linewidth=0.8, label='1 Standard Deviation')
    plt.ylabel('Percentage', fontsize=10)
    plt.legend(fontsize=12)

    # plot the kde and normal fit
    plt.subplot(122)
    plt.plot(x, kde(x), label='Kernel Density Estimation')
    plt.plot(x, y, color='black', linewidth=1, label='Normal Fit')
    plt.ylabel('Probability', fontsize=10)
    plt.axvline(x=avgRet, color='red', linestyle='--',
                linewidth=0.8, label='Mean Count')
    plt.legend(fontsize=12)
    return plt.show()

'''
˫���߲��Զ�ţ��ָ����ʱ��������ֱ�Ӷ�ָ����ʱ
���ȣ��Ƚ�˫���߲��Զ�ţ��ָ����ʱ��ֱ�Ӷ�ָ����ʱ����ͬ��˫���߲����Ǽ���ָ���г��õ�һ�ֲ��ԣ�
���ھ������֮һ���������ö̾��ߺͳ����ߵ����λ�ö��г� �����жϡ�Ӧ��˫������ʱ��ţ��ָ���ָ��
���̼۷ֱ���ʱ�Ľ����ʾ����ţ��ָ���ϲ�����Ч��Ҫ���Ժ�ֱ�Ӷ�ָ����ʱ������ţ��ָ����ʱ��������
��ʤ�ʾ��������������״��������½���
'''
singal_df = VT_Factor('000001.sh', '20070101', '20191031', 250).get_singal
BackTesting(singal_df, ['kernel_250', 'close'], method='MA').plot_net_value
BackTesting(singal_df, ['kernel_250', 'close'], method='MA').summary

#�鿴����ָ������
test=BackTesting(singal_df, ['kernel_250', 'close'], method='MA').back_testing
'''
��֤ 50 ˫���߲��ԱȽ�
'''

singal_df = VT_Factor('000016.sh', '20050101', '20220411', 250).get_singal
BackTesting(singal_df, ['kernel_250', 'close'], method='MA').plot_net_value
BackTesting(singal_df, ['kernel_250', 'close'], method='MA').summary

test=BackTesting(singal_df, ['kernel_250', 'close'], method='MA').back_testing
'''
���� 300 ˫���߲��ԱȽ�
'''
singal_df = VT_Factor('000300.sh', '20050101', '20220411', 250).get_singal
BackTesting(singal_df, ['kernel_250', 'close'], method='MA').plot_net_value
BackTesting(singal_df, ['kernel_250', 'close'], method='MA').summary

'''
��֤ 500 ˫���߲��ԱȽ�
'''
singal_df = VT_Factor('000905.sh', '20070101', '20191031', 250).get_singal
BackTesting(singal_df, ['kernel_250', 'close'], method='MA').plot_net_value
BackTesting(singal_df, ['kernel_250', 'close'], method='MA').summary


'''
��֤��ָ���ִ����ԱȽ�

'''
singal_df = VT_Factor('000001.sh', '20070101', '20191031', 250).get_singal
BackTesting(singal_df, ['kernel_250', 'close'], method='BBANDS').plot_net_value
BackTesting(singal_df, ['kernel_250', 'close'], method='BBANDS').summary

'''
��֤ 50���ִ����ԱȽ�
������֤ 50 ָ���ϲ��ִ����ֲ��Ե�Ӧ�ã�ֱ�Ӷ�ָ��������ʱ��Ȼ�����ʽϸߣ�
������������Ҫ��Դ�� 2009 ����ǰ��֮��ӽ������ʱ��һֱ�ڻس������ֲ�����ʵ��Ӧ�� ���ǽ���ʹ�õģ�
Ͷ������Ҫ���������Ļس��ڡ���ţ��ָ����ʱ�Ĳ�����Ȼǰ�������� û���ر�ߣ�����������ָ�ƽ�ȣ�
09 ���Ժ�������Ժ���ֱ�Ӷ�ָ����ʱ�Ĳ��ԣ�����ʤ��Ҳ����
'''
singal_df = VT_Factor('000016.sh', '20070101', '20191031', 250).get_singal
BackTesting(singal_df, ['kernel_250', 'close'], method='BBANDS').plot_net_value
BackTesting(singal_df, ['kernel_250', 'close'], method='BBANDS').summary

'''
���� 300 ���ִ����ԱȽ�

Ӧ�õ����� 300 �ϣ���ţ��ָ����ʱ�Ĳ�������Ҫ����ֱ�Ӷ�ָ����ʱ�Ĳ��ԡ�
��Ҫԭ���� 2007 ���ţ�ж�ţ��ָ����ʱ�Ĳ���û���ܹ�����ס��2007 ��֮��
ʵ���ϻ��Ƕ�ţ��ָ����ʱ�Ĳ��Ա��ָ�Ϊ�Ƚ�(ǿ��������)��
'''
singal_df = VT_Factor('000300.sh', '20070101', '20191031', 250).get_singal
BackTesting(singal_df, ['kernel_250', 'close'], method='BBANDS').plot_net_value
BackTesting(singal_df, ['kernel_250', 'close'], method='BBANDS').summary

'''
��ҵ��ָ
set123=my_ts.index_basic(market='SZSE')
#set123[set123.name.str.contains('��ҵ��')]
399006.SZ
'''
singal_df = VT_Factor('399006.SZ', '20070101', '20220411', 250).get_singal
BackTesting(singal_df, ['kernel_250', 'close'], method='BBANDS').plot_net_value
BackTesting(singal_df, ['kernel_250', 'close'], method='BBANDS').summary

test=BackTesting(singal_df, ['kernel_250', 'close'], method='BBANDS').back_testing


'''
��֤ 500 ���ִ����ԱȽ�

'''
singal_df = VT_Factor('000905.sh', '20070101', '20191031', 250).get_singal
BackTesting(singal_df, ['kernel_250', 'close'], method='BBANDS').plot_net_value
BackTesting(singal_df, ['kernel_250', 'close'], method='BBANDS').summary


'''
������֤��ָ�źŷֲ�
'''
# ��ʼ��
vt = VT_Factor('000001.sh', '20070101', '20220411', 250)

# ��ȡ����df
singal_df = vt.get_singal

# �鿴���ݽṹ
singal_df.head()



# �鿴�ź� �ֲ�
Data_Distribution_Plot(singal_df, 'kernel_250')
Statistical_indicator(singal_df, 'kernel_250')

# �鿴���ݷֲ���Ӧ��δ������
vt.forward_distribution_plot(250, bins=50)

# �źŷֲ���min~-1SD,-1SD~mean,mean~1SD,1SD~max ��Ӧ��δ���������
vt.forward_distribution_plot(
    250, bins=[0.3211, 0.4863, 0.7126, 0.9389, 1.4011])


  
#�ź�ֵ��С��Ӧδ�������ʵı仯��ͼ
# ��λ���ع�
vt.QuantReg_plot(forward_ret_name='δ��15��������', singal_periods=250)


#�����Է���
periods = [150, 200, 250,300]
singal_name = ['kernel_'+str(x) for x in periods]
singal_name.append('close')
singal_df = VT_Factor('399006.SZ', '20040101', '20220411', periods).get_singal

# ������ͬǰ���������ݲ�ͬ�����в���������ͬһ������
filter_nan = singal_df['kernel_'+str(max(periods))].isna().sum()
slice_df = singal_df.iloc[filter_nan:]
test_one=BackTesting(slice_df, singal_name, method='BBANDS')
test_one.plot_net_value
test_one.summary

