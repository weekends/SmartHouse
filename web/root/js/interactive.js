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
    document.getElementById(id).innerHTML='<b id=' + id + '><font color="red">On</font></b>'
}
function ChangeDisplayStateOff(id)
{
    document.getElementById(id).innerHTML='<b id=' + id + '><font color="white">Off</font></b>'
}


function ChangeOutDisplayStateOn(id)
{
	element = document.getElementById('out_'+id)
	if (element != null) element.innerHTML='<button onclick="change_state('+id+', 0)"><font color="red">Off</font></button>';

	element = document.getElementById('out_inuse_'+id)
	if (element != null) element.innerHTML='<b id=out_inuse_' + id + '><font color="red">On</font></b>'
}

function ChangeOutDisplayStateOff(id)
{
	element = document.getElementById('out_'+id)
	if (element != null) element.innerHTML='<button onclick="change_state('+id+', 1)"><font color="white">On.</font></button>';

	element = document.getElementById('out_inuse_'+id)
	if (element != null) element.innerHTML='<b id=out_inuse_' + id + '><font color="white">Off</font></b>'
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
            if (arr[i][1] == 1) {
                ChangeOutDisplayStateOn(arr[i][0]);
            } else {
                ChangeOutDisplayStateOff(arr[i][0]);
            }
        }
    });
}

function change_state(pin, state)
{
	str="/cgi-bin/outchangestate_clear.fcgi?port="+ pin +"&state="+state
	$.get(str, function(data, status) {
		if (status == 'success') {
			if (state == 1) {
				ChangeOutDisplayStateOn(pin)
			} else {
				ChangeOutDisplayStateOff(pin)
			}
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
    setInterval('GettingGPIOStates()', 5000);
    setInterval('GetTemperaturies()',  5000);
}

