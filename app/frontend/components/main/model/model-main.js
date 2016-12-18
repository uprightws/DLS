(function () {
    'use strict';

    angular.module('modelMain', ['ngMaterial', 'modelService', 'inference', 'validation'])
        .component('modelMain', {
            templateUrl: '/frontend/components/main/model/model-main.html',
            bindings: {
                models: '<',
                selected:'<'
            },
            controller: function ($rootScope, modelService) {

                var self = this;
                this.$onInit = function () {
                    self.models = [];

                    modelService.listInfo().then(
                        function successCallback(response) {
                            response.data.forEach(function (model) {
                                var info = model.info;
                                self.models.push({
                                    'name': info.name,
                                    'id': info.id,
                                    'network': "Test Network",//TODO Add network name to description of trained model
                                    'dataSet': info['dataset-name'],
                                    'dataSetId': info['dataset-id'],
                                    'type': info.type,
                                    'date': info.date.str + " " + info.time.str,
                                    'size': info.size.str,
                                    "trainingData":model.progress
                                });
                            });
                            self.selected = self.models[0];
                            self.initChart(self.selected);
                        },
                        function errorCallback(response) {
                            console.log(response.data);
                        })
                };

                this.selectModel = function( model ) {
                    self.selected = angular.isNumber(model) ? $scope.models[model] : model;
                    $rootScope.$emit('model_select', model);
                    self.initChart(model);
                };
                
                this.initChartTrace = function(xArray, yArray, name){
                    return  {
                                x: xArray,
                                y: yArray,
                                mode: 'lines+markers',
                                name: name
                            };
                }
                
                this.initChartLayout = function(title){
                    return {
                                title: title,
                                //autosize: true,
                                height: 500,
                                width: 1000,
                                xaxis: {
                                    title: 'Iterations',
                                    showline: false
                                },
                                yaxis: {
                                    title: 'Training Parameters',
                                    showline: false
                                }
                            };
                }
                
                this.initChart = function(model){
                           
                            var traceTrainAcc = this.initChartTrace(model.trainingData.iter, model.trainingData.accTrain, 'Training');
                            var tracetrainLoss = this.initChartTrace(model.trainingData.iter, model.trainingData.lossTrain, 'Traininggs');
                            var traceValacc = this.initChartTrace(model.trainingData.iter, model.trainingData.accVal, 'Validation');
                            var traceValLoss = this.initChartTrace(model.trainingData.iter, model.trainingData.lossVal, 'Validation');
                    
                            var dataAcc = [ traceTrainAcc, traceValacc ];
                            var layoutAcc = this.initChartLayout('Accuracy');

                            Plotly.newPlot('model-training-chart', dataAcc, layoutAcc);
                    
                              
                            var dataLoss = [ tracetrainLoss, traceValLoss ];
                            var layoutLoss = this.initChartLayout('Loss Function');

                            Plotly.newPlot('model-validation-chart', dataLoss, layoutLoss);
                };
                
             
            }
        });
})();