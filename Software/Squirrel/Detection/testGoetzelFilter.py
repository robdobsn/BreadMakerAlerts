import math
SIGNAL_SAMPLE_RATE = 10

def GoertzelFilter(samples, freq):
	sPrev = 0.0
	sPrev2 = 0.0
	normalizedfreq = freq / SIGNAL_SAMPLE_RATE;
	coeff = 2 * math.cos(2 * math.pi * normalizedfreq);
	for samp in samples:
		s = samp + coeff * sPrev - sPrev2
		sPrev2 = sPrev
		sPrev = s
	power = sPrev2 * sPrev2 + sPrev * sPrev - coeff * sPrev * sPrev2
	return power

def SqFilter1(samples):
    threshold = 1000
    highCount = 9
    lowCount = 4
    ctr = 0
    lastEdgeCtr = 0
    recogCount = 0
    s0 = samples[0]
    for samp in samples:
        diff = samp - s0
        s0 = samp
        if abs(diff) > threshold:
            thisEdgeCount = ctr - lastEdgeCtr
            testEdgeCount = lowCount if diff > 0 else highCount
            if testEdgeCount - 1 <= thisEdgeCount <= testEdgeCount + 1:
                recogCount += 1
            else:
                recogCount = 0
            lastEdgeCtr = ctr
        ctr += 1
        print(samp, recogCount)

def SqFilter2(samples):
    curValue = -1
    threshold = 1000
    highCount = 9
    lowCount = 4
    ctr = 0
    lastEdgeCtr = 0
    maxFlashLikelihood = 3
    flashLikelihood = 0
    s0 = samples[0]
    for samp in samples:
        diff = samp - s0
        s0 = samp
        if abs(diff) > threshold:
            thisEdgeCount = ctr - lastEdgeCtr
            testEdgeCount = lowCount if diff > 0 else highCount
            if testEdgeCount - 1 <= thisEdgeCount <= testEdgeCount + 1:
                if flashLikelihood < maxFlashLikelihood:
                    flashLikelihood += 1
                curValue = 1 if diff > 0 else 0
            else:
                if flashLikelihood > 0:
                    flashLikelihood -= 1
            lastEdgeCtr = ctr
        else:
            if (ctr - lastEdgeCtr) > highCount + lowCount:
                if flashLikelihood > 0:
                    flashLikelihood -= 1
                lastEdgeCtr = ctr

        ctr += 1
        print(samp, flashLikelihood, curValue)



inputData = [1952,1872,2208,1920,2176,608,480,704,608,1872,2288,1936,2208,2016,2064,2096,2208,1920,656,544,560,
             592,2128,2048,1920,2256,1888,2080,2048,2112,2064,608,448,592,512,2048,2064,2048,2032,2048,2208,1888,
             2144,1952,560,480,512,608,480,2048,2208,2240,1872,1936,2208,1936,2144,1968,640,480,656,480,2160,2176,
             2048,2144,2048,2096,2064,2080,2208,416,624,512,704,1952,2096,2080,2192,1952,2240,1968,2080,2064,
             64,0,64,16,48,0,0,48,80,32,128,48,80,0,80,0,112,0,32,16,0,64,16,0,112,0,64,0,80,48,64,64,80,16,
             64,0,128,32,80,0,48,48,128,48,112,0,128,16,64,0,]
#poww = GoertzelFilter(inputData, 4)
#print(poww)
SqFilter2(inputData)
