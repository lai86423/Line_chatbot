
var c = 10;
var p =parseInt(((c**5*(c+1))+c**2+1)*c**4, 2);
c=c*c;
x = p + String.fromCharCode(--c, ++c+11, c,++c);

console.log(x);
