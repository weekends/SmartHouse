function Test()
{
    document.write("<p>" + Date() + "</p>");
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
	document.getElementById('out_'+id).innerHTML='<button onclick="change_state('+id+', 0)"><font color="red">Off</font></button>';
//	document.getElementById('out_'+id).innerHTML='<b id=out_' + id + '><font color="red">On</font></a></b>';
//	document.getElementById('out_'+id).innerHTML='<b id=out_' + id + '><a target="_blank" href="/cgi-bin/outchangestate.cgi?port='+ id +'&state=0"><font color="red">On</font></a></b>';
}
function ChangeOutDisplayStateOff(id)
{
	document.getElementById('out_'+id).innerHTML='<button onclick="change_state('+id+', 1)"><font color="white">On.</font></button>';
//	document.getElementById('out_'+id).innerHTML='<b id=out_' + id + '><font color="white">Off</font></b>';
//	document.getElementById('out_'+id).innerHTML='<b id=out_' + id + '><a target="_blank" href="/cgi-bin/outchangestate.cgi?port='+ id +'&state=1"><font color="white">Off</font></a></b>';
}

function UpdateDateTime()
{
    var date = new Date();
    document.getElementById('date').innerHTML = date;
}

function GetInputStates()
{
    $.get("/cgi-bin/inputstates.cgi", function(data, status){
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
    $.get("/cgi-bin/outputstates.cgi", function(data, status) {
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
	str="/cgi-bin/outchangestate_clear.cgi?port="+ pin +"&state="+state
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

function GetTemperaturies()
{
    $.get("/cgi-bin/temperatures.cgi", function(data, status) {
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

function GettingGPIOStates()
{
    GetInputStates()
    GetOutputsState()
}

function InitTimer()
{
    GetTemperaturies();
    GettingGPIOStates();

    setInterval('UpdateDateTime()',    1000);
    setInterval('GettingGPIOStates()', 5000);
    setInterval('GetTemperaturies()',  5000);
}

