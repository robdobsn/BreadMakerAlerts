from datetime import datetime, timedelta

class SignalHysteresis:
    curStateSet = False
    curState = False
    curHasChanged = False
    timeStateSet = 0
    trueToFalseSecs = 1
    falseToTrueSecs = 1

    def __init__(self, trueToFalseSecs, falseToTrueSecs):
        self.trueToFalseSecs = trueToFalseSecs
        self.falseToTrueSecs = falseToTrueSecs

    def update(self, curTime, curValue):
        # Handle initial state
        if not self.curStateSet:
            self.curState = curValue
            self.curHasChanged = True
            self.curStateSet = True
            self.timeStateSet = curTime
        # Check if there has been a consistent alternate value for hysteresis period
        elif curValue != self.curState:
            # Change of state - so see if this has been going on for a while
            hysteresisSecs = self.trueToFalseSecs if self.curState else self.falseToTrueSecs
            if (curTime - self.timeStateSet).seconds > hysteresisSecs:
                # It has been going on for a while so make the new state stick
                self.curState = curValue
                self.curHasChanged = True
                self.timeStateSet = curTime
            else:
                self.curHasChanged = False
        else:
            # No change of state
            self.curHasChanged = False
            self.timeStateSet = curTime

    def getValue(self):
        return self.curState

    def hasChanged(self):
        return self.curHasChanged

class BreadMakerStateMC:
    curState = "Idle"
    stateEntryTime = 0
    redLedFlash = SignalHysteresis(5,5)
    redLedSolid = SignalHysteresis(1,1)
    lidIsOpen = SignalHysteresis(2,2)
    stateTimeFS_Flashing = 5
    stateTimeNS_Solid = 15

    def elapsedSinceAndValid(self, curTime, prevTime, timeOut):
        if prevTime == 0:
            return False
        td = curTime - prevTime
        return td.seconds >= timeOut

    def changeState(self, curTime, newState):
        self.curState = newState
        self.stateEntryTime = curTime

    def serviceState(self, curTime, isRedFlashing, isRedAboveThreshold, isLidOpen):

        # Handle settings for any state
        self.redLightFlash.update(curTime, isRedFlashing)
        self.redLightSolid.update(curTime, isRedAboveThreshold)
        self.lidIsOpen.update(curTime, isLidOpen)

        # Handle Idle state
        if self.curState == "Idle":

            # Check for move to pending (flashing red LED)
            if self.elapsedSinceAndValid(self.redLedFlashStarted, self.stateTimeFS_Flashing):
                self.changeState("Pending")

            # Check for move direct to Making Bread (solid red LED)
            if self.elapsedSinceAndValid(self.redLedAboveThresholdStarted, self.stateTimeNS_Solid):
                self.changeState("Running")

        # Handle Pending state
        if self.curState == "Pending":
            # Check for time to start ....


            # Check for return to idle
            if self.elapsedSinceAndValid(self.redLedFlashStarted, self.stateTimeFS_Flashing):
                self.changeState("Idle")

            # Check for now making bread
            if self.elapsedSinceAndValid(self.redLedAboveThresholdStarted, self.stateTimeNS_Solid):
                self.changeState("Running")

        # Handle Running state
        if self.curState == "Running":

            # Check for return to idle (error)
            if self.elapsedSinceAndValid(self.redLedAboveThresholdStarted, self.stateTimeNS_Solid):
                self.changeState("Running")

class FlashDetectFilter:
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

    def update(self, sample):
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

    def getFlashLikelihood(self):
        return self.flashLikelihood

fin = open("../log/Breadmaker6.txt", "r")
lins = fin.readlines()
print("Read " + str(len(lins)) + " lines")
redLedData = []
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
            redLedData.append(int(s.strip()))
        if (sidx % 4 == 0):
            lidLedData.append(int(s.strip()))
            timeData.append(curSampleTime)
            curSampleTime += timedelta(seconds=0.1)
        sidx += 1

print("Found " + str(len(timeData)) + " samples")

redSigHyst = SignalHysteresis(1,10)
redBoolData = []
redHystData = []
redNormData = []
flashFilter = FlashDetectFilter()

for sampIdx in range(len(timeData)):
    curTime = timeData[sampIdx]
    redLedBool = redLedData[sampIdx] > 1500
    redSigHyst.update(curTime, redLedBool)
    redBoolData.append(redLedBool + 1.1)
    redHystData.append(redSigHyst.getValue())
    flashFilter.update(redLedData[sampIdx])
    flashLikelihood = flashFilter.getFlashLikelihood()
    print(redLedData[sampIdx], "\t", redLedBool, "\t", redSigHyst.getValue(), "\t", redSigHyst.hasChanged(), "\t", flashLikelihood, "\t", curTime)
    redNormData.append(redLedData[sampIdx]/2000)

for vv in redLedData:
    # print(str(vv) + ", ", end="")
    print(str(vv) + ", ")

# inputData = [1952,1872,2208,1920,2176,608,480,704,608,1872,2288,1936,2208,2016,2064,2096,2208,1920,656,544,560,
#              592,2128,2048,1920,2256,1888,2080,2048,2112,2064,608,448,592,512,2048,2064,2048,2032,2048,2208,1888,
#              2144,1952,560,480,512,608,480,2048,2208,2240,1872,1936,2208,1936,2144,1968,640,480,656,480,2160,2176,
#              2048,2144,2048,2096,2064,2080,2208,416,624,512,704,1952,2096,2080,2192,1952,2240,1968,2080,2064,
#              64,0,64,16,48,0,0,48,80,32,128,48,80,0,80,0,112,0,32,16,0,64,16,0,112,0,64,0,80,48,64,64,80,16,
#              64,0,128,32,80,0,48,48,128,48,112,0,128,16,64,0,]

# for sample in redLedData:
#     filt.SqFilter(sample)

import matplotlib.pyplot as plt
plt.plot(redNormData, color="r")
plt.plot(redBoolData, color="g")
plt.plot(redHystData, color="b")
# plt.plot(lidLedData, color="b")
plt.show()

