#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
@author: Sergey.Vinogradov@noaa.gov
"""
import os,sys
import argparse
import csdlpy
import datetime
import glob

#==============================================================================
def timestamp():
    print '------'
    print '[Time]: ' + str(datetime.datetime.utcnow()) + ' UTC'
    print '------'
    
#==============================================================================
def findLatestCycle (dirMask):
    
    dirs = glob.glob(dirMask+'*')
    #latestDir = max(dirs, key=os.path.getctime)
    latestDir = max(dirs)    
    D = os.path.basename(latestDir).split('.')[-1]

    files = glob.glob(latestDir + '/*.points.cwl.nc')
    latestFile = max(files)

    F = os.path.basename(latestFile)
    latestCycle =  D + F[F.find('.t')+2:F.find('z.')]

    return latestCycle
    
#==============================================================================
def read_cmd_argv (argv):

    parser = argparse.ArgumentParser()
    
    parser.add_argument('-i','--ofsDir',         required=True)
    parser.add_argument('-s','--domain',         required=True)
    parser.add_argument('-z','--stormCycle',     required=True)    
    parser.add_argument('-o','--outputDir',      required=True)
    parser.add_argument('-t','--tmpDir',         required=True)
    parser.add_argument('-p','--pltCfgFile',     required=True)
    parser.add_argument('-u','--ftpLogin',       required=True)
    parser.add_argument('-f','--ftpPath',        required=True)
    
    args = parser.parse_args()    
           
    if 'latest' in args.stormCycle:
        if args.domain == 'glo':
            #args.stormCycle = findLatestCycle(args.ofsDir+'estofs'+'.')
            args.stormCycle = findLatestCycle(args.ofsDir+'stofs_2d_glo'+'.')
        else:
            #args.stormCycle = findLatestCycle(args.ofsDir+'estofs_'+args.domain+'.')
            args.stormCycle = findLatestCycle(args.ofsDir+'stofs_2d_glo_'+args.domain+'.')
        
    print '[info]: estofs_post.py is configured with :', args
    return args
    
#==============================================================================
def run_post(argv):

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))    
    from estofs import plot
    
    #Receive command line arguments
    args = read_cmd_argv(argv)

    #Locate hsofs path
    if args.domain == 'glo':
        #ofsPath = args.ofsDir +'estofs'+ '.' + args.stormCycle[:-2] +'/'
        ofsPath = args.ofsDir +'stofs_2d_glo'+ '.' + args.stormCycle[:-2] +'/'
    else:
        #ofsPath = args.ofsDir +'estofs_'+ args.domain + '.' + args.stormCycle[:-2] +'/'
        ofsPath = args.ofsDir +'stofs_2d_glo_'+ args.domain + '.' + args.stormCycle[:-2] +'/'
    if not os.path.exists(ofsPath):
        print '[error]: ofs path ' + ofsPath+ ' does not exist. Exiting'
        return
    
    # Try to create tmp directory
    if not os.path.exists(args.tmpDir):
        print '[warn]: tmpDir='+args.tmpDir+' does not exist. Trying to mkdir.'
        try:
            os.makedirs(args.tmpDir)
        except:
            print '[warn]: cannot make tmpDir=' +args.tmpDir
            args.tmpDir = os.path.dirname(os.path.realpath(__file__))
            print '[warn]: look for your output in a current dir='+args.tmpDir

    # Read plotting parameters                   
    pp = csdlpy.plotter.read_config_ini (args.pltCfgFile)
    timestamp()

    # Plotting maxwvel
    if args.domain == 'glo':
        maxwvelFile = \
            ofsPath + 'stofs_2d_glo' + '.t' + args.stormCycle[-2:] + 'z.fields.cwl.maxwvel.nc'
    else:
        maxwvelFile = \
            ofsPath + 'stofs_2d_glo.' + args.domain + '.t' + args.stormCycle[-2:] + 'z.fields.cwl.maxwvel.nc'
    if int(pp['Wind']['plot']) == 0 or not os.path.exists (maxwvelFile):
            print '[error]: No maxwvel file found. Skipping... ', maxwvelFile
    else:
        maxwvel = csdlpy.estofs.getFieldsWaterlevel (maxwvelFile, 'wind_max')
        # Define local files
        gridFile      = os.path.join(args.tmpDir,'fort.14')
        coastlineFile = os.path.join(args.tmpDir,'coastline.dat')
        citiesFile    = os.path.join(args.tmpDir,'cities.csv')
        csdlpy.transfer.download (      pp['Grid']['url'],      gridFile)
        csdlpy.transfer.download ( pp['Coastline']['url'], coastlineFile)
        csdlpy.transfer.download ( pp['Cities']['url'],       citiesFile)

        #Tracks
        trk = []
        adv = []
        if int(pp['Storm']['plot']) ==1:
            trkFile = os.path.join(args.tmpDir,'trk.tmp')
            advFile = os.path.join(args.tmpDir,'adv.tmp')
            csdlpy.transfer.refresh( pp['Storm']['track'],    trkFile)
            csdlpy.transfer.refresh( pp['Storm']['forecast'], advFile)
            trk    = csdlpy.atcf.read.track(trkFile, product='BEST')
            adv    = csdlpy.atcf.read.track(advFile, product='JTWC,OFCL')

        timestamp()
        grid   = csdlpy.adcirc.readGrid(gridFile)
        coast  = csdlpy.plotter.readCoastline(coastlineFile)
        cities = csdlpy.plotter.readCities (citiesFile)

        #titleStr = 'ESTOFS (GFS) ' + args.domain + \
        titleStr = 'STOFS-2D-GLO (GFS) ' + args.domain + \
                    '.' + args.stormCycle[:-2] + '.t' + \
                    args.stormCycle[-2:] + 'z MAX WIND, knots'

        plotFile = args.outputDir +'maxwvel.png'

        plot.maxwind(maxwvel, trk, adv, grid, coast, pp, titleStr, plotFile)
        csdlpy.transfer.upload(plotFile, args.ftpLogin, args.ftpPath)
    #except:
    #    print '[error]: maxele not plotted!'

    
    # Max elevations
    #try: # maxEle
    if int(pp['Limits']['plot']) ==1:
        if args.domain == 'glo':
            maxeleFile = \
                ofsPath + 'stofs_2d_glo' + \
                '.t' + args.stormCycle[-2:] + 'z.fields.cwl.maxele.nc'
        else:
            maxeleFile = \
                ofsPath + 'stofs_2d_glo.' + args.domain + \
                '.t' + args.stormCycle[-2:] + 'z.fields.cwl.maxele.nc'
        if not os.path.exists (maxeleFile):
            #try to compute maxele from fort.63 fields
            if args.domain == 'glo':
                hourlyFields = \
                    ofsPath + 'stofs_2d_glo' + \
                    '.t' + args.stormCycle[-2:] + 'z.fields.cwl.nc'
            else:
                hourlyFields = \
                    ofsPath + 'stofs_2d_glo.' + args.domain + \
                    '.t' + args.stormCycle[-2:] + 'z.fields.cwl.nc'
            print '[info]: Trying to compute maxele from ', hourlyFields
            maxele = csdlpy.adcirc.computeMaxele(hourlyFields)
        else:
            maxele = csdlpy.estofs.getFieldsWaterlevel (maxeleFile, 'zeta_max')    
 
        # Define local files
        gridFile      = os.path.join(args.tmpDir,'fort.14')
        coastlineFile = os.path.join(args.tmpDir,'coastline.dat')
        citiesFile    = os.path.join(args.tmpDir,'cities.csv') 
        csdlpy.transfer.download (      pp['Grid']['url'],      gridFile)
        csdlpy.transfer.download ( pp['Coastline']['url'], coastlineFile)
        csdlpy.transfer.download ( pp['Cities']['url'],       citiesFile)

        #Tracks
        trk = []
        adv = []
        if int(pp['Storm']['plot']) ==1:
            trkFile = os.path.join(args.tmpDir,'trk.tmp')
            advFile = os.path.join(args.tmpDir,'adv.tmp')
            csdlpy.transfer.refresh( pp['Storm']['track'],    trkFile)
            csdlpy.transfer.refresh( pp['Storm']['forecast'], advFile)
            trk    = csdlpy.atcf.read.track(trkFile, product='BEST')
            adv    = csdlpy.atcf.read.track(advFile, product='JTWC,OFCL')
        
        timestamp()
        grid   = csdlpy.adcirc.readGrid(gridFile)
        coast  = csdlpy.plotter.readCoastline(coastlineFile)
        cities = csdlpy.plotter.readCities (citiesFile)

        #titleStr = 'ESTOFS (GFS) ' + args.domain + \
        titleStr = 'STOFS-2D-GLO (GFS) ' + args.domain + \
                    '.' + args.stormCycle[:-2] + '.t' + \
                    args.stormCycle[-2:] + 'z MAX ELEV ' + \
                    pp['General']['units'] + ', ' + pp['General']['datum']

        #plotFile = args.outputDir + 'estofs.' + args.domain +'.'+ \
        #            args.stormCycle +'.maxele.png'
        plotFile = args.outputDir +'maxele.png'
                    
        plot.maxele (maxele, grid, coast, cities, trk, adv, pp, titleStr, plotFile)
        csdlpy.transfer.upload(plotFile, args.ftpLogin, args.ftpPath)
    #except:
    #    print '[error]: maxele not plotted!'        

    # Plotting Stations
    if int(pp['Stations']['plot']) ==1:
        timestamp()
        fcstYear  = args.stormCycle[:-6]
        fcstMonth = args.stormCycle[-6:-4]
        fcstDay   = args.stormCycle[-4:-2]
        fcstHour  = args.stormCycle[-2:]
        
        #titleStr = 'ESTOFS Forecast Cycle ' + \
        titleStr = 'STOFS-2D-GLO Forecast Cycle ' + \
            fcstMonth + '/' + fcstDay + '/' + fcstYear + ' ' +fcstHour + 'UTC'

        if args.domain == 'glo':
            cwlFile  = \
                ofsPath + 'stofs_2d_glo' + \
                '.t' + args.stormCycle[-2:] + 'z.points.cwl.nc'                    
            htpFile  = \
                ofsPath + 'stofs_2d_glo' + \
                '.t' + args.stormCycle[-2:] + 'z.points.htp.nc'
        else:
            cwlFile  = \
                ofsPath + 'stofs_2d_glo.' + args.domain + \
                '.t' + args.stormCycle[-2:] + 'z.points.cwl.nc'                    
            htpFile  = \
                ofsPath + 'stofs_2d_glo.' + args.domain + \
                '.t' + args.stormCycle[-2:] + 'z.points.htp.nc'                    
        #plotPath = args.outputDir + args.domain +\
        #            '.'+ args.stormCycle +'.ts.'
        plotPath = args.outputDir + 'ts-'
        plot.stations (cwlFile, htpFile, pp, titleStr, plotPath, args)

    
    #Clean up temporary folder
    csdlpy.transfer.cleanup(args.tmpDir)

#==============================================================================    
if __name__ == "__main__":

    timestamp()
    run_post (sys.argv[1:])
    timestamp()
    
