
function populateListbox(arr) {
    var out = "";
    var i;
    for(i = 0; i < arr.length; i++) {
        out += '<li';
        if(mv == arr[i].id)
        {
           out += ' class="active" ';
        }
        out += ' onclick="onMvButton(' + arr[i].id + ')"><a href="#?mv=' + arr[i].id + '">' + arr[i].Name + '</a></li>'; 
        
    }
    document.getElementById("MvDrop").innerHTML = out;
}
function makeKeyVal(array, key, val)
{
    var lookup = {};
    for (var i = 0, len = array.length; i < len; i++) {
        lookup[array[i][key]] = array[i][val];
    
    }
    return lookup;
}

function formsubmit(formName)
{
    //alert($(formName).serialize())
    $.post("submit_form.php",
        $(formName).serialize(),
        function(data,status){
            var i = data.indexOf("OK");
            if (i> -1) {
                //code
            }else{
            alert(data);
            }
            });
}
function formsubmitThenReload(formName){
    formsubmit(formName);
    getScript('static_parameters.php', function(){
    filter();
    document.getElementById("filterbox").focus();
   });
}
function filter(){
    
	var x = document.getElementById("frm_filter");
    var criteria = x.elements[0].value;
    document.getElementById("filtertext").innerHTML = 'Filtered to ' + criteria;
    populateTable(irds, criteria);
}
function populateTable(arr, criteria) {
    var out = '<div class="row"><div class="col-sm-12">';
    var i;
    var strategies = makeKeyVal(inputStrategies, "PRIMARY", "description");
    var demodsList = makeKeyVal(demods, "id", "labelnamestatic");
    demodsList[0] = "None";
    demodsList["null"] = "None";
    var even = 1;
    var yesno = {0:"No", 1:"Yes"};
    for(i = 0; i < arr.length; i++) {
        var lineSearchable=arr[i].labelnamestatic + arr[i].name + arr[i].ip +arr[i].model_id + arr[i].MulticastIp + arr[i].id;
        if (lineSearchable.toLowerCase().search(criteria.toLowerCase()) !=-1) {
            
    
    

            out += '<div class="row" id="'+ "equip" +arr[i].id;
            if (even == 0) {
                out += '" style="background-color:lavenderblush;';
                even = 1;
            }else{
            even = 0;
            }
            
            out += '">';
            out += '<div class="col-sm-1"><a href="#" class="btn btn-default"  onclick="editLine('+ arr[i].id+')" role="button">edit</a></div>';
            out += '<div class="col-sm-11"><table width=100%><tr>';
            out += '<td width=5%>'+ arr[i].id+'</td>';
            out += '<td width=5%>' + arr[i].name+'</td>';
            out += '<td width=5%>' + arr[i].model_id+'</td>';
            out += '<td width=5%>' + arr[i].ip+'</td>';
            out += '<td width=5%>' + arr[i].labelnamestatic+'</td>';
            out += '<td width=5%>' + arr[i].MulticastIp+'</td>';
            out += '<td width=5%>' + arr[i].InMTXName+'</td>';
            out += '<td width=5%>' + arr[i].OutMTXName+'</td>';
            out += '<td width=5%>' + arr[i].SAT1+'</td>';
            out += '<td width=5%>' + arr[i].SAT2+'</td>';
            out += '<td width=5%>' + arr[i].SAT3+'</td>';
            out += '<td width=5%>' + arr[i].SAT4+'</td>';
            out += '<td width=5%>' + yesno[arr[i].doesNotUseGateway]+'</td>';
            out += '<td width=5%>' + arr[i].lo_offset+'</td>';
            out += '<td width=5%>' + demodsList[arr[i].Demod]+'</td>';
            out += '<td width=5%>' + yesno[arr[i].Isdemod]+'</td>';
            out += '</tr></table></div>';
         
            out += '</div>';
        }
        
        
        
    }
     out += '</div>';
    out += '</div>';
    document.getElementById("mvTable").innerHTML = out;
}



function build_select(arr, key,val, selected, name, id, nullval){
    out = '<div class="form-group"><label for="sel1">' + name +'</label>';
    out +='<select class="form-control" onchange="formsubmit(editLineForm)" name="'+id+'">';
    var i;
    out += '<option value="'+nullval+'">No Selection</option>';
    for(i = 0; i < arr.length; i++) {
        if (arr[i][key] === selected) {
            out += '<option selected value="'+ arr[i][key] +'">'+ arr[i][val] +'</option>';
        }else{
            out += '<option value="'+ arr[i][key] +'">'+ arr[i][val] +'</option>';
            }
        
        
    }
    out += '  </select></div>';
    return out;
}
function satListSelect(selected, name, id){
    out = '<div class="form-group"><label for="sel1">' + name +'</label>';
    out +='<select class="form-control" onchange="formsubmit(editLineForm)" name="'+id+'">';
    var i;
    var mtx_name_kv = makeKeyVal(mtx_names, "id", "mtxName");
    out += '<option value="">No Selection</option>';
    for(i = 0; i < satlist.length; i++) {
        if (satlist[i]["sat"] === selected) {
            out += '<option selected value="'+ satlist[i]["sat"] +'">'+ satlist[i]["sat"] +'</option>';
        }else{
            out += '<option value="'+ satlist[i]["sat"] +'">'+ satlist[i]["sat"] +'</option>';
            }
        
        
    }
    out += '<option value="null" disabled>-----</option>';
    for(i = 0; i < mtx_out_lband.length; i++) {
        var namestring = mtx_name_kv[mtx_out_lband[i]["matrixid"]] + mtx_out_lband[i]["name"];
        if (namestring === selected) {
            out += '<option selected value="'+ namestring +'">'+ mtx_name_kv[mtx_out_lband[i]["matrixid"]] +"/"+  mtx_out_lband[i]["name"]; +'</option>';
        }else{
            out += '<option value="'+ namestring +'">'+ mtx_name_kv[mtx_out_lband[i]["matrixid"]] +"/"+  mtx_out_lband[i]["name"]; +'</option>';
            }
        
        
    }
    out += '  </select></div>';
    return out;
}
function makecheckbox(label, name, checked){
    var out = '<div class="checkbox"><label><input type="checkbox"';
    if(checked){
        out += ' Checked ';
    }
    out += ' name="'+name+'">'+label+'</label></div>';
    return out;
}
function cancelEdit(){
    populateTable(irds);
}
function editLine(line){
    //populateTable(irds);
    filter();
    var out = "";
    var i;
    var arr = irds
    var mtx_out_sdi_kv = makeKeyVal(mtx_out_sdi, "name", "PRIMARY");
    var mtx_in_sdi_kv = makeKeyVal(mtx_in_sdi, "name", "PRIMARY");
    var mtx_out_asi_kv = makeKeyVal(mtx_out_asi, "name", "PRIMARY");
    var mtx_in_asi_kv = makeKeyVal(mtx_in_asi, "name", "PRIMARY");
    var equipmentkv = makeKeyVal(irds, "id", "labelnamestatic");

    for(i = 0; i < arr.length; i++) {
        if ( arr[i].id ==  line) {
            out += '<div class="col-sm-2"><a href="#" class="btn btn-default"  onclick="cancelEdit()" role="button">Cancel</a> </div>';
            out += '<div class="col-sm-10">Equipment '+ arr[i].id+'<form id="editLineForm" action ="#" method="post" onsubmit=formsubmit(editLineForm) class="form-inline" role="form"><div class="form-group">';
            out += '<input type="hidden" name="formName", value = "updateIRD"><input type="hidden" name="equipmentID", value = "'+ arr[i].id+'"></div>';
            out += '<div class="form-group"><label for="name">Name</label><input type="text" class="form-control" name="name" onchange="formsubmit(editLineForm)" value="'+ arr[i].name+'"></div>';
            out += '<div class="form-group"><label for="ip">IP</label><input type="text" class="form-control" name="ip" onchange="formsubmit(editLineForm)" value="'+ arr[i].ip+'"></div>';
            out += '<div class="form-group"><label for="labelnamestatic">labelnamestatic</label><input type="text" class="form-control" name="labelnamestatic" onchange="formsubmit(editLineForm)" value="'+ arr[i].labelnamestatic+'"></div>';
            out += '<div class="form-group"><label for="MulticastIp">MulticastIp</label><input type="text" class="form-control" name="MulticastIp" onchange="formsubmit(editLineForm)" value="'+ arr[i].MulticastIp+'"></div>';
            // Assuming the equipment is ASI in SDI out
            out += build_select(mtx_out_asi, "PRIMARY", "name",mtx_out_asi_kv[arr[i].InMTXName], "ASI Input", "InMTXName", "null" );
            out += build_select(mtx_in_sdi, "PRIMARY", "name",mtx_in_sdi_kv[arr[i].OutMTXName], "SDI Output", "OutMTXName", "null" );
            out += satListSelect(arr[i].SAT1, "SAT1", "SAT1");
            out += satListSelect(arr[i].SAT2, "SAT2", "SAT2");
            out += satListSelect(arr[i].SAT3, "SAT3", "SAT3");
            out += satListSelect(arr[i].SAT4, "SAT4", "SAT4");
            out += makecheckbox("Does not use TVIPS Gateway", "doesNotUseGateway", (arr[i].doesNotUseGateway ==1))
            out += build_select(demods, "id", "labelnamestatic",arr[i].Demod, "Demod", "Demod",0 );
            out += makecheckbox("Equipment is a demod", "Isdemod", (arr[i].Isdemod ==1))
            out += '</form><button onclick="formsubmitThenReload(editLineForm)"  class="btn btn-default">Submit</button></div>';
           
           
            document.getElementById("equip" + arr[i].id).innerHTML = out;
            
        }
    }
    
}


