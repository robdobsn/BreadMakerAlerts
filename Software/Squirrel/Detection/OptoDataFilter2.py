from datetime import datetime, timedelta

class OptoDataFilter2:
    INIT_0_1_THRESHOLD = 1500
    curValue = -1
    lastSample = 0
    EDGE_DETECT_THRESHOLD = 1000
    EDGE_HIGH_SAMPLE_COUNT = 9
    EDGE_LOW_SAMPLE_COUNT = 4
    sampleCtr = 0
    lastEdgeCtr = 0
    maxFlashLikelihood = 3
    flashLikelihood = 0

    def SqFilter(self, sample):
        if self.curValue == -1:
            self.curValue = 1 if sample > self.INIT_0_1_THRESHOLD else 0
            self.lastSample = sample
        diff = sample - self.lastSample
        self.lastSample = sample
        if abs(diff) > self.EDGE_DETECT_THRESHOLD:
            thisEdgeCount = self.sampleCtr - self.lastEdgeCtr
            testEdgeCount = self.EDGE_LOW_SAMPLE_COUNT if diff > 0 else self.EDGE_HIGH_SAMPLE_COUNT
            if testEdgeCount - 1 <= thisEdgeCount <= testEdgeCount + 1:
                if self.flashLikelihood < self.maxFlashLikelihood:
                    self.flashLikelihood += 1
                self.curValue = 1 if diff > 0 else 0
            else:
                if self.flashLikelihood > 0:
                    self.flashLikelihood -= 1
            self.lastEdgeCtr = self.sampleCtr
        else:
            if (self.sampleCtr - self.lastEdgeCtr) > self.EDGE_HIGH_SAMPLE_COUNT + self.EDGE_LOW_SAMPLE_COUNT:
                if self.flashLikelihood > 0:
                    self.flashLikelihood -= 1
                self.sampleCtr = 0
                self.lastEdgeCtr = self.sampleCtr
        self.sampleCtr += 1
        # print(sample, self.flashLikelihood, self.curValue)

fin = open("../log/Breadmaker6.txt", "r")
lins = fin.readlines()
print("Read " + str(len(lins)) + " lines")
startLedData = []
lidLedData = []
timeData = []
curSampleTime = 0
for lin in lins:
    ss = lin.split("\t")
    sidx = 0
    for s in ss:
        if (s.strip() == ""):
            continue
        if sidx == 0:
            curSampleTime = datetime.strptime(s.strip(), "%Y-%d-%m %H:%M:%S")
            sidx += 1
            continue
        if (sidx + 3) % 4 == 0:
            startLedData.append(int(s.strip()))
        if (sidx % 4 == 0):
            lidLedData.append(int(s.strip()))
            timeData.append(curSampleTime)
            curSampleTime += timedelta(seconds=2)
        sidx += 1

print("Found " + str(len(startLedData)) + "samples")

# inputData = [1952,1872,2208,1920,2176,608,480,704,608,1872,2288,1936,2208,2016,2064,2096,2208,1920,656,544,560,
#              592,2128,2048,1920,2256,1888,2080,2048,2112,2064,608,448,592,512,2048,2064,2048,2032,2048,2208,1888,
#              2144,1952,560,480,512,608,480,2048,2208,2240,1872,1936,2208,1936,2144,1968,640,480,656,480,2160,2176,
#              2048,2144,2048,2096,2064,2080,2208,416,624,512,704,1952,2096,2080,2192,1952,2240,1968,2080,2064,
#              64,0,64,16,48,0,0,48,80,32,128,48,80,0,80,0,112,0,32,16,0,64,16,0,112,0,64,0,80,48,64,64,80,16,
#              64,0,128,32,80,0,48,48,128,48,112,0,128,16,64,0,]
# filt = OptoDataFilter2()
# for sample in startLedData:
#     filt.SqFilter(sample)

import matplotlib.pyplot as plt
plt.plot(startLedData, color="r")
plt.plot(lidLedData, color="b")
plt.show()

