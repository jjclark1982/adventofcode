var input = document.body.innerText.split("\n");
var rows = input.map((text)=>text.split(/\s+/));

function sum(a,b){
    return a+b
}

function checksum(row){
  var min = Math.min.apply(null, row);
  var max = Math.max.apply(null, row);
  return max-min;
}

rows.map(checksum).reduce(sum)

function checksum2(row) {
  for (var i=0; i<row.length; i++) {
    for (var j=0; j<row.length; j++) {
      if (i==j) continue;
      if (row[i] % row[j] == 0) {
        return row[i] / row[j];
      }
    }
  }
  return 0;
}

rows.map(checksum2).reduce(sum)
