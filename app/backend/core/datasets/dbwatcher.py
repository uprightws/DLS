import os
import glob
from app.backend.api import app_flask
from dbimageinfo import DatasetImage2dInfo

class DatasetsWatcher:
    dirDatasets=None
    dictDbInfo=[]
    def __init__(self, pathDir=None):
        if pathDir is None:
            dirRoot = app_flask.config['DLS_FILEMANAGER_BASE_PATH']
            self.dirDatasets = os.path.join(dirRoot, '../data/datasets')
        else:
            self.dirDatasets = pathDir
    def refreshDatasetsInfo(self):
        if os.path.isdir(self.dirDatasets):
            self.dictDbInfo={}
            lstDBDir = glob.glob('%s/dbset-*' % self.dirDatasets)
            for ii,pp in enumerate(lstDBDir):
                tmpDbInfo = DatasetImage2dInfo(pp)
                try:
                    tmpDbInfo.loadDBInfo()
                    self.dictDbInfo[tmpDbInfo.getId()] = tmpDbInfo
                except Exception as err:
                    print ('ERROR::DatasetsWatcher:refreshDatasetsInfo() DB [%s] is invalid \n\tmsg: %s' % (pp, err))
        else:
            raise Exception('Cant find directory with datasets [%s]' % self.dirDatasets)
    def toString(self):
        tstr = '%s' % self.dictDbInfo.values()
        return tstr
    def __str__(self):
        return self.toString()
    def __repr__(self):
        return self.toString()
    # api
    def getDatasetsInfoStatList(self):
        tret=[]
        for db in self.dictDbInfo.values():
            tret.append(db.getInfoStat())
        return tret
    def getDatasetsInfoStatWitHistsList(self):
        tret = []
        for db in self.dictDbInfo.values():
            tret.append(db.getInfoStatWithHists())
        return tret
    def getInfoStatAboutDB(self, dbId):
        if self.dictDbInfo.has_key(dbId):
            return self.dictDbInfo[dbId].getInfoStat()
    def getInfoStatWithHistsAboutDB(self, dbId):
        if self.dictDbInfo.has_key(dbId):
            return self.dictDbInfo[dbId].getInfoStatWithHists()
    def getPreviewImageDataRawForDB(self, dbId):
        if self.dictDbInfo.has_key(dbId):
            return self.dictDbInfo[dbId].getPreviewImageDataRaw()
    def getMeanImageRawForDB(self, dbId):
        if self.dictDbInfo.has_key(dbId):
            return self.dictDbInfo[dbId].getMeanImageDataRaw()
    def getRawImageFromDB(self, dbId, ptype, imdIdx):
        if self.dictDbInfo.has_key(dbId):
            return self.dictDbInfo[dbId].getRawImageFromDB(ptype, imdIdx)
    def getDbRangeInfo(self, dbId, ptype, labelIdx, idxFrom, idxTo):
        if self.dictDbInfo.has_key(dbId):
            return self.dictDbInfo[dbId].getDbRangeInfo(ptype, labelIdx, idxFrom, idxTo)

    def delete(self, dbId):
        if self.dictDbInfo.has_key(dbId):
            print(self.dictDbInfo[dbId])

            return

###############################
if __name__ == '__main__':
    pass