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

function update_output_buttons(id, state)
{
	ico_size=24
	if (state == 1) state = 0; else state = 1;

	element = document.getElementById('out_'+id);

	if (element != null) {
		if (state == 0) ico='/ico/power_red.png';
		else ico = '/ico/power_blue.png';
		element.innerHTML = '<button onclick="change_state('+id+', '+state+')" type="button"><IMG height="'+ico_size+'" width="'+ico_size+'" border="0" src="'+ico+'"></button>';
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
    $.get("/cgi-bin/outputstates.fcgi", function(data, status) {
        var arr = JSON.parse('[' + data + ']')
        for (var i in arr) {
			update_output_buttons(arr[i][0], arr[i][1]);
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

