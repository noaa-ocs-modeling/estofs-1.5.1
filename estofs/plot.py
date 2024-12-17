import csdlpy
import numpy as np
import matplotlib
matplotlib.use('Agg',warn=False)
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from datetime import datetime
from datetime import timedelta as dt
import matplotlib.dates as mdates

#==============================================================================
def maxele (maxele, grid, coast, cities, trk, adv, pp, titleStr, plotFile):
    
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

    f = csdlpy.plotter.plotMap(lonlim, latlim, fig_w=20., coast=coast)
    csdlpy.plotter.addSurface (grid, maxele['value'],clim=clim)
    plt.text (lonlim[0]+0.01, latlim[0]+0.01, titleStr )

    if int(pp['General']['plotmax']) ==1:
        # Find maximal maxele value within the coord limits

        # Exclude Gulf of Maine
        #lonGoM = -70.
        #latGoM = 42.
        #maxmax = np.max(maxele['value'][np.where( \
        #           (lonlim[0] <= maxele['lon']) & (maxele['lon'] <= lonGoM) & \
        #           (latlim[0] <= maxele['lat']) & (maxele['lat'] <= latGoM))])
        maxmax = np.max(maxele['value'][np.where( \
                       (lonlim[0] <= maxele['lon']) & (maxele['lon'] <= lonlim[1]) & \
                       (latlim[0] <= maxele['lat']) & (maxele['lat'] <= latlim[1]))])
        lonmax = maxele['lon'][np.where(maxele['value']==maxmax)]
        latmax = maxele['lat'][np.where(maxele['value']==maxmax)]
        print '[info]: max maxele = ',str(maxmax),'at ',str(lonmax),'x',str(latmax)
        
    	maxStr = 'MAX VAL='+ str(np.round(maxmax,1)) + ' '
    	try:
            maxStr = maxStr + pp['General']['units'] +', '+ pp['General']['datum']
	except:
            pass # in case if there is a problem with pp
        plt.text (lonlim[0]+0.01, latlim[1]-2., maxStr, fontsize='7')
        plt.plot(lonmax, latmax, 'ow',markerfacecolor='k',markersize=8)
        plt.plot(lonmax, latmax, 'ow',markerfacecolor='r',markersize=4)
        plt.text (lonmax+0.05,latmax+0.05, str(np.round(maxmax,1)),color='k',fontsize=6)
    
    plt.text (lonlim[0]+0.01, latlim[1]+0.1,'NOAA / OCEAN SERVICE')   
    if int(pp['Cities']['plot']) ==1:
        csdlpy.plotter.plotCities (cities, lonlim, latlim, col='k', fs=6)
    ax = plt.gca()
    if int(pp['Storm']['plot'])  ==1:
        print '[info]: plotting tracks'
        csdlpy.atcf.plot.track(ax, adv, color='r',   linestyle=':',markersize=1,zorder=10,fs=1)
        csdlpy.atcf.plot.track(ax, trk, color='gray',linestyle=':',markersize=1,zorder=10,fs=1)
    
    #TODO Address the case when lon/lat ticks are not integers
    ticks  = ax.get_xticks()
    print '[info]: Converting longitude labels from negative Westerlies to positive Easterlies'
    labels = ax.get_xticklabels()
    newlabels = []
    n = -1
    for label in labels:
        n += 1
        if ticks[n]>=0:
            newTick = str( int(ticks[n]) ) + 'E'
        elif ticks[n] <= -180:
            newTick = str( int(ticks[n]) + 360) + 'E'
        else:
            newTick = str (-1*int(ticks[n])) + 'W' 
        label.set_text( newTick )
        newlabels.append( label )
    ax.set_xticklabels( newlabels )

    ticks  = ax.get_yticks()
    print '[info]: Converting latitude labels from negative Northerlies to positive Southerlies'
    labels = ax.get_yticklabels()
    newlabels = []
    n = -1
    for label in labels:
        n += 1
        if ticks[n]>=0:
            newTick = str( int(ticks[n]) ) + 'N'
        else:
            newTick = str (-1*int(ticks[n])) + 'S'
        label.set_text( newTick )
        newlabels.append( label )
    ax.set_yticklabels( newlabels )

    csdlpy.plotter.save(titleStr, plotFile)
    plt.close(f) 


#==============================================================================
def maxwind (maxele, tracks, advTrk, grid, coast, pp, titleStr, plotFile):

    # Convert m/s to knots
    maxele['value'] = 1.94384*maxele['value']

    # Default plotting limits, based on advisory track, first position
    clim   = 0.,120.
    try:
        lonlim = float(pp['Limits']['lonmin']),float(pp['Limits']['lonmax'])
        latlim = float(pp['Limits']['latmin']),float(pp['Limits']['latmax'])
        clim   = float(pp['Wind']['cmin']),  float(pp['Wind']['cmax'])
    except: #default limits, in case if not specified in ini file
        pass
    # Find maximal maxele value within the coord limits
    maxmax = np.max(maxele['value'][np.where( \
                   (lonlim[0] <= maxele['lon']) & (maxele['lon'] <= lonlim[1]) & \
                   (latlim[0] <= maxele['lat']) & (maxele['lat'] <= latlim[1]))])
  
    if isinstance(maxmax,(list,)):
        maxmax = maxmax[0]
    lonmax = maxele['lon'][np.where(maxele['value']==maxmax)]
    latmax = maxele['lat'][np.where(maxele['value']==maxmax)]
    if isinstance(lonmax,(list,)):
        lonmax = lonmax[0]
        latmax = latmax[0]
    if maxmax is np.ma.masked:
        maxmax = np.nan
    print '[info]: max maxwvel (knots) = ',np.str(maxmax),'at ', np.str(lonmax),'x', np.str(latmax)

    f = csdlpy.plotter.plotMap(lonlim, latlim, fig_w=20., coast=coast)
    csdlpy.plotter.addSurface (grid, maxele['value'],clim=clim)
    ax = f.gca()
    try:
        csdlpy.atcf.plot.track(ax, advTrk, color='k',linestyle='--',markersize=1,zorder=11)
        csdlpy.atcf.plot.size (ax, advTrk, 'neq64', color='k',zorder=11)
    except:
        pass

    plt.text (lonlim[0]+0.01, latlim[0]-0.2, titleStr )
    if not np.isnan(maxmax):
        maxStr = 'MAX VAL='+ np.str(np.round(maxmax,1)) + ' '
        try:
            maxStr = maxStr + ' knots' #pp['General']['units'] +', '+ pp['General']['datum']
        except:
            pass # in case if there is a problem with pp
        plt.text (lonlim[0]+0.01, latlim[1]-2, maxStr)

    plt.plot(lonmax, latmax, 'ow',markerfacecolor='k',markersize=10)
    plt.plot(lonmax, latmax, 'ow',markerfacecolor='r',markersize=5)
    plt.text (lonmax,latmax, str(np.round(maxmax,1)),color='k',fontsize=10)
    plt.text (lonlim[0]+0.01, latlim[1]+0.1,'NOAA / OCEAN SERVICE')

    try:
        csdlpy.plotter.save(titleStr, plotFile)
    except:
        print '[error]: cannot save maxele figure.'

    plt.close(f)

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
            csdlpy.obs.parse.setDatumsFloodLevels (fullStationName, masterListLocal)            

        # Stage the plot with datums and floodlevels   
        fig, ax, ax2 = csdlpy.plotter.stageStationPlot (xlim, ylim, now, datums, floodlevels)
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
        try: # In case tidal run failed
            ax.plot(cwl['time'], cwl['zeta'][:,n]-htp['zeta'][:,n],
                    color='m',label='STORM SURGE',linewidth=.5)
        except:
            print '[warn]: Tidal output is not plotted.'
            pass
        
        # Find model value closest to Now
        mint        = []
        now_mod_int = []
        now_mod_ind = []
        mint = min(cwl['time'], key=lambda x: abs(x - now))        
        now_mod_ind = np.where(cwl['time'] == mint)[0][0]
        now_mod = cwl['zeta'][now_mod_ind,n]
        offset  = now_obs  -  now_mod 
        #print '[debug]: offset=', str(offset)
        #print '[debug]: now_mod=', str(now_mod)
        #print '[debug]: now_mod_ind=', str(now_mod_ind)
        
        peak_val = np.nanmax(cwl['zeta'][:,n])
        peak_dat = cwl['time'][np.argmax(cwl['zeta'][:,n])]
        
        # Plot peak forecast value
        ax.text(peak_dat, 1.05*peak_val, 
                str(np.round(peak_val,1)) + "m (" + 
                str(np.round(3.28084*peak_val,1)) +"ft)", color='navy',fontsize=7)
        ax.plot([peak_dat, peak_dat], [ylim[0], peak_val], '--',color='navy')
        peak_str = str(peak_dat.hour).zfill(2) + ':' + str(peak_dat.minute).zfill(2) + 'z'
        ax.text(peak_dat+dt(hours=0.5), ylim[0], peak_str ,color='navy', fontsize=7)            
        try:
            ax.plot(peak_dat, peak_val, 'o',markeredgecolor='navy',markerfacecolor='b')
	except:
            print '[warn]: Storm tide output is not plotted.'
            pass

        print offset

        if np.isfinite(offset):
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
        ax.set_xlabel('DATE/TIME UTC')
        ax.grid(True,which='both')   
        
        ax.xaxis.set_major_locator(mdates.DayLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%a %m/%d\n00:00'))
        ax.xaxis.set_minor_locator(MultipleLocator(0.5))
        
        ax.set_xlim (        xlim)
        ax.set_ylim (        ylim)
        ax2.set_ylim(3.28084*ylim[0], 3.28084*ylim[1])
        ax2.plot([],[])

        plt.tight_layout()
        figFile = plotPath + str(n+1).zfill(3) + '.png'
        try:
            plt.savefig(figFile)
        except:
            pass
        plt.close()
        csdlpy.transfer.upload(figFile, args.ftpLogin, args.ftpPath)
        
    csdlpy.transfer.cleanup()
        
