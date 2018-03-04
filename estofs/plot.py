import csdlpy
import numpy as np
import matplotlib
matplotlib.use('Agg',warn=False)
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.dates as mdates
from datetime import datetime
from datetime import timedelta as dt

#==============================================================================
def maxele (maxele, grid, coast, pp, titleStr, plotFile):
    
    # Default plotting limits, based on advisory track, first position
    lonlim = np.min(grid['lon']), np.max(grid['lon'])
    latlim = np.min(grid['lat']), np.max(grid['lat'])
    clim   = 0.,4.5
    try:
        lonlim = float(pp['Limits']['lonmin']),float(pp['Limits']['lonmax'])
        latlim = float(pp['Limits']['latmin']),float(pp['Limits']['latmax'])
        clim   = float(pp['Limits']['cmin']),  float(pp['Limits']['cmax'])
    except: #default limits, in case if not specified in ini file
        pass
    # Find maximal maxele value within the coord limits
    maxmax = np.max(maxele['value'][np.where( \
                   (lonlim[0] <= maxele['lon']) & (maxele['lon'] <= lonlim[1]) & \
                   (latlim[0] <= maxele['lat']) & (maxele['lat'] <= latlim[1]))])
    lonmax = maxele['lon'][np.where(maxele['value']==maxmax)]
    latmax = maxele['lat'][np.where(maxele['value']==maxmax)]
    print '[info]: max maxele = ',str(maxmax),'at ',str(lonmax),'x',str(latmax)
        
    f = csdlpy.plotter.plotMap(lonlim, latlim, fig_w=10., coast=coast)
    csdlpy.plotter.addSurface (grid, maxele['value'],clim=clim)
    
    plt.text (lonlim[0]+0.01, latlim[0]+0.01, titleStr )
    maxStr = 'MAX VAL='+ str(np.round(maxmax,1)) + ' '
    try:
        maxStr = maxStr + pp['General']['units'] +', '+ pp['General']['datum']
    except:
        pass # in case if there is a problem with pp
    plt.text (lonlim[0]+0.01, latlim[1]-0.1, maxStr)
        
    plt.plot(lonmax, latmax, 'ow',markerfacecolor='k',markersize=10)
    plt.plot(lonmax, latmax, 'ow',markerfacecolor='r',markersize=5)
    plt.text (lonmax,latmax, str(np.round(maxmax,1)),color='k',fontsize=10)
    csdlpy.plotter.save(titleStr, plotFile)
    plt.close(f) 

#==============================================================================
def setStationPlot (master, stationName, cwl, n, oldxlim, ylim):
    
    query = ['NOSID','Name',\
             'ETSS HAT-ft','ETSS MSL-ft','ETSS MLLW-ft','ETSS MHHW-ft', \
             'Minor MHHW ft','Moderate MHHW ft','Major MHHW ft']
    
    datum_hat_ft  = np.nan
    datum_msl_ft  = np.nan
    datum_mhhw_ft = np.nan
    datum_mllw_ft = np.nan
    fl_minor_ft   = np.nan
    fl_moder_ft   = np.nan
    fl_major_ft   = np.nan
    obs = dict()
    new_xlim0 = oldxlim[0]
    obs['dates']  = []
    obs['values'] = []
    stationTitle  = stationName    
    # Get data from master list
    for m in master:
        nosid = m[query.index('NOSID')]
        if nosid in stationName:
            #print '[info]: station identified: ' + nosid
            try:
                stationTitle  = m[query.index('NOSID')] + ' ' + m[query.index('Name')]
                datum_hat_ft  = float(m[query.index('ETSS HAT-ft')])
                datum_msl_ft  = float(m[query.index('ETSS MSL-ft')])
                datum_mhhw_ft = float(m[query.index('ETSS MHHW-ft')])
                datum_mllw_ft = float(m[query.index('ETSS MLLW-ft')])
            except:
                pass
            try:
                fl_minor_ft   = float(m[query.index('Minor MHHW ft')])
                fl_moder_ft   = float(m[query.index('Moderate MHHW ft')])
                fl_major_ft   = float(m[query.index('Major MHHW ft')])
            except:
                pass
            break
            
    # Get obs
    now   = datetime.utcnow()
    dates = (now-dt(days=2), now)
    obs   = csdlpy.obs.coops.getData(nosid, dates, product='waterlevelrawsixmin') 
            
    try:
        new_xlim0 = obs['dates'][0]
    except:
        pass
    xlim = [new_xlim0, oldxlim[1]]    
    
    fig, ax = plt.subplots(sharex=True, figsize=(14,4.5))
    ax2 = ax.twinx()
    ax.plot([],[])

    if not np.isnan(fl_minor_ft*fl_moder_ft*fl_major_ft*datum_mhhw_ft*datum_msl_ft):
    
        fl_minor_m = 1./3.28084*(datum_mhhw_ft+fl_minor_ft-datum_msl_ft) 
        if fl_minor_m < ylim[1]:
            ax.plot(xlim[0], fl_minor_m, 'dr', markerfacecolor='r')
            ax.text(xlim[0], fl_minor_m + 0.*cwl['zeta'][2,n],\
                    'Minor Flood: ' + str(np.round(fl_minor_m,2)),color='k',fontsize=7)
            p = patches.Rectangle((mdates.date2num(xlim[0]), fl_minor_m), \
                                  mdates.date2num(xlim[1])-mdates.date2num(xlim[0]), \
                                  ylim[1]-fl_minor_m, \
                                  color='r',alpha=0.15)
            ax.add_patch(p)
                
        fl_moder_m = 1./3.28084*(datum_mhhw_ft+fl_moder_ft-datum_msl_ft) 
        if fl_moder_m < ylim[1]:
            ax.plot(xlim[0], fl_moder_m, 'dr', markerfacecolor='r')
            ax.text(xlim[0], fl_moder_m + 0.*cwl['zeta'][2,n],\
                    'Moderate Flood: '+ str(np.round(fl_moder_m,2)),color='k',fontsize=7)
            p = patches.Rectangle((mdates.date2num(xlim[0]), fl_moder_m), \
                                  mdates.date2num(xlim[1])-mdates.date2num(xlim[0]), \
                                  ylim[1]-fl_moder_m, \
                                  color='r',alpha=0.15)
            ax.add_patch(p)

        fl_major_m = 1./3.28084*(datum_mhhw_ft+fl_major_ft-datum_msl_ft) 
        if fl_major_m < ylim[1]:
            ax.plot(xlim[0], fl_major_m, 'dr', markerfacecolor='r')
            ax.text(xlim[0], fl_major_m + 0.*cwl['zeta'][2,n],\
                    'Major Flood: ' + str(np.round(fl_major_m,2)),color='k',fontsize=7)
            p = patches.Rectangle((mdates.date2num(xlim[0]), fl_major_m), \
                                  mdates.date2num(xlim[1])-mdates.date2num(xlim[0]), \
                                  ylim[1]-fl_major_m, \
                                  color='r',alpha=0.15)
            ax.add_patch(p)

    if datum_msl_ft is not np.nan:

        datum_mhhw_m = 1./3.28084*(datum_mhhw_ft-datum_msl_ft) 
        if datum_mhhw_m < ylim[1]:
            ax.plot(xlim, [datum_mhhw_m, datum_mhhw_m], color='c')
            ax.plot(xlim[1], datum_mhhw_m, 'dc', markerfacecolor='c')
            ax.text(cwl['time'][-60], datum_mhhw_m + 0.*cwl['zeta'][2,n] +0.05, 'MHHW',color='c')

            datum_mllw_m = 1./3.28084*(datum_mllw_ft-datum_msl_ft) 
            if datum_mllw_m > ylim[0]:
                ax.plot(xlim, [datum_mllw_m, datum_mllw_m], color='c')
                ax.plot(xlim[1], datum_mllw_m, 'dc', markerfacecolor='c')
                ax.text(cwl['time'][-60], datum_mllw_m + 0.*cwl['zeta'][2,n] +0.05, 'MLLW',color='c')

            datum_hat_m  = 1./3.28084*(datum_hat_ft-datum_msl_ft) 
            if datum_hat_m < ylim[1]:
                ax.plot(xlim, [datum_hat_m, datum_hat_m], color='y')
                ax.plot(xlim[1], datum_hat_m, 'dy', markerfacecolor='y')
                ax.text(cwl['time'][-60], datum_hat_m + 0.*cwl['zeta'][2,n] +0.05, 'HAT',color='y')

    ax.plot(xlim[1], 0, 'dk',color='k')
    ax.text(cwl['time'][-60], 0.*cwl['zeta'][2,n] +0.05, 'LMSL',color='k')
        
    ax.set_xlabel('DATE UTC')
    ax.grid(True,which='both')   
        
    try:
        ax.plot(obs['dates'], obs['values'],        
                color='g',label='OBSERVED',  linewidth=2.0)

        peak_obs_val = np.nanmax(obs['values'])
        peak_obs_dat = obs['dates'][np.argmax(obs['values'])]
        ax.plot(peak_obs_dat, peak_obs_val, 'go')
        ax.text(peak_obs_dat, 1.06*peak_obs_val, 
                str(np.round(peak_obs_val,1)) + "m (" + 
                   str(np.round(3.28084*peak_obs_val,1)) +"ft)", color='g',
                   fontsize=7, weight='bold')
    except:
        pass     
        
    return fig, ax, ax2, xlim, stationTitle

#==============================================================================
def stations (cwlFile, htpFile, pp, titleStr, plotPath, args):

    clim = -0.5,3.5
    try:
        clim = float(pp['Stations']['cmin']),  float(pp['Stations']['cmax'])
    except:
        pass
    
    # Download master list
    masterListRemote = pp['Stations']['url']
    masterListLocal  = 'masterlist.csv'
    csdlpy.transfer.download(masterListRemote, masterListLocal)
    query = ['NOSID','Name',\
             'ETSS HAT-ft','ETSS MSL-ft','ETSS MLLW-ft','ETSS MHHW-ft', \
             'Minor MHHW ft','Moderate MHHW ft','Major MHHW ft']
    master = csdlpy.obs.parse.stationsList (masterListLocal, query)  
    
    cwl = csdlpy.estofs.getPointsWaterlevel (cwlFile)
    htp = csdlpy.estofs.getPointsWaterlevel (htpFile)

    # Plot limits
    xlim = cwl['time'][0], cwl['time'][-1]
    ylim = clim[0],        clim[1]
    
    nStations = len(cwl['stations'])
    print '[info]: Plotting ' + str(nStations) + ' point stations.'
    
    for n in range(nStations):
        fig, ax, ax2, xlim, stationTitle = \
                setStationPlot (master, cwl['stations'][n], cwl, n, xlim, ylim)

        plt.title(titleStr + ' :: ' + stationTitle, fontsize=10)

        peak_val = np.nanmax(cwl['zeta'][:,n])
        peak_dat = cwl['time'][np.argmax(cwl['zeta'][:,n])]
        ax.plot(peak_dat, peak_val, 'bo')
        ax.text(peak_dat, 1.05*peak_val, 
                str(np.round(peak_val,1)) + "m (" + 
                str(np.round(3.28084*peak_val,1)) +"ft)", color='b',fontsize=7)
        
        ax.plot([peak_dat, peak_dat], ylim, '--b')
        peak_str = str(peak_dat.hour).zfill(2) + ':' + str(peak_dat.minute).zfill(2)
        ax.text(peak_dat, ylim[0], peak_str ,color='b')            

        ax.text(xlim[0],ylim[1]+0.2,'NOAA/NOS')

        ax.plot(cwl['time'], 0.*cwl['zeta'][:,n],   color='gray')
        ax.plot(htp['time'], htp['zeta'][:,n],      color='c',label='ASTRON TIDE')
        ax.plot(cwl['time'], cwl['zeta'][:,n],      color='b',label='STORM TIDE',linewidth=2.0)
        ax.plot(cwl['time'], cwl['zeta'][:,n]-htp['zeta'][:,n], ':', \
                                                    color='k',label='STORM SURGE',linewidth=.5)
        ax.legend(bbox_to_anchor=(0.8, 1.001, 0.17, 0.07), loc=3, 
                  ncol=2, mode="expand", borderaxespad=0., fontsize=7)

        ax.set_ylabel ('WATER LEVELS, meters MSL')
        ax2.set_ylabel('WATER LEVELS, feet MSL')
        ax.set_xlim (        xlim)
        ax.set_ylim (        ylim)
        ax2.set_ylim(3.28084*ylim[0], 3.28084*ylim[1])
        ax2.plot([],[])

        plt.tight_layout()
        figFile = plotPath + str(n+1).zfill(3) + '.png'
        plt.savefig(figFile)
        plt.close()
        csdlpy.transfer.upload(figFile, args.ftpLogin, args.ftpPath)
        
    csdlpy.transfer.cleanup()
        
