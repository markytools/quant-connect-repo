#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from AlgorithmImports import *

class LinearRegressionChannelAlgorithm(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2023, 8, 1)
        self.SetEndDate(2023, 8, 14)
        self.SetCash(100000)
        self.symbol = "NAS100USD" # Replace with your desired symbol

        # Request minute data
        self.AddCfd(self.symbol, Resolution.Minute)

        self.window = 65000  # Number of hourly candles for the linear regression window

        #self.Schedule.On(self.DateRules.EveryDay(self.symbol), self.TimeRules.At(20, 0), self.DailyBiasSignal)
        self.Schedule.On(self.DateRules.Every(DayOfWeek.Monday, DayOfWeek.Tuesday, DayOfWeek.Wednesday, DayOfWeek.Thursday, DayOfWeek.Sunday),
                         self.TimeRules.At(20, 0), self.DailyBiasSignal)

        self.daily_signal = 0
        self.daily_position = 0


    def SuperTrend_old(df, period=10, multiplier=3):

        df['ATR'] = df['High'] - df['Low']
        df['ATR'] = df['ATR'].rolling(period).mean()

        df['HL_avg'] = (df['High'] + df['Low']) / 2
        df['Upper_band'] = df['HL_avg'] + (multiplier * df['ATR'])
        df['Lower_band'] = df['HL_avg'] - (multiplier * df['ATR'])

        df['SuperTrend'] = 0.0

        for i in range(period-1, len(df)):
            if df['Close'][i] <= df['SuperTrend'][i-1]:
                df.at[df.index[i], 'SuperTrend'] = df['Upper_band'][i]
            else:
                df.at[df.index[i], 'SuperTrend'] = df['Lower_band'][i]

        return df

    def rma(series, length):
        alpha = 1.0 / length
        rma_values = [series[0]]
        for i in range(1, len(series)):
            rma_values.append(alpha * series[i] + (1 - alpha) * rma_values[-1])
        return rma_values

    def SuperTrend(df, period=10, multiplier=3):
        tr_list = []
        for i in range(len(df)):
            if i == 0:
                tr_list.append(df['High'][i] - df['Low'][i])
            else:
                tr_list.append(max(df['High'][i] - df['Low'][i],
                                    abs(df['High'][i] - df['Close'][i - 1]),
                                    abs(df['Low'][i] - df['Close'][i - 1])))


        df['ATR'] = tr_list
    
        df['ATR'] = rma(df['ATR'], period)

        df['HL_avg'] = (df['High'] + df['Low']) / 2
        df['Upper_band'] = df['HL_avg'] + (multiplier * df['ATR'])
        df['Lower_band'] = df['HL_avg'] - (multiplier * df['ATR'])

        df['SuperTrend'] = 0.0

        for i in range(period-1, len(df)):
            if df['Close'][i] <= df['SuperTrend'][i-1]:
                df.at[df.index[i], 'SuperTrend'] = df['Upper_band'][i]
            else:
                df.at[df.index[i], 'SuperTrend'] = df['Lower_band'][i]

        df['SuperTrend_switch'] = (df['Upper_band'] == df['SuperTrend']).astype(int)
       
        df['SuperTrend_switch'] = (df['SuperTrend_switch'] != df['SuperTrend_switch'].shift()).astype(int)

        return df


    def DailyBiasSignal(self):

        self.daily_position = 0

        # Calculate Linear Regression Channel
        #history = self.History(self.symbol, self.window, Resolution.Minute)
        history = self.History[QuoteBar](self.symbol, self.window, Resolution.Minute, extendedMarketHours=True)

        close_prices = [bar.Close for bar in history]  # Extract close prices from TradeBar objects
        close_dates = [bar.Time for bar in history]
        df = pd.DataFrame(index=close_dates)
        df['Close'] = close_prices
        df.index = pd.to_datetime(df.index)


        if close_prices:
            self.Debug('-------------------')

            df_h4 = df.copy()
            df_h4 = df_h4.resample('4H').agg({
                'Close': 'last' })

            df_h4.dropna(inplace=True)

            df_h4 = df_h4.iloc[-250:,:]

            x_h4 = range(len(df_h4['Close']))
            slope_h4, intercept_h4 = np.polyfit(x_h4, df_h4['Close'], 1)
            linear_regression_line_h4 = slope_h4 * x_h4 + intercept_h4

            
            std_dev_h4 = df_h4['Close'].std() * 1

            upper_channel_line_h4 = linear_regression_line_h4 + std_dev_h4
            lower_channel_line_h4 = linear_regression_line_h4 - std_dev_h4

            upper_line_adjust_h4 = (upper_channel_line_h4[-1] + linear_regression_line_h4[-1])/2
            lower_line_adjust_h4 = (lower_channel_line_h4[-1] + linear_regression_line_h4[-1])/2

            df_h1 = df.copy()
            df_h1 = df_h1.resample('1H').agg({
                'Close': 'last' })

            df_h1.dropna(inplace=True)

            df_h1 = df_h1.iloc[-250:,:]

            x_h1 = range(len(df_h1['Close']))
            slope_h1, intercept_h1 = np.polyfit(x_h1, df_h1['Close'], 1)
            linear_regression_line_h1 = slope_h1 * x_h1 + intercept_h1
            
            std_dev_h1 = df_h1['Close'].std() * 1.5

            upper_channel_line_h1 = linear_regression_line_h1 + std_dev_h1
            lower_channel_line_h1 = linear_regression_line_h1 - std_dev_h1

            upper_line_adjust_h1 = (upper_channel_line_h1[-1] + linear_regression_line_h1[-1])/2
            lower_line_adjust_h1 = (lower_channel_line_h1[-1] + linear_regression_line_h1[-1])/2

            df_30m = df.copy()
            df_30m = df.resample('30min').agg({
                'Close': 'last' })

            df_30m.dropna(inplace=True)

            df_30m = df_30m.iloc[-250:,:]

            x_30m = range(len(df_30m['Close']))
            slope_30m, intercept_30m = np.polyfit(x_30m, df_30m['Close'], 1)
            linear_regression_line_30m = slope_30m * x_30m + intercept_30m

            
            std_dev_30m = df_30m['Close'].std() * 1.34

            upper_channel_line_30m = linear_regression_line_30m + std_dev_30m
            lower_channel_line_30m = linear_regression_line_30m - std_dev_30m

            upper_line_adjust_30m = (upper_channel_line_30m[-1] + linear_regression_line_30m[-1])/2
            lower_line_adjust_30m = (lower_channel_line_30m[-1] + linear_regression_line_30m[-1])/2
            
            self.Debug(f"History Start Date: {close_dates[0]}, End Date: {close_dates[-1]}")

            # Get the current price
            current_price = self.Securities[self.symbol].Price
            current_date = self.Time
            self.Debug(f"Date: {current_date}, Current Price: {current_price}")

            # Calculate take profit and stop loss levels
            take_profit = current_price * 1.02 # 2% take profit
            stop_loss = current_price * 0.98   # 1% stop loss

            if current_price > upper_line_adjust_h4:
                self.Debug("Signal on 4H TimeFrame: Short Daily Bias - Price above Linear Regression Channel upper line.")
                self.Debug(f"High_thres: {upper_line_adjust_h4}, Low_thres: {lower_line_adjust_h4}, mid_thres: {linear_regression_line_h4[-1]}")
                self.Sell(self.symbol, 1.0)  # Go long
                self.daily_signal = -1
                # Set take profit and stop loss orders
                self.LimitOrder(self.symbol, 1.0, take_profit)
                self.StopMarketOrder(self.symbol, 1.0, stop_loss)

            elif current_price < lower_line_adjust_h4:
                self.Debug("Signal on 4H TimeFrame: Long Daily Bias - Price below Linear Regression Channel lower line.")
                self.Debug(f"High_thres: {upper_line_adjust_h4}, Low_thres: {lower_line_adjust_h4}, mid_thres: {linear_regression_line_h4[-1]}")
                #self.Buy(self.symbol, 1.0)  # Go long
                self.daily_signal = 1
                # Set take profit and stop loss orders
                #self.LimitOrder(self.symbol, -1.0, take_profit)
                #self.StopMarketOrder(self.symbol, -1.0, stop_loss)

            elif current_price > upper_line_adjust_h1:
                self.Debug("Signal on 1H TimeFrame: Short Daily Bias - Price above Linear Regression Channel upper line.")
                self.Debug(f"High_thres: {upper_line_adjust_h1}, Low_thres: {lower_line_adjust_h1}, mid_thres: {linear_regression_line_h1[-1]}")
                #self.Sell(self.symbol, 1.0)  # Go long
                self.daily_signal = -1
                # Set take profit and stop loss orders
                #self.LimitOrder(self.symbol, 1.0, take_profit)
                #self.StopMarketOrder(self.symbol, 1.0, stop_loss)

            elif current_price < lower_line_adjust_h1:
                self.Debug("Signal on 1H TimeFrame: Long Daily Bias - Price below Linear Regression Channel lower line.")
                self.Debug(f"High_thres: {upper_line_adjust_h1}, Low_thres: {lower_line_adjust_h1}, mid_thres: {linear_regression_line_h1[-1]}")
                #self.Buy(self.symbol, 1.0)  # Go long
                self.daily_signal = 1
                # Set take profit and stop loss orders
                #self.LimitOrder(self.symbol, -1.0, take_profit)
                #self.StopMarketOrder(self.symbol, -1.0, stop_loss)

            elif current_price > upper_line_adjust_30m:
                self.Debug("Signal on 30min TimeFrame: Short Daily Bias - Price above Linear Regression Channel upper line.")
                self.Debug(f"High_thres: {upper_line_adjust_30m}, Low_thres: {lower_line_adjust_30m}, mid_thres: {linear_regression_line_30m[-1]}")
                #self.Sell(self.symbol, 1.0)  # Go long
                self.daily_signal = -1
                # Set take profit and stop loss orders
                #self.LimitOrder(self.symbol, 1.0, take_profit)
                #self.StopMarketOrder(self.symbol, 1.0, stop_loss)

            elif current_price < lower_line_adjust_30m:
                self.Debug("Signal on 30m TimeFrame: Long Daily Bias - Price below Linear Regression Channel lower line.")
                self.Debug(f"High_thres: {upper_line_adjust_30m}, Low_thres: {lower_line_adjust_30m}, mid_thres: {linear_regression_line_30m[-1]}")
                #self.Buy(self.symbol, 1.0)  # Go long
                self.daily_signal = 1
                # Set take profit and stop loss orders
                #self.LimitOrder(self.symbol,-1.0,take_profit)
                #self.StopMarketOrder(self.symbol, -1.0, stop_loss)


    def OnData(self, data):
        current_price = self.Securities[self.symbol].Price
        current_date = self.Time

        if current_date.minute % 10 == 5 or current_date.minute % 10 == 0:
            self.Debug("Current minute ends in 5 or 0.")

            # Calculate take profit and stop loss levels
            take_profit = current_price * 1.02 # 2% take profit
            stop_loss = current_price * 0.98   # 1% stop loss

            def rma(series, length):
                alpha = 1.0 / length
                rma_values = [series[0]]
                for i in range(1, len(series)):
                    rma_values.append(alpha * series[i] + (1 - alpha) * rma_values[-1])
                return rma_values

            period = 10
            multiplier = 2

            if (self.daily_signal==1) and (self.daily_position==0):
                #m5_history = self.History(self.symbol, 1500, Resolution.Minute)
                m5_history = self.History[QuoteBar](self.symbol, 1300, Resolution.Minute, extendedMarketHours=True)

                m5_prices = [bar.Close for bar in m5_history]
                m5_high = [bar.High for bar in m5_history]
                m5_low = [bar.Low for bar in m5_history]  # Extract close prices from TradeBar objects
                m5_dates = [bar.Time for bar in m5_history]

                df_m5 = pd.DataFrame(index=m5_dates)
                df_m5['Close'] = m5_prices
                df_m5['High'] = m5_high
                df_m5['Low'] = m5_low

                df_m5.index = pd.to_datetime(df_m5.index)

                df_m5['Close'] = df_m5['Close'].resample('5T').last()
                df_m5['High'] = df_m5['High'].resample('5T').max()
                df_m5['Low'] = df_m5['Low'].resample('5T').min()

                df_m5.dropna(inplace=True)

                df_m5 = df_m5.iloc[-250:,:]


                x_m5 = range(len(df_m5['Close']))
                slope_m5, intercept_m5 = np.polyfit(x_m5, df_m5['Close'], 1)
                linear_regression_line_m5 = slope_m5 * x_m5 + intercept_m5
                
                std_dev_m5 = df_m5['Close'].std() * 1.0

                upper_channel_line_m5 = linear_regression_line_m5 + std_dev_m5
                lower_channel_line_m5 = linear_regression_line_m5 - std_dev_m5

                upper_line_adjust_m5 = (upper_channel_line_m5[-1] + linear_regression_line_m5[-1])/2
                lower_line_adjust_m5 = (lower_channel_line_m5[-1] + linear_regression_line_m5[-1])/2

                if df_m5['Close'][-1] < linear_regression_line_m5[-1]:
                    df_m5 = df_m5.round(2)
                    
                    tr_list = []
                    for i in range(len(df_m5)):
                        if i == 0:
                            tr_list.append(df_m5['High'][i] - df_m5['Low'][i])
                        else:
                            tr_list.append(max(df_m5['High'][i] - df_m5['Low'][i],
                                                abs(df_m5['High'][i] - df_m5['Close'][i -1]),
                                                abs(df_m5['Low'][i] - df_m5['Close'][i - 1])))

                    
                    df_m5['ATR'] = tr_list
                
                    df_m5['ATR'] = rma(df_m5['ATR'], period)

                    df_m5['HL_avg'] = (df_m5['High'] + df_m5['Low']) / 2
                    df_m5['Upper_Band'] = df_m5['HL_avg'] + (multiplier * df_m5['ATR'])
                    df_m5['Lower_Band'] = df_m5['HL_avg'] - (multiplier * df_m5['ATR'])

                    df_m5['SuperTrend'] = 0.0
                    df_m5 = df_m5.round(2)

                            
                    for i in range(period-1, len(df_m5)):
                        #print(i)
                        if df_m5['Lower_Band'][i] > df_m5['Lower_Band'][i - 1] or df_m5['Close'][i - 1] < df_m5['Lower_Band'][i - 1]:
                            df_m5.at[df_m5.index[i], 'Lower_Band'] = df_m5['Lower_Band'][i]
                        else:
                            df_m5.at[df_m5.index[i], 'Lower_Band'] = df_m5['Lower_Band'][i - 1]

                        if df_m5['Upper_Band'][i] < df_m5['Upper_Band'][i - 1] or df_m5['Close'][i - 1] > df_m5['Upper_Band'][i - 1]:
                            df_m5.at[df_m5.index[i], 'Upper_Band'] = df_m5['Upper_Band'][i]
                        else:
                            df_m5.at[df_m5.index[i], 'Upper_Band'] = df_m5['Upper_Band'][i - 1]
                            
                    for i in range(period-1, len(df_m5)):
                        if df_m5['Close'][i] <= df_m5['SuperTrend'][i-1]:
                            df_m5.at[df_m5.index[i], 'SuperTrend'] = df_m5['Upper_Band'][i]
                        else:
                            df_m5.at[df_m5.index[i], 'SuperTrend'] = df_m5['Lower_Band'][i]
                            
                    #df_m5['SuperTrend'] = supertrend
                    df_m5 = df_m5.round(2)
                    df_m5['SuperTrend_switch'] = (df_m5['Upper_Band'] == df_m5['SuperTrend']).astype(int)
                    df_m5['SuperTrend_switch'] = (df_m5['SuperTrend_switch'] != df_m5['SuperTrend_switch'].shift()).astype(int)

                    # Buy Signal
                    if (df_m5['Close'][-1] > df_m5['SuperTrend'][-1]) and (df_m5['SuperTrend_switch'][-1] == 1):
                        #self.Debug(df_m5['SuperTrend_switch'].tail(1))
                        self.Debug(df_m5[['SuperTrend', 'Upper_Band', 'Lower_Band', 'Close']].tail(1))

                        self.Buy(self.symbol, 1.0)  # Go long

                        # Set take profit and stop loss orders
                        self.LimitOrder(self.symbol, -1.0, take_profit)
                        self.StopMarketOrder(self.symbol, -1.0, stop_loss)

                        self.daily_position = 1

            elif (self.daily_signal==-1) and (self.daily_position==0):
                #m5_history = self.History(self.symbol, 1500, Resolution.Minute)
                m5_history = self.History[QuoteBar](self.symbol, 1300, Resolution.Minute, extendedMarketHours=True)

                m5_prices = [bar.Close for bar in m5_history]
                m5_high = [bar.High for bar in m5_history]
                m5_low = [bar.Low for bar in m5_history]  # Extract close prices from TradeBar objects
                m5_dates = [bar.Time for bar in m5_history]

                df_m5 = pd.DataFrame(index=m5_dates)
                df_m5['Close'] = m5_prices
                df_m5['High'] = m5_high
                df_m5['Low'] = m5_low

                df_m5.index = pd.to_datetime(df_m5.index)

                df_m5['Close'] = df_m5['Close'].resample('5T').last()
                df_m5['High'] = df_m5['High'].resample('5T').max()
                df_m5['Low'] = df_m5['Low'].resample('5T').min()

                df_m5.dropna(inplace=True)

                df_m5 = df_m5.iloc[-250:,:]

                x_m5 = range(len(df_m5['Close']))
                slope_m5, intercept_m5 = np.polyfit(x_m5, df_m5['Close'], 1)
                linear_regression_line_m5 = slope_m5 * x_m5 + intercept_m5
                
                std_dev_m5 = df_m5['Close'].std() * 1.0

                upper_channel_line_m5 = linear_regression_line_m5 + std_dev_m5
                lower_channel_line_m5 = linear_regression_line_m5 - std_dev_m5

                upper_line_adjust_m5 = (upper_channel_line_m5[-1] + linear_regression_line_m5[-1])/2
                lower_line_adjust_m5 = (lower_channel_line_m5[-1] + linear_regression_line_m5[-1])/2

                if df_m5['Close'][-1] > linear_regression_line_m5[-1]:
    
                    df_m5 = df_m5.round(2)
                    
                    tr_list = []
                    for i in range(len(df_m5)):
                        if i == 0:
                            tr_list.append(df_m5['High'][i] - df_m5['Low'][i])
                        else:
                            tr_list.append(max(df_m5['High'][i] - df_m5['Low'][i],
                                                abs(df_m5['High'][i] - df_m5['Close'][i -1]),
                                                abs(df_m5['Low'][i] - df_m5['Close'][i - 1])))

                    
                    df_m5['ATR'] = tr_list
                
                    df_m5['ATR'] = rma(df_m5['ATR'], period)

                    df_m5['HL_avg'] = (df_m5['High'] + df_m5['Low']) / 2
                    df_m5['Upper_Band'] = df_m5['HL_avg'] + (multiplier * df_m5['ATR'])
                    df_m5['Lower_Band'] = df_m5['HL_avg'] - (multiplier * df_m5['ATR'])

                    df_m5['SuperTrend'] = 0.0
                    df_m5 = df_m5.round(2)
                    uptrend = True
                    supertrend = []

                            
                    for i in range(period-1, len(df_m5)):
                        #print(i)
                        if df_m5['Lower_Band'][i] > df_m5['Lower_Band'][i - 1] or df_m5['Close'][i - 1] < df_m5['Lower_Band'][i - 1]:
                            df_m5.at[df_m5.index[i], 'Lower_Band'] = df_m5['Lower_Band'][i]
                        else:
                            df_m5.at[df_m5.index[i], 'Lower_Band'] = df_m5['Lower_Band'][i - 1]

                        if df_m5['Upper_Band'][i] < df_m5['Upper_Band'][i - 1] or df_m5['Close'][i - 1] > df_m5['Upper_Band'][i - 1]:
                            df_m5.at[df_m5.index[i], 'Upper_Band'] = df_m5['Upper_Band'][i]
                        else:
                            df_m5.at[df_m5.index[i], 'Upper_Band'] = df_m5['Upper_Band'][i - 1]
                            
                    for i in range(period-1, len(df_m5)):
                        if df_m5['Close'][i] <= df_m5['SuperTrend'][i-1]:
                            df_m5.at[df_m5.index[i], 'SuperTrend'] = df_m5['Upper_Band'][i]
                        else:
                            df_m5.at[df_m5.index[i], 'SuperTrend'] = df_m5['Lower_Band'][i]
                            
                    #df_m5['SuperTrend'] = supertrend
                    df_m5 = df_m5.round(2)
                    df_m5['SuperTrend_switch'] = (df_m5['Upper_Band'] == df_m5['SuperTrend']).astype(int)
                    df_m5['SuperTrend_switch'] = (df_m5['SuperTrend_switch'] != df_m5['SuperTrend_switch'].shift()).astype(int)



                    # Sell Signal

                    if (df_m5['Close'][-1] < df_m5['SuperTrend'][-1]) and (df_m5['SuperTrend_switch'][-1] == 1):
                        self.Debug(df_m5['SuperTrend_switch'].tail(1))
                        self.Debug(df_m5['SuperTrend'].tail(1))
                        self.Debug(df_m5['Upper_Band'].tail(1))
                        self.Debug(df_m5['Lower_Band'].tail(1))
                        self.Debug(df_m5['Close'].tail(1))
                
                        self.Sell(self.symbol, 1.0)  # Go long

                        # Set take profit and stop loss orders
                        self.LimitOrder(self.symbol, 1.0, take_profit)
                        self.StopMarketOrder(self.symbol, 1.0, stop_loss)

                        self.daily_position = 1


            else:
                pass


    def OnEndOfAlgorithm(self):
        self.Debug("Backtest completed.")

