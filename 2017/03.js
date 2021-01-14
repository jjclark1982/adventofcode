function prob3(input) {
    var side = Math.floor(Math.sqrt(input));
    var radius = Math.floor(side/2);

    var distCorner = (input - side*side);
    while(distCorner > (side+1)) {
        distCorner -= (side+1);
    }

    var distCenter = Math.abs(distCorner - radius);
    return distCenter+radius;
}
prob3(368078);


var values = [0, 1];
function findValue(i) {
    // given an index, find adjacent indices
    // then for each adjacent index, add
    // (values[j] || 0)
    var side = Math.floor(Math.sqrt(input));
    var radius = Math.floor(side/2);

    var distCorner = (input - side*side);
}
for (var i=values.length; i<100; i++) {
    values[i] = findValue(i);
}
806 880 931
