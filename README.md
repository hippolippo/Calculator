# Calculator
This is a calculator written in python with the goal of supporting all features I can think of

Running Expression.py will start a calculator REPL

REPL commands:
<ul>
<li>#EXIT or #QUIT: exits the repl</li>
<li>#SETVAR x: will allow you to set the value of the variable specified for use in later expressions</li>
<li>Coming Soon: #DEFINE func x: will allow you to define a function to call in later expressions</li>
<li>Coming Soon: #IMPORT module: import constants or functions into the environment</li>
</ul>

Calculator commands:
<ul>
<li>x + y: adds x and y</li>
<li>x - y: subtracts x and y</li>
<li>x * y: multiplies x and y</li>
<li>x / y: divides x and y</li>
<li>x ^ y: raises x to the yth power</li>
<li>fun x: calls a function "fun" with the parameter x</li>
<li>let x = y in z: evaluates z with the variable x being set to y</li>
<li>let fun x = y in z: evaulates z with the function "fun" being set to y with the parameter x</li>
<li>(x): evaluates x before any surrounding operations</li>
</ul>

Built-in functions:
<ul>
<li>sin</li>
<li>sinh</li>
<li>asin</li>
<li>asinh</li>
<li>cos</li>
<li>cosh</li>
<li>acos</li>
<li>acosh</li>
<li>tan</li>
<li>tanh</li>
<li>atan</li>
<li>atanh</li>
<li>ceil</li>
<li>abs</li>
<li>floor</li>
<li>trunc</li>
<li>ln</li>
<li>lg</li>
<li>log</li>
<li>sqrt</li>
<li>degrees</li>
<li>radians</li>
<li>erf</li>
<li>gamma</li>
<li>pi</li>
<li>e</li>
<li>tau</li>
</ul>