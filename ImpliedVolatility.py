import numpy as np
from scipy.stats import norm

class impliedVolatility(object):
    def __init__(self,s0,x,mktprice,days,rate=0.035,q=0):
        self.s0 = s0                                # underlying price
        self.x = x                                  # strike price
        self.mktprice = mktprice                    # market price
        self.t = float(days)/365                    # time to expire (30 days)
        self.rate = rate                            # risk-free interest rate
        self.q = q                                  # dividend yield
        # if self.x-self.s0-self.mktprice > 0:
        #     self.s0 = self.s0 + (self.x-self.s0-self.mktprice)

        # 用二分法求implied volatility
        self.C = 0
        self.P = 0
        self.upper = 1
        self.lower = 0

    def callRealizedVol(self):
        count = 0
        self.sigma=0.9                            # initial volatility
        while abs(self.C-self.mktprice)>1e-6:
            count = count +1
            if count > 50:
                # print('CALL market price ERROR')
                self.sigma = None
                break
            d1 =(np.log(self.s0/self.x)+(self.rate-self.q+self.sigma**2/2)*self.t)/(self.sigma*np.sqrt(self.t))
            d2 =d1-self.sigma*np.sqrt(self.t)
            self.C =self.s0*np.exp(-self.q*self.t)*norm.cdf(d1)-self.x*np.exp(-self.rate*self.t)*norm.cdf(d2)
            self.P =self.x*np.exp(-self.rate*self.t)*norm.cdf(-d2)-self.s0*np.exp(-self.q*self.t)*norm.cdf(-d1)
            # print(C)
            if self.C-self.mktprice > 0:
                self.upper =self.sigma
                self.sigma=(self.sigma+self.lower)/2
            else:
                self.lower =self.sigma
                self.sigma =(self.sigma+self.upper)/2
        # print(self.sigma)
        return self.sigma
    def putRealizedVol(self):
        self.sigma=0.9                            # initial volatility
        count = 0
        while abs(self.P-self.mktprice)>1e-6:
            count = count +1
            if count > 50:
                # print('PUT market price ERROR')
                self.sigma = None
                break
            d1=(np.log(self.s0/self.x)+(self.rate-self.q+self.sigma**2/2)*self.t)/(self.sigma*np.sqrt(self.t))
            d2=d1-self.sigma*np.sqrt(self.t)
            self.C =self.s0*np.exp(-self.q*self.t)*norm.cdf(d1)-self.x*np.exp(-self.rate*self.t)*norm.cdf(d2)
            self.P =self.x*np.exp(-self.rate*self.t)*norm.cdf(-d2)-self.s0*np.exp(-self.q*self.t)*norm.cdf(-d1)
            if self.P-self.mktprice > 0:
                self.upper =self.sigma
                self.sigma=(self.sigma+self.lower)/2
            else:
                self.lower=self.sigma
                self.sigma=(self.sigma+self.upper)/2
        # print(self.sigma, self.P-self.mktprice)
        return self.sigma


            # print(sigma) # implied volatility



## 2.467 2.7 0.2296 8
# S0=2.467 # underlying price
# X=2.7 # strike price
# mktprice=0.2296 # market price
# # print(X-S0-mktprice)
# foo = impliedVolatility(S0,X,mktprice,8)
# # foo.callRealizedVol()
# foo.putRealizedVol()

