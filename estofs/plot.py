import csdlpy
import numpy as np
import matplotlib
matplotlib.use('Agg',warn=False)
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.dates as mdates
from matplotlib.ticker import MultipleLocator
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
def stageStationPlot (xlim, ylim, now, datums, floodlevels):
    """
    stages the hydrograph plot with vertical datums and flood levels.
    Returns figure and axis handles.
    """

    fig, ax = plt.subplots(sharex=True, figsize=(14,4.5))
    ax2 = ax.twinx()
    ax.plot([],[])

    datum_mhhw_ft = datums['datum_mhhw_ft']
    datum_mllw_ft = datums['datum_mllw_ft']
    datum_msl_ft  = datums['datum_msl_ft']
    datum_hat_ft  = datums['datum_hat_ft']
    
    fl_major_ft   = floodlevels['fl_major_ft']
    fl_moder_ft   = floodlevels['fl_moder_ft']
    fl_minor_ft   = floodlevels['fl_minor_ft']

    # Compute and plot minor flood level
    fl_minor_m = 1./3.28084*(datum_mhhw_ft+fl_minor_ft-datum_msl_ft) 
    if not np.isnan(fl_minor_m) and fl_minor_m < ylim[1]:
        ax.plot(xlim[0], fl_minor_m, 'dr', markerfacecolor='r')
        ax.text(xlim[0], fl_minor_m,\
                'Minor Flood: ' + str(np.round(fl_minor_m,2)),color='k',fontsize=7)
        p = patches.Rectangle((mdates.date2num(xlim[0]), fl_minor_m), \
                              mdates.date2num(xlim[1])-mdates.date2num(xlim[0]), \
                              ylim[1]-fl_minor_m, \
                              color='r',alpha=0.15)
        ax.add_patch(p)
            
    # Compute and plot moderate flood level
    fl_moder_m = 1./3.28084*(datum_mhhw_ft+fl_moder_ft-datum_msl_ft) 
    if not np.isnan(fl_moder_m) and fl_moder_m < ylim[1]:
        ax.plot(xlim[0], fl_moder_m, 'dr', markerfacecolor='r')
        ax.text(xlim[0], fl_moder_m,\
                'Moderate Flood: '+ str(np.round(fl_moder_m,2)),color='k',fontsize=7)
        p = patches.Rectangle((mdates.date2num(xlim[0]), fl_moder_m), \
                              mdates.date2num(xlim[1])-mdates.date2num(xlim[0]), \
                              ylim[1]-fl_moder_m, \
                              color='r',alpha=0.15)
        ax.add_patch(p)

    # Compute and plot major flood level
    fl_major_m = 1./3.28084*(datum_mhhw_ft+fl_major_ft-datum_msl_ft) 
    if not np.isnan(fl_major_m) and fl_major_m < ylim[1]:
        ax.plot(xlim[0], fl_major_m, 'dr', markerfacecolor='r')
        ax.text(xlim[0], fl_major_m,\
                'Major Flood: ' + str(np.round(fl_major_m,2)),color='k',fontsize=7)
        p = patches.Rectangle((mdates.date2num(xlim[0]), fl_major_m), \
                              mdates.date2num(xlim[1])-mdates.date2num(xlim[0]), \
                              ylim[1]-fl_major_m, \
                              color='r',alpha=0.15)
        ax.add_patch(p)

    # Compute and plot MHHW datum
    datum_mhhw_m = 1./3.28084*(datum_mhhw_ft-datum_msl_ft) 
    if not np.isnan(datum_mhhw_m) and datum_mhhw_m < ylim[1]:
        ax.plot(xlim, [datum_mhhw_m, datum_mhhw_m], color='c')
        ax.plot(xlim[1], datum_mhhw_m, 'dc', markerfacecolor='c')
        ax.text(xlim[1] - dt(hours=6), 
                datum_mhhw_m + 0.05, 'MHHW',color='c',fontsize=7)

    # Compute and plot MLLW datum
    datum_mllw_m = 1./3.28084*(datum_mllw_ft-datum_msl_ft) 
    if not np.isnan(datum_mllw_m) and datum_mllw_m > ylim[0] and datum_mllw_m < ylim[1]:
        ax.plot(xlim, [datum_mllw_m, datum_mllw_m], color='c')
        ax.plot(xlim[1], datum_mllw_m, 'dc', markerfacecolor='c')
        ax.text(xlim[1] - dt(hours=6), 
                datum_mllw_m + 0.05, 'MLLW',color='c',fontsize=7)

    # Compute and plot HAT datum
    datum_hat_m  = 1./3.28084*(datum_hat_ft-datum_msl_ft) 
    if not np.isnan(datum_hat_m) and datum_hat_m < ylim[1]:
        ax.plot(xlim, [datum_hat_m, datum_hat_m], color='y')
        ax.plot(xlim[1], datum_hat_m, 'dy', markerfacecolor='y')
        ax.text(xlim[1] - dt(hours=6), 
                datum_hat_m  + 0.05, 'HAT',color='y',fontsize=7)

    # Plot LMSL datum
    ax.plot(xlim[1], 0, 'dk',color='k')
    ax.text(xlim[1] - dt(hours=6), 0.05, 'LMSL',color='k',fontsize=7)

    # Plot 'now' line
    ax.plot( [now, now], ylim, 'k',linewidth=1)
    ax.text(  now + dt(hours=1),  ylim[1]-0.4,'N O W', color='k',fontsize=6, 
              rotation='vertical', style='italic')
    
    return fig, ax, ax2

#==============================================================================
def setDatumsFloodLevels (stationid, masterList):

    query = ['NOSID','Name','NWSID', \
             'ETSS HAT-ft','ETSS MSL-ft','ETSS MLLW-ft','ETSS MHHW-ft', \
             'Minor MHHW ft','Moderate MHHW ft','Major MHHW ft']
    master = csdlpy.obs.parse.stationsList (masterList, query)  

    datums = dict()
    datums['datum_hat_ft']  = np.nan
    datums['datum_msl_ft']  = np.nan
    datums['datum_mhhw_ft'] = np.nan
    datums['datum_mllw_ft'] = np.nan
    
    floodlevels = dict()
    floodlevels['fl_minor_ft']   = np.nan
    floodlevels['fl_moder_ft']   = np.nan
    floodlevels['fl_major_ft']   = np.nan

    stationTitle  = stationid   
    nosid         = stationid
    # Get data from master list
    for m in master:
        nosid = m[query.index('NOSID')]
        if nosid in stationid:
            try:
                stationTitle  = m[query.index('Name')] + \
                                  ' (NOS:' + m[query.index('NOSID')] + ' ' + \
                                  ' NWS:' + m[query.index('NWSID')] + ')'
                
                datums['datum_hat_ft']  = float(m[query.index('ETSS HAT-ft')])
                datums['datum_msl_ft']  = float(m[query.index('ETSS MSL-ft')])
                datums['datum_mhhw_ft'] = float(m[query.index('ETSS MHHW-ft')])
                datums['datum_mllw_ft'] = float(m[query.index('ETSS MLLW-ft')])
            except:
                pass
            try:
                floodlevels['fl_minor_ft'] = float(m[query.index('Minor MHHW ft')])
                floodlevels['fl_moder_ft'] = float(m[query.index('Moderate MHHW ft')])
                floodlevels['fl_major_ft'] = float(m[query.index('Major MHHW ft')])
            except:
                pass
            break

    return datums, floodlevels, nosid, stationTitle

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
    
#    Read model output
    cwl = csdlpy.estofs.getPointsWaterlevel (cwlFile)
    htp = csdlpy.estofs.getPointsWaterlevel (htpFile)
    nStations = len(cwl['stations'])
    print '[info]: Plotting ' + str(nStations) + ' point stations.'
    
    now   = datetime.utcnow()
    dates = (now-dt(days=2), now)
 
    # Plot limits
    xlim =    min(dates[0],  cwl['time'][0] ),    \
              max(dates[-1], cwl['time'][-1])
    ylim = clim[0], clim[1]
    
    for n in range(nStations):
        
        fullStationName = cwl['stations'][n]
        # Get datums        
        datums, floodlevels, nosid, stationTitle = \
            setDatumsFloodLevels (fullStationName, masterListLocal)            
        # Stage the plot with datums and floodlevels   
        fig, ax, ax2 = stageStationPlot (xlim, ylim, now, datums, floodlevels)
        plt.title(titleStr + ' @ ' + stationTitle, fontsize=9)

       # Get OBS
        obs   = csdlpy.obs.coops.getData(nosid, 
                                         dates, product='waterlevelrawsixmin') 
        # Plot
        now_obs = np.nan
        try:
            ax.plot(obs['dates'], obs['values'],
                    color='lime',label='OBSERVED',  linewidth=2.0)

            peak_obs_val = np.nanmax(obs['values'])
            peak_obs_dat = obs['dates'][np.argmax(obs['values'])]
            
            if ylim[0] <= peak_obs_val and peak_obs_val <= ylim[1]:
                    
                ax.plot(peak_obs_dat, peak_obs_val, 'o',
                        markerfacecolor='limegreen', markeredgecolor='k')
                ax.plot([peak_obs_dat, peak_obs_dat],[ylim[0],peak_obs_val], 
                        '--',c='limegreen')
                ax.text(peak_obs_dat, 1.06*peak_obs_val, 
                        str(np.round(peak_obs_val,1)) + "m (" + 
                           str(np.round(3.28084*peak_obs_val,1)) +"ft)",
                           color='forestgreen', fontsize=7, weight='bold')
                        
            # Find offset
            now_obs = obs['values'][obs['dates'].index(min(obs['dates'], \
                          key=lambda x: abs(x - now)))]
        except:
            pass     

        ax.plot(htp['time'], htp['zeta'][:,n],      
                color='c',label='ASTRON TIDE',linewidth=.5)
        ax.plot(cwl['time'], cwl['zeta'][:,n],      
                color='navy',label='STORM TIDE',linewidth=2.0)
        ax.plot(cwl['time'], cwl['zeta'][:,n]-htp['zeta'][:,n],
                color='m',label='STORM SURGE',linewidth=.5)
        
        # Find model value closest to Now
        mint = min(cwl['time'], key=lambda x: abs(x - now))        
        now_mod_ind = np.where(cwl['time'] == mint)[0][0]
        now_mod = cwl['zeta'][now_mod_ind,n]
        offset  = now_obs  -  now_mod 
        print '[debug]: offset=', str(offset)
        
        peak_val = np.nanmax(cwl['zeta'][:,n])
        peak_dat = cwl['time'][np.argmax(cwl['zeta'][:,n])]
        
        # Plot peak forecast value
        ax.text(peak_dat, 1.05*peak_val, 
                str(np.round(peak_val,1)) + "m (" + 
                str(np.round(3.28084*peak_val,1)) +"ft)", color='navy',fontsize=7)
        ax.plot([peak_dat, peak_dat], [ylim[0], peak_val], '--',color='navy')
        peak_str = str(peak_dat.hour).zfill(2) + ':' + str(peak_dat.minute).zfill(2) + 'z'
        ax.text(peak_dat+dt(hours=0.5), ylim[0], peak_str ,color='navy', fontsize=7)            
        ax.plot(peak_dat, peak_val, 'o',markeredgecolor='navy',markerfacecolor='b')

        # Plot offset forecast
        ax.plot(cwl['time'][now_mod_ind:], offset + cwl['zeta'][now_mod_ind:,n],      
                color='gray', linestyle=':', linewidth=.5)
        
        # offset value
        if ylim[0] <= 0.5*(now_mod+now_obs) and 0.5*(now_mod+now_obs) <= ylim[1]:
            ax.text(cwl['time'][now_mod_ind]+dt(hours=1), 0.5*(now_mod+now_obs), 
                    r'$\Delta$='+str(np.round(offset,2)) + 'm', color='gray',
                    fontsize=7, fontstyle='italic', fontweight='bold')

        # add offseted peak forecast value
        if ylim[0] <= peak_val+offset and peak_val+offset <= ylim[1]:
            ax.plot(peak_dat, peak_val+offset, marker='+',
                    markeredgecolor='gray', markerfacecolor='gray', markersize=5)
            ax.text(peak_dat, 1.05*(peak_val+offset), 
                str(np.round(peak_val+offset,1)) + "m (" + 
                str(np.round(3.28084*(peak_val+offset),1)) +"ft)", color='gray',
                   fontstyle='italic', fontsize=6)

        ax.legend(bbox_to_anchor=(0.8, 1.001, 0.17, 0.07), loc=3, 
                  ncol=2, mode="expand", borderaxespad=0., fontsize=7)

        ax.text(xlim[0],ylim[1]+0.05,'NOAA / OCEAN SERVICE')
        ax.set_ylabel ('WATER LEVELS, meters MSL')
        ax2.set_ylabel('WATER LEVELS, feet MSL')
        ax.set_xlabel('DATE UTC')
        ax.grid(True,which='both')   
        
        ax.xaxis.set_major_locator(mdates.DayLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d\n00:00'))
        ax.xaxis.set_minor_locator(MultipleLocator(0.5))
        
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
    
