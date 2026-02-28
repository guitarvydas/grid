let parameters = {};
function pushParameter (name, v) {
    if (!parameters [name]) {
        parameters [name] = [];
    }
    parameters [name].push (v);
}
function popParameter (name) {
    parameters [name].pop ();
}
function getParameter (name) {
    let top = parameters [name].pop ();
    parameters [name].push (top);
    return top;
}


let _rewrite = {

main : function (stuff,) {
enter_rule ("main");
    set_return (`${stuff.rwr ().join ('')}`);
return exit_rule ("main");
},
stuff : function (x,) {
enter_rule ("stuff");
    set_return (`${x.rwr ()}`);
return exit_rule ("stuff");
},
keyword : function (kw,) {
enter_rule ("keyword");
    set_return (`${downcase (`${kw.rwr ()}`,)}`);
return exit_rule ("keyword");
},
string : function (dqL,cs,dqR,) {
enter_rule ("string");
    set_return (`"${cs.rwr ().join ('')}"`);
return exit_rule ("string");
},
strchar_escapedquote : function (dq1,dq2,) {
enter_rule ("strchar_escapedquote");
    set_return (`\"`);
return exit_rule ("strchar_escapedquote");
},
strchar_other : function (c,) {
enter_rule ("strchar_other");
    set_return (`${c.rwr ()}`);
return exit_rule ("strchar_other");
},
ident : function (c,tailcs,) {
enter_rule ("ident");
    set_return (`${downcase (`${c.rwr ()}${tailcs.rwr ().join ('')}`,)}`);
return exit_rule ("ident");
},
idtail : function (c,) {
enter_rule ("idtail");
    set_return (`${c.rwr ()}`);
return exit_rule ("idtail");
},
comment : function (q,cs,nl,) {
enter_rule ("comment");
    set_return (`⎝${cs.rwr ().join ('')}⎠${incnl ()}`);
return exit_rule ("comment");
},
nl : function (c,) {
enter_rule ("nl");
    set_return (`${incnl ()}\n`);
return exit_rule ("nl");
},
_terminal: function () { return this.sourceString; },
_iter: function (...children) { return children.map(c => c.rwr ()); }
}
