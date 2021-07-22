var data = bsrnSelect.data;
var out = JSON.stringify(data)
var file = new Blob([out], { type: "text/plain" });
var elem = document.createElement("a");
elem.href = URL.createObjectURL(file);
elem.download = "selected-data.json";
document.body.appendChild(elem);
elem.click();
document.body.removeChild(elem);
