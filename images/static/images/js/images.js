var cols_per_row = 4;
var ic_size = 600;
var imgs = [];

String.prototype.format = function() {
    var s = this,
        i = arguments.length;

    while (i--) {
        s = s.replace(new RegExp('\\{' + i + '\\}', 'gm'), arguments[i]);
    }
    return s;
};

$(document).ready(function(){

	if (Object.keys(data).length==0){
		container = document.getElementById('image_container');
		alertcontainerdiv = document.createElement('div');
		alertcontainerdiv.setAttribute('style', 'padding-top: 100px')
		alertdiv = document.createElement('div');
		alertdiv.setAttribute('class', 'alert alert-danger');
		alertdiv.innerHTML = "<strong>Oh snap!</strong> Wasn't able to retrieve any scan data."
		container.appendChild(alertcontainerdiv);
		alertcontainerdiv.appendChild(alertdiv);
	}
	else {
		create_images();
	}

	

	$(document.body).on('DetButtons:selection', function(event, param) {
    	create_images();
	});
	$(document.body).on('DetButtons:deselection', function(event, param) {
    	create_images();
	});

	$(document.body).on('Scan:begin', function(event, new_data){
		data = new_data;
		create_images();
	});

	$(document.body).on('Scan:update', function(event, new_data){

		create_images();
	});

	$(document.body).on('Scan:reply', function(event, new_data) {
		data = new_data;
		create_images();
	});

});

var update_images = function(){
	for (var i = 0; i < imgs.length; i++) {
		imgs[i].updateData({data:data['scan_data'], det: selected_detectors[i]})
	};
}

var create_images = function(){
	create_image_divs()

	for (var i = 0; i < imgs.length; i++) {
		delete imgs[i];
	};

	imgs = [];

	for (var i = 0; i < selected_detectors.length; i++) {
		imgs.push(new ImagePlot({containerId: 'image'+(i+1), data: data['scan_data'], det: selected_detectors[i]}));
	};
}

var create_image_divs = function(){
	n_rows = parseInt(selected_detectors.length/cols_per_row);
	n_cols = selected_detectors.length%cols_per_row;

	var img_container = document.getElementById('image_container');
	while( img_container.hasChildNodes() ){
	    img_container.removeChild(img_container.lastChild);
	}
	
	image_container_width = $("#image_container").width();
	var s = '<table><tbody>';
	for (var i = 0; i < n_rows+1; i++) {
		s += '<tr>';
		for (var j = 0; j < n_cols; j++) {
			s += ' <td> \
					<div id="image{0}" class="lImage" style="width:{1}px;height:{2}px;padding:auto;"></div> \
				   </td>'.format(i*cols_per_row+j+1, d3.min([image_container_width/n_cols, ic_size]), d3.min([image_container_width/n_cols, ic_size]));
		};
		s += '</tr>';
	};
	img_container.innerHTML = s+'</tbody></table>';
}



