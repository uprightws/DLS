/**
 * Created by ar on 11.09.16.
 */

'use strict';

angular.module('datasetImage2dPaging2', ['ngMaterial', 'cl.paging'])
.component('datasetImage2dPaging2', {
    restrict: 'E',
    templateUrl: '/frontend/components/preview/dataset-image2d-preview/dataset-image2d-paging2.html',
     bindings: {
         paramDatabase:     '@',
         paramType:         '@',
         paramClass:        '@',
         paramClassType:    '@'
     },
    controller: function ($scope, $http, dbinfoService) {
        var self        = this;
        self.$onInit = function () {
            $scope.currentPage = 0;
            $scope.paging = {
                totalImages: 0,
                total:  0,
                current: 1,
                align: 'center start',
                onPageChanged: loadPages
            };
            //
            self.numPerPage = 24;
            dbinfoService.getInfoStatWithHistsAboutDB(self.paramDatabase).then(function successCallback(response) {
                var tdata       = response.data;

                var tdataHist   = null;
                var numAll      = 0;
                if(self.datasetType=='val') {
                    tdataHist = response.data.hist.histVal;
                    numAll    =response.data.info.numTrain;
                } else {
                    tdataHist = response.data.hist.histTrain;
                    numAll    = response.data.info.numVal;
                }
                var mapCls={};
                for(var kk=0; kk<tdataHist.length; kk++) {
                    mapCls[tdataHist[kk][0]]=tdataHist[kk][1];
                }
                var tnum = 0;
                if(self.paramClassType=='all') {
                    tnum = numAll;
                } else {
                    tnum = mapCls[self.paramClass];
                }
                self.listIndexes=[];
                $scope.paging.totalImages = tnum;
                var tmpCnt = 0;
                for(var ii=0; ii<$scope.paging.totalImages; ii+=self.numPerPage) {
                    var pStartImg = ii;
                    var pStopImg  = ii+self.numPerPage;
                    if (pStopImg>=$scope.paging.totalImages) {
                        pStopImg = $scope.paging.totalImages;
                    }
                    var tmp = {
                        from:   pStartImg,
                        to:     pStopImg
                    };
                    self.listIndexes.push(tmp);
                    tmpCnt++;
                }
                $scope.paging.total = tmpCnt;
                loadPages();
            },function errorCallback(response) {
                console.log(response);
            });
        };
        //
        function loadPages() {
            if($scope.paging.total>0) {
                // console.log('Current page is : ' + $scope.paging.current);
                $scope.currentPage  = $scope.paging.current;
                self.currentIdx     = self.listIndexes[$scope.currentPage-1];
                var tmp = [];
                var numItems = self.currentIdx.to - self.currentIdx.from;
                for(var ii=0; ii<numItems; ii++) {
                    tmp.push(self.currentIdx.from + ii);
                }
                // self.currentListIdx = tmp;
                // console.log(self.currentListIdx);
                //
                dbinfoService.getDatasetRangeInfo(
                    self.paramDatabase,
                    self.paramType,
                    self.currentIdx.from,
                    self.currentIdx.to
                ).then(
                    function successCallback(response) {
                        self.currentListIdx = response.data;
                    },
                    function errorCallback(response) {
                        console.log(response);
                    }
                );
            }
        }
    }
});


