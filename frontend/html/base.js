

moment.tz.setDefault("Etc/UTC");

function getBrowserName() {
  var browserName = '';
  var userAgent = navigator.userAgent;
  (typeof InstallTrigger !== 'undefined') && (browserName = 'Firefox');
  ( /* @cc_on!@*/ false || !!document.documentMode) && (browserName = 'IE');
  (!!window.chrome && userAgent.match(/OPR/)) && (browserName = 'Opera');
  (!!window.chrome && userAgent.match(/Edge/)) && (browserName = 'Edge');
  (!!window.chrome && !userAgent.match(/(OPR|Edge)/)) && (browserName = 'Chrome');

  /**
   * Expected returns
   * Firefox, Opera, Edge, Chrome
   */
  return browserName;
}

function updateText(id, text){
    if ($(id).text != text){
        $(id).text(text);
    }
    
}
function build_basic_select(arr, label, id, usesDiv, cls) {
    usesDiv = usesDiv || 0;
    cls = cls || "selectpicker";

    out = "";
    if (usesDiv) {
        out += '<div class="form-group">';
    }

    out += '<label for="sel1">' + label + '</label>';
    out += '<select class="' + cls + '" id="' + id + '">';
    var i;
    if (cls == "combobox") {
        out += '<option value=""></option>';
    } else {
        out += '<option value="">No Selection</option>';
    }
    for (i = 0; i < arr.length; i++) {
        out += '<option value="' + arr[i] + '">' + arr[i] + '</option>';
    }

    out += '  </select>';
    if (usesDiv) {
        out += '</div>';
    }

    return out;
}

function  build_combobox(arr, key,val, selected, label, id, usesDiv, cls, nullValue){
    usesDiv = usesDiv || 0;
    cls = cls || "selectpicker";
    nullValue = nullValue || "";
    out = "";
    if (usesDiv) {
        out += '<div class="form-group">';
    }
    out += '<label for="sel1">' + label + '</label>';
    out += '<select class="' + cls + '" id="' + id + '" name="' + id + '">';
    var i;
    if (cls == "combobox") {
        out += '<option value="'+nullValue+'"></option>';
    } else {
        out += '<option value="'+nullValue+'">No Selection</option>';
    }
    for(i = 0; i < arr.length; i++) {
        if (arr[i][key] === selected) {
            out += '<option selected value="'+ arr[i][key] +'">'+ arr[i][val] +'</option>';
        }else{
            out += '<option value="'+ arr[i][key] +'">'+ arr[i][val] +'</option>';
        }


    }
    out += '  </select>';
    if (usesDiv) {
        out += '</div>';
    }
    return out;
}
