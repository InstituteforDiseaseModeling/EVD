
// ****** Histogram code ********

//parent function
var Histogram = function(sets){

	//settings
	var self = this
	self.height = 225
	self.width = 350
	self.padding = { 'xAxis': 50,
					 'yAxis': 100,
					 'rightEdge': 15,
					 'topEdge': 15
					}

	self.color = 'blue'
	self.data = sets.data
	self.title = sets.title

	//append div and svg
	self.div = d3.select('#hist-container')//.append('div')
		//.style('height', self.height + 'px')
		//.style('width', self.width + 'px')
		//.style('display', 'inline-block') //TODO LEARN ABOUT THIS SO WE CAN POSITION DIVS WRT MAP

	self.svg = self.div.append('svg').attr('id', self.title+'-svg').style('width', self.width)

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

	//get x-and y-axis set up
	allScales['xAxisFunction'] = d3.svg.axis()
				.scale(allScales['xScale'])
				.orient('bottom')
				.ticks(10)
				.tickFormat(d3.format('d'))

	allScales['yAxisFunction'] = d3.svg.axis()
				.scale(allScales['yAxisScale'])
				.orient('left')
				.ticks(7)

	self.scaleFunctions = allScales

	//position rects within svg
	self.rectFeatures = function(rect){
		rect.attr('width', allScales['xWidth']) 
			.attr('height', function(d){return allScales['yScale'](d.cases)})
			.attr('x', function(d){return (allScales['xScale'](d.id) + self.padding['xAxis']) })
			.attr('y', function(d){return (self.height - self.padding['yAxis']) - allScales['yScale'](d.cases)})
			.attr('id', function(d){return d.id})
			.style('fill', self.color)
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

	//y-axis
	self.svg
			.append('g')
			.attr('class', 'axis')
			.attr('transform', 'translate(' + self.padding['xAxis']+ ','+ self.padding['topEdge'] + ')')
			.call(self.scaleFunctions['yAxisFunction'])


	//draw rects 
	self.rects = self.svg.selectAll('rect')
		.data(self.data)

	self.rects.enter().append('rect').call(self.rectFeatures)
	self.rects.exit().remove()
	self.rects.transition().duration(500).call(self.rectFeatures)

	//TODO: labels
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

	//let's take the 'cumulative' bit out, we can plot that elsewhere 
	try{
		delete initial_data['Cumulative']
	}
	catch (e) {}

	self.data = []
	var alldata = []
	d3.keys(initial_data).map(function(d){
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