$(document).ready(function() {
	var selected_row;

	bloodhound = new Bloodhound({
		datumTokenizer: function(d) {
			return Bloodhound.tokenizers.whitespace(d.val);
		},
		limit: 100,
		queryTokenizer: Bloodhound.tokenizers.whitespace,
		remote: {
			url: '/search?q=%QUERY',
			wildcard: '%QUERY',
		},
	});

	function display_results(datums) {
		if (datums.length >= 1) {
			var output = "<table class='ui compact table'>";
			datums.map(function(datum) {
				output += "<tr><td class='collapsing'>";
				if (datum.styled) {
					output += "<div class='ui circular label' title='Styled'>S</div>";
				}
				output += "</td><td>";
				output += "<a href='/metric/" + datum.name_urlsafe + "/'>";
				output += datum.name + "</a></td></tr>";
			})
			output += "</table>";
			$("#results").html(output);
		}
		else {
			$("#results").html("Nothing found.");
		}
	}

	$("#search").keydown(function(event) {
		var rows = $("tr");
		if (event.which == 13 && selected_row) {
			window.location = selected_row.find("a")[0].href;
		}
		else if (event.which == 40) {
			if (selected_row) {
				selected_row.removeClass("active");
				next = selected_row.next();
				if (next.length > 0) {
					selected_row = next.addClass("active");
				} else {
					selected_row = rows.eq(0).addClass("active");
				}
			} else {
				selected_row = rows.eq(0).addClass("active");
			}
		}
		else if (event.which == 38) {
			if (selected_row) {
				selected_row.removeClass("active");
				prev = selected_row.prev();
				if (prev.length > 0) {
					selected_row = prev.addClass("active");
				} else {
					selected_row = rows.last().addClass("active");
				}
			} else {
				selected_row = rows.last().addClass("active");
			}
		}
	});

	$("#search").keyup(function(event) {
		query = $("#search").val();
		if (event.which != 38 && event.which != 40) {
			if (query.length > 1 || event.which == 13) {
				bloodhound.search(query, function(d){}, display_results);
				selected_row = null;
			}
			else if (query.length <= 1) {
				$("#results").html("");
				selected_row = null;
			}
		}
	});

	$('#search').select();
});
