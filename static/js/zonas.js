/************************************************************************************/
/************************************************************************************/
/****************Desarrollador, Programador: Alan Claros Camacho ********************/
/****************E-mail: alan_Claros13@hotmail.com **********************************/
/************************************************************************************/
/************************************************************************************/

//control especifico del modulo
function controlModulo() {

	return true;
}

function sendSearchZona() {
	token_search = document.forms['search'].elements['csrfmiddlewaretoken'].value;

	datos_search = {
		'module_x': document.forms['form_operation'].elements['module_x'].value,
		'csrfmiddlewaretoken': token_search,
		'search_button_x': 'acc',
	}
	datos_search['search_zona'] = document.getElementById('search_zona').value;
	datos_search['search_codigo'] = document.getElementById('search_codigo').value;

	div_modulo.html(imagen_modulo);
	div_modulo.load('/', datos_search, function () {
		//termina de cargar la ventana
	});
}

function mandarFormularioZona(operation, operation2, formulario, add_button, button_cancel) {
	if (verifyForm()) {
		document.forms[formulario].elements[add_button].disabled = true;
		document.forms[formulario].elements[button_cancel].disabled = true;

		//document.forms[formulario].submit();
		token_operation = document.forms['form_operation'].elements['csrfmiddlewaretoken'].value;
		module_x = document.forms['form_operation'].elements['module_x'].value;

		var fd = new FormData();
		fd.append('csrfmiddlewaretoken', token_operation);
		fd.append('module_x', module_x);
		fd.append('operation_x', operation);
		fd.append('id', document.forms['form_operation'].elements['id'].value);

		fd.append(operation2, 'acc');

		fd.append('ciudad', document.getElementById('ciudad').value);
		fd.append('zona', document.getElementById('zona').value);
		fd.append('codigo', document.getElementById('codigo').value);
		fd.append('activo', document.getElementById('activo').checked ? 1 : 0);

		div_modulo.html(imagen_modulo);

		$.ajax({
			url: '/',
			type: 'post',
			data: fd,
			contentType: false,
			processData: false,
			success: function (response) {
				if (response != 0) {
					div_modulo.html(response);
				} else {
					alert('error al realizar la operacion, intentelo de nuevo');
				}
			},
		});
	}
}

function confirmarEliminarZona() {
	if (confirm('Esta seguro de querer eliminar esta zona?')) {
		token_operation = document.forms['form_operation'].elements['csrfmiddlewaretoken'].value;

		document.forms['formulario'].elements['add_button'].disabled = true;
		document.forms['formulario'].elements['button_cancel'].disabled = true;

		datos_operation = {
			'module_x': document.forms['form_operation'].elements['module_x'].value,
			'csrfmiddlewaretoken': token_operation,
			'operation_x': 'delete',
			'delete_x': 'acc',
		}
		datos_operation['id'] = document.forms['form_operation'].elements['id'].value;
		datos_operation['zona'] = document.getElementById('zona').value;

		div_modulo.html(imagen_modulo);
		div_modulo.load('/', datos_operation, function () {
			//termina de cargar la ventana
		});
	}
}