function UpdateDateTime()
{
	var options = { weekday:'short', month:'short', day:'numeric', year:'numeric', hour:'numeric', minute:'numeric', second:'numeric' };
    var date = new Date(); //.toLocaleString('en-US', options);
    document.getElementById('date').innerHTML = date;
}


function GetTemperaturies()
{
    $.get("/cgi-bin/temperatures.fcgi", function(data, status) {
		if (status == 'success') {
        	var arr = JSON.parse('[' + data + ']')
        	for (var i in arr) {
            	document.getElementById(arr[i][0]).innerHTML=arr[i][1];
        	}
		} else {
			alert("Ошибка получения температуры: "+status+data)
		}
    }) .fail(function(data) {
    	//alert( "Скрипт получения температуры вернул ошибку либо не найден.");
	});
}


function ChangeDisplayStateOn(id)
{
    document.getElementById(id).innerHTML='<b id=' + id + '><font color="red">'+id+'</font></b>';
}
function ChangeDisplayStateOff(id)
{
    document.getElementById(id).innerHTML='<b id=' + id + '><font color="white">'+id+'</font></b>';
}

function update_output_buttons(id, state, page)
{
	cfg_page=false
	ico_size=24
	if (page == 'configured_outputs.fcgi') cfg_page=true

	if (state == 1) state = 0; else state = 1;

	element = document.getElementById('out_'+id);

	if (element != null) {
		if (cfg_page == true) {
			if (state == 0) ico='/ico/Power_On.png';
			else ico = '/ico/Power_Off.png';
			ico_width=48
			ico_height=48

			name_element = document.getElementById('name_'+id)
			if (name_element != null) name = name_element.innerText
			else name = 'No name element'

			element.innerHTML = `
<button onclick="change_state(${id}, ${state})" type="button">
	<div class="container">
		<img height="${ico_height}" width="${ico_width}" border="0" src="${ico}">
		<div class="middle-left"><font color="white" id=name_${id}>${name}</font></div>
	</div>
</button>`;
		} else {
			if (state == 0) ico='/ico/Power_On.png';
			else ico = '/ico/Power_Off.png';
			element.innerHTML = '<button onclick="change_state('+id+', '+state+')" type="button"><IMG height="'+ico_size+'" width="'+ico_size+'" border="0" src="'+ico+'"></button>';
		}
	} else {
		element = document.getElementById('out_inuse_'+id);
		if (element != null) {
			if (state == 0) ico='/ico/lightbulb-On.png';
			else ico = '/ico/lightbulb-Off.png';
			element.innerHTML='<b id=out_inuse_' + id + '><IMG height="'+ico_size+'" width="'+ico_size+'" border="0" src="'+ico+'"></b>';
		}
	}
}


function GetInputStates()
{
    $.get("/cgi-bin/inputstates.fcgi", function(data, status){
        var arr = JSON.parse('[' + data + ']')
        for (var i in arr) {
			if (arr[i][1] == 1) {
                ChangeDisplayStateOn(arr[i][0]);
            } else {
                ChangeDisplayStateOff(arr[i][0]);
            }
        }
    });
}

function GetOutputsState()
{
	path = window.location.pathname;
	page = path.split("/").pop();

    $.get("/cgi-bin/outputstates.fcgi", function(data, status) {
        var arr = JSON.parse('[' + data + ']')
        for (var i in arr) {
			update_output_buttons(arr[i][0], arr[i][1], page);
        }
    });
}

function change_state(pin, state)
{
	str="/cgi-bin/outchangestate_clear.fcgi?port="+ pin +"&state="+state
	$.get(str, function(data, status) {
		if (status == 'success') {
			GetOutputsState()
			//update_output_buttons(pin, state);
		} else {
			alert("Ошибка изменения состояния выхода: "+pin+"\n"+status+"\n"+data)
		}
	});
}


function GettingGPIOStates()
{
    GetOutputsState()
    GetInputStates()
}

function InitTimer()
{
    GetTemperaturies();
    GettingGPIOStates();

    setInterval('UpdateDateTime()',    1000);
    setInterval('GettingGPIOStates()', 1000);
    setInterval('GetTemperaturies()',  5000);
}

