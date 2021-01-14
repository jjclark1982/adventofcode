var input = document.body.innerText.trim();
var sum = 0;
for (i = 0; i < input.length; i++) {
  var c1 = input[i];
  var c2 = input[i+1 % input.length];
  if (c1 === c2) { sum += parseInt(c1) }
};
sum
