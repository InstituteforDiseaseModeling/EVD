//Subnational-level map of Ebola


//////////////////
///SETUP
//////////////////

	//Projections, locate things on page
		var settings = {width: document.getElementById('full-page').clientWidth,
						height: 1150,
						padding: 70}

		// Set map projection
			 var center = d3.geo.centroid(topojson.feature(national, national.objects.layer))
			 var map_scale  = 5000;
			 var projection = d3.geo.equirectangular().scale(map_scale).center(center)
			          .translate([settings.width/2, settings.height/4]);

				// Set path generator -- how coordinates translate into a path element
				var path = d3.geo.path().projection(projection)

		//generate main SVG, smaller G which will contain the actual map, and title G
			var full_svg = d3.select('#full-page').append('svg')
						.attr('width', settings.width)
						.attr('height', settings.height)
						.attr('id', 'full-svg')

			var map_g = d3.select('#full-svg')
						 .append('g')
						 .attr('id', 'map-g')
						 .attr('transform', 'translate (0,' + settings.padding + ')')


//////////////////
///PLOTTING
//////////////////
	//assign names to national paths
		var national_settings = {0: {'iso3':'GIN',
								  'color': 'green'},
							  1: {'iso3':'LBR',
								  'color': 'blue'},
							  2: {'iso3':'SLE',
								  'color': 'red'}}


	//Function to get all the values out of key-value pairs of an object
	var getValues = function(obj){
		var values = []
		for (var key in obj){
			values.push(obj[key])
		}
		return values
	}


	//function for subnat plotting on national click
	var showSubnats = function(d){
		//get rid of the current subnats ones
			map_g.selectAll('.subnational').remove()
			//$('.subnational').fadeOut(400)

		//get properties of national value, load shapefile
			var nat_name = $(this).attr('id')
			var nat_color = $(this).attr('fill')
			var subnat_shape = topojson.feature(subnats, subnats.objects[nat_name + '_subnat']).features

		//load file that maps elements of the ordered list of subnationals to the subnat names
			var name_map = subnat_name_mapping[nat_name]

		//load the incidence data
			var national_cases = all_case_data[nat_name]
			var cumulative_cases = national_cases['Cumulative']

		// get min and max, and set up a color scale
			var case_values = getValues(cumulative_cases)
			var min = d3.min(case_values)
			var max = d3.max(case_values)
			var color_scale = d3.scale.linear().range(['white', nat_color]).domain([min, max])

		//plot subnats
			var subnat_paths = map_g.selectAll('.' + nat_name)
					.data(subnat_shape)
					.enter()
					.append('path')
					.attr('class', 'subnational ' + nat_name)
					.attr('id', function(d,i){return name_map[i]})
					.attr('parent_id', nat_name)
					.attr('fill', nat_color)
					.attr('stroke', '#000')
					.attr('d', path)

		//fill in colors
			subnat_paths.attr('fill', function(d,i){
				var subnat_name = $(this).attr('id')
				var value = cumulative_cases[subnat_name]
				var color = color_scale(value)
				return color
			})
	
	}

	//define national data
	var nat_data = topojson.feature(national, national.objects.layer).features

	//plot outlines of countries
		var national_paths = map_g.selectAll('.national')
			.data(nat_data)
			.enter()
			.append('path')
			.attr('class', 'national')
			.attr('id', function(d,i){return national_settings[i].iso3})
			.attr('fill', function(d,i){return national_settings[i].color})
			.attr('fill-opacity', 0.7)
			.attr('stroke', "#000")
			.attr('stroke-width', 2)
			.attr('d', path)
		  .on('click', showSubnats)


		// //mouseover text: list name of province and number of cases so far
		// $('#map-g path').poshytip({
		// 	alignTo: 'cursor', // Align to cursor
		// 	followCursor: true, // follow cursor when it moves
		// 	showTimeout: 0, // No fade in
		// 	hideTimeout: 0,  // No fade out
		// 	alignX: 'center', // X alignment
		// 	alignY: 'inner-bottom', // Y alignment
		// 	className: 'tip-twitter', // Class for styling
		// 	offsetY: 10, // Offset vertically
		// 	slide: false, // No slide animation
		// 	content: function(d){
		// 		var obj = this.__data__ // Data associated with element
		// 		console.log(obj)
		// 		var name = $(this).attr('id') // Name from properties
		// 		console.log(name)
		// 		var nat_name = $(this).attr('parent_id')
		// 		console.log(nat_name)
		// 		var cases = all_case_data[nat_name]['Cumulative'][name] // iso3
		// 		//mean = data[iso3] == undefined ? '' : data[iso3].mean // Value
		// 		return name + ' : ' + cases + ' Cases' // String to return
		// 	}
		// })


