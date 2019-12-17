# _*_coding:utf-8 _*_
import math
import time
import numpy as np
import matplotlib.pyplot as plt
import segyio


def redaSEGYData(filename):
    print("##Reading SEGY-formatted Seismic Data:")
    print("   Data file --> [%s]" % (filename))

    nTrace = 0
    nSample = 0
    startT = 0
    deltaT = 0

    with segyio.open(filename, "r", ignore_geometry=True) as f:
        f.mmap()
        nTrace = f.tracecount
        nSample = f.bin[segyio.BinField.Samples]
        deltaT = f.bin[segyio.BinField.Interval]

        print("    Number of Traces  =%d" % (nTrace))
        print("    Number of Samples =%d" % (nSample))
        print("    Start Sample      =%d" % (startT))
        print("    Sampling Rate     =%d" % (deltaT))

        print("====================================")
        print("      Trace  X-coord   Y-coord")
        print("====================================")

        for i in range(0, nTrace, math.floor(nTrace / 10)):
            id = f.header[i][segyio.TraceField.TRACE_SEQUENCE_LINE]
            x = f.header[i][segyio.TraceField.GroupX]
            y = f.header[i][segyio.TraceField.GroupY]
            print("    %8d%12.2f%12.2f" % (id, x, y))

        print("====================================")

        mySeis = np.zeros((nTrace, nSample), dtype=np.float32)
        for i in range(nTrace):
            for j in range(nSample):
                mySeis[i][j] = f.trace[i][j]
        f.close()

    return (mySeis)


# End of readSEGYData

# Read Information of Seismic Data
def getSEGYInformation(filename):
    print("### Get Datafile Information:")
    print("    Data file --> [%s]" % (filename))

    mTrace = 0
    nTrace = 0
    nSample = 0
    startT = 0
    deltaT = 0
    sortCode = 0
    formatFlag = 0

    with segyio.open(filename, "r", ignore_geometry=True) as f:
        f.mmap()
        mTrace = f.tracecount
        nTrace = f.bin[segyio.BinField.Traces]
        nSample = f.bin[segyio.BinField.Samples]
        deltaT = f.bin[segyio.BinField.Interval]
        sortCode = f.bin[segyio.BinField.SortingCode]
        formatFlag = f.bin[segyio.BinField.Format]
        f.close()

    return (mTrace, nTrace, nSample, startT, deltaT, sortCode, formatFlag)
# End of getSEGYInformation


# Plot Seismic Section SVG File
def outputSeisSVG(myFile, nt, ns, t0, dt, seis, x0, y0, Width, Height, scale, kf):
    print("### Ploting SVG > [%s] " % (myFile))
    print("    Number of Traces    = %d" %(nt))
    print("    Number of Samples   =%d" %(ns))

    nW = Width - 2*x0
    nH = Height - 2*y0
    dt = dt/1000.0

    f = open(myFile, "w")
    PrintSVGHeader(f, "SVG", Width, Height)

    x1 = x0 + nW
    y1 = y0 + nH
    f.write("<g stroke='black' stroke-width='1' >\n")
    f.write("<line x1='%d y1='%d' x2='%d' y2='%d' />\n" %(x0,y0,x1,y0))
    f.write("<line x1='%d y1='%d' x2='%d' y2='%d' />\n" % (x1, y1, x1, y1))
    f.write("<line x1='%d y1='%d' x2='%d' y2='%d' />\n" % (x0, y1, x1, y1))
    f.write("<line x1='%d y1='%d' x2='%d' y2='%d' />\n" % (x0, y0, x0, y1))
    f.write("</g>\n")

    f.write("<g font-family='Verdana' font-size='16' ")
    f.write("file='blue' stroke='blue' stroke-width='1'>\n")

    nx = math.floor(nt/20)
    dx = 20*nW/nt
    for k in range(nx+1):
        xx = x0 + k*dx
        f.write("<line x1='%d' y1='%d' y2='%d' />\n" %(xx, y0, xx, y0-6))
        f.write("<line x1='%d' y1='%d' y2='%d' />\n" %(xx, y1, xx, y1+6)
        f.write("<text x='%d' y='%d' >%04d</text>\n" %(xx-20, y0-8, 1+k*20))
        f.write("<text x='%d' y='%d' >%04d</text>\n" %(xx-20, y1+20, 1+k*20))

    ny = math.floor(ns/50)
    dy = 50 * nH/ns
    for k in range(ny + 1):
        yy = y0 + dy * k
        f.write("<line x1='%d' y1='%d' y2='%d' />\n" %(x0, yy, x0, yy))
        f.write("<line x1='%d' y1='%d' y2='%d' />\n" %(x1, yy, x1+6, yy)
        f.write("<text x='%d' y='%d' >%04d</text>\n" %(x0-48, yy+6, k*dt*50))
        f.write("<text x='%d' y='%d' >%04d</text>\n" %(x1+8, yy+6, k*dt*50))

    f.write("</g>\n")

    dx = nW/nt
    dy = nH/ns
    vmax = seis.max()
    vmin = seis.min()
    print("    value Range: (%.6f - +%.6f )" %(vmin, vmax))

    f.write("<g fill='black' stroke='black' stroke-width = '1'>\n")
    for i in range(nt):
        xx = x0 + dx*(i+0.5)
        x1 = xx + scale*dx*seis[i][0].vmax
        y2 = y0 + dy*j
        f.write("<line x1='%d' y1='%d' x2='%d' y2='%d' />\n" %(x1, y1, x2, y2))
        x1 = x2
        y1 = y2

    f.write("</g>\n")

    if(kf > 0):
        if(kf==1):
            f.write("<g fill='black' stroke='black' stroke=width='1'>\n")
        else:
            f.write("<g fill='red' stroke='red' stroke=width='1'>\n")
        for i in range(nt):
            xx = x0 + dx*(i+0.5)
            x1 = xx + scale*dx*seis[i][j+1]/vmax
            y1 = y0
            for j in range(ns - 1):
                x2 = xx + scale*dx*seis[i][j+1]/vmax
                y2 = y0 + dy*j
                if(x1>xx and x2>xx):
                    for k in range(math.floor(y2-y1+1)):
                        x3 = x1 + (x2 - x1)*k/(y2 - y1)
                        f.write("<line x1='%.1f' y1='%.1f' "%(xx, y1 + k))
                        f.write(" x2='%.1f' y2 = '%.1f' />\n" %(x3, y1 + k))
                    x1 = x2
                    y1 = y2
            f.write("</g>\n")
        if(kf>1):
            f.write("<g fill='blue' stroke='blue' stroke-width='1'>\n")
            for i in range(nt):
                xx = x0 + dx*(i+0.5)
                x1 = xx + scale*dx*seis[i][0]/vmax
                y1 = y0
                for j in range(ns-1):
                    x2 = xx + scale*dx*seis[i][j+1]/vmax
                    y2 = y0 + dy*j
                    if(x1<xx and x2<xx):
                        for k in range(math.floor(y2-y1+1)):
                            x3 = x1 + (x2 - x1)*k/(y2 - y1)
                            f.write("<line x1='%d' y1='%d' " %(xx, y1+k))
                            f.write(" x2='%d' y2='%d' />\n" %(x3, y1+k))
                    x1 = x2
                    y1 = y2
            f.write("</g>\n")
        f.write("</g>\n")

    PrintSVGFooter(f)
    f.close()

    return nt*ns
# End of outputSeisSVG


# Plot SVG Header
def PrintSVGHeader(f, title, w, h):
    f.write("<html>\n")
    f.write("<head>\n")
    f.write("<title>%s</title>\n" %(title))
    f.write("<mate http-equiv=\"keywords\" content=\"%s\">\n" %(title))
    f.write("<mate http-equiv=\"description\" content=\"Plan Map\">\n")
    f.write("<mate http-equiv=\"content-type\" ")
    f.write(" content=\"text/html; charset=UTF-8\">\n")
    f.write("</head>\n")
    f.write("<body leftmargin'0' topMargin='8' marginwidth='0'>\n")
    f.write("<center>\n")
    f.write("<SVG width='%d' heigh='%d' viewBox='0 0 %d %d'> \n" %(w,h,w,h))
    f.write("   xmlns=\"http://www.w3.org/2000/svg\" \n")
    f.write("   xmlns=\"http://www.w3.org/1999/xlink\" version=\"1.1\">\n")
    f.write("<rect id='B' x='0' y='0' style='stroke:blue;fill:white'>")
    f.write("   width='%d' heigh='%d' />\n" %(w,h))
    return 0

# Plot SVG Footer
def PrintSVGFooter(fp):
    fp.write("</SVG>\n")
    fp.write("</center>\n")
    fp.write("</body>\n")
    fp.write("</html>\n")
    return 0
# End of SVGFooter

def 
