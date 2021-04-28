function BaobabFreezerView() {
    var that = this;

    this.load = function() {
        temperatureGraph()

    };

    function temperatureGraph(){
        Highcharts.getJSON(
            window.location.href+'/getGraphData',
            function (data) {
                Highcharts.chart('container', {
                    chart: {
                        zoomType: 'x'
                    },
                    title: {
                        text: 'Freezer Temperature over time'
                    },
                    xAxis: {
                        type: 'datetime'
                    },
                    yAxis: {
                        title: {
                            text: 'Temperature (°C)'
                        }
                    },
                    tooltip: {
                        formatter: function () {
                            var point = this.points[0];
                            return '<b>' + point.series.name + '</b><br/>' + Highcharts.dateFormat('%A %B %e %Y', this.x) + ':<br/>' +
                                Highcharts.numberFormat(point.y, 2) + '°C';
                        },
                        shared: true
                        },
                    legend: {
                        enabled: false
                    },
                    plotOptions: {
                        area: {
                            fillColor: {
                                linearGradient: {
                                    x1: 0,
                                    y1: 0,
                                    x2: 0,
                                    y2: 1
                                },
                                stops: [
                                    [0, Highcharts.getOptions().colors[0]],
                                    [1, Highcharts.color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
                                ]
                            },
                            marker: {
                                radius: 2
                            },
                            lineWidth: 1,
                            states: {
                                hover: {
                                    lineWidth: 1
                                }
                            },
                            threshold: null
                        }
                    },

                    series: [{
                        type: 'area',
                        name: 'Temperature',
                        data: data
                    }]
                });
            }
        );
        // End
    }

}
