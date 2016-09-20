/**
 * Created by ar on 11.09.16.
 */

'use strict';

angular.module('datasetImage2dPreview2', ['ngMaterial', 'datasetImage2dPaging2', 'cl.paging'])
.component('datasetImage2dPreview2', {
    templateUrl: '/frontend/components/preview/dataset-image2d-preview/dataset-image2d-preview2.html',
    bindings: {
        databaseId:     '@',
        datasetType:    '@',
        listClasses:    '<'
    },
    controller: function ($scope, $http, dbinfoService) {
        var self = this;
        self.listClasses = [];
        self.$onInit = function () {
            self.listClasses = [];
            dbinfoService.getInfoStatWithHistsAboutDB(self.databaseId).then(
                function successCallback(response) {
                    var tdataHist   = response.data.hist.histTrain;
                    var numAll      = response.data.info.numTrain;
                    if(self.datasetType=='val') {
                        tdataHist = response.data.hist.histVal;
                        numAll      = response.data.info.numVal;
                    }
                    var tret=[];
                    for(var ii=0; ii<tdataHist.length; ii++) {
                        var tkey = tdataHist[ii][0];
                        var tnum = tdataHist[ii][1];
                        tret.push({
                            type:   'class',
                            idx:    tkey,
                            num:    tnum,
                            info:   tkey
                        });
                    }
                    // all data:
                    tret.push({
                        type:   'all',
                        idx:    '---',
                        num:    numAll
                    });
                    self.listClasses = tret;
                    // console.log(self.listClasses);
                }, function errorCallback(response) {
                    console.log(response);
                }
            );
        };
    }
});