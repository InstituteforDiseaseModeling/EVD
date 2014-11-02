
// ****** Histogram code ********

//parent function
var Histogram = function(sets){

	//settings
	var self = this
	self.height = 80
	self.width = 360
	self.padding = { 'xAxis': 35,
					 'yAxis': 15,
					 'rightEdge': 15,
					 'topEdge': 5
					}

	self.color = 'firebrick' // navy, firebrick, olive
	self.data = sets.data
	self.title = sets.title

	//append div and svg
	self.svg = d3.select('#hist-container').append('svg')
				 .attr('id', self.title + '-svg')
				 .style('width', self.width)
				 .style('height', self.height)

	//create scales that both the axes and the rects will use for sizing
	var allScales = {}
	allScales['xScale'] =  d3.scale.linear()
									.domain([0, d3.max(self.data, function(d){return d.id})])
									.range([0, self.width-self.padding['xAxis'] - self.padding['rightEdge']])
	
	allScales['yScale'] =  d3.scale.linear()
									.domain([0, sets.max])
									.range([0, self.height - self.padding['yAxis'] - self.padding['topEdge'] ])

	allScales['yAxisScale'] = d3.scale.linear()
									.domain([0, sets.max])
									.range([self.height - self.padding['yAxis'] - self.padding['topEdge'], 0])

	allScales['xWidth'] = allScales['xScale'](1) - allScales['xScale'](0)

	// convert 52 week numeric scale to months...
	var t = d3.time.scale()
		.domain([new Date(2012, 0, 1), new Date(2012, 11, 31)])
		.range([0, self.width - self.padding['xAxis'] - self.padding['rightEdge']])

	allScales['xAxisFunction'] = d3.svg.axis()
		.scale(t)
		.orient("bottom")
		.ticks(d3.time.months)
		.tickSize(6, 0)
		.tickFormat(d3.time.format("%b"));

	//get x-and y-axis set up
	//allScales['xAxisFunction'] = d3.svg.axis()
	//			.scale(allScales['xScale'])
	//			.orient('bottom')
	//			.ticks(10)
	//			.tickFormat(d3.format('d'))

	allScales['yAxisFunction'] = d3.svg.axis()
				.scale(allScales['yAxisScale'])
				.orient('left')
				.ticks(2)

	self.scaleFunctions = allScales

	//position rects within svg
	self.rectFeatures = function(rect){
		rect.attr('width', allScales['xWidth']) 
			.attr('height', function(d){return allScales['yScale'](d.cases)})
			.attr('x', function(d){return (allScales['xScale'](d.id) + self.padding['xAxis']) })
			.attr('y', function(d){return (self.height - self.padding['yAxis']) - allScales['yScale'](d.cases)})
			.attr('id', function(d){return d.id})
			.style('fill', self.color)
			.style('fill-opacity', 0.5)
	}

	self.draw()
}

//function to draw rects, axes, and labels
Histogram.prototype.draw = function() {
	var self=this

	//draw axes

	//x-axis
	self.svg 
			.append('g')
			.attr('class', 'axis')
			.attr('transform', 'translate(' + self.padding['xAxis'] + ',' + (self.height - self.padding['yAxis']) +')')
			.call(self.scaleFunctions['xAxisFunction'])
	  .selectAll(".tick text")
		.style("text-anchor", "start")
		.attr("x", 4)
		.attr("y", 4);

	//y-axis
	self.svg
			.append('g')
			.attr('class', 'axis')
			.attr('transform', 'translate(' + self.padding['xAxis']+ ','+ self.padding['topEdge'] + ')')
			.call(self.scaleFunctions['yAxisFunction'])
	  .append("text")
		//.attr("transform", "rotate(-90)")
		.attr("y", 6)
		.attr("x", 6)
		.attr("dy", ".71em")
		.attr("class","district-text")
		//.style("text-anchor", "end")
		.text(self.title);



	//draw rects 
	self.rects = self.svg.selectAll('rect')
		.data(self.data)

	self.rects.enter().append('rect').call(self.rectFeatures)
	self.rects.exit().remove()
	self.rects.transition().duration(500).call(self.rectFeatures)
}


// ****** View code ********

//EbolaView will create the full set of charts for this viz
//to start: just histograms
// TODO: incorporate mapping function

var EbolaView = function(iso3){
	var self = this
	self.charts = []
	self.build(iso3)
} 

// build function
EbolaView.prototype.build = function(iso3){
	var self = this
	self.prepData(iso3)
	self.makePlots()
	//self.makeInteractive()
}

// prep data
EbolaView.prototype.prepData = function(iso3){
	var self=this
	var initial_data = all_case_data[iso3]

	//let's take the 'cumulative' bit out after sorting districts by cumulative counts
	try {
		sorted_keys=d3.keys(initial_data['Cumulative']).sort(function (a, b) { return -(initial_data['Cumulative'][a] - initial_data['Cumulative'][b]) });
		delete initial_data['Cumulative']
	}
	catch (e) {
		d3.keys(initial_data)
	}

	self.data = []
	var alldata = []
	//d3.keys(initial_data)
	sorted_keys
		.map(function (d) {
		var cases = initial_data[d]
		alldata.push.apply(alldata, cases)
		var obs = cases.length
		var data = []
		
		d3.range(obs).map(function(d,i){ 
			data.push({id:i, cases:cases[i]})
		})
		self.data[d] = data
	})
	//we want each plot to be scaled to the maximum among all districts, not just its own max
	self.maxdata = d3.max(alldata) 

}

//make plots 
EbolaView.prototype.makePlots = function(){
	var self = this
	d3.keys(self.data).map(function(d){
		self.charts[d] = new Histogram( {
			data: self.data[d],
			title: d,
			max: self.maxdata
			})
	})
}


// ****** Instantiation code ********

var testView = new EbolaView('LBR')