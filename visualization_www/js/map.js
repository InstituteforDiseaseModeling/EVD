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
		var national_settings = [{'iso3':'GIN',
								  'color': 'purple'},
							    {'iso3':'LBR',
								  'color': 'purple'},
							    {'iso3':'SLE',
								  'color': 'purple'}]


	// aggregate subnational and national data to get proper colorscales on the district and national level 

		//combine all the subnational data; find the biggest value
		var all_data = []
		var summed_vals = {}
		for (i=0; i<national_settings.length; i++) {
			var nat_name = national_settings[i]['iso3']
			var nat_data = all_case_data[nat_name]['Cumulative']
			var nat_array = d3.keys(nat_data).map(function(d) { return nat_data[d] })
			all_data.push.apply(all_data, nat_array)
			summed_vals[nat_name] = d3.sum(nat_array)
		}

		//set minima and maxima for district-level colorscale
		var district_min = d3.min(all_data)
		var district_max = d3.max(all_data)

		//set minima and maxima for national-level colorscale 
		var summed_array = d3.keys(summed_vals).map(function(d){return summed_vals[d]})
		var national_min = d3.min(summed_array)
		var national_max = d3.max(summed_array)


	//function for subnat plotting on national click
	var showSubnats = function(d){

		//get properties of national value, load shapefile
			var nat_name = $(this).attr('id')
			var nat_color = $(this).attr('fill')
			var subnat_shape = topojson.feature(subnats, subnats.objects[nat_name + '_subnat']).features

		//get rid of the current subnats 
			map_g.selectAll('.subnational').remove()
			//$('.subnational').fadeOut(400)


		//load file that maps elements of the ordered list of subnationals to the subnat names
			var name_map = subnat_name_mapping[nat_name]

		//load the incidence data
			var national_cases = all_case_data[nat_name]
			var cumulative_cases = national_cases['Cumulative']

		// get min and max, and set up a color scale
			var case_values = d3.keys(cumulative_cases).map(function(d) {return cumulative_cases[d]})
			var color_scale = d3.scale.linear().range(['white', nat_color]).domain([district_min, district_max])

		//plot subnats
			var subnat_paths = map_g.selectAll('.subnational')
					.data(subnat_shape)
					.enter()
					.append('path')
					.attr('class', 'subnational' )
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

		//mouseover text: list name of province and number of cases so far
			$('#map-g .subnational').poshytip({
			alignTo: 'cursor', // Align to cursor
			followCursor: true, // follow cursor when it moves
			showTimeout: 0, // No fade in
			hideTimeout: 0,  // No fade out
			alignX: 'center', // X alignment
			alignY: 'inner-bottom', // Y alignment
			className: 'tip-twitter', // Class for styling
			offsetY: 10, // Offset vertically
			slide: false, // No slide animation
			content: function(d){
				var obj = this.__data__ // Data associated with element
				var name = $(this).attr('id') // Name from properties
				var nat_name = $(this).attr('parent_id')
				var cases = all_case_data[nat_name]['Cumulative'][name] // iso3
				return name + ' : ' + cases + ' Cases' // String to return
			}
			})
	
	}

	//define national data
	var nat_shape_data = topojson.feature(national, national.objects.layer).features

	//plot outlines of countries
		var national_paths = map_g.selectAll('.national')
			.data(nat_shape_data)
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


		//make national fill dependent on cumulative cases nationally
		national_paths.attr('fill', function(d,i){
			var nat_name = $(this).attr('id')
			var base_color = national_settings[i]['color']
			var nat_cases = summed_vals[nat_name]
			var nat_color_scale = d3.scale.linear().range(['white', base_color]).domain([0, national_max])
			var nat_color = nat_color_scale(nat_cases)
			return nat_color
		})






