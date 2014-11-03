//Subnational-level map of Ebola


//////////////////
///SETUP
//////////////////

	//Projections, locate things on page
		var settings = {width: document.getElementById('map-container').clientWidth,
						height: 800,
						padY: 20,
						padX: -180}

		// Set map projection
			 var center = d3.geo.centroid(topojson.feature(national, national.objects.layer))
			 var map_scale  = 3800;
			 var projection = d3.geo.equirectangular().scale(map_scale).center(center)
					  //.translate([settings.width/2, settings.height/4]);
					  //.translate([settings.width/2, settings.height/4]);

				// Set path generator -- how coordinates translate into a path element
				var path = d3.geo.path().projection(projection)

		//generate main SVG, smaller G which will contain the actual map, and title G
			var full_svg = d3.select('#map-container').append('svg')
						.attr('width', settings.width)
						.attr('height', settings.height)
						.attr('id', 'full-svg')

			var map_g = d3.select('#full-svg')
						 .append('g')
						 .attr('id', 'map-g')
						 .attr('transform', 'translate ('+settings.padX+',' + settings.padY + ')')


		//function to get the first element of an object
		var firstElem = function(obj) {
		    for (var key in obj) {
		        if (obj.hasOwnProperty(key)) return key;
		    }
		}


		//function for customizeable poshytip mouseovers
		var makePoshyTip = function(identifier, contentFunction){
			$(identifier).poshytip({
			alignTo: 'cursor', // Align to cursor
			followCursor: true, // follow cursor when it moves
			showTimeout: 0, // No fade in
			hideTimeout: 0,  // No fade out
			alignX: 'center', // X alignment
			alignY: 'inner-bottom', // Y alignment
			className: 'tip-twitter', // Class for styling
			offsetY: 10, // Offset vertically
			slide: false, // No slide animation
			content: contentFunction
			})
		}


//////////////////
///PLOTTING
//////////////////

	//assign names to national paths
		var national_settings = [{'iso3':'GIN',
								  'fullName': 'Guinea',
								  'color': 'navy'},
								{'iso3':'LBR',
								  'fullName': 'Liberia',
								  'color': 'firebrick'},
								{'iso3':'SLE',
								 'fullName': 'Sierra Leone',
								  'color': 'olive'}]


	// We need to do a couple of things with this data before we map:

	// 1. Even though you only see one country's subnationals at a time, we should scale the cloropleth 
	//  	to the highest-case district of all countries-- otherwise, the highest-case district in LBR 
	//		will look just as severe as the highest case country in GIN, even though the former has far 
	//		fewer cases.

	// 2. We should do something similar for the national-level colors: scale to the highest-case country

	// 3. The data is already set up in time series by district, so it's easy to make histograms for them.
	//		We should also make a national-level time series of incidence that is displayed when the screen loads.

	// We do all of these things in the following loop. 

		//combine all the subnational data; find the biggest value
		var all_subnational_values = []
		var national_cases = {}
		national_cases['Cumulative'] = {}

		for (i=0; i<national_settings.length; i++) {

			var nat_name = national_settings[i]['iso3']

			// 1. extract subnational case data; later we will take the max of these values and use it for the color scale 
			var subnat_data = all_case_data[nat_name]
			var cum_subnat_data = subnat_data['Cumulative'] //extract cumulative case data from each district; this will still be an object
			var cum_subnat_array = d3.keys(cum_subnat_data).map(function(d) { return cum_subnat_data[d] }) // extract just the case counts from this object; this will be an array
			all_subnational_values.push.apply(all_subnational_values, cum_subnat_array) // push that array into the country-spanning array we want to take the maximum value of

			// 2. Sum values across districts to get a national cumulative value; use this to scale the national colors
			national_cases[nat_name] = []
			national_cases['Cumulative'][nat_name] = d3.sum(cum_subnat_array)

			// 3. Generate a national-level time series
			var first_element = firstElem(subnat_data)
			var week_count = subnat_data[first_element].length

			for (j=0; j<week_count; j++) {
				var element_j = d3.keys(subnat_data).map(function(d){
					if ( (d=="Cumulative") || (d=="National") ){
						return 0
					}
					return subnat_data[d][j]
				})
			    national_cases[nat_name][j] = d3.sum(element_j)
			} //end subnat loop
		} //end national loop
 
		//set minima and maxima for district-level colorscale
		var district_min = 0//d3.min(all_subnational_values)
		var district_max = d3.max(all_subnational_values)

		//set minima and maxima for national-level colorscale 
		var summed_array = d3.keys(national_cases['Cumulative']).map(function(d){return national_cases['Cumulative'][d]})
		var national_min = 0//d3.min(summed_array)
		var national_max = d3.max(summed_array)


	//function for subnat plotting on national click
		var showSubnats = function (d) {

		//get properties of national value, load shapefile
			var nat_name = $(this).attr('id')
			var nat_color = $(this).attr('fill')
			var subnat_shape = topojson.feature(subnats, subnats.objects[nat_name + '_subnat']).features

		//get rid of the current subnats 
			map_g.selectAll('.subnational').remove()
			//$('.subnational').fadeOut(400)

		//load file that maps elements of the ordered list of subnationals (in shapefile) to the subnat names
			var name_map = subnat_name_mapping[nat_name]

		//load the incidence data
			var national_cases = all_case_data[nat_name]
			var cumulative_cases = national_cases['Cumulative']

			// some districts have no reported cases, and as such do not appear in our data.
			// To ensure that these get mapped appropriately, we add zeroed entries for them 
			// to our cumulative_cases object.
			for (j=0; j<d3.keys(name_map).length; j++) {
				if (d3.keys(cumulative_cases).indexOf(name_map[j])== -1){
					cumulative_cases[ name_map[j] ] = 0
				}
			}

		// set up a color scale using the min and max for districts in all countries, for consistency
			var color_scale = d3.scale.sqrt().range(['white', nat_color]).domain([district_min, district_max])

		//plot subnats
			var subnat_paths = map_g.selectAll('.subnational')
					.data(subnat_shape)
					.enter()
					.append('path')
					.attr('class', 'subnational' )
					.attr('id', function (d, i) {return name_map[i]})
					.attr('parent_id', nat_name)
					.attr('fill', nat_color)
					.attr('stroke', '#000')
					.attr('stroke-width', 0.2)
					.attr('stroke-opacity', 0.5)
					.attr('d', path)

		//fill in colors
			subnat_paths.attr('fill', function(d,i){
				var subnat_name = $(this).attr('id')
				var value = cumulative_cases[subnat_name]
				var color = color_scale(value)
				return color
			})


		// set up inputs for subnational map poshytip
			var subnatIdentifier = '#map-g .subnational'
			var subnatContentFunction = function(d){
				var obj = this.__data__ // Data associated with element
				var name = $(this).attr('id') // Name from properties
				var nat_name = $(this).attr('parent_id')
				var cases = all_case_data[nat_name]['Cumulative'][name] // iso3
				return name + ' : ' + cases + ' Cases' // String to return
			}

			makePoshyTip(subnatIdentifier, subnatContentFunction)

			d3.selectAll('.case-hist').remove()
			var testView = new EbolaView(nat_name, 'subnational')
	
	}


	//define national data
	var nat_shape_data = topojson.feature(national, national.objects.layer).features

	//plot outlines of countries
		var national_paths = map_g.selectAll('.national')
			.data(nat_shape_data)
			.enter()
			.append('path')
			.attr('class', function(d,i){return 'national' + ' ' + national_settings[i].fullName})
			.attr('id', function(d,i){return national_settings[i].iso3})
			.attr('fill', function(d,i){return national_settings[i].color})
			.attr('fill-opacity', 0.5)
			.attr('stroke', "#000")
			.attr('stroke-width', 0.5)
			.attr('stroke-opacity', 0.5)
			.attr('d', path)
		  .on('click', showSubnats)


		//make national fill dependent on cumulative cases nationally
		national_paths.attr('fill', function(d,i){
			var nat_name = $(this).attr('id')
			var base_color = national_settings[i]['color']
			var nat_cases = d3.sum(national_cases[nat_name])
			var nat_color_scale = d3.scale.linear().range(['white', base_color]).domain([0, national_max])
			var nat_color = nat_color_scale(nat_cases)
			return nat_color
		})


	//set up inputs for national map poshytip
		var natIdentifier = '#map-g .national'
		var natContentFunction = function(d){
			var natName = $(this).attr('id') // iso3 for pulling case count
			var fullName = $(this).attr('class') // full name for pretty poshytip
			fullName = fullName.replace('national ', '') 
			var cases = national_cases['Cumulative'][natName] //cumulative case count
			return fullName + ' : ' + cases + ' Cases' // String to return
		}

		makePoshyTip(natIdentifier, natContentFunction)

	//plot national bar charts
	var natPlots = new EbolaView('G', 'national')






