import numpy as np

from scipy.signal import argrelextrema
import scipy.integrate as integrate
import scipy.special as special
from scipy.integrate import odeint
from scipy.constants import constants as const
from scipy.fftpack import fft, fftfreq

import matplotlib.pyplot as plt

import stlab

hbar = const.hbar
ec = const.e

##################
##################

def testplot(x,y):
    plt.plot(x,y)
    plt.show()
    plt.close()

def Qp(Ic,R,C):
    return R*np.sqrt(2*ec*Ic*C/hbar)
    
def rcsj_curr(y, t, i, Q):
    # y0 = phi, y1 = dphi/dt
    y0, y1 = y
    dydt = (y1, -1/Q*y1 - np.sin(y0) + i)
    return dydt

def rcsj_volt(y, t, i, Q, R1, R2):
    y0, y1 = y
    dydt = [y1, -y1/Q/(1+R2/R1) - np.sin(y0) + i/(1+R2/R1)]
    return dydt

def rcsj_iv(current,time,Q=4,tsamp=0.01,svpng=False,printmessg=True,prefix=[]):
    current = current.tolist()      # makes it faster ?
    voltage = []
    # FFT = []
    # FFTx = []
    t = time
    y0 = (0,0) # always start at zero phase and zero current
    idxstart = int(-tsamp*len(t)) # only sample the last tsamp=1% of evaluated time
    for k,i in enumerate(current):
        
        y = odeint(rcsj_curr, y0, t, args=(i,Q), printmessg=printmessg)
        y0 = y[-1,:]             # new initial condition based on last iteration
        idx = argrelextrema(y[idxstart:,1], np.greater)
        
        if len(idx[0])<2:
            mean = 0
            voltage.append(mean)
        else:
            x1, x2 = idx[0][-2], idx[0][-1]
            mean = np.mean([y[x1+idxstart:x2+idxstart,1]])
            voltage.append(mean)
            
            if svpng:
                plt.plot(t[idxstart:],y[idxstart:,1])
                plt.plot([t[x1+idxstart],t[x2+idxstart]],[y[x1+idxstart,1],y[x2+idxstart,1]],'o')
                plt.ylim(0,3*Q)
                plt.savefig('iv/test/voltage_{:.2f}_{:.2f}.png'.format(Q,i))
                plt.close()
        
        '''
        signal = y[:,1]
        F = fftfreq(len(time), d=time[1]-time[0])
        F = F[:len(F)//2]
        
        signal_fft = fft(y)
        signal_fft = signal_fft[:len(signal_fft)//2]
        FFTx.append(F)
        FFT.append(signal_fft)
        '''
        
        if prefix:
            data2save = {'Time (wp*t)' : time, 'Phase (rad)' : y[:,0], 'AC Voltage (V)' : y[:,1]}
            data2save = stlab.stlabdict(data2save)
            data2save.addparcolumn('Current (Ic)',i)
            data2save.addparcolumn('DC Voltage (V)',mean)
            data2save.addparcolumn('Q ()',Q)
            if k == 0:
                idstring = 'Q={:.2f}'.format(Q)
                myfile = stlab.newfile(prefix,idstring,data2save.keys(),
                usedate=False,usefolder=False)#,mypath='simresults/')
            stlab.savedict(myfile,data2save)
            if k == len(current):
                myfile.close()
                
               
        if svpng:
            fig, ax = plt.subplots(2,sharex=True)
            ax[0].plot(t,y[:,0])
            ax[1].plot(t,y[:,1])
            fig.subplots_adjust(hspace=0)
            plt.savefig('iv/sols/sols_{:.2f}_{:.2f}.png'.format(Q,i))
            plt.close()
            
        if printmessg:
            print('Done: Q={:.2f}, i={:.2f}'.format(Q,i)) 

    return (np.asarray(current),np.asarray(voltage))

##################
##################


if __name__ == '__main__':
    currents = np.arange(0.,2.01,0.01)
    all_currents = np.concatenate([currents[:-1],currents[::-1]])
    time = np.arange(0,500,0.01)

    #qs = [20,10,4,3,2,1,0.1,0.05]
    #ts = [0.1,0.1,0.1,0.1,0.1,0.1,0.8,0.8]
    qs = [10,4,1,0.1]
    ts = [0.1,0.1,0.1,0.8]
    iv = []
    prefix = '../simresults/rcsj_time' # 1.9GB per file
    iv = [rcsj_iv(all_currents,time,Q=qq,tsamp=tt,svpng=False,prefix=prefix) for qq,tt in zip(qs,ts)]

    [plt.plot(ivv[0],ivv[1]/Q,'.-',label=str(Q)) for ivv,Q in zip(iv,qs)]

    plt.xlabel(r'$I/I_c$')
    plt.ylabel(r'$V/Q$')
    plt.legend()
    plt.savefig('../plots/ivcs_updown.png',bbox_to_inches='tight')
    plt.show()
    plt.close()





