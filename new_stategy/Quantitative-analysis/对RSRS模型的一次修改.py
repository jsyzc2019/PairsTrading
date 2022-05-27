﻿# coding: utf-8
# 引入库
import tushare as ts
# 标记交易时点
import talib
import numpy as np
import pandas as pd

import statsmodels.api as sm  # 线性回归

import pyfolio as pf  # 组合分析工具


import itertools  # 迭代器工具


# 画图
import matplotlib.pyplot as plt
import seaborn as sns


# 设置字体 用来正常显示中文标签
plt.rcParams['font.family'] = 'serif'
#mpl.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['font.sans-serif'] = ['SimHei']  #用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  #用来正常显示负号
# 用来正常显示负号
plt.rcParams['axes.unicode_minus'] = False
# 图表主题
plt.style.use('seaborn')

import sys 
sys.path.append("G://GitHub//PairsTrading//new_stategy//foundation_tools//") 
import foundation_tushare 
from Creat_RSRS import (RSRS,rolling_apply)  # 自定义信号生成
import json

# 使用ts
# 请根据自己的情况填写ts的token
setting = json.load(open('C:\config\config.json'))
pro  = foundation_tushare.TuShare(setting['token'], max_retry=60)
#pro = ts.pro_api('your token')

#数据获取及回测用函数

def query_index_data(ts_code: str, start: str, end: str, fields: str) -> pd.DataFrame:
    
    '''获取指数行情数据'''

    df = pro.index_daily(ts_code=ts_code, start_date=start,
                         end_date=end, fields='ts_code,trade_date,'+fields)
    
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    
    df.set_index('trade_date', inplace=True)
    df.sort_index(inplace=True)

    return df


# 持仓标记
def add_flag(signal_ser: pd.Series, S: float) -> pd.DataFrame:
    '''
    开平仓标记 
        1-open/hold 0-close
        signal_ser:index-date values-RSRS
        S:阈值
    '''

    flag = pd.Series(np.zeros(len(signal_ser)), index=signal_ser.index)

    pre_day = signal_ser.index[0]

    for trade, signal in signal_ser.items():

        if signal > S:

            flag[trade] = 1

        elif signal < -S:

            flag[trade] = 0

        else:

            flag[trade] = flag[pre_day]

        pre_day = trade

    return flag


def creat_algorithm_returns(signal_df: pd.DataFrame, benchmark_ser: pd.Series, S: float) -> tuple:
    '''生成策略收益表'''

    flag_df = signal_df.apply(lambda x: add_flag(x, S))

    log_ret = np.log(benchmark_ser / benchmark_ser.shift(1))  # 获取对数收益率
    
    next_ret = log_ret.shift(-1)  # 获取next_ret

    # 策略收益
    algorithm_ret = flag_df.apply(lambda x: x * next_ret)

    # 使用pyfolio分析格式化index
    algorithm_ret = algorithm_ret.tz_localize('UTC')
    algorithm_ret = algorithm_ret.dropna()

    benchmark = log_ret.tz_localize('UTC').reindex(algorithm_ret.index)

    return algorithm_ret, benchmark


def view_nav(algorithm_ret: pd.DataFrame, benchmark_ser: pd.Series):
    '''画净值图'''
    
    plt.rcParams['font.family'] = 'Microsoft JhengHei'
    # 策略净值
    algorithm_cum = (1 + algorithm_ret).cumprod()

    benchmark = (1 + benchmark_ser).cumprod()

    benchmark = benchmark.reindex(algorithm_cum.index)

    algorithm_cum.plot(figsize=(18, 8))  # 画图
    benchmark.plot(label='benchmark', ls='--', color='black')
    plt.legend()

def view_signal(close_ser: pd.Series, signal_ser: pd.Series):

    '''查看信号与指数的关系'''
    
    plt.rcParams['font.family'] = 'Microsoft JhengHei'
    close_ser = close_ser.reindex(signal_ser.index)
    plt.figure(figsize=(18, 8))
    close_ser.plot(color='Crimson')
    plt.ylabel('收盘价')
    plt.legend(['close'], loc='upper left')

    plt.twinx()
    signal_ser.plot()
    plt.ylabel('信号')
    plt.legend([signal_ser.name], loc='upper right')


#数据结构

#创业板指  399006.SZ
index_name='000300.SH'
start='20050101'
end='20220429'

index_df = pro.query('index_daily', ts_code=index_name, 
start_date=start, end_date=end,fields='trade_date,close,pre_close,high,low,amount')    
close_df=index_df
close_df.index = pd.to_datetime(close_df.trade_date)
del close_df['trade_date']
close_df.sort_index(inplace=True)  # 排序   
# 日行情数据获取
fields = ['close', 'pre_close', 'high', 'low', 'money']
#close_df = query_index_data('000300.SH', '20090101',
#                            '20200813', 'close,pre_close,high,low,amount')
close_df.rename(columns={'amount': 'money'}, inplace=True)
close_df.tail()


#获取原始RSRS_passivation指标
rsrs = RSRS()  # 调用RSRS计算类
signal_df = rsrs.get_RSRS(close_df, 16, 600, 'ols')  # 获取各RSRS信号

signal_df.head()

algorithm_ret, benchmark = creat_algorithm_returns(
    signal_df, close_df['close'], 0.7)

view_nav(algorithm_ret, benchmark)
pf.plotting.show_perf_stats(algorithm_ret['RSRS_passivation'],
                            benchmark)

#按照猜想改造钝化器
class RSRS_improve1(RSRS):

    # 重写RSRS钝化指标
    @staticmethod
    def cala_passivation_RSRS(df: pd.DataFrame, ret_quantile: pd.Series) -> pd.DataFrame:
        '''
        钝化RSRS
            df:index-date columns - |RSRS_z|R_2|
            ret_quantile:收益波动率百分位
        '''

        df['RSRS_passivation'] = df['RSRS_z'] * \
            np.power(df['R_2'], 2 * (1 - ret_quantile.reindex(df.index)))

        return df    

rsrs = RSRS_improve1() # 调用RSRS计算类
signal_df = rsrs.get_RSRS(close_df,16,600,'ols') # 获取各RSRS信号

signal_df.head()

'''
改造后的RSRS_passivation信号2011-07-15至2020-08-13年化波动率由15.6%降为15.1%,夏普从0.81提升至0.87,最大回撤由-21%降低为-20.7%,虽然各项风险指标提升不多但证明思路也许是对的。

初步结论：通过波动率百分位识别震荡可能过于简单而我们把模型中的 quantile(std(ret),M) 看作是震荡过滤器的话,将其替换为数据范围在0~1的一个震荡过滤指标,可能会对回撤有提升效果                                

'''

algorithm_ret_ver1, benchmark = creat_algorithm_returns(
    signal_df, close_df['close'], 0.7)

compare_df = pd.concat([algorithm_ret_ver1['RSRS_passivation'],
                        algorithm_ret['RSRS_passivation']], axis=1)
compare_df.columns = ['改造后', '改造前']

view_nav(compare_df, benchmark)

pf.plotting.show_perf_stats(algorithm_ret_ver1['RSRS_passivation'],
                            benchmark)

#获取最后一天收盘买卖信号 
flag_df=signal_df.apply(lambda x: add_flag(x, 0.7))
flag_df.tail()
'''
使用LR指标当作震荡过滤器
LR指标概述

当LR处于0.4~0.6范围之内时，我们认为此时价格的趋势不明朗，处于震荡区间;
当LR大于0.6时，认为价格的趋势是向上的，并且LR指标值越大，向上的趋势就越强；
当LR小于0.4时，认为价格的趋势是向下的，并且LR指标值越小，向下的趋势就越强。
'''
# LR指标
def cala_LR(close: pd.Series) -> pd.Series:
    '''
    close：index-date value-close
    '''
    periods = list(range(10, 250, 10))
    ma = pd.concat([close.rolling(i).mean() for i in periods], axis=1)
    ma.columns = periods
    ma = ma.dropna()

    return ma.apply(lambda x: np.mean(np.where(close.loc[x.name] > x, 1, 0)), axis=1)


class RSRS_improve2(RSRS):

    # 重写方法 加入ls过滤器
    def get_RSRS(self, df: pd.DataFrame, LR_ser: pd.Series, N: int, M: int, method: str) -> pd.DataFrame:
        '''
        计算各类RSRS

            df:index-date columns-|close|high|low|money|pre_close|
            N:计算RSRS
            M:修正标准分所需参数
            method:选择 ols 或 wls 回归
        '''
        selects = {'ols': (df, lambda x: self._cala_ols(x, 'low', 'high'), N),
                   'wls': (df, lambda x: self._cala_wls(x, 'low', 'high', 'money'), N)}

        ret_quantile = LR_ser.rolling(M).apply(
            lambda x: x.rank(pct=True)[-1], raw=False)

        rsrs_df = rolling_apply(*selects[method])  # 计算RSRS

        res_df = (rsrs_df.pipe(self.cala_RSRS_z, M)
                  .pipe(self.cala_revise_RSRS)
                  .pipe(self.cala_negative_revise_RSRS)
                  .pipe(self.cala_passivation_RSRS, ret_quantile))

        return res_df.drop(columns='R_2').iloc[M:]  


# 获取计算lr所需数据
#price_df = query_index_data('000300.SH', '20080101', '20200813', 'close')
price_df=close_df[['close']]
# 指标计算
LR = cala_LR(price_df['close']) 


rsrs = RSRS_improve2()  # 调用RSRS计算类
signal_df = rsrs.get_RSRS(close_df, (1 - LR), 16, 600, 'ols')  # 获取各RSRS信号

signal_df.tail()

#获取最后一天收盘买卖信号 

flag_df=signal_df.apply(lambda x: add_flag(x, 0.7))
flag_df.tail()
'''
更改过滤器后的RSRS_passivation信号2011-07-15至2020-08-13年化波动率由15.6%降为15.2%,
夏普从0.81提升至0.91,最大回撤由-21%降至-17.5% 
'''
algorithm_ret_ver2, benchmark = creat_algorithm_returns(
    signal_df, close_df['close'], 0.7)



view_nav(algorithm_ret_ver2['RSRS_passivation'], benchmark)

pf.plotting.show_perf_stats(algorithm_ret_ver2['RSRS_passivation'],
                            benchmark)

'''
改造前后回撤情况比较:

2011-09-06至2012-01-04产生回撤由改造前的20.97%降为改造后为17.46%，持续回撤天数由364降为344;
2019-03-05至2020-07-03的回撤在改造后没有发生；
2014-12-19至2015-01-16的回撤持续时间由185降为75天
'''   

print('改造后回撤区间')
pf.plotting.show_worst_drawdown_periods(algorithm_ret_ver2['RSRS_passivation'])

print('改造前回撤区间')
pf.plotting.show_worst_drawdown_periods(algorithm_ret['RSRS_passivation']) 

'''
改造后特定行情下依旧会出现回撤,但更快走出回撤或减少回撤,在2019年上半年的行情下能过获得并守住收益。
下图能直观看到改造前后2019年净值的区别。
'''

fig = plt.figure(figsize=(18, 6))
ax = fig.add_subplot(121)

pf.plotting.plot_drawdown_periods(
    algorithm_ret_ver2['RSRS_passivation'], top=5)
ax.set_title('改造后 十大回撤区间')

ax = fig.add_subplot(122)
pf.plotting.plot_drawdown_periods(algorithm_ret['RSRS_passivation'], top=5)
ax.set_title('改造前 十大回撤区间')   


#附LR指标与HS300的关系图
view_signal(price_df['close'],LR) 



#######################################
flag_df = signal_df.apply(lambda x: add_flag(x, 0.7))
#评测模型

test123=close_df['close'].pct_change()*100
test123.columns = ['pct_chg'] 

test4=pd.merge(test123,flag_df,how='inner', left_index=True, right_index=True)
test4.columns=['pct_chg','RSRS_MARK','RSRS_z_MARK','RSRS_revise_MARK','RSRS_negative_r_MARK','RSRS_passivation_MARK']                          	                          

summary(test4)

###########复用评测#################

def summary(back_testing):

        back_df = back_testing

        index_name = '年化收益率,累计收益率,夏普比率,最大回撤,持仓总天数,交易次数,平均持仓天数,获利天数, \
        亏损天数,胜率(按天),平均盈利率(按天),平均亏损率(按天),平均盈亏比(按天),盈利次数,亏损次数, \
        单次最大盈利,单次最大亏损,胜率(按此),平均盈利率(按次),平均亏损率(按次),平均盈亏比(按次)'.split(
            ',')

        # 寻找标列
        mark_list = [x for x in back_df.columns if x.split('_')[-1] == 'MARK']

        temp = []
        mark_size = len(mark_list)  # 列数

        if mark_size > 1:

            for m in mark_list:

                df = pd.DataFrame(risk_indicator(
                    back_df, m), index=index_name)
                temp.append(df)

            return pd.concat(temp, axis=1)

        else:

            return pd.DataFrame(risk_indicator(back_df, m), index=index_name)

    # 计算风险指标

def risk_indicator(x_df, mark_col):
        '''
        传入经back_testing

        '''
        df = x_df.copy()

        summary_dic = {}

        # 格式化数据
        def format_x(x):
            return '{:.2%}'.format(x)

        # 获取回测数据
        df['pct_chg'] = df['pct_chg']/100
        df['NEXT_RET'] = df['pct_chg'].shift(-1)

        NOT_NAN_RET = df['NEXT_RET'].dropna()*df[mark_col]
        RET = df['NEXT_RET']*df[mark_col]

        CUM_RET = (1+RET).cumprod()  # series

        # 计算年化收益率
        annual_ret = CUM_RET.dropna()[-1]**(250/len(NOT_NAN_RET)) - 1

        # 计算累计收益率
        cum_ret_rate = CUM_RET.dropna()[-1] - 1

        # 最大回撤
        max_nv = np.maximum.accumulate(np.nan_to_num(CUM_RET))
        mdd = -np.min(CUM_RET / max_nv - 1)

        # 夏普
        sharpe_ratio = np.mean(NOT_NAN_RET) / \
            np.nanstd(NOT_NAN_RET, ddof=1)*np.sqrt(250)

        # 盈利次数
        temp_df = df.copy()

        diff = temp_df[mark_col] != temp_df[mark_col].shift(1)
        temp_df[mark_col+'_diff'] = diff.cumsum()
        cond = temp_df[mark_col] == 1
        # 每次开仓的收益率情况
        temp_df = temp_df[cond].groupby(mark_col+'_diff')['NEXT_RET'].sum()

        # 标记买入卖出时点
        mark = df[mark_col]
        pre_mark = np.nan_to_num(df[mark_col].shift(-1))
        # 买入时点
        trade = (mark == 1) & (pre_mark < mark)

        # 交易次数
        trade_count = len(temp_df)

        # 持仓总天数
        total = np.sum(mark)

        # 平均持仓天数
        mean_hold = total/trade_count
        # 获利天数
        win = np.sum(np.where(RET > 0, 1, 0))
        # 亏损天数
        lose = np.sum(np.where(RET < 0, 1, 0))
        # 胜率
        win_ratio = win/total
        # 平均盈利率（天）
        mean_win_ratio = np.sum(np.where(RET > 0, RET, 0))/win
        # 平均亏损率（天）
        mean_lose_ratio = np.sum(np.where(RET < 0, RET, 0))/lose
        # 盈亏比(天)
        win_lose = win/lose

        # 盈利次数
        win_count = np.sum(np.where(temp_df > 0, 1, 0))
        # 亏损次数
        lose_count = np.sum(np.where(temp_df < 0, 1, 0))
        # 单次最大盈利
        max_win = np.max(temp_df)
        # 单次最大亏损
        max_lose = np.min(temp_df)
        # 胜率
        win_rat = win_count/len(temp_df)
        # 平均盈利率（次）
        mean_win = np.sum(np.where(temp_df > 0, temp_df, 0))/len(temp_df)
        # 平均亏损率（天）
        mean_lose = np.sum(np.where(temp_df < 0, temp_df, 0))/len(temp_df)
        # 盈亏比(次)
        mean_wine_lose = win_count/lose_count

        summary_dic[mark_col] = [format_x(annual_ret), format_x(cum_ret_rate), sharpe_ratio, format_x(
            mdd), total, trade_count, mean_hold, win, lose, format_x(win_ratio), format_x(mean_win_ratio),
            format_x(mean_lose_ratio), win_lose, win_count, lose_count, format_x(
                max_win), format_x(max_lose),
            format_x(win_rat), format_x(mean_win), format_x(mean_lose), mean_wine_lose]

        return summary_dic

##############################


df = pd.DataFrame()
next_ret = close_df['close'].pct_change().shift(-1)
next_ret1 = close_df['close'].pct_change()
df['RSRS_passivation'] = next_ret * flag_df['RSRS_passivation']
df['LogisticRegression'] = next_ret.loc[test_df.index] * lr.predict(x_test)
import empyrical as ep
ep.cum_returns(df).plot(figsize=(18,6))

ep.cum_returns(next_ret1).plot(color='darkgray',label='创业板')
plt.legend();  