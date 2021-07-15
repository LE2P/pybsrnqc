var inds = cb_obj.indices;
var d1 = bsrnData.data;
var d2 = bsrnSelect.data;
var keys = Object.keys(d2)

for(var j in keys){
  var key = keys[j]
  d2[key] = [];
  for (var i = 0; i < inds.length; i++) {
    d2[key].push(d1[key][inds[i]]);
  }
}

bsrnSelect.change.emit();
